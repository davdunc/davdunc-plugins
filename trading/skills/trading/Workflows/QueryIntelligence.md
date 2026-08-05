---
description: Search the trading intelligence base for insights by topic, setup, analyst, or ticker
---

# QueryIntelligence Workflow

## Steps

### 1. Parse the Query

Determine what the user is searching for:
- **Setup:** "what does intel say about VWAP plays" → search Setups/
- **Regime:** "how to trade ranging markets" → search MarketRegimes/
- **Psychology:** "what about revenge trading" → search Psychology/
- **Analyst:** "what has SMB Capital said" → search Analysts/
- **Ticker:** "any intel on ARM" → search all files for ticker mention
- **General:** broad search across all intelligence files

### 2. Search the Intelligence Base

Base path: `~/.claude/LifeOS/USER/TRADING/Intelligence/`

Search strategy:
1. Grep for keywords across relevant directories
2. Read matching files
3. Extract relevant sections

### 3. Present Results

For each match:
- Source and date
- The insight/quote
- Context of how it applies to the query

### 4. Cross-Reference

If the query relates to a specific setup or ticker:
- Also check `PlaybookSetups.md` for the formal setup definition
- Check `~/.claude/LifeOS/USER/TRADING/Reviews/` for historical trades matching this pattern
- Check TELOS WISDOM.md for personal lessons related to the topic

### 5. Synthesize

If multiple sources address the topic, provide a synthesis:
- Points of consensus across analysts
- Contradictions or alternative approaches
- Your own historical performance with this setup/pattern
