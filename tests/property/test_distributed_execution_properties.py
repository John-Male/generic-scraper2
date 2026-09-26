from __future__ import annotations

import random

import pytest

from generic_scraper.config import ScraperType
from tests.acceptance.steps.distributed_execution_and_artifacts_fake import (
    FakeOrchestrator,
    Job,
    ResourceRequirements,
    WorkerNode,
)
from tests.property.support import for_each_trial


def _random_resources(rng: random.Random) -> ResourceRequirements:
    gpu = rng.choice([True, False])
    memory_gb = rng.choice([None, float(rng.randint(0, 16))])
    return ResourceRequirements(gpu=gpu, memory_gb=memory_gb)


def _random_node(rng: random.Random, node_id: str) -> WorkerNode:
    return WorkerNode(
        node_id=node_id, gpu=rng.choice([True, False]), memory_gb=float(rng.randint(0, 16))
    )


@pytest.mark.property
def test_worker_node_satisfies_matches_the_gpu_and_memory_invariant() -> None:
    def check(rng: random.Random) -> None:
        node = _random_node(rng, "n")
        resources = _random_resources(rng)

        gpu_ok = (not resources.gpu) or node.gpu
        memory_ok = resources.memory_gb is None or node.memory_gb >= resources.memory_gb
        expected = gpu_ok and memory_ok

        assert node.satisfies(resources) == expected

    for_each_trial(check)


@pytest.mark.property
def test_orchestrator_schedules_one_distinct_satisfying_node_per_shard() -> None:
    def check(rng: random.Random) -> None:
        resources = _random_resources(rng)
        nodes = [_random_node(rng, f"n{i}") for i in range(rng.randint(1, 8))]
        matching = [node for node in nodes if node.satisfies(resources)]
        if not matching:
            return
        shards = rng.randint(1, len(matching))
        job = Job(config=ScraperType(), shards=shards, resources=resources)

        result = FakeOrchestrator(nodes).schedule(job)

        assert len(result.worker_nodes) == shards
        assert len({node.node_id for node in result.worker_nodes}) == shards
        assert all(node.satisfies(resources) for node in result.worker_nodes)
        assert len(result.artifacts) == shards

    for_each_trial(check)
