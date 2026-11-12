# Data Sources, Coverage and Licensing

## Prices — Yahoo Finance public chart API
- **Provider:** Yahoo Finance (`query1.finance.yahoo.com/v8/finance/chart`)
- **Coverage used here:** daily OHLCV for NSE (`.NS`), BSE (`.BO`), US and other
  listed tickers; indices such as `^NSEI` (NIFTY 50) and `^GSPC` (S&P 500) as benchmarks.
- **Frequency:** end-of-day / delayed data as served by the public endpoint.
  This project has **no exchange connectivity and no real-time feed**, and
  does not claim any.
- **Corporate actions:** the chart endpoint's prices are used as returned;
  users should verify split/dividend adjustment behaviour for their use case.

## Redistribution gate (important)
Cached price CSVs downloaded from Yahoo are **excluded from this public
repository**. Public accessibility is not the same as a redistribution
licence, and Yahoo's terms do not clearly grant public redistribution of
downloaded price history. The mandatory pre-publication check therefore
concluded:

- Raw cached datasets: **excluded** (`data/cache/*.csv` is git-ignored).
- Download/ingestion/local-caching code: included — run the tool and it
  fetches data under your own usage of the provider.
- Generated analysis reports in `reports/`: included. They are this
  project's own analysis and commentary containing summary statistics,
  attributed to the source and date — not raw datasets.
- No other datasets are bundled. Any future sample data must have a
  demonstrably permissive licence, recorded here before inclusion.

## Fundamentals — known gap
Yahoo's `quoteSummary` endpoint (P/E, ROE, margins, balance-sheet fields)
requires an authenticated crumb and returns 401 to anonymous callers.
`fetch_fundamentals()` therefore returns "not available" in the default
configuration and the Fundamentals Agent scores neutral and says so in
every report. Plugging in a licensed fundamentals provider is on the
roadmap; no financial-statement values are ever estimated or invented.

## Known gaps
- No survivorship-bias-free historical index-constituent universe.
- No intraday data, no order-book data, no options/futures analytics.
- Market calendars are approximated by the provider's trading days.
