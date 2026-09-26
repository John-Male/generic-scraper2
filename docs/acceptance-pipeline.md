# Acceptance pipeline

This project follows the
[Acceptance Pipeline Specification](https://github.com/unclebob/Acceptance-Pipeline-Specification):
Gherkin feature file -> JSON IR -> generated test entry points -> test run.

```text
features/<n>.feature
  -> gherkin-parser                         (supplied APS tool)
  -> tests/acceptance/build/ir/<n>.json     (IR, gitignored)
  -> acceptance-entrypoint-generator         (tests/acceptance/generator.py)
  -> tests/acceptance/generated/test_<n>.py (generated tests, gitignored)
  -> pytest                                  (single runner for unit + acceptance)
```

The root `conftest.py` runs this pipeline for every feature listed in
`ACTIVE_FEATURES` before collection, so a plain `pytest` regenerates and runs
acceptance tests alongside unit tests. `ACTIVE_FEATURES` grows by one entry
per feature slice the coder has implemented step handlers for; listing an
unimplemented feature there would generate acceptance tests with no matching
step handler and fail the suite.

`scripts/run_acceptance.sh` runs only the acceptance tests (same codegen,
scoped to `tests/acceptance`).

## Components

- `tests/acceptance/runtime.py` -- expands IR into scenario executions
  (background steps prepended, one execution per example row) and runs a
  execution's steps against the step registry.
- `tests/acceptance/registry.py` -- `StepRegistry`, with `given`/`when`/`then`
  decorators. Step handlers are matched by keyword and a regex against the
  literal step text (placeholders included, e.g. `"<engine>"`); the regex
  captures the placeholder *name*, and the handler looks that name up in the
  current example row.
- `tests/acceptance/generator.py` -- `acceptance-entrypoint-generator`. Reads
  IR, embeds it in a generated test file (one test function per scenario
  execution), and writes per-feature metadata (`implementation_hash` etc.)
  under `tests/acceptance/generated/metadata/`.
- `tests/acceptance/steps/` -- hand-written step handlers, one module per
  feature area, imported by `tests/acceptance/steps/__init__.py` so generated
  tests only need `from tests.acceptance import steps`.

## Acceptance mutation (gherkin-mutator)

`gherkin-mutator` checks that scenarios actually notice when their example
data changes: it mutates one example cell at a time in the parser IR and
re-runs the already-generated acceptance tests against each mutated IR.

Generated tests embed their IR at generation time (`IR = json.loads(...)`),
but the mutator must run the *same* generated entry points against many
mutated IR variants without regenerating them. `_run()` in each generated
test therefore calls `resolve_ir(IR)`
(`tests/acceptance/runtime.py`) instead of using `IR` directly: with the
`GENERIC_SCRAPER_ACCEPTANCE_IR` environment variable unset, it returns the
embedded IR (a plain `pytest` run is unaffected); when set, it loads IR from
the path in that variable instead.

`tests/acceptance/mutation_runner.py` is the project-specific runner
adapter the mutator's `--runner-worker` speaks to: a persistent
newline-delimited-JSON worker that, per job, points
`GENERIC_SCRAPER_ACCEPTANCE_IR` at the job's mutated `feature_json` and runs
`pytest <generated_dir> -q` as a subprocess, classifying the result as
`test_success`, `test_failure`, or `infrastructure_error`.
`scripts/gherkin-mutator-runner-worker` is its CLI entry point. Example
invocation for feature 01, from the repo root:

```sh
gherkin-mutator \
  --feature features/01_initialize_scraper.feature \
  --generated-dir tests/acceptance/generated \
  --runner-worker scripts/gherkin-mutator-runner-worker \
  --level soft
```
