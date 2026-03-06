import json
from datetime import date, timedelta
from pathlib import Path

from .config import DATA_DIR


def _watchlist_path(d: date) -> Path:
    return DATA_DIR / f"watchlist_{d.isoformat()}.json"


def save_watchlist(watchlist: list[dict], d: date | None = None) -> Path:
    d = d or date.today()
    path = _watchlist_path(d)
    path.write_text(json.dumps(watchlist, indent=2, default=str))
    return path


def load_watchlist(d: date | None = None) -> list[dict]:
    d = d or date.today()
    path = _watchlist_path(d)
    if path.exists():
        return json.loads(path.read_text())
    return []


def load_previous_watchlist() -> tuple[date | None, list[dict]]:
    today = date.today()
    for i in range(1, 5):
        d = today - timedelta(days=i)
        wl = load_watchlist(d)
        if wl:
            return d, wl
    return None, []
