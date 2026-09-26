# mutation-stamp: sha256=1af9c745a857f4c14a272c130949535b690d3a6e5dfda82885f9aeca3547c904
# acceptance-mutation-manifest-begin
# {"version":1,"tested_at":"2026-09-16T20:06:20.114516Z","feature_name":"Error handling, retries, and fallback behavior","feature_path":"features/08_error_handling_and_retries.feature","background_hash":"74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b","implementation_hash":"sha256:2ee9d0f8ada5c9aee5ecf3ef24e37db6007c0c51e31389cf7e9ea4b94a056d11","scenarios":[{"index":0,"name":"error_handling_and_retries-1","scenario_hash":"1eda339b0444eef3c15e5f969eed1844e76d41738d4d6fb60d42724aa87b39a6","mutation_count":2,"result":{"Total":2,"Killed":2,"Survived":0,"Errors":0},"tested_at":"2026-09-16T20:06:20.114516Z"},{"index":1,"name":"error_handling_and_retries-2","scenario_hash":"df918a20fdd9a87afd45029b26d8ab83ee1ac208a5b939654665ea75f73dc627","mutation_count":2,"result":{"Total":2,"Killed":2,"Survived":0,"Errors":0},"tested_at":"2026-09-16T20:06:20.114516Z"},{"index":2,"name":"error_handling_and_retries-3","scenario_hash":"83d56711f89155ae79b413b94bba9879f1c4dfe61e9a68fe4e0961491a3406b1","mutation_count":2,"result":{"Total":2,"Killed":2,"Survived":0,"Errors":0},"tested_at":"2026-09-16T20:06:20.114516Z"}]}
# acceptance-mutation-manifest-end

@swarm-forge @resilience
Feature: Error handling, retries, and fallback behavior
  As a robust scraper
  I want the Scraper to handle common errors, retry, and fallback gracefully
  So that scraping jobs are resilient in distributed environments

  # error_handling_and_retries-1: Retry on transient network error
  Scenario Outline: error_handling_and_retries-1
    Given I have a ScraperType configuration with "scraper_engine" set to "requests"
    And retry policy set to <attempts> attempts with exponential backoff
    When a transient network error occurs during fetch
    Then the Scraper should retry up to <attempts> times before failing

    Examples:
      | attempts |
      | 3        |
      | 5        |

  # error_handling_and_retries-2: Fall back to secondary engine on engine failure
  Scenario Outline: error_handling_and_retries-2
    Given I have a ScraperType configuration with "scraper_engine" set to "<engine>"
    And "secondary" set to "requests"
    And "<engine>" fails to start on the worker
    When I initialize the Scraper
    Then the Scraper should attempt to use "requests" as the secondary engine
    And the initialization should succeed

    Examples:
      | engine     |
      | selenium   |
      | playwright |

  # error_handling_and_retries-3: Fail with descriptive error when no engine available
  Scenario Outline: error_handling_and_retries-3
    Given I have a ScraperType configuration with "scraper_engine" set to "<engine>"
    When I initialize the Scraper
    Then the Scraper initialization should fail with "<error>"

    Examples:
      | engine  | error                         |
      | unknown | UnsupportedScraperEngineError |
