from datetime import date, datetime, timedelta, timezone

from polygon import RESTClient

from .config import POLYGON_API_KEY

# US Eastern Time offset (ET = UTC-5, EDT = UTC-4)
# Polygon timestamps are Unix epoch (UTC). We must convert to ET explicitly.
try:
    from zoneinfo import ZoneInfo
    _ET = ZoneInfo("America/New_York")
except Exception:
    _ET = timezone(timedelta(hours=-5))  # fallback, no DST handling


def _client() -> RESTClient:
    return RESTClient(api_key=POLYGON_API_KEY)


def get_ticker_details(ticker: str) -> dict:
    """Get basic price/volume info for a ticker using daily aggregates."""
    client = _client()
    today = date.today()
    from_date = today - timedelta(days=5)

    try:
        aggs = list(client.get_aggs(
            ticker=ticker,
            multiplier=1,
            timespan="day",
            from_=from_date.isoformat(),
            to=today.isoformat(),
            adjusted=True,
            sort="asc",
        ))
    except Exception:
        return {"ticker": ticker, "price": None, "change_pct": None, "volume": 0}

    if len(aggs) < 2:
        return {"ticker": ticker, "price": None, "change_pct": None, "volume": 0}

    current = aggs[-1]
    prev = aggs[-2]
    change_pct = ((current.close - prev.close) / prev.close * 100) if prev.close else 0

    return {
        "ticker": ticker,
        "price": current.close,
        "change_pct": round(change_pct, 2),
        "volume": current.volume or 0,
        "prev_close": prev.close,
        "prev_volume": prev.volume or 0,
    }


def get_premarket_volume(ticker: str) -> int:
    """Get pre-market volume (4:00 AM - 9:30 AM ET) from aggregate bars."""
    client = _client()
    today = date.today()

    try:
        aggs = list(client.get_aggs(
            ticker=ticker,
            multiplier=1,
            timespan="minute",
            from_=today.isoformat(),
            to=today.isoformat(),
            adjusted=True,
            sort="asc",
            limit=50000,
        ))
    except Exception:
        return 0

    total_volume = 0
    for agg in aggs:
        if agg.timestamp:
            ts_et = datetime.fromtimestamp(agg.timestamp / 1000, tz=timezone.utc).astimezone(_ET)
            hour = ts_et.hour
            # Pre-market: 4:00 AM - 9:29 AM ET
            if 4 <= hour < 9 or (hour == 9 and ts_et.minute < 30):
                total_volume += agg.volume or 0
    return total_volume


def get_relative_volume(ticker: str) -> tuple[float, str]:
    """Calculate RVOL: most recent day's volume / average of prior 20 days.

    During pre-market, Polygon may not yet have a daily bar for today,
    so the most recent bar may be yesterday. Returns (rvol, source) where
    source is 'today' or 'prev_day' so callers know what they're getting.
    """
    client = _client()
    today = date.today()
    from_date = today - timedelta(days=30)

    try:
        aggs = list(client.get_aggs(
            ticker=ticker,
            multiplier=1,
            timespan="day",
            from_=from_date.isoformat(),
            to=today.isoformat(),
            adjusted=True,
            sort="asc",
        ))
    except Exception:
        return 0.0, "unavailable"

    if len(aggs) < 2:
        return 0.0, "unavailable"

    latest = aggs[-1]
    latest_date = datetime.fromtimestamp(latest.timestamp / 1000, tz=timezone.utc).date()
    source = "today" if latest_date == today else "prev_day"

    latest_vol = latest.volume or 0
    hist_vols = [a.volume for a in aggs[:-1] if a.volume]
    if not hist_vols:
        return 0.0, source

    avg_vol = sum(hist_vols) / len(hist_vols)
    if avg_vol == 0:
        return 0.0, source
    return round(latest_vol / avg_vol, 2), source


