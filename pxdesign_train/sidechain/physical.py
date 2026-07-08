"""Physical regularization losses for side chains.

Used when the predicted residue type != GT type (so atom-level coordinate MSE is
undefined): we fall back to physics — chemical bond lengths, bond angles, steric
clashes, and (stub) rotamer plausibility. Also usable as an auxiliary term when
types match. All terms are differentiable and finite.

This deliverable ships bond/angle/clash; `rotamer` is an intentional stub
(returns 0) per the spec — FangWu flagged the exact rotamer/physical
formulation as not finalized.
"""
from typing import Optional

import torch


def bond_loss(
    coords: torch.Tensor,     # [B, A, 3]
    bond_idx: torch.Tensor,   # [nb, 2] long
    ideal: torch.Tensor,      # [nb] ideal bond lengths (Angstrom)
) -> torch.Tensor:
    """Mean squared deviation of bonded pair distances from ideal lengths."""
    if bond_idx.numel() == 0:
        return coords.sum() * 0.0
    i, j = bond_idx[:, 0], bond_idx[:, 1]
    d = (coords[:, i] - coords[:, j]).norm(dim=-1)   # [B, nb]
    return ((d - ideal) ** 2).mean()


def angle_loss(
    coords: torch.Tensor,      # [B, A, 3]
    angle_idx: torch.Tensor,   # [na, 3] long (i, j-centre, k)
    ideal_cos: torch.Tensor,   # [na] cos of ideal angle
    eps: float = 1e-8,
) -> torch.Tensor:
    """Mean squared deviation of cos(angle) at centre atom j from ideal."""
    if angle_idx.numel() == 0:
        return coords.sum() * 0.0
    i, j, k = angle_idx[:, 0], angle_idx[:, 1], angle_idx[:, 2]
    v1 = coords[:, i] - coords[:, j]
    v2 = coords[:, k] - coords[:, j]
    cos = (v1 * v2).sum(-1) / (v1.norm(dim=-1) * v2.norm(dim=-1) + eps)  # [B, na]
    return ((cos - ideal_cos) ** 2).mean()


def clash_loss(
    coords: torch.Tensor,     # [B, A, 3]
    clash_dist: float = 2.0,
    valid_mask: Optional[torch.Tensor] = None,  # [B, A] bool
) -> torch.Tensor:
    """Penalise non-adjacent atom pairs closer than `clash_dist` (relu^2).

    Excludes self-pairs (and, when `valid_mask` given, padded atoms). This is a
    simplified steric term over all i<j pairs — bonded neighbours are tolerated
    because ideal bond lengths (~1.3-1.5 Å) exceed typical clash thresholds set
    below the van-der-Waals sum.
    """
    B, A, _ = coords.shape
    if A < 2:
        return coords.sum() * 0.0
    d = torch.cdist(coords, coords)             # [B, A, A]
    iu = torch.triu_indices(A, A, offset=1, device=coords.device)
    dij = d[:, iu[0], iu[1]]                     # [B, npair]
    pen = torch.relu(clash_dist - dij) ** 2
    if valid_mask is not None:
        pv = valid_mask[:, iu[0]] & valid_mask[:, iu[1]]
        pen = pen * pv.to(pen.dtype)
        denom = pv.sum().clamp_min(1).to(pen.dtype)
        return pen.sum() / denom
    return pen.mean()


def _dihedral(p0, p1, p2, p3, eps: float = 1e-8) -> torch.Tensor:
    """Signed dihedral angle (radians) of atom quadruples. Each p*: [..., 3]."""
    b0 = p0 - p1
    b1 = p2 - p1
    b2 = p3 - p2
    b1n = b1 / (b1.norm(dim=-1, keepdim=True) + eps)
    v = b0 - (b0 * b1n).sum(-1, keepdim=True) * b1n
    w = b2 - (b2 * b1n).sum(-1, keepdim=True) * b1n
    x = (v * w).sum(-1)
    y = (torch.cross(b1n, v, dim=-1) * w).sum(-1)
    return torch.atan2(y, x)


