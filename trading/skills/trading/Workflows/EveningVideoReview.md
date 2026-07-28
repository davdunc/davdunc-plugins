---
description: Evening review of StockedUp and TraderTV Live YouTube videos — trending stocks, catalysts, tomorrow's watchlist
---

# EveningVideoReview Workflow

Runs after market close (4 PM CT / 5 PM ET or later). Discovers today's videos from StockedUp and
TraderTV Live, pulls transcripts, extracts trading intelligence, and writes a structured digest plus
a pre-game notes file for tomorrow's MorningGamePlan.

## Channels

Authoritative list lives in `AnalystSources.md`; `video_intel.py --list` prints it. Current state:

| Channel            | Handle           | Format                                  | Filter |
|--------------------|------------------|-----------------------------------------|--------|
| StockedUp          | @StockedUp       | 1 evening recap/day                     | none |
| TraderTV Live      | @TraderTVLive    | 4+ videos/day; session recaps only      | 7 keywords |
| Kristen Zisek      | @KristenZisek    | occasional earnings Shorts              | none |
| Blue Cloud Trading | @BlueCloudTrading| ~daily evening Ichimoku scan            | 1 keyword |

## Steps

### Step 1 — Discover today's videos

Run `video_intel.py` for all registered channels at once:

```bash
python3 ~/.claude/Tools/video_intel.py                    # prior session, every channel
python3 ~/.claude/Tools/video_intel.py --date 2026-07-27  # explicit date
python3 ~/.claude/Tools/video_intel.py --channel StockedUp
```

Channels come from `AnalystSources.md` — any `### Name` block with a `**Channel ID:**` line is
picked up automatically. Run `--list` to see what is registered and which channels are filtered.

The tool handles the **UTC rollover**: evening hosts record after the ET close, so a "07/27" recap
can carry a published stamp of 07-28. Next-calendar-day publishes up to 10:00 UTC (05:00 ET) count
as the target session; anything later is genuinely the next session's video.

If today is Saturday or Sunday the default already walks back to the most recent weekday.

If a channel has no videos for the date, note it but continue with whichever channel has content.

**Title filtering.** Channels that post many videos a day declare a `**Filter keywords:**` line in
`AnalystSources.md` (backtick-quoted fragments). TraderTV Live posts 4+ videos/day and is filtered
to recap-style titles; StockedUp and Kristen Zisek are unfiltered. Non-matching videos are reported
as `skipped (title filter)` on stderr — they are never dropped silently. To take everything anyway:

```bash
python3 ~/.claude/Tools/video_intel.py --all
```

To pull one specific video regardless of channel, date window or filter, pass its ID:

```bash
python3 ~/.claude/Tools/video_intel.py VIDEO_ID [VIDEO_ID ...]
```

### Step 2 — Extract transcripts

The tool writes one plain-text transcript per video to
`~/.claude/LifeOS/USER/TRADING/Intelligence/transcripts/` and prints the path for each. Read those
files for the analysis pass. Naming is `{DATE}_{Channel}_{videoId}.txt`, or
`{DATE}_direct_{videoId}.txt` for a directly-requested ID.

The cache is authoritative: a transcript already on disk is never refetched (reported as `cached`).
A video whose captions are not ready yet — live stream processed within the last 1-2 hours — fails
with `empty (rc=...)` rather than writing a file. Note it in the output and skip that video; retry
after 7 PM CT.

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

**StockedUp entries → `~/.claude/LifeOS/USER/TRADING/Intelligence/Analysts/StockedUp.md`**
**TraderTV Live entries → `~/.claude/LifeOS/USER/TRADING/Intelligence/Analysts/TraderTVLive.md`**

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
- `~/.claude/LifeOS/USER/TRADING/Intelligence/MarketRegimes/` (file matching current regime type)

For setup insights, also append to:
- `~/.claude/LifeOS/USER/TRADING/Intelligence/Setups/[SetupName].md`

### Step 6 — Write tomorrow's pre-game notes

Write (or overwrite) a pre-game notes file that MorningGamePlan can pick up:

**File:** `~/.claude/LifeOS/USER/TRADING/Reviews/{TOMORROW_DATE}-evening-notes.md`

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

**fabric fails:** The tool reports `empty (rc=N)`, `timeout`, or `fabric not installed` per video
and continues to the next. Log it, skip that video, keep going.

**Filter excluded everything:** Output reads `N video(s) for {date}, none matched the title filter`.
This is NOT the same as a quiet news day — re-run with `--all` before concluding a channel was
silent, and check whether the channel changed its title convention.

## Integration with MorningGamePlan

MorningGamePlan Phase 1 (symbol discovery) should check for a same-date evening notes file:

```bash
TOMORROW=$(date +%Y-%m-%d)
NOTES=~/.claude/LifeOS/USER/TRADING/Reviews/${TOMORROW}-evening-notes.md
```

If it exists, the watchlist tickers from that file should be pre-seeded into the game plan's
symbol list alongside the Finviz gapper scan.
