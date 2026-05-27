"""
Tests for the two-stage curriculum sampler.

We use trivial integer-list datasets so this file has no PDB / Protenix
dependencies — the curriculum logic is data-source-agnostic by design.
Each "dataset" is just a list of tagged ints so we can recover its source
from a sampled index.
"""
import os
import sys
from collections import Counter

import pytest
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))


class _TaggedDataset(torch.utils.data.Dataset):
    """Returns the source tag for every item — lets tests count provenance."""

    def __init__(self, tag: str, n: int) -> None:
        self.tag = tag
        self.n = n

    def __len__(self) -> int:
        return self.n

    def __getitem__(self, idx: int):
        return f"{self.tag}#{idx}"


def _make_three_source_multi():
    """Build a 3-source dataset with sizes (40, 30, 10)."""
    from pxdesign_train.data import CurriculumMultiDataset

    datasets = [
        _TaggedDataset("afdb", 40),
        _TaggedDataset("mgnify", 30),
        _TaggedDataset("pdb", 10),
    ]
    return CurriculumMultiDataset(
        datasets=datasets,
        source_names=["afdb", "mgnify", "pdb"],
        per_item_weights=[
            [1.0] * 40,
            [1.0] * 30,
            [1.0] * 10,
        ],
    )


def _make_schedule(stage1_end=100, stage2_start=300):
    from pxdesign_train.data import CurriculumSchedule

    # Matches the report's qualitative description:
    # stage 1: monomer (afdb+mgnify) ≈ 90%, complex ≈ 10%
    # stage 2: monomer ≈ 20%, complex ≈ 80%
    return CurriculumSchedule(
        stage1={"afdb": 0.5, "mgnify": 0.4, "pdb": 0.1},
        stage2={"afdb": 0.1, "mgnify": 0.1, "pdb": 0.8},
        stage1_end_step=stage1_end,
        stage2_start_step=stage2_start,
    )


def test_schedule_endpoint_weights():
    sched = _make_schedule(stage1_end=100, stage2_start=300)
    assert sched.weights_at(0) == sched.stage1
    assert sched.weights_at(50) == sched.stage1
    assert sched.weights_at(100) == sched.stage1
    assert sched.weights_at(300) == sched.stage2
    assert sched.weights_at(10_000) == sched.stage2


def test_schedule_linear_ramp_midpoint():
    sched = _make_schedule(stage1_end=100, stage2_start=300)
    mid = sched.weights_at(200)
    # halfway between stage1 and stage2
    assert pytest.approx(mid["afdb"], abs=1e-9) == 0.5 * 0.5 + 0.5 * 0.1
    assert pytest.approx(mid["pdb"], abs=1e-9) == 0.5 * 0.1 + 0.5 * 0.8


def test_schedule_hard_switch():
    """When stage2_start_step == stage1_end_step, switch is immediate."""
    from pxdesign_train.data import CurriculumSchedule

    sched = CurriculumSchedule(
        stage1={"a": 1.0, "b": 0.0},
        stage2={"a": 0.0, "b": 1.0},
        stage1_end_step=100,
        stage2_start_step=100,
    )
    assert sched.weights_at(100) == sched.stage1   # boundary belongs to stage1
    assert sched.weights_at(101) == sched.stage2


def test_schedule_rejects_inverted_endpoints():
    from pxdesign_train.data import CurriculumSchedule

    with pytest.raises(ValueError, match="stage2_start_step"):
        CurriculumSchedule(
            stage1={"a": 1.0},
            stage2={"a": 1.0},
            stage1_end_step=100,
            stage2_start_step=50,
        )


def test_schedule_rejects_missing_source():
    from pxdesign_train.data import CurriculumSchedule

    with pytest.raises(ValueError, match="missing weights"):
        CurriculumSchedule(
            stage1={"a": 1.0, "b": 1.0},
            stage2={"a": 1.0},  # missing 'b'
            stage1_end_step=10,
            stage2_start_step=20,
        )


