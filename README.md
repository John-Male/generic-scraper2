# generic-scraper2

Minimal Swarm Forger project scaffold with Python code.

## Files

- `swarm_forger.py` - small Python module that describes the project
- `tests/test_swarm_forger.py` - focused unit tests

## Run tests

```bash
python -m unittest tests.test_swarm_forger
```

## Generic Scraper

This repository also contains a Python web-scraping package developed with the SwarmForge four-pack.
It supports configurable fetch engines and HTML processors, with unit, property, and acceptance
tests.

Create an environment and run the scraper test suite with:

```sh
python -m venv .venv
source .venv/bin/activate
pip install requests beautifulsoup4 lxml PyYAML pytest pytest-bdd ruff mypy
pytest
```

Behavioral requirements are in `features/`; project setup and acceptance-pipeline details are in
`docs/`.
