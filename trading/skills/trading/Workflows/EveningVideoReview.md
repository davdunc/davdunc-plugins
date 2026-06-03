---
description: Evening review of StockedUp and TraderTV Live YouTube videos — trending stocks, catalysts, tomorrow's watchlist
---

# EveningVideoReview Workflow

Runs after market close (4 PM CT / 5 PM ET or later). Discovers today's videos from StockedUp and
TraderTV Live, pulls transcripts, extracts trading intelligence, and writes a structured digest plus
a pre-game notes file for tomorrow's MorningGamePlan.

## Channels

| Channel      | YouTube Handle      | Channel ID                 | Format                |
|--------------|---------------------|----------------------------|-----------------------|
| StockedUp    | @StockedUp          | UC-m6zNItyoDk5lSykDlhE4Q  | 1 evening recap/day   |
| TraderTV Live| @TraderTVLive       | UCn75vF3UxwWeWPAY4-5Z6HQ  | 4+ videos/day; filter to session recaps |

## Steps

### Step 1 — Discover today's videos

Run the transcript fetch script for both channels:

```bash
python3 ~/falcon/dashboard/transcript_fetch.py --channel stocked-up
python3 ~/falcon/dashboard/transcript_fetch.py --channel tradertv
```

If today's date is Saturday or Sunday, use the most recent trading day (last Friday) instead.

If a channel has no videos for the date, note it but continue with whichever channel has content.

For TraderTV Live, the script automatically filters to recap-style videos using title keywords
(`stock market live`, `recap`, `live trading`, `bear raid`, `open`, `close`). If the filter
excludes all videos and the user wants a specific video, pass the video ID directly:

```bash
python3 ~/falcon/dashboard/transcript_fetch.py VIDEO_ID
```

### Step 2 — Extract transcripts

The script outputs JSON with `transcript` field for each video. Parse this and extract the full
transcript text. If `has_transcript: false`, the video's captions aren't available yet (live
stream processed within last 1-2 hours). Note this in the output and skip that video.

### Step 3 — Analyze transcripts for trading intelligence

For EACH transcript, extract the following using a focused analytical pass:

#### A. Stock Tickers Mentioned

Scan for uppercase ticker patterns (1-5 capital letters preceded by `$` or as standalone known
symbols). For each ticker found, extract:
- Full context sentence(s) where it's mentioned
- Whether it's bullish, bearish, or neutral context
- Whether it's named as a next-day play or watchlist candidate

Common ticker aliases to recognize: SPY (S&P 500), QQQ (Nasdaq), IWM (Russell 2000), TLT (bonds),
USO (oil), GLD (gold), VIX (volatility index).

#### B. Key Market Catalysts

Extract events mentioned that are moving or expected to move the market:
- Macro: Fed decisions, yield moves, CPI/PPI/jobs data, geopolitical events
- Earnings: company results or upcoming earnings reports
- News: single-event catalysts (executive tweets, regulatory rulings, acquisitions, etc.)
- Sector themes: rotation into/out of sectors, sector ETF moves

#### C. Tomorrow's Watchlist

Identify stocks or setups the presenter explicitly names for the next trading day:
- Phrases like: "watching X tomorrow", "X is on my list", "if X does Y, I'm interested",
  "going to be watching", "tomorrow's play", "game plan for tomorrow"
- These are the highest-priority items for the pre-game notes file

#### D. Market Regime

Identify regime language:
- Trending vs. choppy
- Risk-on vs. risk-off
- Sector rotation signals
- Overall market bias for tomorrow (bullish, bearish, neutral, selective)

#### E. Setup Types Mentioned

Note any specific setups discussed (VWAP bounce, gap and go, ORB, FL, 9EMA cross, etc.) that
connect to the playbook. Store these in the intelligence base for setup reinforcement.

### Step 4 — Generate the evening review digest

Output this structured format to the console:

