# mutation-stamp: sha256=eb1703d78e60d58e256e2ab92fc218dd648cd50dbaf272ccad00bb8d39f8fcab
# acceptance-mutation-manifest-begin
# {"version":1,"tested_at":"2026-09-16T20:06:19.433708Z","feature_name":"Initialize Scraper with chosen scraping engine","feature_path":"features/01_initialize_scraper.feature","background_hash":"ef173a8c4604cb1767ef74335cbbe07fa15d32bc7a33e200220c8d1e4117f131","implementation_hash":"sha256:8cac69505986e7c022d41f1da3b114c8b05421ab721c1e962c70fc25bc56e042","scenarios":[{"index":0,"name":"initialize_scraper-0","scenario_hash":"1e4623fa4090d60e4dcae7044692ec642e20b171fd93fc78f8e232919de64c9b","mutation_count":2,"result":{"Total":2,"Killed":2,"Survived":0,"Errors":0},"tested_at":"2026-09-16T19:01:34.614025Z"},{"index":1,"name":"initialize_scraper-1","scenario_hash":"2326413279424362ca048443a0a0b1cb2bbc090851e628a4f9196bfacb6ca43b","mutation_count":3,"result":{"Total":3,"Killed":3,"Survived":0,"Errors":0},"tested_at":"2026-09-16T19:01:34.614025Z"}]}
# acceptance-mutation-manifest-end

@swarm-forge @init
Feature: Initialize Scraper with chosen scraping engine
  As a test runner using Swarm Forge
  I want to initialize the Scraper with a chosen engine
  So that the scraper uses the correct technique for fetching pages

  Background:
    Given default scraper configuration exists

  # initialize_scraper-0: Load ScraperType configuration from a spec
  Scenario Outline: initialize_scraper-0
    Given a scraper spec in "<format>" format with "scraper_engine" set to "requests"
    When I load the ScraperType configuration from the spec
    Then the ScraperType should have "scraper_engine" set to "requests"

    Examples:
      | format |
      | dict   |
      | yaml   |

  # initialize_scraper-1: Initialize Scraper with different engines
  Scenario Outline: initialize_scraper-1
    Given I have a ScraperType configuration with "scraper_engine" set to "<engine>"
    When I initialize the Scraper
    Then the Scraper should use the "<engine>" engine
    And the Scraper should be ready to fetch pages

    Examples:
      | engine     |
      | requests   |
      | playwright |
      | selenium   |
