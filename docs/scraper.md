# Scraper initialization

`ScraperType` is the configuration object a caller builds to describe how a
scrape should run. `Scraper` takes a `ScraperType` and selects the matching
engine.

```python
from generic_scraper import Scraper, ScraperType

scraper = Scraper(ScraperType(scraper_engine="requests"))
scraper.engine_name  # "requests"
scraper.is_ready()    # True
```

## Loading a spec

`load_scraper_type` builds a `ScraperType` from a spec supplied as a `dict` or
as a YAML string, for callers that receive configuration as data rather than
constructing `ScraperType` directly:

```python
from generic_scraper import load_scraper_type

load_scraper_type({"scraper_engine": "requests"})
load_scraper_type("scraper_engine: requests\n")
```

## Engines

| `scraper_engine` value | Adapter            |
| ----------------------- | ------------------ |
| `requests`               | `RequestsEngine`    |
| `playwright`              | `PlaywrightEngine`  |
| `selenium`                | `SeleniumEngine`    |

Engines live behind the `generic_scraper.engines.Engine` interface and are
looked up through `generic_scraper.engines.ENGINE_REGISTRY` by name. Adding a
new engine means adding one adapter and one registry entry; it does not
require changing the other adapters.

## Browser configuration

For the `playwright` and `selenium` engines, `browser_type` selects which
browser the engine launches (e.g. `"chrome"`, `"firefox"`). `Scraper.browser`
reports what was launched; it is `None` for engines with no browser concept,
such as `requests`.

```python
scraper = Scraper(ScraperType(scraper_engine="playwright", browser_type="firefox"))
scraper.browser  # "firefox"
```

## Defaults, fallbacks, and errors

An empty `ScraperType()` defaults to the `requests` engine with no browser
configured. If the configured `scraper_engine` is unavailable, `Scraper`
falls back to the configured `secondary` engine (if set and available), then
to `requests`. Availability is checked through an injectable `is_available`
callable (`(engine_name: str) -> bool`), defaulting to assuming every
registered engine is available; callers and tests can override it to
simulate an engine being unavailable on the current worker:

```python
config = ScraperType(scraper_engine="playwright", secondary="selenium")
scraper = Scraper(config, is_available=lambda name: name != "playwright")
scraper.engine_name  # "selenium"
```

A `scraper_engine` that names no registered engine at all (a caller
configuration error, not a transiently-unavailable one) raises
`UnsupportedScraperEngineError` immediately, without attempting any
fallback:

```python
Scraper(ScraperType(scraper_engine="unknown"))  # raises UnsupportedScraperEngineError
```

## Retries

`retry_attempts` (default `1`, i.e. no retry) bounds how many times
`Scraper.fetch_page`/`fetch` retry a fetch that raises `TransientFetchError`,
with exponential backoff between attempts, before letting the error
propagate. Backoff sleeps through an injectable `sleep` callable
(`(seconds: float) -> None`), defaulting to `time.sleep`; tests inject a
no-op to stay hermetic:

```python
scraper = Scraper(ScraperType(retry_attempts=3), sleep=lambda seconds: None, transport=flaky_transport)
scraper.fetch_page("https://example.com")  # retries up to 3 times on TransientFetchError
```

## Proxy and headers

Setting `use_proxy=True` with `proxy_url` and `proxy_port` routes the
`requests` engine's HTTP client through that proxy; `Scraper.proxy` reports
the configured `"<proxy_url>:<proxy_port>"`, or `None` if no proxy is
configured. `proxy_pass_key`/`proxy_pass_val` add a header (e.g. for an
authentication token) sent on every request, independent of whether a proxy
is configured; `Scraper.headers` reports the configured headers.

```python
config = ScraperType(
    use_proxy=True,
    proxy_url="http://proxy.example",
    proxy_port="8080",
    proxy_pass_key="X-Proxy-Auth",
    proxy_pass_val="dummy-token-abc",
)
scraper = Scraper(config)
scraper.proxy    # "http://proxy.example:8080"
scraper.headers  # {"X-Proxy-Auth": "dummy-token-abc"}
```

## Processing types

`processing_type` selects which library parses fetched HTML.
`Scraper.processor_name` reports the configured processor, or `None` if
`processing_type` isn't set.

| `processing_type` value | Adapter                 |
| ------------------------ | ----------------------- |
| `beautifulsoup`            | `BeautifulSoupProcessor` |
| `lxml`                      | `LxmlProcessor`          |
| `html.parser`                | `HtmlParserProcessor`    |
| `regex`                       | `RegexProcessor`         |

Processors live behind the `generic_scraper.processors.Processor` interface
and are looked up through `generic_scraper.processors.PROCESSOR_REGISTRY` by
name, the same pattern as engines.

```python
scraper = Scraper(ScraperType(processing_type="lxml"))
scraper.processor_name  # "lxml"
```

## Fetching and parsing

`Scraper.fetch(url)` fetches `url` with the configured engine and parses the
result with the configured processor, returning a `ParsedDocument` (currently
just `.title`). It raises `ValueError` if `processing_type` isn't configured.

Each engine fetches through an injectable `transport` callable
(`(url: str) -> str`), passed to `Scraper(config, transport=...)`, which is
how tests substitute a fixture page for a real network call or browser
launch -- `RequestsEngine`'s default transport does a real
`requests.Session.get`, translating connection errors and timeouts into
`TransientFetchError` (see Retries, above); `PlaywrightEngine`/
`SeleniumEngine` have no real driver wired up yet and raise if `fetch` is
called without an injected transport.

```python
scraper = Scraper(
    ScraperType(processing_type="beautifulsoup"),
    transport=lambda url: "<html><head><title>Example</title></head></html>",
)
document = scraper.fetch("https://example.com")
document.title  # "Example"
```

## Distributed execution (features/07)

Sharding, artifact upload, and node affinity/resource constraints describe
the external Swarm Forge orchestrator's behavior, not this library's --
per the project constitution, that orchestrator is an interface this
project codes against, not one it implements. `generic_scraper` has no
production code for this; `features/07_distributed_execution_and_artifacts.feature`
is exercised entirely by a test-double orchestrator
(`FakeOrchestrator`/`WorkerNode`/`InMemoryArtifactStore` in
`tests/acceptance/steps/distributed_execution_and_artifacts_fake.py`),
scoped to acceptance and property testing only.
