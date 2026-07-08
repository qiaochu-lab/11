"""Local-frame side-chain coordinate loss.

Primary side-chain supervision: MSE between predicted and GT side-chain
coordinates expressed in the residue-local frame (SideCraft spec eq. L_sc^local).
Masked and averaged over valid side-chain atoms only.
"""
import torch


def sidechain_local_loss(
    pred_local: torch.Tensor,   # [..., A, 3]
    gt_local: torch.Tensor,     # [..., A, 3]
    mask: torch.Tensor,         # [..., A] bool/float
    eps: float = 1e-6,
) -> torch.Tensor:
    """Masked mean squared error over valid side-chain atoms. Returns scalar.

    Broadcasting-robust: when `pred_local` carries a leading per-sigma axis
    (`[N_sample, L, A, 3]`) but `gt_local`/`mask` are per-token (`[L, A, ...]`),
    the squared error broadcasts over the sample axis. We expand the mask to the
    broadcasted shape so the denominator counts the SAME atoms the numerator sums
    — otherwise the loss would scale with N_sample. This is a masked mean, so its
    scale is invariant to N_sample.
    """
    se = ((pred_local - gt_local) ** 2).sum(dim=-1)   # [..., A] (may broadcast)
    m = mask.to(se.dtype).expand_as(se)               # match numerator's coverage
    return (se * m).sum() / (m.sum() + eps)
