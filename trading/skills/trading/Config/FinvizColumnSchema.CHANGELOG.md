# Changelog: FinvizColumnSchema.json

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the schema
uses [Semantic Versioning](https://semver.org/):

- **MAJOR**: a column ID is removed or changes meaning, or a valid selection becomes invalid.
- **MINOR**: new column IDs or catalog entries. Every selection that was valid stays valid.
- **PATCH**: corrections to names, categories, descriptions or documentation.

## [1.1.0] - 2026-11-19

Verified against the live Finviz Elite export (`v=152`, AAPL and SPY, every ID from 0 to 260
requested in chunks). The API serves 157 contiguous column IDs, 0–156. Every ID above 156 is dropped.

### Added
- IDs **151–156** in `columns.items.enum` and `columnDefinition.id.maximum` (was 150, now 156):
  Security Type, Tracked Index, Candlestick, Dilution Risk, Performance (MTD), Average Dollar Volume.
- Catalog entries for **IDs 96–156** (61 columns). The 1.0.0 catalog stopped at 95, so IDs 96–150
  were valid but undocumented:
  - **intraday**: Performance (30 Minutes / 1 Hour / 2 Hours / 4 Hours), IDs 96–99.
  - **ETF**, all `assetScope: etf`:
    - Asset Type, ETF Type, Region, Single Category, Sector/Theme, Tags, Active/Passive (100–106);
    - Net Expense Ratio, Total Holdings, AUM, NAV, NAV %, Net Flows and Net Flows % over 1M / 3M / YTD / 1Y (107–119);
    - Return 1Y / 3Y / 5Y / 10Y / Since Inception (120–124);
    - Tracked Index (152).
  - **news**: News Time, News URL, News Title (135–137). The latest headline per ticker comes inline with a screen.
  - **events**: EPS Surprise and Revenue Surprise (127–128).
  - **technical**: All-Time High, All-Time Low, 52-Week Range, Candlestick.
  - **growth**: EPS / Sales Year Over Year TTM, EPS / Sales Growth Past 3 Years.
  - **valuation**: Enterprise Value, EV/EBITDA, EV/Sales.
  - **dividends**: Dividend TTM, Dividend Ex Date, Dividend Growth 1Y / 3Y / 5Y.
  - **price-volume**: After-Hours Volume, Average Dollar Volume.
  - **performance**: Performance 3Y / 5Y / 10Y / MTD.
  - **classification**: Exchange, Security Type.
  - **fundamentals**: Dilution Risk.
- Top-level `version` and `$comment` (verification date, endpoint, this changelog).

### Unchanged
- IDs 0–95: every name in the 1.0.0 catalog still matches the live CSV header exactly.
- The `c=` pattern, `profile`, and the category and asset-scope enums need no new values.

### Notes
- **Endpoint:** `https://elite.finviz.com/export.ashx` now answers **301 → `/export`**, and
  `news_export.ashx` answers **301 → `/news_export`**. Clients must follow redirects or call the
  new paths. A client that doesn't follow redirects gets an empty body.
- **Classifications that could not be confirmed:**
  - The `assetScope` of Daily Digest (150, category `other`), Dilution Risk (154) and After-Hours
    Volume (141) is a best guess. All three were blank for both test tickers at verification time
    (premarket).
  - The ETF columns are blank for stocks and filled for SPY.

## [1.0.0] - 2026-05-27

Initial schema, published with "Taming the Finviz Elite Export API with a JSON Schema"
(davidduncan.org). Column IDs 0–150 in the enum, catalog entries for 0–95.
