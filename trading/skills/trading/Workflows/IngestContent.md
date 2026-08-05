---
description: Extract trading intelligence from YouTube videos, articles, and podcasts
---

# IngestContent Workflow

## Steps

### 1. Identify Source

Determine the content type and source:
- YouTube video → extract transcript
- Article URL → fetch and parse
- Podcast → transcribe if audio URL provided

For YouTube, use the existing ContentAnalysis or Research skill's YouTube extraction capability (Fabric patterns).

### 2. Extract Transcript/Content

Get the full text content from the source.

### 3. Run Trading-Specific Extraction

Extract the following categories from the content:

**Setup Insights:**
- Any specific trade setups mentioned (ORB, VWAP, gap, breakout, etc.)
- Entry criteria, exit criteria, stop placement
- Examples and case studies

**Market Regime Commentary:**
- Trending, ranging, volatile, gap day analysis
- How to adapt strategy to current conditions
- Sector rotation insights

**Ticker-Specific Analysis:**
- Any specific tickers discussed with analysis
- Key levels, catalysts, thesis

**Risk Management:**
- Position sizing rules
- Stop loss strategies
- When to sit out

**Psychology & Discipline:**
- Mental game insights
- Common mistakes discussed
- Behavioral patterns to watch for

### 4. Classify and Store

For each extracted insight:

1. **Determine category:** Setup, Regime, Psychology, or Ticker-specific
2. **Append to the appropriate intelligence file:**
   - Setup insights → `~/.claude/LifeOS/USER/TRADING/Intelligence/Setups/[SetupName].md`
   - Regime insights → `~/.claude/LifeOS/USER/TRADING/Intelligence/MarketRegimes/[Regime].md`
   - Psychology → `~/.claude/LifeOS/USER/TRADING/Intelligence/Psychology/[Topic].md`
3. **Store full extract:** `~/.claude/LifeOS/USER/TRADING/Intelligence/Analysts/[SourceName].md`

**Entry format for each insight:**
```markdown
### [Insight Title]
- **Source:** [Channel/Author Name]
- **Date extracted:** [YYYY-MM-DD]
- **URL:** [source URL]
- **Context:** [1-2 sentence summary]

[The actual insight/quote/technique]
```

### 5. Update AnalystSources.md

If this is a new source, add it to `~/.claude/skills/Trading/AnalystSources.md` with:
- Platform, URL, Focus area, Key value

### 6. Create Intelligence Files If Needed

If a setup, regime, or psychology file doesn't exist yet, create it with a header:

```markdown
# [Topic Name]

Intelligence gathered from analyst content, personal experience, and market research.

---

[First entry here]
```

### 7. Confirm and Summarize

Output:
- Number of insights extracted
- Which intelligence files were updated
- Key takeaways in 3-5 bullets
- Ask if anything was missed or should be recategorized
