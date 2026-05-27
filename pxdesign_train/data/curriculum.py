"""
Two-stage curriculum data weighter for PXDesign-d.

The PXDesign technical report (p. 24) trains in two stages:
  - Stage 1: upweight AFDB + MGnify monomer distillation data → learn protein
    backbone geometry unconditionally.
  - Stage 2: shift sampling distribution toward PDB complexes for target-
    conditioned design.

The "gradually shift" language implies a smooth transition, not a hard switch.
We support both: a linear ramp between `stage1_end_step` and `stage2_start_step`,
with a stepwise schedule recovered when the two are equal.

This module reuses Protenix's per-item weight format (one list of floats per
source dataset; `pxdesign_train` does not change how within-source weights are
calculated — `get_weighted_pdb_weight` etc. still apply). It adds:

  - `CurriculumSchedule`: a (stage1, stage2, ramp endpoints) dataclass that
    given a training step returns the per-source mixture weights.
  - `CurriculumMultiDataset`: a multi-source dataset whose merged weights are
    recomputed on demand from a source-mixture dict — Protenix's
    `WeightedMultiDataset` only supports static source weights, so we needed
    a thin variant.
  - `CurriculumSampler` (+ DDP twin): wraps the multi-dataset and calls
    `set_step()` to update weights before each epoch.

Design choice: we tie curriculum progression to the trainer's global step
counter (not epoch), because the report describes stage lengths in steps
("max_steps 100k", typical AF3 trainers). Callers pass `set_step(global_step)`
before each `__iter__()`.
"""
from dataclasses import dataclass, field
from typing import Iterator, Optional, Sequence

import torch
from torch.utils.data import Dataset, DistributedSampler, Sampler


@dataclass
class CurriculumSchedule:
    """Per-source weight schedule for the two-stage curriculum.

    Args:
        stage1: source -> weight at and before `stage1_end_step`.
        stage2: source -> weight at and after `stage2_start_step`.
        stage1_end_step: last step at which weights == stage1 exactly.
        stage2_start_step: first step at which weights == stage2 exactly. Must
            be >= stage1_end_step. When equal, the transition is a hard switch.
        sources: ordered list of source names; weights returned by `weights_at`
            follow this order. If None, inferred from `set(stage1) | set(stage2)`
            sorted alphabetically.

    Example matching the report (gradual ramp from monomer- to complex-heavy):
        CurriculumSchedule(
            stage1={"afdb": 0.5, "mgnify": 0.4, "pdb_complex": 0.1},
            stage2={"afdb": 0.1, "mgnify": 0.1, "pdb_complex": 0.8},
            stage1_end_step=40_000,
            stage2_start_step=60_000,
        )
    """

    stage1: dict[str, float]
    stage2: dict[str, float]
    stage1_end_step: int
    stage2_start_step: int
    sources: Optional[list[str]] = None

    def __post_init__(self) -> None:
        if self.stage1_end_step < 0:
            raise ValueError(f"stage1_end_step must be >= 0, got {self.stage1_end_step}")
        if self.stage2_start_step < self.stage1_end_step:
            raise ValueError(
                f"stage2_start_step ({self.stage2_start_step}) must be >= "
                f"stage1_end_step ({self.stage1_end_step})"
            )
        if self.sources is None:
            self.sources = sorted(set(self.stage1) | set(self.stage2))
        # Sanity-check that every source has weights for both stages — missing
        # entries silently get 0 weight which is rarely what the caller meant.
        missing_in_1 = [s for s in self.sources if s not in self.stage1]
        missing_in_2 = [s for s in self.sources if s not in self.stage2]
        if missing_in_1 or missing_in_2:
            raise ValueError(
                f"Schedule sources {self.sources} missing weights — stage1: "
                f"{missing_in_1}, stage2: {missing_in_2}"
            )

    def weights_at(self, step: int) -> dict[str, float]:
        """Return source -> aggregate weight at the given step."""
        if step <= self.stage1_end_step:
            return {s: float(self.stage1[s]) for s in self.sources}
        if step >= self.stage2_start_step:
            return {s: float(self.stage2[s]) for s in self.sources}
        # Linear interpolation in the ramp window.
        span = max(1, self.stage2_start_step - self.stage1_end_step)
        t = (step - self.stage1_end_step) / span
        return {
            s: (1.0 - t) * float(self.stage1[s]) + t * float(self.stage2[s])
            for s in self.sources
        }


