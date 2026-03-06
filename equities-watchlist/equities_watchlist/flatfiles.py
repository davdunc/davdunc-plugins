import csv
import gzip
import io
from datetime import date, timedelta
from pathlib import Path

import boto3
from botocore.config import Config

from .config import DATA_DIR, MASSIVE_S3_ACCESS_KEY, MASSIVE_S3_SECRET_KEY

CACHE_DIR = DATA_DIR / "flatfiles"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

BUCKET = "flatfiles"
ENDPOINT = "https://files.massive.com"


def _s3_client():
    session = boto3.Session(
        aws_access_key_id=MASSIVE_S3_ACCESS_KEY,
        aws_secret_access_key=MASSIVE_S3_SECRET_KEY,
    )
    return session.client(
        "s3",
        endpoint_url=ENDPOINT,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )


def _cache_path(data_type: str, d: date) -> Path:
    return CACHE_DIR / f"{data_type}_{d.isoformat()}.csv"


def _s3_key(data_type: str, d: date) -> str:
    """Build S3 object key for a given data type and date."""
    return f"us_stocks_sip/{data_type}/{d.year}/{d.month:02d}/{d.isoformat()}.csv.gz"


def _download_and_cache(data_type: str, d: date) -> Path:
    """Download a flat file from S3, decompress, and cache locally."""
    cache = _cache_path(data_type, d)
    if cache.exists():
        return cache

    s3 = _s3_client()
    key = _s3_key(data_type, d)

    resp = s3.get_object(Bucket=BUCKET, Key=key)
    compressed = resp["Body"].read()

    decompressed = gzip.decompress(compressed).decode("utf-8")
    cache.write_text(decompressed, newline="")

    return cache