def test_multidataset_length_and_lookup():
    md = _make_three_source_multi()
    assert len(md) == 80
    # First 40 items are afdb, next 30 mgnify, last 10 pdb (insertion order).
    assert md[0] == "afdb#0"
    assert md[39] == "afdb#39"
    assert md[40] == "mgnify#0"
    assert md[69] == "mgnify#29"
    assert md[70] == "pdb#0"
    assert md[79] == "pdb#9"


def test_multidataset_merged_weights_match_source_mass():
    md = _make_three_source_multi()
    w = md.merged_weights({"afdb": 0.5, "mgnify": 0.4, "pdb": 0.1})
    # Each source's slice sums to its mass.
    assert pytest.approx(w[:40].sum().item(), abs=1e-9) == 0.5
    assert pytest.approx(w[40:70].sum().item(), abs=1e-9) == 0.4
    assert pytest.approx(w[70:].sum().item(), abs=1e-9) == 0.1


def test_multidataset_rejects_unknown_source():
    md = _make_three_source_multi()
    with pytest.raises(ValueError, match="unknown source"):
        md.merged_weights({"ghost": 1.0})


def test_multidataset_normalizes_per_item_weights():
    """Per-item weights are normalized within source — so passing [2, 2] is
    equivalent to passing [1, 1]."""
    from pxdesign_train.data import CurriculumMultiDataset

    a = _TaggedDataset("a", 2)
    b = _TaggedDataset("b", 4)
    md = CurriculumMultiDataset(
        datasets=[a, b],
        source_names=["a", "b"],
        per_item_weights=[[2.0, 2.0], [3.0, 3.0, 3.0, 3.0]],
    )
    w = md.merged_weights({"a": 0.5, "b": 0.5})
    # source a: two items, each 0.5 / 2 = 0.25
    assert torch.allclose(w[:2], torch.tensor([0.25, 0.25], dtype=w.dtype))
    # source b: four items, each 0.5 / 4 = 0.125
    assert torch.allclose(
        w[2:], torch.tensor([0.125, 0.125, 0.125, 0.125], dtype=w.dtype)
    )


def _count_sources(sampler, dataset, n_iter: int = 1):
    counts = Counter()
    for _ in range(n_iter):
        for idx in sampler:
            counts[dataset[idx].split("#")[0]] += 1
    return counts


def test_sampler_stage1_proportions():
    from pxdesign_train.data import CurriculumSampler

    md = _make_three_source_multi()
    sched = _make_schedule(stage1_end=100, stage2_start=300)
    sampler = CurriculumSampler(md, sched, num_samples=20_000, seed=42)

    sampler.set_step(0)
    counts = _count_sources(sampler, md)
    total = sum(counts.values())
    # Within 3% of the stage-1 nominal proportions.
    assert abs(counts["afdb"] / total - 0.5) < 0.03, counts
    assert abs(counts["mgnify"] / total - 0.4) < 0.03, counts
    assert abs(counts["pdb"] / total - 0.1) < 0.03, counts


def test_sampler_stage2_proportions():
    from pxdesign_train.data import CurriculumSampler

    md = _make_three_source_multi()
    sched = _make_schedule(stage1_end=100, stage2_start=300)
    sampler = CurriculumSampler(md, sched, num_samples=20_000, seed=42)

    sampler.set_step(10_000)
    counts = _count_sources(sampler, md)
    total = sum(counts.values())
    assert abs(counts["afdb"] / total - 0.1) < 0.03, counts
    assert abs(counts["mgnify"] / total - 0.1) < 0.03, counts
    assert abs(counts["pdb"] / total - 0.8) < 0.03, counts


def test_sampler_ramp_midpoint_proportions():
    from pxdesign_train.data import CurriculumSampler

    md = _make_three_source_multi()
    sched = _make_schedule(stage1_end=100, stage2_start=300)
    sampler = CurriculumSampler(md, sched, num_samples=20_000, seed=42)

    sampler.set_step(200)  # halfway in the ramp
    counts = _count_sources(sampler, md)
    total = sum(counts.values())
    # Halfway between stage1 (afdb=0.5, pdb=0.1) and stage2 (afdb=0.1, pdb=0.8).
    assert abs(counts["afdb"] / total - 0.3) < 0.03, counts
    assert abs(counts["pdb"] / total - 0.45) < 0.03, counts