class CurriculumMultiDataset(Dataset):
    """Multi-source dataset that exposes per-item weights with a dynamic
    per-source aggregate mass.

    Same idea as Protenix's `WeightedMultiDataset` but factored so source mass
    can be rebound at runtime. Per-item weights are normalized within source
    once at construction — applying source mass is then a simple per-bucket
    scalar multiply.

    Args:
        datasets: list of `torch.utils.data.Dataset` objects, one per source.
            Each dataset's `__getitem__(i)` returns whatever the trainer
            expects (a Protenix `BaseSingleDataset` returns a feature dict).
        source_names: ordered list of source names, parallel to `datasets`.
        per_item_weights: list parallel to `datasets`. Inner list is
            `len(datasets[i])` floats — the relative weight of each item
            within its source. Normalized to sum=1 at init.

    Notes:
        * If you want uniform sampling within a source, pass `[1.0] * len(ds)`.
        * Per-item weights are NOT renormalized when source mass changes —
          that's intentional: changing source mass should only rescale, not
          rebalance, within-source preferences.
    """

    def __init__(
        self,
        datasets: list[Dataset],
        source_names: list[str],
        per_item_weights: list[Sequence[float]],
    ) -> None:
        if not (len(datasets) == len(source_names) == len(per_item_weights)):
            raise ValueError(
                f"length mismatch: {len(datasets)} datasets, "
                f"{len(source_names)} names, {len(per_item_weights)} weight lists"
            )
        if len(set(source_names)) != len(source_names):
            raise ValueError(f"duplicate source name(s) in {source_names}")
        for ds, name, w in zip(datasets, source_names, per_item_weights):
            if len(ds) != len(w):
                raise ValueError(
                    f"source '{name}': dataset has {len(ds)} items but "
                    f"{len(w)} weights"
                )

        self.datasets = datasets
        self.source_names = list(source_names)

        # Normalize per-item weights within source. Store as a flat tensor
        # plus per-source slice offsets so the merged-weights computation is
        # one elementwise multiply.
        self._offsets = [0]
        flat_normalized = []
        self._source_idx_per_item: list[int] = []
        self._local_idx_per_item: list[int] = []
        for source_idx, (ds, w) in enumerate(zip(datasets, per_item_weights)):
            w_t = torch.as_tensor(w, dtype=torch.float64)
            s = w_t.sum().item()
            if s <= 0:
                raise ValueError(
                    f"source '{self.source_names[source_idx]}' has total per-item weight 0"
                )
            w_t = w_t / s
            flat_normalized.append(w_t)
            self._source_idx_per_item.extend([source_idx] * len(ds))
            self._local_idx_per_item.extend(range(len(ds)))
            self._offsets.append(self._offsets[-1] + len(ds))
        self._flat_normalized = torch.cat(flat_normalized)
        self._n = self._offsets[-1]

    def __len__(self) -> int:
        return self._n

    def __getitem__(self, idx: int):
        src = self._source_idx_per_item[idx]
        local = self._local_idx_per_item[idx]
        return self.datasets[src][local]

    def merged_weights(self, source_mass: dict[str, float]) -> torch.Tensor:
        """Return [N] sampling weights given per-source aggregate mass.

        Missing or zero-mass sources are simply zeroed out — sampling will
        never draw from them.
        """
        # Validate keys.
        unknown = set(source_mass) - set(self.source_names)
        if unknown:
            raise ValueError(f"unknown source name(s) in source_mass: {unknown}")

        mass = torch.zeros(len(self.source_names), dtype=torch.float64)
        for i, name in enumerate(self.source_names):
            mass[i] = float(source_mass.get(name, 0.0))

        w = self._flat_normalized.clone()
        for src_idx in range(len(self.source_names)):
            lo, hi = self._offsets[src_idx], self._offsets[src_idx + 1]
            w[lo:hi] = w[lo:hi] * mass[src_idx]
        return w


