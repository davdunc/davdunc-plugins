# Trading Preferences — Template

Copy this file to `~/.claude/PAI/USER/SKILLCUSTOMIZATIONS/Trading/PREFERENCES.md` and fill in your values. Do NOT commit the populated version to a public repo — it contains broker account numbers and risk parameters.

## API Keys

All API keys are stored in `~/.claude/.env`. Reference them by env var name; do NOT duplicate values here.

| Service | Env Var | Notes |
|---------|---------|-------|
| Finviz | `FINVIZ_API_KEY` | Screener data |
| Massive.com | `MASSIVE_API_KEY` | OHLCV / market data REST API |
| Massive flat files | `MASSIVE_S3_ACCESS_KEY` + `MASSIVE_S3_SECRET_KEY` | Bulk historical (S3-compatible) |
| Polygon.io | `POLYGON_API_KEY` | News + snapshots fallback |
| Notion | `NOTION_API_KEY` | Game plan + review database integration |
| SEC EDGAR | `EDGAR_USER_AGENT` | User-Agent string, not a secret |
| DAS Trader CMD API | `DAS_USER`, `DAS_PASS`, `DAS_ACCT`, `DAS_LIVE_ACCT`, `DAS_HOST`, `DAS_PORT` | TCP socket on Windows host |

## Account Configuration

### DAS Trader / Cobra Trading
- **Live account:** `<your-live-account-id>` (e.g. 1RB16917)
- **Sim account:** `<your-sim-account-id>` (e.g. TR4425)
- **Trade export path:** `<windows-path-to-Trade_Review>` (e.g. `/mnt/c/Users/<winuser>/OneDrive/Documents/Trade_Review/`)

### Notion
- **Workspace:** `<your-workspace-name>`
- **Game Plan DB data source:** `collection://<uuid>`
- **Fresh News DB data source:** `collection://<uuid>`
- **Second Day Plays DB data source:** `collection://<uuid>`

### Slack
- **Watchlist channel ID:** `<channel-id>` (e.g. C0B5U2DHB0U)

## Trading Preferences

### Risk Parameters

> **R-CONFIG — SINGLE SOURCE OF TRUTH**
> All Trading skill workflows (MorningGamePlan, DailyReview, IngestTrades) read R-basis from this block.
> Update these three numbers when account size or risk tolerance changes; do NOT hard-code R values anywhere else.

| Variable | Value | Meaning |
|----------|-------|---------|
| `ACCOUNT_SIZE` | **$<your-account>** | Working capital across LIVE + SIM |
| `R_PERCENT` | **1.0%** | Max risk per trade as % of account |
| `R_VALUE` | **$<derived>** | Derived: `ACCOUNT_SIZE × R_PERCENT` — this is **1R** |
| `DAILY_MAX_R` | **3R ($<derived>)** | Auto-disengage at -3R daily loss |
| `PER_SYMBOL_MAX_R` | **1R ($<derived>)** | Per-ticker hard stop lockout for the session |
| `MAX_LIVE_TICKERS` | **2** | Concurrent LIVE-account tickers per session |

**How to update:** Edit the three primary values above (`ACCOUNT_SIZE`, `R_PERCENT`, derived `R_VALUE`). Workflows + memories that reference R will recompute against the new basis on next run.

**How workflows reference this:** Use phrasing like *"1R per PREFERENCES.md ($X derived)"* or *"max −3R per PREFERENCES.md"* — never hard-code dollar amounts in workflow output, always express in R-units with the derived dollar in parentheses for operator readability.

### Schedule
- **Time zone:** `<your-tz>` (e.g. Central CT)
- **Pre-market routine:** `<HH:MM-HH:MM>` local
- **Market open:** `08:30 CT` / `09:30 ET`
- **Trading window:** `<your-window>`

### Screener Defaults (Finviz)
- **Min gap %:** 3
- **Min pre-market volume:** 500,000
- **Min price:** $5.00
- **Max price:** $500.00

### EDGAR Defaults
- **Filing lookback:** 30 days
- **Filing types:** 8-K, 10-Q, S-1, SC 13D, Form 4
- **Catalyst keywords:** acquisition, merger, partnership, offering, FDA, approval, contract, restructuring, leadership, insider

### Banned Tickers (Live Account)
List tickers you've audited and decided not to trade LIVE (e.g. from a multi-week broker audit). Example format:
- `MU` — sim only until 5 consecutive profitable sim sessions
- `<TICKER>` — `<reason + criteria for re-enable>`

### Multi-Day / Overnight Hold Rule
- **No overnight or weekend holds** unless the position was explicitly thesis-positioned in advance with a defined invalidation level documented in the morning game plan.
- All intraday positions must be flat by EOD unless the above thesis-and-invalidation pre-condition is met.

### Per-Symbol Stop Lockout
- **Hard stop per ticker: 1R = $<derived> loss** — once a ticker reaches −1R cumulative for the session, that ticker is closed and locked for the rest of the day.
- Enforcement: DAS-side hotkey/script lockout (configured separately in DAS Trader). PAI side: any review/agent recognizing a per-symbol stop hit MUST refuse to advise further entries on that ticker for the session.
