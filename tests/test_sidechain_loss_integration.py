"""Side-chain terms integrated into the composite PXDesignLoss."""
import os
import sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "Protenix")))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "PXDesign")))

from pxdesign_train.loss import PXDesignLoss
from pxdesign_train.sidechain.instantiate import MAX_SC, sidechain_mask


def _coord_args(n_atom=6):
    pred = torch.randn(1, n_atom, 3, requires_grad=True)  # [N_sample, N_atom, 3]
    gt = torch.randn(1, n_atom, 3)
    sigma = torch.tensor([10.0])                          # [N_sample]
    cmask = torch.ones(n_atom)
    rep = torch.zeros(n_atom, dtype=torch.bool)
    rep[::1] = True                                       # every atom is a token here
    return pred, gt, sigma, cmask, rep


def _loss():
    # Disable align + lddt + distogram so the composite reduces to a clean MSE
    # (keeps the test focused on the side-chain additions).
    return PXDesignLoss(align_before_mse=False, weight_lddt=0.0, weight_disto=0.0)


def test_backward_compat_without_sidechain_args():
    pred, gt, sigma, cmask, rep = _coord_args()
    out = _loss().forward(pred, gt, sigma, cmask, rep)
    assert "sc_local" in out and "sc_phys" in out
    assert out["sc_local"].item() == 0.0 and out["sc_phys"].item() == 0.0


def test_sidechain_local_term_contributes():
    pred, gt, sigma, cmask, rep = _coord_args()
    restypes = ["ALA", "PHE", "LYS"]
    amask = sidechain_mask(restypes)[None]                 # [1, L, MAX_SC]
    sc_pred = torch.randn(1, 3, MAX_SC, 3, requires_grad=True)
    sc_gt = torch.randn(1, 3, MAX_SC, 3)

    base = _loss().forward(pred, gt, sigma, cmask, rep)["loss"]
    out = _loss().forward(
        pred, gt, sigma, cmask, rep,
        sc_pred_local=sc_pred, sc_gt_local=sc_gt, sc_atom_mask=amask,
    )
    assert out["sc_local"].item() > 0.0
    assert out["loss"].item() > base.item()   # side-chain term adds to total
    out["loss"].backward()
    assert torch.isfinite(sc_pred.grad).all()


def test_type_match_routing_masks_coord_loss():
    pred, gt, sigma, cmask, rep = _coord_args()
    amask = sidechain_mask(["ALA", "PHE", "LYS"])[None]
    sc_pred = torch.randn(1, 3, MAX_SC, 3)
    sc_gt = torch.randn(1, 3, MAX_SC, 3)
    # No residue matches -> coord loss masked to nothing -> sc_local == 0.
    no_match = torch.zeros(1, 3, dtype=torch.bool)
    out = _loss().forward(
        pred, gt, sigma, cmask, rep,
        sc_pred_local=sc_pred, sc_gt_local=sc_gt, sc_atom_mask=amask,
        sc_type_match=no_match,
    )
    assert out["sc_local"].item() == 0.0