class CurriculumSampler(Sampler):
    """Single-process sampler with a curriculum-driven source mixture.

    The trainer calls `set_step(global_step)` before each new `__iter__()`
    (or relies on `set_epoch()` for the standard PyTorch dance) and the
    sampler recomputes its multinomial weights from `schedule.weights_at(step)`.

    Args:
        dataset: the `CurriculumMultiDataset`.
        schedule: the `CurriculumSchedule`.
        num_samples: number of indices to draw per epoch.
        seed: RNG seed; combined with epoch and step into the actual generator
            seed so each epoch's draw is deterministic and distinct.
        epoch_size_in_steps: how many trainer steps correspond to one
            `__iter__()` of the sampler. With epoch_size=1 (the typical AF3
            setup where each "epoch" is one step's batch), this is irrelevant
            and `set_step()` should be called directly.
    """

    def __init__(
        self,
        dataset: CurriculumMultiDataset,
        schedule: CurriculumSchedule,
        num_samples: int,
        seed: int = 0,
        epoch_size_in_steps: int = 1,
    ) -> None:
        # Validate schedule's source names cover the dataset's.
        missing = set(dataset.source_names) - set(schedule.sources)
        if missing:
            raise ValueError(
                f"schedule does not cover dataset sources {missing}; "
                f"schedule sources are {schedule.sources}"
            )
        self.dataset = dataset
        self.schedule = schedule
        self.num_samples = num_samples
        self.seed = seed
        self.epoch = 0
        self.step = 0
        self.epoch_size_in_steps = epoch_size_in_steps

    def set_epoch(self, epoch: int) -> None:
        self.epoch = epoch
        # Advance step by epoch * step-per-epoch unless caller is driving step
        # directly via `set_step()`. We don't overwrite `self.step` here.

    def set_step(self, step: int) -> None:
        self.step = step

    def _current_weights(self) -> torch.Tensor:
        mass = self.schedule.weights_at(self.step)
        return self.dataset.merged_weights(mass)

    def __iter__(self) -> Iterator[int]:
        g = torch.Generator()
        # Mix all three: base seed, epoch (in case trainer only calls
        # set_epoch), and step (in case trainer calls set_step).
        g.manual_seed(self.seed + self.epoch * 1_000_003 + self.step)
        w = self._current_weights()
        if (w > 0).sum().item() == 0:
            raise RuntimeError(
                f"No sources have positive mass at step {self.step}; "
                f"schedule={self.schedule.weights_at(self.step)}"
            )
        indices = torch.multinomial(w, self.num_samples, replacement=True, generator=g)
        return iter(indices.tolist())

    def __len__(self) -> int:
        return self.num_samples


class CurriculumDistributedSampler(DistributedSampler):
    """DDP twin of `CurriculumSampler`.

    Mirrors Protenix's `DistributedWeightedSampler` shape: sample
    `num_samples` globally and slice by rank. Same `set_step()` API.
    """

    def __init__(
        self,
        dataset: CurriculumMultiDataset,
        schedule: CurriculumSchedule,
        num_samples: int,
        num_replicas: Optional[int] = None,
        rank: Optional[int] = None,
        seed: int = 0,
    ) -> None:
        super().__init__(dataset, num_replicas=num_replicas, rank=rank, shuffle=False)
        missing = set(dataset.source_names) - set(schedule.sources)
        if missing:
            raise ValueError(
                f"schedule does not cover dataset sources {missing}"
            )
        self.dataset = dataset
        self.schedule = schedule
        self.num_samples = num_samples
        self.seed = seed
        self.epoch = 0
        self.step = 0

        import math
        self.num_samples_per_replica = math.ceil(self.num_samples / self.num_replicas)
        self.total_size = self.num_samples_per_replica * self.num_replicas

    def set_epoch(self, epoch: int) -> None:
        self.epoch = epoch

    def set_step(self, step: int) -> None:
        self.step = step

    def __iter__(self) -> Iterator[int]:
        g = torch.Generator()
        g.manual_seed(self.seed + self.epoch * 1_000_003 + self.step)
        w = self.dataset.merged_weights(self.schedule.weights_at(self.step))
        if (w > 0).sum().item() == 0:
            raise RuntimeError(
                f"No sources have positive mass at step {self.step}"
            )
        indices = torch.multinomial(w, self.total_size, replacement=True, generator=g)
        indices = indices[self.rank : self.total_size : self.num_replicas]
        return iter(indices.tolist())

    def __len__(self) -> int:
        return self.num_samples_per_replica
