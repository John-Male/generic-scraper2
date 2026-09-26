# mutation-stamp: sha256=3ce6b6eac96bf466099a1be67ed6c7d028a1054bfc4da47644cec382edf76c10
# acceptance-mutation-manifest-begin
# {"version":1,"tested_at":"2026-09-16T20:06:19.526393Z","feature_name":"Configure browser type for browser-based scraping engines","feature_path":"features/02_browser_configuration.feature","background_hash":"74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b","implementation_hash":"sha256:68f3d7f3a212126b18f1d6c801e5e80f60d2915aea664249bef942d22ff5175e","scenarios":[{"index":0,"name":"browser_configuration-1","scenario_hash":"724078cef04abe701c3e2aaa540088089530b9252d1621d993a8bb2e3696b464","mutation_count":8,"result":{"Total":8,"Killed":8,"Survived":0,"Errors":0},"tested_at":"2026-09-16T19:36:35.925527Z"}]}
# acceptance-mutation-manifest-end

@swarm-forge @browser
Feature: Configure browser type for browser-based scraping engines
  As a distributed test
  I want to set the browser type when using Playwright or Selenium
  So that the Scraper launches the correct browser on the worker node

  # browser_configuration-1: Set browser type for Playwright or Selenium
  Scenario Outline: browser_configuration-1
    Given I have a ScraperType configuration with "scraper_engine" set to "<engine>"
    And "browser_type" set to "<browser>"
    When I initialize the Scraper
    Then the Scraper should launch "<browser>" for "<engine>"

    Examples:
      | engine     | browser |
      | playwright | chrome  |
      | playwright | firefox |
      | selenium   | chrome  |
      | selenium   | firefox |
