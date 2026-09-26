# mutation-stamp: sha256=2f87130919af98866cc596fead790083c4d88c01cfc8f939432df13ff44be030
# acceptance-mutation-manifest-begin
# {"version":1,"tested_at":"2026-09-16T20:06:19.799337Z","feature_name":"Choose processing type for parsing responses","feature_path":"features/05_processing_types.feature","background_hash":"74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b","implementation_hash":"sha256:5c7a6e7492fd9b03527d7cc8510fda3220897d5acb98e8fa5c0dfd4e98e33fff","scenarios":[{"index":0,"name":"processing_types-1","scenario_hash":"2917ca443462e87844e8019f15c9ed1e24cdce573695264a3daa5dc4172b41a4","mutation_count":4,"result":{"Total":4,"Killed":4,"Survived":0,"Errors":0},"tested_at":"2026-09-16T19:42:26.570257Z"}]}
# acceptance-mutation-manifest-end

@swarm-forge @parser
Feature: Choose processing type for parsing responses
  As a developer running tests in Swarm Forge
  I want to select a processing type (parser) for the Scraper
  So that the Scraper can parse HTML using different libraries

  # processing_types-1: Initialize Scraper with different processing types
  Scenario Outline: processing_types-1
    Given I have a ScraperType configuration with "processing_type" set to "<processor>"
    When I initialize the Scraper
    Then the Scraper should use "<processor>" to parse HTML responses

    Examples:
      | processor     |
      | beautifulsoup |
      | lxml          |
      | html.parser   |
      | regex         |