def _read_csv(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def get_day_aggs(d: date) -> list[dict]:
    """Get all stock day aggregates for a given date."""
    path = _download_and_cache("day_aggs_v1", d)
    return _read_csv(path)


def get_minute_aggs(d: date) -> list[dict]:
    """Get all stock minute aggregates for a given date."""
    path = _download_and_cache("minute_aggs_v1", d)
    return _read_csv(path)


def get_day_aggs_for_ticker(ticker: str, d: date) -> list[dict]:
    """Filter day aggregates for a specific ticker."""
    return [row for row in get_day_aggs(d) if row.get("ticker") == ticker]


def get_minute_aggs_for_ticker(ticker: str, d: date) -> list[dict]:
    """Filter minute aggregates for a specific ticker."""
    return [row for row in get_minute_aggs(d) if row.get("ticker") == ticker]


def get_previous_trading_day(d: date | None = None) -> date:
    """Find the most recent trading day before the given date."""
    d = d or date.today()
    # Try up to 4 days back (covers weekends + holidays)
    for i in range(1, 5):
        candidate = d - timedelta(days=i)
        cache = _cache_path("day_aggs_v1", candidate)
        if cache.exists():
            return candidate
    # Default to yesterday if no cache found
    return d - timedelta(days=1)


def get_ohlc_for_ticker(ticker: str, d: date) -> dict | None:
    """Get OHLC data for a ticker from flat files.

    Returns dict with open, high, low, close, volume or None.
    """
    rows = get_day_aggs_for_ticker(ticker, d)
    if not rows:
        return None
    row = rows[0]
    return {
        "open": float(row.get("open", 0)),
        "high": float(row.get("high", 0)),
        "low": float(row.get("low", 0)),
        "close": float(row.get("close", 0)),
        "volume": int(float(row.get("volume", 0))),
    }


def analyze_intraday_moves(ticker: str, d: date, move_threshold_pct: float = 1.0) -> list[dict]:
    """Detect significant intraday price moves from minute-level data.

    A 'significant move' is a sustained directional move exceeding move_threshold_pct
    within a rolling window, or a single bar with outsized volume.

    Returns a list of move events with timestamps, direction, magnitude, and volume.
    """
    bars = get_minute_aggs_for_ticker(ticker, d)
    if not bars:
        return []

    # Parse into numeric values
    parsed = []
    for bar in bars:
        try:
            ts = int(bar.get("window_start", 0))
            parsed.append({
                "timestamp_ns": ts,
                "open": float(bar.get("open", 0)),
                "high": float(bar.get("high", 0)),
                "low": float(bar.get("low", 0)),
                "close": float(bar.get("close", 0)),
                "volume": int(float(bar.get("volume", 0))),
                "transactions": int(float(bar.get("transactions", 0))),
            })
        except (ValueError, TypeError):
            continue

    if len(parsed) < 10:
        return []

    # Calculate average volume per bar for comparison
    avg_vol = sum(b["volume"] for b in parsed) / len(parsed)

    moves = []

    # Detect moves using a rolling 5-minute window
    window = 5
    for i in range(window, len(parsed)):
        window_open = parsed[i - window]["open"]
        window_close = parsed[i]["close"]
        if window_open == 0:
            continue

        pct_change = (window_close - window_open) / window_open * 100
        window_vol = sum(parsed[j]["volume"] for j in range(i - window + 1, i + 1))
        window_high = max(parsed[j]["high"] for j in range(i - window + 1, i + 1))
        window_low = min(parsed[j]["low"] for j in range(i - window + 1, i + 1))

        if abs(pct_change) >= move_threshold_pct:
            # Convert nanosecond timestamp to ET
            ts_seconds = parsed[i]["timestamp_ns"] // 1_000_000_000
            from datetime import datetime, timezone
            try:
                from zoneinfo import ZoneInfo
                _et = ZoneInfo("America/New_York")
            except Exception:
                _et = timezone(timedelta(hours=-5))
            dt = datetime.fromtimestamp(ts_seconds, tz=timezone.utc).astimezone(_et)
            time_str = dt.strftime("%H:%M ET")

            # Check if this overlaps with a previous move (dedup)
            if moves and abs(parsed[i]["timestamp_ns"] - moves[-1]["timestamp_ns"]) < 300_000_000_000:
                # Within 5 min of last move, keep the larger one
                if abs(pct_change) > abs(moves[-1]["pct_change"]):
                    moves[-1] = {
                        "timestamp_ns": parsed[i]["timestamp_ns"],
                        "time": time_str,
                        "direction": "UP" if pct_change > 0 else "DOWN",
                        "pct_change": round(pct_change, 2),
                        "price_from": round(window_open, 2),
                        "price_to": round(window_close, 2),
                        "window_high": round(window_high, 2),
                        "window_low": round(window_low, 2),
                        "volume": window_vol,
                        "vol_vs_avg": round(window_vol / (avg_vol * window), 2) if avg_vol > 0 else 0,
                    }
                continue

            moves.append({
                "timestamp_ns": parsed[i]["timestamp_ns"],
                "time": time_str,
                "direction": "UP" if pct_change > 0 else "DOWN",
                "pct_change": round(pct_change, 2),
                "price_from": round(window_open, 2),
                "price_to": round(window_close, 2),
                "window_high": round(window_high, 2),
                "window_low": round(window_low, 2),
                "volume": window_vol,
                "vol_vs_avg": round(window_vol / (avg_vol * window), 2) if avg_vol > 0 else 0,
            })

    return moves


def get_previous_day_summary(
    tickers: list[str] | None = None,
    d: date | None = None,
    move_threshold_pct: float = 1.0,
) -> dict:
    """Analyze previous day's intraday action for key stocks.

    Returns OHLC, significant moves, and session structure for each ticker.
    """
    d = d or get_previous_trading_day()
    if tickers is None:
        tickers = ["NVDA", "SPY", "QQQ", "AAPL", "TSLA", "AMD", "META", "AMZN", "MSFT", "GOOGL"]

    summaries = {}
    for ticker in tickers:
        ohlc = get_ohlc_for_ticker(ticker, d)
        if not ohlc:
            continue

        moves = analyze_intraday_moves(ticker, d, move_threshold_pct)

        # Session structure: where did it open vs close relative to range?
        day_range = ohlc["high"] - ohlc["low"]
        if day_range > 0:
            close_position = (ohlc["close"] - ohlc["low"]) / day_range
        else:
            close_position = 0.5

        if close_position > 0.7:
            session_type = "strong_close"
        elif close_position < 0.3:
            session_type = "weak_close"
        else:
            session_type = "inside_close"

        change_pct = ((ohlc["close"] - ohlc["open"]) / ohlc["open"] * 100) if ohlc["open"] else 0

        summaries[ticker] = {
            "date": d.isoformat(),
            "ohlc": ohlc,
            "change_pct": round(change_pct, 2),
            "session_type": session_type,
            "close_position_in_range": round(close_position, 2),
            "significant_moves": moves,
            "move_count": len(moves),
        }

    return {"date": d.isoformat(), "summaries": summaries}


def get_previous_day_atr_1min(ticker: str, periods: int = 14, d: date | None = None) -> float:
    """Calculate ATR on 1-minute bars from the previous trading day's flat file data.

    Use as a fallback when current-day intraday data is insufficient.
    """
    d = d or get_previous_trading_day()
    bars = get_minute_aggs_for_ticker(ticker, d)
    if len(bars) < periods + 1:
        return 0.0

    parsed = []
    for bar in bars:
        try:
            parsed.append({
                "high": float(bar.get("high", 0)),
                "low": float(bar.get("low", 0)),
                "close": float(bar.get("close", 0)),
            })
        except (ValueError, TypeError):
            continue

    if len(parsed) < periods + 1:
        return 0.0

    true_ranges = []
    for i in range(1, len(parsed)):
        h = parsed[i]["high"]
        l = parsed[i]["low"]
        pc = parsed[i - 1]["close"]
        tr = max(h - l, abs(h - pc), abs(l - pc))
        true_ranges.append(tr)

    if len(true_ranges) < periods:
        return 0.0

    atr = sum(true_ranges[-periods:]) / periods
    return round(atr, 4)


def calculate_camarilla_from_flatfiles(ticker: str, d: date | None = None) -> dict | None:
    """Calculate Camarilla pivots using flat file OHLC data."""
    d = d or get_previous_trading_day()
    ohlc = get_ohlc_for_ticker(ticker, d)
    if not ohlc:
        return None

    h = ohlc["high"]
    l = ohlc["low"]
    c = ohlc["close"]

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
        "source": "flatfiles",
        "date": d.isoformat(),
    }