```
═══ EVENING REVIEW — {DATE} ══════════════════════════════════════════
SOURCES:
  StockedUp:     "{title}" ({duration})
  TraderTV Live: "{title}" ({duration})

MARKET REGIME: {one-line regime assessment}

TICKERS MENTIONED
  {TICKER}  {bullish/bearish/neutral}  {context — 1 sentence}
  ...

KEY CATALYSTS FOR TOMORROW
  • {catalyst description}
  ...

TOMORROW'S WATCHLIST (explicitly named for next day)
  {TICKER}  {setup or thesis from video}
  ...

SETUPS DISCUSSED
  {Setup type}  —  {how it was used in context}
  ...

INTELLIGENCE BASE UPDATED
  {list of files written}
```

### Step 5 — Store to intelligence base

For each source, append a dated entry to the analyst file:

**StockedUp entries → `~/.claude/PAI/USER/TRADING/Intelligence/Analysts/StockedUp.md`**
**TraderTV Live entries → `~/.claude/PAI/USER/TRADING/Intelligence/Analysts/TraderTVLive.md`**

Entry format:
```markdown
### {Video Title}
- **Date:** {YYYY-MM-DD}
- **URL:** https://www.youtube.com/watch?v={video_id}
- **Regime:** {regime assessment}
- **Key tickers:** {comma-separated list}

**Catalysts:**
{bullet list of catalysts}

**Tomorrow's watchlist:**
{bullet list of named tickers/setups}

**Setup insights:**
{any setup-type observations worth keeping}
```

If either analyst file does not exist, create it with this header:
```markdown
# {Channel Name} — Intelligence

Trading intelligence extracted from daily market recap videos.

---
```

For significant regime insights, also append to:
- `~/.claude/PAI/USER/TRADING/Intelligence/MarketRegimes/` (file matching current regime type)

For setup insights, also append to:
- `~/.claude/PAI/USER/TRADING/Intelligence/Setups/[SetupName].md`

### Step 6 — Write tomorrow's pre-game notes

Write (or overwrite) a pre-game notes file that MorningGamePlan can pick up:

**File:** `~/.claude/PAI/USER/TRADING/Reviews/{TOMORROW_DATE}-evening-notes.md`

```markdown
# Evening Notes — {TODAY_DATE} → {TOMORROW_DATE}

## Market Regime
{regime assessment from both sources}

## Watchlist from Evening Review
| Ticker | Thesis | Source |
|--------|--------|--------|
| {TICKER} | {thesis} | StockedUp |
| {TICKER} | {thesis} | TraderTV Live |

## Key Catalysts to Watch
{bullet list}

## Macro / Yields / Macro Backdrop
{macro commentary if significant}

## Setup Notes
{any setup-specific notes for tomorrow}
```

### Step 7 — Confirm and summarize

Output:
- Total videos processed / skipped (no captions)
- Total tickers extracted across all videos
- Tomorrow's watchlist ticker count
- Which intelligence files were updated
- Path to pre-game notes file

Ask: "Should I add any of these tickers to tomorrow's game plan, or run a deeper research pass on any of them?"

## Graceful degradation

**No videos today:** Output "No {channel} videos found for {date}. Is it a market holiday or weekend?"
Check if the most recent video is from the prior trading day and offer to process that instead.

**No captions available:** Output "{video_id} captions not yet available (live stream too recent).
Try again after 7 PM CT." Do not error — process whichever videos have captions.

**yt-dlp fails:** Log the error, skip the video, continue.

## Integration with MorningGamePlan

MorningGamePlan Phase 1 (symbol discovery) should check for a same-date evening notes file:

```bash
TOMORROW=$(date +%Y-%m-%d)
NOTES=~/.claude/PAI/USER/TRADING/Reviews/${TOMORROW}-evening-notes.md
```

If it exists, the watchlist tickers from that file should be pre-seeded into the game plan's
symbol list alongside the Finviz gapper scan.
