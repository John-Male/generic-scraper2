# mutation-stamp: sha256=b714cf2011b303dc69a55924e726fa2bddadeff9c4229c6621e32d1d6546a82f
# acceptance-mutation-manifest-begin
# {"version":1,"tested_at":"2026-09-16T20:06:19.707707Z","feature_name":"Proxy configuration and header pass key","feature_path":"features/04_proxy_and_headers.feature","background_hash":"b56c08df142d99ee7fe78cfd17e12dc4ea48c796219cddebd4f2cb3504ddfca9","implementation_hash":"sha256:03dd969af226c7a9f17fa1beb4b24b5e12a5d179474193586899a3cd655eb2e3","scenarios":[{"index":0,"name":"proxy_and_headers-1","scenario_hash":"4df6739155fd10401bb4e2674b36165b50a0d582ff6987a96a43796abdc15596","mutation_count":4,"result":{"Total":4,"Killed":4,"Survived":0,"Errors":0},"tested_at":"2026-09-16T19:41:16.461584Z"},{"index":1,"name":"proxy_and_headers-2","scenario_hash":"8efd0f43d88683864292c4df866d388be7a76053d481fd567a0f5809cb6fbef0","mutation_count":4,"result":{"Total":4,"Killed":4,"Survived":0,"Errors":0},"tested_at":"2026-09-16T19:41:16.461584Z"}]}
# acceptance-mutation-manifest-end

@swarm-forge @proxy
Feature: Proxy configuration and header pass key
  As a secure distributed scraper
  I want to configure proxy settings and pass key header data
  So that the Scraper can route requests through a proxy and include authentication headers

  Background:
    Given I have a ScraperType configuration with "use_proxy" set to "true"

  # proxy_and_headers-1: Initialize Scraper with proxy settings
  Scenario Outline: proxy_and_headers-1
    Given "scraper_engine" set to "requests"
    And "proxy_url" set to "<proxy_url>"
    And "proxy_port" set to "<proxy_port>"
    When I initialize the Scraper
    Then the Scraper should configure the HTTP client to use the proxy "<proxy_url>:<proxy_port>"

    Examples:
      | proxy_url             | proxy_port |
      | http://proxy.example  | 8080       |
      | http://proxy.internal | 3128       |

  # proxy_and_headers-2: Include pass key header when provided
  Scenario Outline: proxy_and_headers-2
    Given "proxy_pass_key" set to "<pass_key>"
    And "proxy_pass_val" set to "<pass_val>"
    When I initialize the Scraper
    Then the Scraper should include header "<pass_key>: <pass_val>" on proxied requests

    Examples:
      | pass_key     | pass_val        |
      | X-Proxy-Auth | dummy-token-abc |
      | X-Auth-Token | dummy-token-xyz |
