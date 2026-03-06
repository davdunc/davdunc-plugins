import asyncio
import json
from datetime import date

from mcp.server.fastmcp import FastMCP

from . import calendar_events, finviz_client, flatfiles, polygon_client
from .config import MASSIVE_S3_ACCESS_KEY, MIN_ATR_1MIN, MIN_PREMARKET_VOLUME, MIN_RVOL
from .persistence import load_previous_watchlist, load_watchlist, save_watchlist

mcp = FastMCP(
    "equities-watchlist",
    instructions="Daily equities watchlist and trading plan generator",
)


async def _enrich_with_polygon(ticker: str) -> dict:
    """Get Polygon data for a single ticker (RVOL, ATR, pre-market volume, prev close)."""
    loop = asyncio.get_event_loop()

    # Use flat files for pivots when S3 credentials are available, fall back to API
    pivot_fn = (
        flatfiles.calculate_camarilla_from_flatfiles
        if MASSIVE_S3_ACCESS_KEY
        else polygon_client.get_camarilla_pivots
    )

    rvol_result, atr, pm_vol, pivots, details = await asyncio.gather(
        loop.run_in_executor(None, polygon_client.get_relative_volume, ticker),
        loop.run_in_executor(None, polygon_client.get_atr_1min, ticker),
        loop.run_in_executor(None, polygon_client.get_premarket_volume, ticker),
        loop.run_in_executor(None, pivot_fn, ticker),
        loop.run_in_executor(None, polygon_client.get_ticker_details, ticker),
    )

    # get_relative_volume returns (value, source)
    rvol, rvol_source = rvol_result

    prev_close = details.get("prev_close")
    atr_source = "intraday" if atr > 0 else "unavailable"

    # Always fall back to previous day ATR when intraday is 0
    if atr == 0.0:
        # Try flat files first (faster, no API call)
        if MASSIVE_S3_ACCESS_KEY:
            atr = await loop.run_in_executor(
                None, flatfiles.get_previous_day_atr_1min, ticker,
            )
            if atr > 0:
                atr_source = "prev_day"

        # If flat files didn't work, fall back to Polygon API previous day
        if atr == 0.0:
            atr = await loop.run_in_executor(
                None, polygon_client.get_prev_day_atr_1min, ticker,
            )
            if atr > 0:
                atr_source = "prev_day"

    return {
        "rvol": rvol,
        "rvol_source": rvol_source,
        "atr_1min": atr,
        "atr_source": atr_source,
        "premarket_volume": pm_vol,
        "prev_close": prev_close,
        "pivots": pivots,
    }


def _score_candidate(candidate: dict) -> float:
    """Score a candidate for ranking. Higher = more interesting."""
    score = 0.0
    pm_vol = candidate.get("premarket_volume", 0)
    rvol = candidate.get("rvol", 0)
    atr = candidate.get("atr_1min", 0)
    has_news = candidate.get("has_news", False)
    is_prev_day = candidate.get("previous_day", False)

    # Volume is the most important factor
    score += min(pm_vol / 10_000, 50)  # cap contribution at 50

    # RVOL contribution
    score += min(rvol * 5, 25)

    # ATR contribution
    score += min(atr * 3, 15)

    # News bonus
    if has_news:
        score += 10

    # Previous day carryover bonus
    if is_prev_day:
        score += 8

    return round(score, 2)


