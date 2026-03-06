import logging

import httpx

from .config import FINVIZ_API_KEY

# Suppress httpx logging to avoid leaking API keys in URLs
logging.getLogger("httpx").setLevel(logging.WARNING)

BASE_URL = "https://elite.finviz.com/export.ashx"
QUOTE_URL = "https://elite.finviz.com/quote.ashx"
NEWS_URL = "https://finviz.com/api/news"


def _headers() -> dict:
    return {
        "User-Agent": "equities-watchlist/0.1",
    }


def _auth_params() -> dict:
    return {"auth": FINVIZ_API_KEY} if FINVIZ_API_KEY else {}


async def get_screener_results(filters: str | None = None) -> list[dict]:
    """Run a Finviz screener and return results.

    Args:
        filters: Finviz filter string, e.g. "sh_relvol_o2,ta_averagetruerange_o1"
                 See https://finviz.com/help/screener.ashx for filter codes.
    """
    params = {
        "v": "152",  # custom view with key columns
        "f": filters or "sh_relvol_o2",
        "ft": "4",   # all filters
        "o": "-relativevolume",  # sort by RVOL descending
        **_auth_params(),
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(BASE_URL, params=params, headers=_headers())
        resp.raise_for_status()

    import csv
    import io

    lines = resp.text.strip()
    if not lines:
        return []

    reader = csv.DictReader(io.StringIO(lines))
    return [dict(row) for row in reader]


async def get_news_for_ticker(ticker: str) -> list[dict]:
    """Get recent news headlines for a ticker from Finviz."""
    params = {
        "t": ticker,
        **_auth_params(),
    }
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                f"https://elite.finviz.com/quote.ashx",
                params={"t": ticker, **_auth_params()},
                headers=_headers(),
                follow_redirects=True,
            )
            resp.raise_for_status()
        except Exception:
            return []

    # Parse news from the HTML response - extract news table rows
    import re
    news_items = []
    # Look for news links in the page
    pattern = r'class="tab-link-news"[^>]*>([^<]+)</a>'
    matches = re.findall(pattern, resp.text)
    for headline in matches[:10]:
        news_items.append({"headline": headline.strip()})
    return news_items


async def get_premarket_movers() -> list[dict]:
    """Get pre-market movers using Finviz screener filters."""
    # Finviz filter for stocks with high relative volume in pre-market
    filters = "sh_relvol_o2,sh_avgvol_o200"  # RVOL > 2, Avg Volume > 200K
    return await get_screener_results(filters)


async def screen_watchlist_candidates() -> list[dict]:
    """Screen for watchlist candidates matching our criteria:
    - RVOL > 2
    - Average True Range > 1
    - Average Volume > 200K (ensures liquidity)
    """
    filters = "sh_relvol_o2,ta_averagetruerange_o1,sh_avgvol_o200"
    return await get_screener_results(filters)
