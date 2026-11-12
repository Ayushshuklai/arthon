# Contributing

Issues and pull requests are welcome.

- Run the tests before opening a PR: `python -m unittest discover -s tests -v`
  (synthetic data only — tests must never call the network).
- Financial calculations and data transformations require tests.
- Do not commit market-data caches, `.env` files, or credentials.
  See `docs/DATA_SOURCES.md` for the redistribution rules.
- Keep agent evidence strings factual: if a number appears in a report, its
  formula must be findable in the code.
- Educational project: contributions must not present outputs as financial advice.