def get_atr_1min(ticker: str, periods: int = 14) -> float:
    """Calculate ATR on 1-minute bars for the current day."""
    client = _client()
    today = date.today()

    try:
        aggs = list(client.get_aggs(
            ticker=ticker,
            multiplier=1,
            timespan="minute",
            from_=today.isoformat(),
            to=today.isoformat(),
            adjusted=True,
            sort="asc",
            limit=50000,
        ))
    except Exception:
        return 0.0

    if len(aggs) < periods + 1:
        return 0.0

    true_ranges = []
    for i in range(1, len(aggs)):
        high = aggs[i].high or 0
        low = aggs[i].low or 0
        prev_close = aggs[i - 1].close or 0
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        true_ranges.append(tr)

    if len(true_ranges) < periods:
        return 0.0

    # Simple ATR: average of last `periods` true ranges
    atr = sum(true_ranges[-periods:]) / periods
    return round(atr, 4)


def get_prev_day_atr_1min(ticker: str, periods: int = 14) -> float:
    """Calculate ATR on 1-minute bars from the most recent completed trading day via API.

    Fallback for when today's intraday data is insufficient and flat files are unavailable.
    """
    client = _client()
    today = date.today()

    # Try up to 4 days back to find a trading day
    for days_back in range(1, 5):
        d = today - timedelta(days=days_back)
        try:
            aggs = list(client.get_aggs(
                ticker=ticker,
                multiplier=1,
                timespan="minute",
                from_=d.isoformat(),
                to=d.isoformat(),
                adjusted=True,
                sort="asc",
                limit=50000,
            ))
        except Exception:
            continue

        if len(aggs) < periods + 1:
            continue

        true_ranges = []
        for i in range(1, len(aggs)):
            high = aggs[i].high or 0
            low = aggs[i].low or 0
            prev_close = aggs[i - 1].close or 0
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            true_ranges.append(tr)

        if len(true_ranges) >= periods:
            return round(sum(true_ranges[-periods:]) / periods, 4)

    return 0.0


def get_camarilla_pivots(ticker: str) -> dict | None:
    """Calculate Camarilla pivot points from previous day's OHLC.

    Returns R4, R3, R2, R1, PP, S1, S2, S3, S4 levels.
    """
    client = _client()
    today = date.today()
    from_date = today - timedelta(days=5)

    try:
        aggs = list(client.get_aggs(
            ticker=ticker,
            multiplier=1,
            timespan="day",
            from_=from_date.isoformat(),
            to=today.isoformat(),
            adjusted=True,
            sort="asc",
        ))
    except Exception:
        return None

    if len(aggs) < 2:
        return None

    # Use the previous completed day's OHLC
    prev = aggs[-2]
    h = prev.high or 0
    l = prev.low or 0
    c = prev.close or 0

    if h == 0 or l == 0 or c == 0:
        return None

    hl_range = h - l

    return {
        "R4": round(c + hl_range * 1.1 / 2, 2),
        "R3": round(c + hl_range * 1.1 / 4, 2),
        "R2": round(c + hl_range * 1.1 / 6, 2),
        "R1": round(c + hl_range * 1.1 / 12, 2),
        "PP": round((h + l + c) / 3, 2),
        "S1": round(c - hl_range * 1.1 / 12, 2),
        "S2": round(c - hl_range * 1.1 / 6, 2),
        "S3": round(c - hl_range * 1.1 / 4, 2),
        "S4": round(c - hl_range * 1.1 / 2, 2),
        "prev_high": round(h, 2),
        "prev_low": round(l, 2),
        "prev_close": round(c, 2),
    }


def get_market_overview() -> dict:
    """Get current levels for SPY, QQQ, VIX, DIA using daily aggregates."""
    symbols = ["SPY", "QQQ", "VIXY", "DIA"]
    overview = {}
    for sym in symbols:
        details = get_ticker_details(sym)
        overview[sym] = {
            "price": details["price"],
            "change_pct": details["change_pct"],
            "volume": details["volume"],
        }
    return overview