def rotamer_loss(
    coords: torch.Tensor,          # [B, A, 3]
    torsion_idx: torch.Tensor,     # [nt, 4] long (i,j,k,l defining a chi torsion)
    targets: torch.Tensor,         # [n_rot] canonical staggered angles (radians)
) -> torch.Tensor:
    """Periodic penalty pulling each side-chain torsion toward the nearest
    canonical staggered rotamer value (min over targets of 1-cos(theta-target))."""
    if torsion_idx.numel() == 0:
        return coords.sum() * 0.0
    i, j, k, l = torsion_idx[:, 0], torsion_idx[:, 1], torsion_idx[:, 2], torsion_idx[:, 3]
    theta = _dihedral(coords[:, i], coords[:, j], coords[:, k], coords[:, l])  # [B, nt]
    # distance to each canonical target, periodic via cosine
    diff = theta.unsqueeze(-1) - targets.view(1, 1, -1)          # [B, nt, n_rot]
    pen = (1.0 - torch.cos(diff)).min(dim=-1).values             # [B, nt]
    return pen.mean()


def contact_loss(
    coords: torch.Tensor,              # [B, A, 3] side-chain atoms
    backbone_coords: torch.Tensor,     # [B, M, 3] backbone atoms
    valid_mask: Optional[torch.Tensor] = None,  # [B, A] bool
    max_dist: float = 8.0,
    eps: float = 1e-8,
) -> torch.Tensor:
    """Compatibility term: each side-chain atom should stay near some backbone
    atom (soft hinge on its nearest-backbone distance beyond `max_dist`) —
    discourages side chains flying away from the fold. Won't distort valid
    geometry (only penalises runaway atoms)."""
    d = torch.cdist(coords, backbone_coords)           # [B, A, M]
    nearest = d.min(dim=-1).values                     # [B, A]
    pen = torch.relu(nearest - max_dist) ** 2
    if valid_mask is not None:
        m = valid_mask.to(pen.dtype)
        return (pen * m).sum() / (m.sum() + eps)
    return pen.mean()


def physical_loss(
    coords: torch.Tensor,
    bond_idx: Optional[torch.Tensor] = None,
    ideal_bond: Optional[torch.Tensor] = None,
    angle_idx: Optional[torch.Tensor] = None,
    ideal_cos: Optional[torch.Tensor] = None,
    torsion_idx: Optional[torch.Tensor] = None,
    rotamer_targets: Optional[torch.Tensor] = None,
    backbone_coords: Optional[torch.Tensor] = None,
    valid_mask: Optional[torch.Tensor] = None,
    weights: Optional[dict] = None,
) -> dict:
    """Aggregate physical loss. Terms present only when their inputs are given.
    Returns dict with bond/angle/clash/rotamer/contact/total."""
    w = {"bond": 1.0, "angle": 1.0, "clash": 1.0, "rotamer": 1.0, "contact": 1.0}
    if weights:
        w.update(weights)
    zero = coords.sum() * 0.0
    b = bond_loss(coords, bond_idx, ideal_bond) if bond_idx is not None else zero
    a = angle_loss(coords, angle_idx, ideal_cos) if angle_idx is not None else zero
    c = clash_loss(coords, valid_mask=valid_mask)
    r = (rotamer_loss(coords, torsion_idx, rotamer_targets)
         if torsion_idx is not None and rotamer_targets is not None else zero)
    ct = (contact_loss(coords, backbone_coords, valid_mask)
          if backbone_coords is not None else zero)
    total = (w["bond"] * b + w["angle"] * a + w["clash"] * c
             + w["rotamer"] * r + w["contact"] * ct)
    return {"bond": b, "angle": a, "clash": c, "rotamer": r, "contact": ct, "total": total}
