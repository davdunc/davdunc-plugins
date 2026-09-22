---
description: Deep dive research on a specific ticker — quote, OHLCV, filings, and intelligence
---

# ResearchTicker Workflow

## Steps

### 1. Get Fundamentals (Finviz)

Pull the Finviz snapshot for the ticker:
- Price, Change%, Volume, Avg Volume, Relative Volume
- Market Cap, Float, Short Interest %
- ATR, RSI, 52-Week Range
- Sector, Industry
- Earnings date (if upcoming)

### 2. Get OHLCV (Massive.com)

Pull historical candle data:
- **Daily candles (20 days):** Identify trend, calculate Camarilla pivots from yesterday
- **Weekly candles (12 weeks):** Higher timeframe context
- **Calculate:**
  - Camarilla S1-S4, R1-R4 from prior day
  - ATR (14-period)
  - Key support/resistance levels
  - Whether 9-EMA is above/below VWAP and 21-EMA

### 3. Check SEC Filings (EDGAR)

**Full method + endpoints:** `Reference/DataSources.md → SEC EDGAR`. Summary: ticker → CIK via
`company_tickers.json`, then `data.sec.gov/submissions/CIK....json` for the filing list, then fetch the
specific document. Requires a descriptive `User-Agent` with contact info (`EDGAR_USER_AGENT` env var) or
sec.gov returns 403 — this is not optional and not a bug to route around.

- Last 30 days of 8-K, 10-Q, S-1, SC 13D, Form 4
- Extract catalyst keywords from filing descriptions (see `DataSources.md` for the list)
- **Dilution check (ATM/shelf offerings, resale registrations, warrant overhang):** read S-3, 424B5,
  424B3 filings — search for "at-the-market", registered resale share counts, and warrant strike
  prices vs. shares outstanding. A news-only scan misses all of these; see the worked USDE example in
  memory `reference_sec_edgar_access.md`.
- **Insider transactions (Form 4):** parse `<transactionCode>` (P=purchase, S=sale),
  `<transactionShares>`, `<transactionPricePerShare>` — don't trust a news headline's dollar figure
  without confirming shares × price against it.
- Flag: offerings, acquisitions, partnerships, FDA events, insider activity
- Summarize any material findings in 2-3 sentences

### 4. Query Intelligence Base

Search the intelligence base for:
- Any analyst mentions of this ticker
- Matching setup patterns (if the chart matches a known playbook setup)
- Sector/industry insights
- Historical notes from past game plans or reviews

### 5. Match to Playbook Setup

Based on the data gathered, determine:
- Which playbook setup does this match? (per PlaybookSetups.md)
- What grade would this get? (A+ through C)
- Long bias, short bias, or neutral?

### 6. Output Research Report

```
═══ TICKER RESEARCH: [SYMBOL] ═══

FUNDAMENTALS:
Price: $X | ATR: $X | Float: XM | Short: X%
Mkt Cap: $XB | Rel Vol: X.Xx | RSI: XX
Sector: [sector] | Earnings: [date or N/A]

KEY LEVELS (Camarilla from prior day):
R4: $X.XX | R3: $X.XX | R2: $X.XX | R1: $X.XX
S1: $X.XX | S2: $X.XX | S3: $X.XX | S4: $X.XX

RECENT FILINGS:
[List of filings with dates and catalyst flags]

SETUP MATCH: [setup name] | GRADE: [X] | BIAS: [Long/Short/Neutral]

INTELLIGENCE:
[Relevant analyst insights, past review notes]

TRADE PLAN (if actionable):
Entry: [trigger]
Stop: [level]
Target: [level]
R:R: [ratio]
```
