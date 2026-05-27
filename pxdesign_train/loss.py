"""
PXDesign-d composite training loss.

Equation 4 from the PXDesign technical report (p. 24):

    L = (0.03 · L_disto + 1.0 · L_LDDT) · 1{σ̂ < 4 Å}  +  4.0 · L_MSE

- L_MSE is over all heavy atoms (target included — the report explicitly notes
  target coords are NOT frozen during training).
- L_LDDT and L_disto are gated by the per-sample σ being < 4 Å — only at low
  noise do we ask the model to be geometrically tight.

We reuse Protenix's `SmoothLDDTLoss` (Algorithm 27 in AF3) and use the
distogram heads from `heads.py`. We do NOT use Protenix's `MSELoss` directly:
that class applies a `weighted_rigid_align` and per-type weights (DNA/RNA/ligand)
which the PXDesign report does not mention. We write a plain heavy-atom MSE
matching the report's wording.
"""
from typing import Any, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

from protenix.model.loss import SmoothLDDTLoss
from protenix.metrics.rmsd import weighted_rigid_align


class PXDesignLoss(nn.Module):
    """Composite loss for PXDesign-d training.

    Args:
        weight_mse:    coefficient on MSE term (4.0 per report eq. 4)
        weight_lddt:   coefficient on smooth-LDDT term (1.0 per report)
        weight_disto:  coefficient on distogram term (0.03 per report)
        sigma_low_threshold: σ-mask cutoff in Å (4.0 per report).
            LDDT and distogram terms are zeroed when σ ≥ this value.
        no_bins:       number of distogram bins (64).
        min_bin:       distogram lower edge in Å (matches Protenix default).
        max_bin:       distogram upper edge in Å.
        lddt_radius:   neighbour radius used for the LDDT mask (15 Å for protein).
        align_before_mse: rigid-align GT to prediction before MSE (AF3 standard).
    """

    def __init__(
        self,
        weight_mse: float = 4.0,
        weight_lddt: float = 1.0,
        weight_disto: float = 0.03,
        sigma_low_threshold: float = 4.0,
        no_bins: int = 64,
        min_bin: float = 2.3125,
        max_bin: float = 21.6875,
        lddt_radius: float = 15.0,
        align_before_mse: bool = True,
        eps: float = 1e-6,
    ) -> None:
        super().__init__()
        self.weight_mse = weight_mse
        self.weight_lddt = weight_lddt
        self.weight_disto = weight_disto
        self.sigma_low_threshold = sigma_low_threshold
        self.no_bins = no_bins
        self.min_bin = min_bin
        self.max_bin = max_bin
        self.lddt_radius = lddt_radius
        self.align_before_mse = align_before_mse
        self.eps = eps

        # Protenix's SmoothLDDTLoss takes Python None to mean "no reduction".
        self.smooth_lddt = SmoothLDDTLoss(reduction=None)

    @staticmethod
    def _build_lddt_mask(
        true_coordinate: torch.Tensor,
        coordinate_mask: torch.Tensor,
        radius: float,
    ) -> torch.Tensor:
        """Returns [..., N_atom, N_atom] mask of atom pairs within `radius` Å in GT."""
        d = torch.cdist(true_coordinate, true_coordinate)  # [..., N_atom, N_atom]
        within = (d < radius).to(d.dtype)
        pair_valid = coordinate_mask[..., :, None] * coordinate_mask[..., None, :]
        # Exclude self-pairs.
        n = within.shape[-1]
        eye = torch.eye(n, device=d.device, dtype=d.dtype)
        return within * pair_valid * (1 - eye)

    @staticmethod
    def _bin_distances(
        coords: torch.Tensor,
        rep_atom_mask: torch.Tensor,
        no_bins: int,
        min_bin: float,
        max_bin: float,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Compute one-hot distogram labels and pair-valid mask on representative atoms."""
        rep = rep_atom_mask.bool()
        tok_coords = coords[..., rep, :]                # [..., N_token, 3]
        d = torch.cdist(tok_coords, tok_coords)         # [..., N_token, N_token]
        boundaries = torch.linspace(min_bin, max_bin, steps=no_bins - 1, device=d.device)
        bins = torch.sum(d.unsqueeze(-1) > boundaries, dim=-1)  # [..., N_token, N_token]
        return F.one_hot(bins, no_bins).to(coords.dtype), torch.ones_like(d, dtype=coords.dtype)

    def _mse_term(
        self,
        pred: torch.Tensor,                  # [..., N_sample, N_atom, 3]
        gt_aug: torch.Tensor,                # [..., N_sample, N_atom, 3]
        coordinate_mask: torch.Tensor,       # [..., N_atom]
    ) -> torch.Tensor:
        """Heavy-atom MSE, mean over atoms, mean over samples. Returns [...]."""
        if self.align_before_mse:
            # AF3-style rigid-align GT to prediction with uniform weights.
            with torch.no_grad():
                w = coordinate_mask.float()
                w_sample = w[..., None, :].expand_as(pred[..., 0]).contiguous()
                with torch.amp.autocast("cuda", enabled=False):
                    gt_aligned = weighted_rigid_align(
                        x=gt_aug.float(),
                        x_target=pred.float(),
                        atom_weight=w_sample.float(),
                        stop_gradient=True,
                    ).to(pred.dtype).detach()
        else:
            gt_aligned = gt_aug

        se = ((pred - gt_aligned) ** 2).sum(dim=-1)             # [..., N_sample, N_atom]
        mask = coordinate_mask[..., None, :]                    # [..., 1, N_atom]
        per_sample = (se * mask).sum(dim=-1) / (mask.sum(dim=-1) + self.eps)  # [..., N_sample]
        return per_sample.mean(dim=-1)                          # [...]

    def _distogram_term(
        self,
        logits: torch.Tensor,                # [..., N_token, N_token, no_bins]
        true_coord: torch.Tensor,            # [..., N_atom, 3]
        coordinate_mask: torch.Tensor,       # [..., N_atom]
        rep_atom_mask: torch.Tensor,         # [N_atom]
    ) -> torch.Tensor:
        with torch.no_grad():
            true_bins, _ = self._bin_distances(
                true_coord, rep_atom_mask, self.no_bins, self.min_bin, self.max_bin,
            )
            tok_valid = coordinate_mask[..., rep_atom_mask.bool()]      # [..., N_token]
            pair_valid = tok_valid[..., :, None] * tok_valid[..., None, :]  # [..., N_token, N_token]

        # Softmax CE per pair, masked.
        log_probs = F.log_softmax(logits.float(), dim=-1)
        per_pair_ce = -(true_bins * log_probs).sum(dim=-1)  # [..., N_token, N_token]
        per_pair_ce = per_pair_ce * pair_valid
        denom = pair_valid.sum(dim=(-1, -2)) + self.eps
        return per_pair_ce.sum(dim=(-1, -2)) / denom  # [...]

    def forward(
        self,
        pred_coordinate: torch.Tensor,       # [..., N_sample, N_atom, 3]
        gt_coordinate_aug: torch.Tensor,     # [..., N_sample, N_atom, 3]
        sigma: torch.Tensor,                 # [..., N_sample]
        coordinate_mask: torch.Tensor,       # [..., N_atom]
        rep_atom_mask: torch.Tensor,         # [N_atom]
        distogram_logits: Optional[torch.Tensor] = None,  # [..., N_token, N_token, no_bins]
    ) -> dict[str, torch.Tensor]:
        """Compute the composite loss.

        Returns a dict with keys: "loss", "mse", "lddt", "distogram", "sigma_low_frac".
        Each component is a scalar (mean over batch).
        """
        # σ-mask: 1 where sigma < threshold, else 0. Per (batch, sample).
        sigma_low = (sigma < self.sigma_low_threshold).to(pred_coordinate.dtype)

        # --- MSE (always on) ---
        mse = self._mse_term(pred_coordinate, gt_coordinate_aug, coordinate_mask)  # [...]

        # --- Smooth LDDT (gated) ---
        # SmoothLDDTLoss takes [..., N_sample, N_atom, 3] and returns per-sample lddt loss;
        # we use dense_forward + reduction='none' to get a per-batch scalar after averaging.
        # We compute LDDT under σ-mask by multiplying loss by mean σ-mask over samples.
        gt_single = gt_coordinate_aug[..., 0, :, :]  # use first-sample GT for the mask
        lddt_mask = self._build_lddt_mask(gt_single, coordinate_mask, self.lddt_radius)
        lddt_per_batch = self.smooth_lddt.dense_forward(
            pred_coordinate=pred_coordinate,
            true_coordinate=gt_single,
            lddt_mask=lddt_mask,
        )  # smooth_lddt with reduction='none' returns [...]
        # Apply σ-mask: average over samples where σ < threshold.
        gate_lddt = sigma_low.mean(dim=-1)  # [...]
        lddt = lddt_per_batch * gate_lddt

        # --- Distogram (gated) ---
        if distogram_logits is not None:
            disto = self._distogram_term(
                distogram_logits, gt_single, coordinate_mask, rep_atom_mask,
            )
            disto = disto * gate_lddt
        else:
            disto = torch.zeros_like(mse)

        total = (
            self.weight_mse * mse
            + self.weight_lddt * lddt
            + self.weight_disto * disto
        )

        return {
            "loss": total.mean(),
            "mse": mse.mean().detach(),
            "lddt": lddt.mean().detach(),
            "distogram": disto.mean().detach(),
            "sigma_low_frac": sigma_low.mean().detach(),
        }
