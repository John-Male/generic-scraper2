from __future__ import annotations

from typing import Any

import pytest

from generic_scraper.config import ScraperType
from tests.acceptance import steps  # noqa: F401  (registers step handlers)
from tests.acceptance.registry import registry
from tests.acceptance.steps.distributed_execution_and_artifacts_fake import (
    FakeOrchestrator,
    InMemoryArtifactStore,
    Job,
    ResourceRequirements,
    WorkerNode,
)


def test_job_shards_and_resources_steps_share_the_same_job() -> None:
    world: dict[str, Any] = {"config": ScraperType()}

    registry.dispatch(
        "given",
        "the job is configured to run with <shards> parallel shards",
        world=world,
        example={"shards": "3"},
    )
    registry.dispatch(
        "given",
        "the job requests GPU true and memory 8GB",
        world=world,
        example={},
    )

    job = world["job"]
    assert job.shards == 3
    assert job.resources == ResourceRequirements(gpu=True, memory_gb=8.0)


def test_worker_node_satisfies_when_unconstrained() -> None:
    node = WorkerNode(node_id="n1", gpu=False, memory_gb=1.0)

    assert node.satisfies(ResourceRequirements()) is True


def test_worker_node_rejects_insufficient_memory() -> None:
    node = WorkerNode(node_id="n1", gpu=False, memory_gb=1.0)

    assert node.satisfies(ResourceRequirements(memory_gb=2.0)) is False


def test_worker_node_rejects_missing_gpu() -> None:
    node = WorkerNode(node_id="n1", gpu=False, memory_gb=8.0)

    assert node.satisfies(ResourceRequirements(gpu=True)) is False


def test_worker_node_accepts_gpu_node_for_gpu_job() -> None:
    node = WorkerNode(node_id="n1", gpu=True, memory_gb=8.0)

    assert node.satisfies(ResourceRequirements(gpu=True, memory_gb=4.0)) is True


def test_orchestrator_assigns_one_distinct_node_per_shard() -> None:
    nodes = [WorkerNode(node_id=f"n{i}", memory_gb=4.0) for i in range(3)]
    orchestrator = FakeOrchestrator(nodes)
    job = Job(config=ScraperType(), shards=2)

    result = orchestrator.schedule(job)

    assert len(result.worker_nodes) == 2
    assert len({node.node_id for node in result.worker_nodes}) == 2
    assert len(result.artifacts) == 2


def test_orchestrator_only_assigns_nodes_satisfying_constraints() -> None:
    nodes = [
        WorkerNode(node_id="small", memory_gb=1.0),
        WorkerNode(node_id="big", memory_gb=8.0),
    ]
    orchestrator = FakeOrchestrator(nodes)
    job = Job(config=ScraperType(), shards=1, resources=ResourceRequirements(memory_gb=4.0))

    result = orchestrator.schedule(job)

    assert result.worker_nodes == [nodes[1]]


def test_orchestrator_raises_when_not_enough_satisfying_nodes() -> None:
    nodes = [WorkerNode(node_id="small", memory_gb=1.0)]
    orchestrator = FakeOrchestrator(nodes)
    job = Job(config=ScraperType(), shards=2)

    with pytest.raises(ValueError, match="not enough nodes"):
        orchestrator.schedule(job)


def test_artifact_store_records_uploaded_artifacts() -> None:
    store = InMemoryArtifactStore()

    store.upload("parsed_result.json")

    assert store.uploaded == ["parsed_result.json"]
