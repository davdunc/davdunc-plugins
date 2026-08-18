# Analyst Sources

Sources for trading intelligence extraction. Add YouTube channels, podcasts, blogs, and analysts here. The IngestContent workflow uses this to tag and classify extracted content.

## How to Add a Source

```
User: "ingest this video https://youtube.com/watch?v=xyz"
```

The system will:
1. Extract the transcript
2. Identify the source/channel
3. Run setup, regime, and psychology extraction patterns
4. Append insights to the intelligence base
5. Store full extract in `Intelligence/Analysts/[SourceName].md`

## Active Sources

*Add sources as you discover them. Format:*

### [SourceName]
- **Platform:** YouTube / Podcast / Blog
- **URL:** [channel/feed URL]
- **Focus:** [What they specialize in]
- **Key value:** [Why you follow them]

---

### StockedUp
- **Platform:** YouTube
- **URL:** https://www.youtube.com/@StockedUp
- **Channel ID:** UC-m6zNItyoDk5lSykDlhE4Q
- **RSS:** https://www.youtube.com/feeds/videos.xml?channel_id=UC-m6zNItyoDk5lSykDlhE4Q
- **Cadence:** 1 video/day, published after market close
- **Focus:** End-of-day market recap, macro catalysts (yields, oil, geopolitics), tomorrow's watchlist
- **Key value:** Best single source for next-day pre-game context. Always includes explicit ticker watchlist for tomorrow with thesis. Strong macro-to-micro linkage (30Y yield → SPY → sector rotation). Bookmap/tape reading commentary.
- **Tone:** Educational, measured, macro-first

### TraderTV Live
- **Platform:** YouTube
- **URL:** https://www.youtube.com/@TraderTVLive
- **Channel ID:** UCn75vF3UxwWeWPAY4-5Z6HQ
- **RSS:** https://www.youtube.com/feeds/videos.xml?channel_id=UCn75vF3UxwWeWPAY4-5Z6HQ
- **Cadence:** 4+ videos/day; filter to "Stock Market Live" and "Recap" titled videos
- **Focus:** Intraday live trading, tape reading, level 2, momentum plays
- **Key value:** Live execution commentary on Gap and Go, VWAP bounces, bear raids. Shows what the crowd is watching intraday.
- **Tone:** Live, fast-paced, momentum-focused
- **Filter keywords:** `stock market live`, `recap`, `live trading`, `bear raid`, `trading floor`, `open`, `close`

### Kristen Zisek
- **Platform:** YouTube Shorts
- **URL:** https://www.youtube.com/@KristenZisek
- **Channel ID:** UCLqRujjaNTOIbsmc1Bmos3w
- **Cadence:** Near-daily "Market Update: {Weekday} Morning" Shorts, published **07:49–08:30 ET**
- **⚠️ MORNING channel, not evening.** Pull during MorningGamePlan Phase 1
  (`video_intel.py --channel Kristen --date $(date +%F)`), not in EveningVideoReview — an evening run
  fetches the *prior* morning's update, which is already priced in by the time you plan.
- **Focus:** Earnings breakdowns, consumer sector, accessible retail investor analysis
- **Key value:** Fast earnings summaries with consumer behavior context. Good for capturing market reactions to consumer staples/retail misses. Connects macro stress (consumer confidence) to individual stock moves.
- **Tone:** Educational, conversational, accessible

### Blue Cloud Trading
- **Platform:** YouTube
- **URL:** https://www.youtube.com/@BlueCloudTrading
- **Channel ID:** UCzAO0HYt7Eb9r5PN56XizVQ
- **RSS:** https://www.youtube.com/feeds/videos.xml?channel_id=UCzAO0HYt7Eb9r5PN56XizVQ
- **Host:** George
- **Cadence:** ~daily, evening (recorded ~18:40 ET); plus weekly members-only sector scan
- **Format:** Replays CNBC Halftime/Power Lunch clips, then charts every name mentioned. 60-75 min.
- **Method:** **Ichimoku** (price vs 9/26 period, cloud, chikou span, senkou A vs B) on **weekly first, then daily** + **directional movement index** (ADX9, +DI/-DI). Awards a "blue flag" only when a name meets full bullish Ichimoku criteria on BOTH weekly and daily.
- **Key value:** A consistent, mechanical bull/bear filter applied to whatever the CNBC panel is talking about — useful as an independent check on a discretionary thesis. The blue-flag count is a fast breadth read.
- **Tone:** Methodical, level-driven, explicitly avoids "it's cheap" reasoning
- **Publishes:** evening piece lands 20:00–21:16 ET (= 00:00+ UTC next day; rollover window applies)
- **Filter keywords:** `technical analysis by blue cloud`, `half time`, `stock market analysis`, `power lunch`
  <!-- `half time`, not `half time report`: the channel titles these "Half Time & Closing Bell",
       which the longer keyword does not match. Cost us 2026-08-17 entirely. This widens the
       match but does NOT fix the general fragility — 2026-08-14 was lost to a guest-quote
       headline ("Josh Brown says ...") that no keyword list would anticipate. Blue Cloud posts
       ~1 video/day, so the filter is guarding against a volume problem it does not have;
       removing the line outright is the proposed real fix, pending the pipeline owner's call. -->
  <!-- 2026-07-28: the single "technical analysis by blue cloud" keyword matched only 1 of 15 recent
       videos. Their evening titles lead with the guest/thesis ("TOM LEE SAYS...", "Half Time Report
       - Stock picks") and append the analysis phrase inconsistently. Broadened to match the real
       title conventions. #shorts clips still fall through, which is intended. -->, ticker + date in title
