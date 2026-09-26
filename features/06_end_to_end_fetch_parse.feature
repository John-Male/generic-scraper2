# mutation-stamp: sha256=8187a6732d5474a352598242cb9b602f55f8e6f241b544a277e9fe86cbcc5ad7
# acceptance-mutation-manifest-begin
# {"version":1,"tested_at":"2026-09-16T20:06:19.889627Z","feature_name":"End-to-end fetch and parse using configured options","feature_path":"features/06_end_to_end_fetch_parse.feature","background_hash":"b38ab00dd76c2904e72f067e8caf18ba7d576fc479c8c858361cc95ae75ba096","implementation_hash":"sha256:6aa303e8641e43bc892bf99589646d864f9855bfac6c9add60f0ede290e234fb","scenarios":[{"index":0,"name":"end_to_end_fetch_parse-1","scenario_hash":"e635734e47da1abc8de00646d10ac311f24791b7affa1460534d6f07bfa24e8e","mutation_count":8,"result":{"Total":8,"Killed":8,"Survived":0,"Errors":0},"tested_at":"2026-09-16T19:51:58.465186Z"}]}
# acceptance-mutation-manifest-end

@swarm-forge @e2e
Feature: End-to-end fetch and parse using configured options
  As a distributed test
  I want the Scraper to fetch a page and parse it using the configured engine and processor
  So that I can verify the full pipeline works across Swarm Forge workers

  Background:
    Given a test URL "https://example.com/test-page"

  # end_to_end_fetch_parse-1: Fetch and parse using engine and processor
  Scenario Outline: end_to_end_fetch_parse-1
    Given I have a ScraperType configuration with "scraper_engine" set to "<engine>"
    And "processing_type" set to "<processor>"
    When I initialize the Scraper
    And I fetch the test URL
    Then the Scraper should return a parsed document using "<processor>"
    And the parsed document should contain the page title

    Examples:
      | engine     | processor     |
      | requests   | beautifulsoup |
      | requests   | lxml          |
      | selenium   | beautifulsoup |
      | playwright | html.parser   |
