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
- **Cadence:** Occasional; earnings-driven Shorts (1-3 min)
- **Focus:** Earnings breakdowns, consumer sector, accessible retail investor analysis
- **Key value:** Fast earnings summaries with consumer behavior context. Good for capturing market reactions to consumer staples/retail misses. Connects macro stress (consumer confidence) to individual stock moves.
- **Tone:** Educational, conversational, accessible
