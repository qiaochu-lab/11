"""
Warm-start fine-tuning helpers.

Fine-tuning is just training with a non-empty `load_checkpoint_path` and (very
strongly recommended) `load_strict=False`. The `PXDesignTrainer` already
supports this — this module is mostly a place to document the workflow and
provide one convenience wrapper.

Typical workflows:

  - **Continue training from the released PXDesign-d checkpoint**:
    Use `pxdesign_v0.1.0.pt`. Set `load_strict=False` because our trainer adds
    head modules (the distogram heads) that the released checkpoint doesn't
    include — those will initialize randomly, everything else loads in place.

  - **Warm-start from a Protenix base checkpoint**:
    The diffusion module weights are shape-compatible. Almost all parameters
    transfer; the design-specific `design_condition_embedder.*` modules
    initialize randomly. Per the report this is NOT how ByteDance trained
    PXDesign-d (they trained from scratch), but it's a reasonable fine-tuning
    shortcut for downstream experiments.

Recommended fine-tune hyperparameters (vs the report's training defaults):
  - lr: 1e-5 instead of 5e-4 (10–50× lower)
  - warmup_steps: 100–500 instead of 2000
  - max_steps: 1k–10k instead of 100k
  - keep loss weights from eq. 4 unchanged
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional

import torch

from pxdesign_train.runner.trainer import (
    PXDesignTrainer,
    TrainerComponents,
)


def make_finetune_configs(
    base_configs: Any,
    *,
    lr: float = 1e-5,
    warmup_steps: int = 200,
    max_steps: int = 5_000,
    ema_decay: float = 0.999,
) -> Any:
    """Return a deep-copy of `base_configs` with fine-tune-appropriate values.

    Use this as `configs` in `train_from_components(..., configs=...)`.
    """
    cfg = deepcopy(base_configs)
    if hasattr(cfg, "training"):
        cfg.training.lr = lr
        cfg.training.warmup_steps = warmup_steps
        cfg.training.max_steps = max_steps
        cfg.training.ema_decay = ema_decay
    else:
        # dict-style configs (before parse_configs())
        cfg["training"]["lr"] = lr
        cfg["training"]["warmup_steps"] = warmup_steps
        cfg["training"]["max_steps"] = max_steps
        cfg["training"]["ema_decay"] = ema_decay
    if hasattr(cfg, "load_strict"):
        cfg.load_strict = False
    else:
        cfg["load_strict"] = False
    return cfg


def finetune_from_components(
    configs: Any,
    components: TrainerComponents,
    *,
    load_checkpoint_path: str,
    device: Optional[torch.device] = None,
    checkpoint_dir: Optional[str] = None,
    rank: int = 0,
    world_size: int = 1,
    max_steps: Optional[int] = None,
) -> PXDesignTrainer:
    """Convenience wrapper around `train_from_components` for the fine-tune case.

    Equivalent to `train_from_components(..., load_checkpoint_path=...)` but
    enforces `load_strict=False` on the configs (the released
    `pxdesign_v0.1.0.pt` won't have the training-side distogram heads, so a
    strict load would fail).
    """
    if hasattr(configs, "load_strict"):
        configs.load_strict = False
    elif isinstance(configs, dict) and "load_strict" in configs:
        configs["load_strict"] = False

    trainer = PXDesignTrainer(
        configs=configs,
        components=components,
        device=device,
        rank=rank,
        world_size=world_size,
        checkpoint_dir=checkpoint_dir,
        load_checkpoint_path=load_checkpoint_path,
    )
    trainer.run(max_steps=max_steps)
    return trainer