@mcp.tool()
async def get_watchlist(
    extra_tickers: list[str] | None = None,
) -> str:
    """Build today's equities watchlist by screening for candidates.

    Screens using:
    - Finviz: RVOL > 2, ATR > 1, Avg Volume > 200K
    - Polygon: pre-market volume > 25K, RVOL, 1-min ATR
    - Previous day's watchlist carried over as potential short candidates

    Args:
        extra_tickers: Optional additional tickers to include in screening.

    Returns:
        JSON watchlist with scored and ranked candidates.
    """
    candidates = {}

    # 1. Get Finviz screener candidates
    try:
        finviz_results = await finviz_client.screen_watchlist_candidates()
        for row in finviz_results:
            ticker = row.get("Ticker", "").strip().upper()
            if ticker:
                candidates[ticker] = {
                    "ticker": ticker,
                    "source": "finviz_screener",
                    "finviz_data": row,
                }
    except Exception as e:
        pass  # Finviz may be unavailable

    # 2. Add previous day's watchlist
    prev_date, prev_watchlist = load_previous_watchlist()
    for item in prev_watchlist:
        ticker = item.get("ticker", "")
        if ticker not in candidates:
            candidates[ticker] = {
                "ticker": ticker,
                "source": "previous_day",
                "previous_day": True,
                "prev_date": prev_date.isoformat() if prev_date else None,
            }
        else:
            candidates[ticker]["previous_day"] = True
            candidates[ticker]["prev_date"] = prev_date.isoformat() if prev_date else None

    # 3. Add extra tickers
    if extra_tickers:
        for ticker in extra_tickers:
            ticker = ticker.upper().strip()
            if ticker and ticker not in candidates:
                candidates[ticker] = {
                    "ticker": ticker,
                    "source": "manual",
                }

    # 4. Enrich all candidates with Polygon data
    enrichment_tasks = []
    tickers_to_enrich = list(candidates.keys())
    for ticker in tickers_to_enrich:
        enrichment_tasks.append(_enrich_with_polygon(ticker))

    enrichments = await asyncio.gather(*enrichment_tasks, return_exceptions=True)
    for ticker, enrichment in zip(tickers_to_enrich, enrichments):
        if isinstance(enrichment, Exception):
            continue
        candidates[ticker].update(enrichment)

    # 5. Get news for top candidates (parallel)
    news_tickers = list(candidates.keys())[:30]

    async def _fetch_news(t: str) -> tuple[str, list]:
        try:
            return t, await finviz_client.get_news_for_ticker(t)
        except Exception:
            return t, []

    news_results = await asyncio.gather(*[_fetch_news(t) for t in news_tickers])
    for ticker, news in news_results:
        candidates[ticker]["news"] = news
        candidates[ticker]["has_news"] = len(news) > 0

    # 6. Filter candidates
    filtered = []
    for ticker, data in candidates.items():
        is_prev_day = data.get("previous_day", False)
        pm_vol = data.get("premarket_volume", 0)
        rvol = data.get("rvol", 0)
        atr = data.get("atr_1min", 0)

        # Previous day candidates pass through without meeting criteria
        if is_prev_day:
            data["filter_reason"] = "previous_day_carryover"
            data["score"] = _score_candidate(data)
            filtered.append(data)
            continue

        # Use Finviz volume as fallback when pre-market data isn't available
        finviz_vol = 0
        if "finviz_data" in data:
            try:
                finviz_vol = int(data["finviz_data"].get("Volume", "0"))
            except (ValueError, TypeError):
                finviz_vol = 0
        effective_vol = pm_vol if pm_vol > 0 else finviz_vol

        # Must meet minimum volume
        if effective_vol < MIN_PREMARKET_VOLUME:
            continue
        data["effective_volume"] = effective_vol

        # Must meet at least one of: RVOL or ATR threshold
        meets_rvol = rvol >= MIN_RVOL
        meets_atr = atr >= MIN_ATR_1MIN

        if meets_rvol or meets_atr:
            data["score"] = _score_candidate(data)
            filtered.append(data)

    # 8. Sort by score descending
    filtered.sort(key=lambda x: x.get("score", 0), reverse=True)

    # 9. Save watchlist
    save_watchlist(filtered)

    return json.dumps(filtered, indent=2, default=str)


