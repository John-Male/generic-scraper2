from __future__ import annotations

from tests.acceptance.registry import StepContext, given, then, when
from tests.acceptance.steps.distributed_execution_and_artifacts_fake import (
    FakeOrchestrator,
    InMemoryArtifactStore,
    Job,
    ResourceRequirements,
    default_nodes,
)


def _get_or_create_job(ctx: StepContext) -> Job:
    job = ctx.world.get("job")
    if job is None:
        job = Job(config=ctx.world["config"])
        ctx.world["job"] = job
    return job


@given(r"the job is configured to run with <(?P<placeholder>[A-Za-z0-9_]+)> parallel shards")
def set_job_shards(ctx: StepContext) -> None:
    job = _get_or_create_job(ctx)
    job.shards = int(ctx.example[ctx.match.group("placeholder")])


@given(r"the job requests GPU (?P<gpu>true|false) and memory (?P<memory>\d+)GB")
def set_job_resources(ctx: StepContext) -> None:
    job = _get_or_create_job(ctx)
    job.resources = ResourceRequirements(
        gpu=ctx.match.group("gpu") == "true",
        memory_gb=float(ctx.match.group("memory")),
    )


@when(r"the orchestrator schedules the job")
def schedule_job(ctx: StepContext) -> None:
    orchestrator = FakeOrchestrator(default_nodes())
    ctx.world["schedule_result"] = orchestrator.schedule(ctx.world["job"])


@then(r"the job should run on <(?P<placeholder>[A-Za-z0-9_]+)> distinct worker nodes")
def assert_distinct_worker_nodes(ctx: StepContext) -> None:
    expected = int(ctx.example[ctx.match.group("placeholder")])
    node_ids = [node.node_id for node in ctx.world["schedule_result"].worker_nodes]
    assert len(node_ids) == expected
    assert len(set(node_ids)) == expected


@then(r"each worker should produce a parsed artifact")
def assert_each_worker_produced_artifact(ctx: StepContext) -> None:
    result = ctx.world["schedule_result"]
    assert len(result.artifacts) == len(result.worker_nodes)


@then(r"the job should be placed on a node that satisfies the resource constraints")
def assert_placed_on_satisfying_node(ctx: StepContext) -> None:
    result = ctx.world["schedule_result"]
    job = ctx.world["job"]
    assert len(result.worker_nodes) >= 1
    assert all(node.satisfies(job.resources) for node in result.worker_nodes)


@given(r'a worker produced "<(?P<placeholder>[A-Za-z0-9_]+)>"')
def worker_produced_artifact(ctx: StepContext) -> None:
    ctx.world["artifact"] = ctx.example[ctx.match.group("placeholder")]
    ctx.world["artifact_store"] = InMemoryArtifactStore()


@when(r"the worker finishes the shard")
def worker_finishes_shard(ctx: StepContext) -> None:
    ctx.world["artifact_store"].upload(ctx.world["artifact"])


@then(
    r'the artifact "<(?P<placeholder>[A-Za-z0-9_]+)>" should be uploaded to'
    r" the job artifact store"
)
def assert_artifact_uploaded(ctx: StepContext) -> None:
    artifact = ctx.example[ctx.match.group("placeholder")]
    assert artifact in ctx.world["artifact_store"].uploaded
