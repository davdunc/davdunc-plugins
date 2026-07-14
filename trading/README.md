# trading

Claude Code skill for intraday momentum trading — morning game plans, daily reviews (R-units, both-account aware), evening video review of analyst recaps, SEC EDGAR filings lookup, statistical covariance, and deterministic publish to Notion + Slack + DAS Trader Market Viewer.

## Installation

```bash
cd ~/Projects
git clone https://github.com/davdunc/davdunc-plugins.git
cd davdunc-plugins/trading
# Symlink the skill into your Claude Code skills directory
ln -s "$PWD/skills/trading" ~/.claude/skills/Trading
```

## Configuration

The skill expects user-specific configuration in `~/.claude/PAI/USER/SKILLCUSTOMIZATIONS/Trading/`. Copy the template to bootstrap:

```bash
mkdir -p ~/.claude/PAI/USER/SKILLCUSTOMIZATIONS/Trading
cp ~/.claude/skills/Trading/Templates/SKILLCUSTOMIZATIONS/PREFERENCES.template.md \
   ~/.claude/PAI/USER/SKILLCUSTOMIZATIONS/Trading/PREFERENCES.md
# Edit PREFERENCES.md with your broker accounts, R-CONFIG, banned tickers, etc.
```

Initialize the intelligence base:

```bash
mkdir -p ~/.claude/PAI/USER/TRADING/Intelligence/{Setups,Analysts,MarketRegimes,Psychology}
mkdir -p ~/.claude/PAI/USER/TRADING/Reviews
# Optional: copy the seed Offsides-Short setup template
cp ~/.claude/skills/Trading/Templates/Intelligence/Setups/OffsidesShort.md \
   ~/.claude/PAI/USER/TRADING/Intelligence/Setups/
```

## Required Applications

| Application | Purpose | Install |
|-------------|---------|---------|
| Python 3.11+ | Workflow scripts | `dnf5 install python3` or `uv python install` |
| `falcon-stats` CLI | **Canonical P&L source for DailyReview** (per workflow HARD RULE) | `uv tool install falcon-stats` or `pip install falcon-stats` |
| `boto3` | DynamoDB persistence + S3 flat files | `uv pip install boto3` |
| `yt-dlp` | EveningVideoReview transcript fetch | `dnf5 install yt-dlp` |
| `bun` | LifeOS inference tools | https://bun.sh/install |
| `gh` CLI | EDGAR / GitHub fallback | `dnf5 install gh` |
| `curl` | Voice notify daemon (port 8888) | system default |
| DAS Trader Pro | Real-time quotes + order execution | Windows-side install (operator-managed) |

## Required Environment Variables

Stored in `~/.claude/.env` (not committed):

```bash
# Market data
POLYGON_API_KEY=...
FINVIZ_API_KEY=...
MASSIVE_API_KEY=...
MASSIVE_S3_ACCESS_KEY=...
MASSIVE_S3_SECRET_KEY=...

# Integrations
NOTION_API_KEY=...
EDGAR_USER_AGENT="<your-name> <your-email>"

# DAS Trader CMD API (TCP socket on Windows host)
DAS_HOST=172.18.160.1
DAS_PORT=9910
DAS_USER=...
DAS_PASS=...
DAS_ACCT=<sim-account-id>
DAS_LIVE_ACCT=<live-account-id>

# AWS (DynamoDB falcon-trades us-east-2)
AWS_DEFAULT_REGION=us-east-2
FALCON_TRADES_TABLE=falcon-trades
```

## Required MCP Connectors (claude.ai side)

| Connector | Purpose |
|-----------|---------|
| Notion | Game plan + daily review DB writes |
| Slack | #watchlist deterministic posts |
| MT Newswires (optional) | Alternative catalyst stream — workflow defaults to Polygon newsfeed |

## Workflows

| Workflow | Trigger phrases | Purpose |
|----------|----------------|---------|
| **MorningGamePlan** | "morning game plan", "build game plan" | Macro context + screener + intel + thesis → publish to Notion + Slack + DAS |
| **DailyReview** | "daily review", "report card" | falcon-stats ingest (both accounts) + R-units P&L + discipline score + multi-day trend |
| **EveningVideoReview** | "evening review", "tradertv", "stocked up" | StockedUp + TraderTV transcript ingest + tomorrow's watchlist |
| **WeeklyReadiness** | "sunday prep", "week ahead" | Cross-session pattern review + week-ahead bias |
| **IngestTrades** | "ingest trades" | DAS Trades.csv → falcon-stats → DynamoDB |
| **WeeklyReview** | "weekly review" | 5-day discipline + R-stat aggregation |
| **ResearchTicker** | "research TICKER", "what's the story on" | EDGAR + Polygon + intel-base lookup |
| **IngestContent** | "ingest video", "extract from youtube" | Analyst content → Intelligence/Analysts/ |
| **QueryIntelligence** | "what does my intel say" | Search intelligence base |
| **UpdateTelos** | "save trading lessons" | Trading lessons → TELOS |

## HARD RULES (baked into workflows)

These are workflow-level blockers that prevent recurring failure patterns:

1. **`falcon-stats ingest` is the ONLY allowed P&L source** for DailyReview (no hand-rolled FIFO aggregation)
2. **Both accounts MUST be confirmed** before drafting any P&L summary (LIVE + SIM)
3. **R-units required** for all P&L + outcome reporting (read R-CONFIG from PREFERENCES.md)
4. **Publish is deterministic** — after synthesis, immediately fire Notion + Slack + DAS in parallel; never AskUserQuestion about publish-yes-or-no

See `Workflows/DailyReview.md` and `Workflows/MorningGamePlan.md` for the full ⛔ HARD RULES sections.

## File Layout

```
skills/trading/
├── SKILL.md                          # Skill manifest + workflow routing
├── Workflows/                        # 10 workflows (Morning/Daily/Weekly/Ingest/Research)
├── Reference/                        # PlaybookSetups, RulesOfEngagement, DataSources, AnalystSources
├── Config/                           # FinvizColumnSchema.json, youtube-channels.json
└── Templates/
    ├── SKILLCUSTOMIZATIONS/
    │   └── PREFERENCES.template.md   # Copy to ~/.claude/PAI/USER/SKILLCUSTOMIZATIONS/Trading/
    └── Intelligence/
        └── Setups/OffsidesShort.md   # Scaled-SS template for EXTREME z-score gaps
```

## Compatibility

- **Operating system:** Linux (tested Fedora 44 + Ubuntu/WSL2) — DAS Trader runs Windows-side, accessed via TCP socket
- **Claude Code:** v2.1.x or later
- **LifeOS (formerly PAI):** 4.0.3 or later (uses Algorithm v3.7.0 mode framing)
- **Falcon ecosystem:** designed to integrate with the operator's FL (Fashionably Late) auto-trader; works standalone if FL is absent