@mcp.tool()
async def get_trading_plan() -> str:
    """Generate a morning trading plan with market context and watchlist.

    Includes:
    - Market overview (SPY, QQQ, VIX, DIA levels)
    - Today's ranked watchlist with scores
    - Previous day carryover candidates (potential shorts)
    - Key data per ticker: RVOL, ATR, pre-market volume, news

    Returns:
        Formatted trading plan as markdown text.
    """
    # Load today's watchlist (run get_watchlist first if empty)
    watchlist = load_watchlist()
    if not watchlist:
        raw = await get_watchlist()
        watchlist = json.loads(raw)

    # Market overview
    loop = asyncio.get_event_loop()
    overview = await loop.run_in_executor(None, polygon_client.get_market_overview)

    prev_date, prev_wl = load_previous_watchlist()

    lines = []
    lines.append(f"# Trading Plan - {date.today().isoformat()}")
    lines.append("")

    # Market context
    lines.append("## Market Overview")
    lines.append("")
    lines.append("| Symbol | Price | Change % | Volume |")
    lines.append("|--------|-------|----------|--------|")
    for sym, data in overview.items():
        price = f"${data['price']:.2f}" if data["price"] else "N/A"
        chg = f"{data['change_pct']:.2f}%" if data["change_pct"] is not None else "N/A"
        vol = f"{int(data['volume']):,}" if data["volume"] else "N/A"
        lines.append(f"| {sym} | {price} | {chg} | {vol} |")
    lines.append("")

    # Previous day carryover
    prev_tickers = {item.get("ticker") for item in prev_wl} if prev_wl else set()
    if prev_tickers:
        lines.append(f"## Previous Day Carryover ({prev_date})")
        lines.append("*Potential short candidates: trapped shorts may cause rapid price drops*")
        lines.append("")
        for item in watchlist:
            if item.get("previous_day"):
                ticker = item["ticker"]
                score = item.get("score", 0)
                lines.append(f"- **{ticker}** (score: {score})")
        lines.append("")

    # Main watchlist (compact overview)
    lines.append("## Watchlist (Ranked by Score)")
    lines.append("")
    lines.append("| # | Ticker | Score | RVOL | ATR(1m) | PM Vol | Prev Close | News |")
    lines.append("|---|--------|-------|------|---------|--------|------------|------|")
    for i, item in enumerate(watchlist, 1):
        ticker = item.get("ticker", "?")
        score = item.get("score", 0)
        rvol = item.get("rvol", 0)
        rvol_flag = "†" if item.get("rvol_source") == "prev_day" else ""
        atr = item.get("atr_1min", 0)
        atr_flag = "†" if item.get("atr_source") == "prev_day_close" else ""
        pm_vol = item.get("premarket_volume", 0)
        prev_close = item.get("prev_close")
        prev_close_str = f"${prev_close:.2f}" if prev_close else "N/A"
        has_news = "Yes" if item.get("has_news") else "No"
        prev = " *" if item.get("previous_day") else ""
        lines.append(
            f"| {i} | {ticker}{prev} | {score} | {rvol}{rvol_flag} | {atr}{atr_flag} | {pm_vol:,} | {prev_close_str} | {has_news} |"
        )
    lines.append("")
    lines.append("\\* = previous day carryover (short candidate)")
    lines.append("† = value from previous trading day (current day data not yet available)")
    lines.append("")

    # Per-ticker detail cards (top 15): pivots + catalyst + key levels
    lines.append("## Ticker Detail Cards")
    lines.append("")
    for i, item in enumerate(watchlist[:15], 1):
        ticker = item.get("ticker", "?")
        prev_close = item.get("prev_close")
        prev_close_str = f"${prev_close:.2f}" if prev_close else "N/A"
        atr = item.get("atr_1min", 0)
        atr_source = item.get("atr_source", "intraday")
        pivots = item.get("pivots")
        news = item.get("news", [])
        flags = []
        if item.get("previous_day"):
            flags.append("PREV DAY CARRYOVER")
        if atr_source == "prev_day_close":
            flags.append("ATR from prev close")

        lines.append(f"### {i}. {ticker}")
        if flags:
            lines.append(f"**Flags**: {' | '.join(flags)}")
        lines.append(f"**Prev Close**: {prev_close_str} | **ATR(1m)**: {atr}")

        if pivots:
            lines.append(
                f"**Key Levels**: S3 {pivots['S3']} | S1 {pivots['S1']} | "
                f"PP {pivots['PP']} | R1 {pivots['R1']} | R3 {pivots['R3']}"
            )
            lines.append(
                f"**Full Range**: S4 {pivots['S4']} to R4 {pivots['R4']} | "
                f"Prev H/L: {pivots.get('prev_high', 'N/A')}/{pivots.get('prev_low', 'N/A')}"
            )

        if news:
            lines.append(f"**Top Catalyst**: {news[0].get('headline', 'N/A')}")
            if len(news) > 1:
                lines.append(f"**Also**: {news[1].get('headline', 'N/A')}")
        else:
            lines.append("**Catalyst**: None (volume/technical screen only)")

        lines.append("")

    plan = "\n".join(lines)
    return plan