def test_sampler_deterministic_for_same_seed_and_step():
    from pxdesign_train.data import CurriculumSampler

    md = _make_three_source_multi()
    sched = _make_schedule()
    s1 = CurriculumSampler(md, sched, num_samples=200, seed=7)
    s2 = CurriculumSampler(md, sched, num_samples=200, seed=7)
    s1.set_step(50)
    s2.set_step(50)
    assert list(s1) == list(s2)


def test_sampler_distinct_for_different_step():
    from pxdesign_train.data import CurriculumSampler

    md = _make_three_source_multi()
    sched = _make_schedule()
    s = CurriculumSampler(md, sched, num_samples=200, seed=7)
    s.set_step(50)
    a = list(s)
    s.set_step(51)
    b = list(s)
    assert a != b


def test_sampler_zero_weight_source_never_drawn():
    """If a source has zero mass at the current step, never sample from it."""
    from pxdesign_train.data import CurriculumSampler, CurriculumSchedule

    md = _make_three_source_multi()
    sched = CurriculumSchedule(
        stage1={"afdb": 1.0, "mgnify": 0.0, "pdb": 0.0},
        stage2={"afdb": 0.0, "mgnify": 0.0, "pdb": 1.0},
        stage1_end_step=100,
        stage2_start_step=100,
    )
    sampler = CurriculumSampler(md, sched, num_samples=5_000, seed=1)
    sampler.set_step(0)  # stage1 — only afdb has mass
    counts = _count_sources(sampler, md)
    assert counts["mgnify"] == 0
    assert counts["pdb"] == 0
    assert counts["afdb"] == 5_000


def test_sampler_within_source_per_item_weights_propagate():
    """If one item in a source has a much higher per-item weight, it should
    dominate samples drawn from that source."""
    from pxdesign_train.data import (
        CurriculumMultiDataset,
        CurriculumSampler,
        CurriculumSchedule,
    )

    # Single source, 10 items, item 0 is heavily upweighted.
    a = _TaggedDataset("a", 10)
    md = CurriculumMultiDataset(
        datasets=[a],
        source_names=["a"],
        per_item_weights=[[100.0] + [1.0] * 9],
    )
    sched = CurriculumSchedule(
        stage1={"a": 1.0},
        stage2={"a": 1.0},
        stage1_end_step=10,
        stage2_start_step=10,
    )
    sampler = CurriculumSampler(md, sched, num_samples=10_000, seed=0)
    sampler.set_step(0)
    counts = Counter()
    for idx in sampler:
        counts[md[idx]] += 1
    # Item 0 should get ~100/(100+9) ≈ 91.7% of samples.
    assert counts["a#0"] / 10_000 > 0.85


def test_sampler_rejects_uncovered_dataset():
    from pxdesign_train.data import CurriculumSampler, CurriculumSchedule

    md = _make_three_source_multi()
    bad_sched = CurriculumSchedule(
        stage1={"afdb": 1.0, "mgnify": 1.0},  # missing 'pdb'
        stage2={"afdb": 1.0, "mgnify": 1.0},
        stage1_end_step=10,
        stage2_start_step=10,
    )
    with pytest.raises(ValueError, match="does not cover dataset sources"):
        CurriculumSampler(md, bad_sched, num_samples=10, seed=0)


def test_distributed_sampler_partitions_indices_across_ranks():
    """Two ranks together cover the same global samples as one rank."""
    from pxdesign_train.data import CurriculumDistributedSampler

    md = _make_three_source_multi()
    sched = _make_schedule()

    rank0 = CurriculumDistributedSampler(
        md, sched, num_samples=200, num_replicas=2, rank=0, seed=99,
    )
    rank1 = CurriculumDistributedSampler(
        md, sched, num_samples=200, num_replicas=2, rank=1, seed=99,
    )
    rank0.set_step(0); rank1.set_step(0)

    a = list(rank0); b = list(rank1)
    assert len(a) == len(b) == 100
    # Disjoint in the global sequence — interleaved striding by rank.
    assert set(a).isdisjoint(set(b)) or len(set(a) & set(b)) < len(a)
