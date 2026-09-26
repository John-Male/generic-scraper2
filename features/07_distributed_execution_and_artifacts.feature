# mutation-stamp: sha256=06d5ff8b5c0879330cd390ee8ed852e0e030f526ee77f3e5a8fdf8f0a7444c07
# acceptance-mutation-manifest-begin
# {"version":1,"tested_at":"2026-09-16T20:06:19.979350Z","feature_name":"Distributed execution, artifact upload, and node affinity","feature_path":"features/07_distributed_execution_and_artifacts.feature","background_hash":"74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b","implementation_hash":"sha256:e3382e9c756747dd770f33c141a0e1037c7edb9ba0d6b807713cd34325906264","scenarios":[{"index":0,"name":"distributed_execution_and_artifacts-1","scenario_hash":"75021041b06f8e7d8fd0ad68bf876c07e9bb60132fff983317d06547e3a65320","mutation_count":2,"result":{"Total":2,"Killed":2,"Survived":0,"Errors":0},"tested_at":"2026-09-16T19:57:49.711079Z"},{"index":1,"name":"distributed_execution_and_artifacts-2","scenario_hash":"7afdb414c77a95f6ea8c4a675d3e2e53d4a858386f8ae9e58cc368d517dd0531","mutation_count":1,"result":{"Total":1,"Killed":1,"Survived":0,"Errors":0},"tested_at":"2026-09-16T19:57:49.711079Z"}]}
# acceptance-mutation-manifest-end

@swarm-forge @distributed @artifacts
Feature: Distributed execution, artifact upload, and node affinity
  As a Swarm Forge orchestrated job
  I want to run scraping tasks across multiple workers, collect artifacts, and control node affinity
  So that scraping jobs scale and results are preserved

  # distributed_execution_and_artifacts-1: Run scraping job across multiple workers
  Scenario Outline: distributed_execution_and_artifacts-1
    Given I have a ScraperType configuration with "scraper_engine" set to "requests"
    And the job is configured to run with <shards> parallel shards
    When the orchestrator schedules the job
    Then the job should run on <shards> distinct worker nodes
    And each worker should produce a parsed artifact

    Examples:
      | shards |
      | 3      |
      | 5      |

  # distributed_execution_and_artifacts-2: Upload artifacts to central storage
  Scenario Outline: distributed_execution_and_artifacts-2
    Given a worker produced "<artifact>"
    When the worker finishes the shard
    Then the artifact "<artifact>" should be uploaded to the job artifact store

    Examples:
      | artifact           |
      | parsed_result.json |

  # distributed_execution_and_artifacts-3: Respect node affinity and resource limits
  Scenario: distributed_execution_and_artifacts-3
    Given I have a ScraperType configuration with "browser_type" set to "chrome"
    And the job requests GPU false and memory 2GB
    When the orchestrator schedules the job
    Then the job should be placed on a node that satisfies the resource constraints