@mcp.tool()
async def get_previous_watchlist() -> str:
    """Load the most recent previous day's watchlist.

    These are candidates that may be good short plays due to trapped shorts
    causing rapid price declines.

    Returns:
        JSON of the previous day's watchlist with the date it was created.
    """
    prev_date, prev_wl = load_previous_watchlist()
    result = {
        "date": prev_date.isoformat() if prev_date else None,
        "count": len(prev_wl),
        "watchlist": prev_wl,
    }
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def get_previous_day_analysis(
    tickers: list[str] | None = None,
    move_threshold_pct: float = 1.0,
) -> str:
    """Analyze previous trading day's intraday price action from flat file minute data.

    Detects significant intraday moves, session structure (strong/weak/inside close),
    and correlates timing for news analysis. Defaults to key market-moving stocks:
    NVDA, SPY, QQQ, AAPL, TSLA, AMD, META, AMZN, MSFT, GOOGL.

    Args:
        tickers: List of tickers to analyze. Defaults to major market movers.
        move_threshold_pct: Minimum % move in a 5-min window to flag. Default 1.0%.

    Returns:
        JSON with per-ticker OHLC, session type, and significant intraday moves with timestamps.
    """
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, flatfiles.get_previous_day_summary, tickers, None, move_threshold_pct
    )

    # Fetch news for each analyzed ticker to correlate with moves
    for ticker in result.get("summaries", {}):
        try:
            news = await finviz_client.get_news_for_ticker(ticker)
            result["summaries"][ticker]["recent_news"] = [
                n.get("headline", "") for n in news[:5]
            ]
        except Exception:
            result["summaries"][ticker]["recent_news"] = []

    return json.dumps(result, indent=2, default=str)


@mcp.tool()
async def get_calendar_events() -> str:
    """Get today's market-moving calendar events: economic releases, earnings, and dividends.

    Returns:
    - Economic event sensitivity map (NFP, CPI, FOMC, etc.) with affected tickers
    - Earnings reporting today (before and after market) from Finviz
    - Earnings reporting this week
    - Upcoming ex-dividend dates for watchlist stocks

    Call this as part of the morning brief to flag binary event risk and
    adjust trade plans accordingly.
    """
    # Get all calendar data in parallel
    econ_events, earnings_today, earnings_week = await asyncio.gather(
        calendar_events.get_economic_calendar(),
        calendar_events.get_earnings_today(),
        calendar_events.get_earnings_this_week(),
    )

    # Get watchlist tickers for dividend check
    watchlist = load_watchlist()
    wl_tickers = [item.get("ticker", "") for item in watchlist[:50]]

    # Dividends check (sync, run in executor)
    loop = asyncio.get_event_loop()
    dividends = await loop.run_in_executor(
        None, calendar_events.get_upcoming_dividends, wl_tickers
    ) if wl_tickers else []

    # Build the earnings tickers set for quick lookup
    earnings_today_tickers = {
        e["ticker"] for e in earnings_today.get("all_today", [])
    }

    # Flag which watchlist stocks have earnings today
    earnings_on_watchlist = []
    for item in watchlist:
        ticker = item.get("ticker", "")
        if ticker in earnings_today_tickers:
            timing = "before_market"
            for e in earnings_today.get("after_market", []):
                if e["ticker"] == ticker:
                    timing = "after_market"
                    break
            earnings_on_watchlist.append({
                "ticker": ticker,
                "timing": timing,
                "warning": "EARNINGS TODAY: binary event risk",
            })

    result = {
        "date": date.today().isoformat(),
        "economic_event_sensitivity": econ_events,
        "earnings_today": {
            "before_market_count": len(earnings_today.get("before_market", [])),
            "after_market_count": len(earnings_today.get("after_market", [])),
            "before_market": earnings_today.get("before_market", [])[:30],
            "after_market": earnings_today.get("after_market", [])[:30],
        },
        "earnings_this_week_count": len(earnings_week),
        "earnings_on_watchlist": earnings_on_watchlist,
        "upcoming_dividends": dividends,
    }

    return json.dumps(result, indent=2, default=str)


