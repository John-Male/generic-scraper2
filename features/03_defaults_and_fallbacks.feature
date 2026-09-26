# mutation-stamp: sha256=ffe0818ff0a1c1264e4f5d798f0c1aa06ff97830e6cc9760490ed1206715e9b0
# acceptance-mutation-manifest-begin
# {"version":1,"tested_at":"2026-09-16T20:06:19.617962Z","feature_name":"Default and secondary choices for ScraperType","feature_path":"features/03_defaults_and_fallbacks.feature","background_hash":"74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b","implementation_hash":"sha256:1aab89b0682de69387b9e97dcca688b2bd3665f219afd1ba7231473d19b31508","scenarios":[{"index":1,"name":"defaults_and_fallbacks-2","scenario_hash":"8c16707517ca4becc6d54d609ed3965eac825514f948f31ee0bbaf8ecc0dd080","mutation_count":2,"result":{"Total":2,"Killed":2,"Survived":0,"Errors":0},"tested_at":"2026-09-16T19:36:36.036056Z"}]}
# acceptance-mutation-manifest-end

@swarm-forge @defaults
Feature: Default and secondary choices for ScraperType
  As a resilient scraper
  I want sensible defaults and fallback options
  So that the Scraper can operate even when some options are not provided or unavailable

  # defaults_and_fallbacks-1: Use default values when none provided
  Scenario: defaults_and_fallbacks-1
    Given I have an empty ScraperType configuration
    When I initialize the Scraper
    Then the Scraper should use "requests" as the default scraper engine
    And the Scraper should have no browser configured

  # defaults_and_fallbacks-2: Fall back when primary engine unavailable and no secondary configured
  Scenario Outline: defaults_and_fallbacks-2
    Given I have a ScraperType configuration with "scraper_engine" set to "<engine>"
    And "<engine>" is not available on the worker node
    When I initialize the Scraper
    Then the Scraper should fall back to "requests"

    Examples:
      | engine     |
      | playwright |
      | selenium   |
