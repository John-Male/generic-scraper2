"""Test-double orchestrator for features/07.

The real Swarm Forge orchestrator is external to this project and out of
scope (see the project constitution): this fake exists only to exercise
distributed execution, artifact upload, and node affinity behavior in
acceptance and property tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from generic_scraper.config import ScraperType


@dataclass
class ResourceRequirements:
    gpu: bool = False
    memory_gb: float | None = None


@dataclass
class Job:
    config: ScraperType
    shards: int = 1
    resources: ResourceRequirements = field(default_factory=ResourceRequirements)


@dataclass
class WorkerNode:
    node_id: str
    gpu: bool = False
    memory_gb: float = 0.0

    def satisfies(self, resources: ResourceRequirements) -> bool:
        if resources.gpu and not self.gpu:
            return False
        if resources.memory_gb is not None and self.memory_gb < resources.memory_gb:
            return False
        return True


@dataclass
class ScheduleResult:
    worker_nodes: list[WorkerNode]
    artifacts: list[str]


class FakeOrchestrator:
    """Assigns shards to worker nodes satisfying resource constraints."""

    def __init__(self, nodes: list[WorkerNode]) -> None:
        self._nodes = nodes

    def schedule(self, job: Job) -> ScheduleResult:
        candidates = [node for node in self._nodes if node.satisfies(job.resources)]
        if len(candidates) < job.shards:
            raise ValueError(
                f"not enough nodes satisfying constraints: need {job.shards}, "
                f"have {len(candidates)}"
            )
        assigned = candidates[: job.shards]
        artifacts = [f"artifact-{node.node_id}" for node in assigned]
        return ScheduleResult(worker_nodes=assigned, artifacts=artifacts)


class InMemoryArtifactStore:
    def __init__(self) -> None:
        self._uploaded: list[str] = []

    def upload(self, artifact: str) -> None:
        self._uploaded.append(artifact)

    @property
    def uploaded(self) -> list[str]:
        return list(self._uploaded)


def default_nodes() -> list[WorkerNode]:
    return [
        WorkerNode(node_id="node-1", gpu=False, memory_gb=4.0),
        WorkerNode(node_id="node-2", gpu=False, memory_gb=4.0),
        WorkerNode(node_id="node-3", gpu=False, memory_gb=4.0),
        WorkerNode(node_id="node-4", gpu=True, memory_gb=8.0),
        WorkerNode(node_id="node-5", gpu=True, memory_gb=8.0),
    ]