@mcp.prompt()
def morning_trading_brief() -> str:
    """Generate a complete morning trading brief with big picture analysis and if/then trade plans.

    Call get_trading_plan first, then use this prompt to structure your analysis.
    """
    return """You are an experienced intraday equities trader preparing your morning brief.

Before generating this brief, call these tools in order:
1. get_previous_day_analysis: analyze yesterday's intraday moves on key stocks
2. get_trading_plan: get today's market overview, watchlist, pivots, and news
3. get_calendar_events: get economic releases, earnings, and dividends for today

Using ALL of this data, produce the following structured analysis.
Keep it tight and scannable. This is a working document, not a research report.

---

## 1. Today's Setup (Lead with What Matters)

### Bias & Scheduled Events
State these FIRST. Everything else is context.

- **Intraday bias**: Long-biased / short-biased / neutral. One sentence justifying with data.
- **Key event**: If a high-impact release is scheduled (NFP, CPI, FOMC, etc.), state the time
  and your recommendation (trade before or wait). Bold the event name.
  - Which watchlist names are most sensitive? (Reference the event sensitivity data.)
  - If no major event: say "No scheduled catalysts. Trade the tape."

### Market Regime (3-4 bullets, no more)
- **SPY/QQQ**: Trend direction, key level, yesterday's session type (strong/weak/inside close).
- **Volatility**: VIXY level and what it means for sizing and stops.
- **Risk tone**: Risk-on or risk-off? One sentence of evidence.
- **Dominant theme**: The single macro narrative driving today's tape.

### Yesterday in 30 Seconds
For SPY, QQQ, and the 2-3 most significant movers from the previous day analysis:
- What moved, when, and why (correlate timestamps with headlines).
- Session structure: who won, buyers or sellers?
- Has overnight news changed the narrative?

Do NOT repeat information that's already in the ticker detail cards. Keep this to broad market
context only.

---

## 2. If/Then Trade Plans (Top 10 Only)

Use the **Ticker Detail Cards** from the trading plan data. The key levels, prev close,
ATR, and top catalyst are already there. Do NOT restate them. Instead, build on them:

### [TICKER] - [Long / Short / Both] Bias
**Setup**: One sentence. Why is this name in play and what's the thesis?

**Long trigger**: Price reclaims [specific R1/PP level] with volume > [threshold].
Target [R2/R3]. Stop below [S1/entry candle low].

**Short trigger** (if applicable): Price rejects [R3/R1] and breaks [PP/S1].
Target [S2/S3]. Stop above [rejection level].

**Kill switch**: One line stating what invalidates both directions entirely.

**Flags** (only if applicable, skip if none):
- EARNINGS TODAY (BMO/AMC): binary risk
- EX-DIVIDEND approaching: distorted price action
- EVENT SENSITIVE (NFP/CPI/etc.): wait for release before entry
- PREV DAY CARRYOVER: trapped longs, short bias
- ATR from prev close†: monitor early range for confirmation

Keep each plan to 6-8 lines max. If you can't make a clean case, skip the ticker.

---

## 3. Stocks to Avoid

Only list stocks that are ON the watchlist but should NOT be traded today.
Do NOT list a stock here if you gave it an if/then plan above. That's contradictory.

Reasons to flag (one line each):
- Illiquid ADR (wide spreads, low US-session volume). Exclude heavily-traded ADRs like
  BABA, TSM, NVO which are fine.
- ETF with no edge (broad index, leveraged decay)
- ATR too low relative to price (commissions eat the move)
- Binary event with unclear direction (FDA, earnings AMC with no lean)
- Ex-dividend distortion
- No catalyst + no clear technical setup (volume screen only, skip)

---

## Formatting Rules
- Use $ and specific prices from Camarilla levels. Never say "near support." Say "$157.01 (PP)".
- Previous close is your overnight reference point. Note where price is relative to it.
- ATR† means the value is from the previous day's close. Flag if relying on it for stop sizing.
- Score is a relative ranking (volume-weighted). Higher = more liquid + more catalysts.
  Don't explain the formula, just use rank order.
- Never use em dashes. Use colons, commas, periods, or parentheses instead.
- Max 2 pages when printed. If it's longer, you're being too verbose.
"""


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
