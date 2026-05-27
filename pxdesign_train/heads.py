"""
Distogram heads for PXDesign-d training.

The technical report (p. 24) says PXDesign-d adds a distogram loss "on projected
token embeddings". The released config (`PXDesign/pxdesign/configs/configs_base.py`)
declares two heads but instantiates neither — both are commented out in
`pxdesign/model/pxdesign.py` (the released build is inference-only):

  design_distogram_head:           c_z=128,  no_bins=64
  design_diffusion_distogram:      c_z=768,  no_bins=64

The 768 matches the DiffusionModule's `c_token=768` token embedding, so
`design_diffusion_distogram` is the per-step diffusion-token version mentioned
in the report. The 128-dim head operates on the conditioning pair `z` from
`DesignConditionEmbedder`.

This module ships both. The composite loss uses both (or just the conditioning
one if no diffusion-token embedding is supplied).
"""
from typing import Optional

import torch
import torch.nn as nn

from protenix.model.modules.primitives import LinearNoBias


class DesignDistogramHead(nn.Module):
    """Distogram on the conditioning pair embedding z ([..., N_token, N_token, c_z]).

    Symmetrises z, projects to no_bins logits. Cheap and always available because
    z comes straight out of `DesignConditionEmbedder` — no DiffusionModule hooks
    needed. Matches the `design_distogram_head` config block.
    """

    def __init__(self, c_z: int = 128, no_bins: int = 64) -> None:
        super().__init__()
        self.no_bins = no_bins
        self.proj = LinearNoBias(in_features=c_z, out_features=no_bins)

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        # Symmetrise the pair embedding before projection (AF2/3 convention).
        z = 0.5 * (z + z.transpose(-2, -3))
        return self.proj(z)  # [..., N_token, N_token, no_bins]


class DesignDiffusionDistogramHead(nn.Module):
    """Distogram on projected diffusion-module token embeddings.

    The report's "projected token embeddings" phrase implies the head reads from
    the per-step token features produced inside the DiffusionModule (c_token=768).
    We turn them into pair logits via outer-sum + linear, then symmetrise.

    NOTE: extracting these token embeddings from Protenix's `DiffusionModule`
    requires either subclassing it or hooking its internal transformer output —
    the upstream class only returns the final coordinate update. Wiring this in
    is part of piece 4 (the data/model integration). For piece 2 we build the
    head module itself so the parameter shapes match the config block.
    """

    def __init__(self, c_token: int = 768, no_bins: int = 64) -> None:
        super().__init__()
        self.no_bins = no_bins
        # outer-sum -> linear is the simplest stable choice; alternative is
        # outer-concat -> linear (2*c_token in). Matches AF2 distogram head shape.
        self.proj_a = LinearNoBias(in_features=c_token, out_features=c_token)
        self.proj_b = LinearNoBias(in_features=c_token, out_features=c_token)
        self.out = LinearNoBias(in_features=c_token, out_features=no_bins)

    def forward(self, tokens: torch.Tensor) -> torch.Tensor:
        """
        Args:
            tokens: per-token diffusion features [..., N_token, c_token]
        Returns:
            logits [..., N_token, N_token, no_bins]
        """
        a = self.proj_a(tokens)  # [..., N_token, c_token]
        b = self.proj_b(tokens)
        pair = a[..., :, None, :] + b[..., None, :, :]  # outer-sum
        pair = 0.5 * (pair + pair.transpose(-2, -3))     # symmetrise
        return self.out(torch.relu(pair))                # [..., N_token, N_token, no_bins]
