# new-generic-scraper

Read every .feature file in features/. They are hand-written and are the source of truth — do not rewrite them wholesale.

First review them: normalize the Gherkin to our conventions, prune example-table columns that don't change behavior, pull repeated setup into Background, and list back anything ambiguous or untestable. Wait for my answers before proceeding.

Then cut the smallest coherent slice from features/01_initialize_scraper.feature — spec loading and engine selection only — and hand it to the coder with the scenario names and the step definitions needed in tests/acceptance/steps/.
