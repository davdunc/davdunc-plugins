import csv
import io
from datetime import date, timedelta

import httpx
from polygon import RESTClient

from .config import FINVIZ_API_KEY, POLYGON_API_KEY

# Major economic events and their market-sensitive sectors/tickers
ECONOMIC_EVENT_SENSITIVITY = {
    "Non Farm Payrolls": {
        "description": "Monthly jobs report, most market-moving economic release",
        "sensitive_long": ["TLT", "GLD", "GDX", "XHB", "IWM"],  # on weak print
        "sensitive_short": ["UUP", "JPM", "GS"],  # on weak print (inverse on strong)
        "volatility": "high",
    },
    "CPI": {
        "description": "Consumer Price Index: inflation gauge, drives Fed policy expectations",
        "sensitive_long": ["TLT", "GLD", "XHB", "IWM"],  # on cool print
        "sensitive_short": ["UUP"],  # on cool print
        "volatility": "high",
    },
    "PPI": {
        "description": "Producer Price Index: leading indicator for CPI",
        "sensitive_long": ["TLT", "GLD"],
        "sensitive_short": ["UUP"],
        "volatility": "medium",
    },
    "FOMC": {
        "description": "Federal Reserve rate decision and statement",
        "sensitive_long": ["TLT", "GLD", "QQQ", "IWM", "XHB"],
        "sensitive_short": ["UUP"],
        "volatility": "high",
    },
    "Retail Sales": {
        "description": "Monthly consumer spending data",
        "sensitive_long": ["XLY", "XRT", "WMT", "TGT", "AMZN"],
        "sensitive_short": ["XLP"],
        "volatility": "medium",
    },
    "GDP": {
        "description": "Gross Domestic Product: broad economic growth measure",
        "sensitive_long": ["SPY", "IWM", "XLF"],
        "sensitive_short": ["TLT", "GLD"],
        "volatility": "medium",
    },
    "ISM Manufacturing": {
        "description": "Manufacturing sector health: expansion/contraction signal",
        "sensitive_long": ["XLI", "CAT", "DE"],
        "sensitive_short": [],
        "volatility": "medium",
    },
    "ISM Services": {
        "description": "Services sector health: largest part of US economy",
        "sensitive_long": ["SPY", "XLF"],
        "sensitive_short": [],
        "volatility": "medium",
    },
    "Jobless Claims": {
        "description": "Weekly unemployment claims: labor market health",
        "sensitive_long": ["TLT", "GLD"],
        "sensitive_short": ["UUP"],
        "volatility": "low",
    },
    "PCE": {
        "description": "Personal Consumption Expenditures: Fed's preferred inflation gauge",
        "sensitive_long": ["TLT", "GLD", "XHB"],
        "sensitive_short": ["UUP"],
        "volatility": "high",
    },
}


async def get_economic_calendar() -> list[dict]:
    """Fetch today's and tomorrow's economic events from Polygon."""
    client = RESTClient(api_key=POLYGON_API_KEY)
    today = date.today()
    tomorrow = today + timedelta(days=1)

    events = []

    # Check known event schedule patterns
    # Polygon doesn't have a dedicated economic calendar endpoint,
    # so we match against our known event sensitivity map
    # In production, you'd integrate with a dedicated economic calendar API

    # For now, return the sensitivity map so Claude can cross-reference
    # with news headlines that mention these events
    for event_name, info in ECONOMIC_EVENT_SENSITIVITY.items():
        events.append({
            "event": event_name,
            "description": info["description"],
            "sensitive_tickers_on_dovish": info["sensitive_long"],
            "sensitive_tickers_on_hawkish": info["sensitive_short"],
            "volatility_impact": info["volatility"],
        })

    return events


async def get_earnings_today() -> list[dict]:
    """Get stocks reporting earnings today (before and after market)."""
    results = {"before_market": [], "after_market": [], "all_today": []}

    async with httpx.AsyncClient(timeout=15) as client:
        for period, key in [
            ("earningsdate_todaybefore", "before_market"),
            ("earningsdate_todayafter", "after_market"),
        ]:
            params = {
                "v": "152",
                "f": period,
                "ft": "4",
                "auth": FINVIZ_API_KEY,
            }
            try:
                resp = await client.get(
                    "https://elite.finviz.com/export.ashx",
                    params=params,
                    headers={"User-Agent": "equities-watchlist/0.1"},
                    follow_redirects=True,
                )
                resp.raise_for_status()
                reader = csv.DictReader(io.StringIO(resp.text))
                for row in reader:
                    ticker = row.get("Ticker", "").strip()
                    if ticker:
                        entry = {
                            "ticker": ticker,
                            "company": row.get("Company", ""),
                            "market_cap": row.get("Market Cap", ""),
                            "timing": "before_market" if key == "before_market" else "after_market",
                        }
                        results[key].append(entry)
                        results["all_today"].append(entry)
            except Exception:
                continue

    return results


async def get_earnings_this_week() -> list[dict]:
    """Get all stocks reporting earnings this week."""
    params = {
        "v": "152",
        "f": "earningsdate_thisweek",
        "ft": "4",
        "auth": FINVIZ_API_KEY,
    }

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                "https://elite.finviz.com/export.ashx",
                params=params,
                headers={"User-Agent": "equities-watchlist/0.1"},
                follow_redirects=True,
            )
            resp.raise_for_status()
            reader = csv.DictReader(io.StringIO(resp.text))
            return [
                {
                    "ticker": row.get("Ticker", "").strip(),
                    "company": row.get("Company", ""),
                    "market_cap": row.get("Market Cap", ""),
                }
                for row in reader
                if row.get("Ticker", "").strip()
            ]
        except Exception:
            return []


def get_upcoming_dividends(tickers: list[str]) -> list[dict]:
    """Check for upcoming ex-dividend dates for given tickers."""
    client = RESTClient(api_key=POLYGON_API_KEY)
    today = date.today()
    upcoming_window = today + timedelta(days=5)

    results = []
    for ticker in tickers:
        try:
            divs = list(client.list_dividends(
                ticker=ticker,
                ex_dividend_date_gte=today.isoformat(),
                ex_dividend_date_lte=upcoming_window.isoformat(),
                limit=5,
            ))
            for d in divs:
                results.append({
                    "ticker": d.ticker,
                    "ex_date": str(d.ex_dividend_date),
                    "pay_date": str(d.pay_date),
                    "amount": d.cash_amount,
                    "frequency": str(d.frequency) if d.frequency else None,
                })
        except Exception:
            continue

    return results


def get_recent_filings(ticker: str) -> dict | None:
    """Get the most recent earnings filing date and estimate next one."""
    client = RESTClient(api_key=POLYGON_API_KEY)
    try:
        fins = list(client.vx.list_stock_financials(ticker=ticker, limit=5))
        if not fins:
            return None

        # Find the most recent quarterly filing
        quarterly = [f for f in fins if f.fiscal_period and f.fiscal_period.startswith("Q")]
        if not quarterly:
            return None

        latest = quarterly[0]
        filing_date = latest.filing_date

        # Estimate next earnings based on ~90 day cadence
        if filing_date:
            from datetime import datetime
            fd = datetime.strptime(str(filing_date), "%Y-%m-%d").date()
            est_next = fd + timedelta(days=90)
            days_until = (est_next - date.today()).days

            return {
                "ticker": ticker,
                "last_period": f"{latest.fiscal_period} {latest.fiscal_year}",
                "last_filing_date": str(filing_date),
                "estimated_next_earnings": est_next.isoformat(),
                "days_until_estimated": days_until,
                "earnings_imminent": days_until <= 7,
            }
    except Exception:
        pass

    return None
