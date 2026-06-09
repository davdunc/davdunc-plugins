#!/usr/bin/env python3
"""Camarilla pivot levels for a ticker, from the prior completed daily bar.

Source: Polygon prev-day aggregate (api.polygon.io/v2/aggs/ticker/{T}/prev) — the
Massive/Polygon key is entitled to aggregates. Camarilla S3/S4 + R3/R4 are the
support/resistance the MorningGamePlan watchlist uses; S4/R4 are the breakout
levels, S3/R3 the reversion band.
"""
from __future__ import annotations
import argparse, json, os, sys

POLY = "https://api.polygon.io/v2/aggs/ticker/{t}/prev?adjusted=true&apiKey={k}"


def _key() -> str:
    k = os.environ.get("POLYGON_API_KEY")
    if not k:
        envp = os.path.expanduser("~/.claude/.env")
        if os.path.exists(envp):
            for line in open(envp):
                line = line.split("#", 1)[0].strip()
                if line.startswith("POLYGON_API_KEY="):
                    k = line.split("=", 1)[1].strip()
                    break
    if not k:
        raise RuntimeError("POLYGON_API_KEY not set (env or ~/.claude/.env)")
    return k


def camarilla(h: float, l: float, c: float) -> dict:
    rng = h - l
    return {
        "R4": c + rng * 1.1 / 2, "R3": c + rng * 1.1 / 4,
        "R2": c + rng * 1.1 / 6, "R1": c + rng * 1.1 / 12,
        "PP": (h + l + c) / 3,
        "S1": c - rng * 1.1 / 12, "S2": c - rng * 1.1 / 6,
        "S3": c - rng * 1.1 / 4, "S4": c - rng * 1.1 / 2,
        # breakout extension targets (H5/L5 style)
        "R5": c + (c + rng * 1.1 / 2 - (c - rng * 1.1 / 2)) * 1.168 / 2 if rng else c,
    }


def compute(ticker: str) -> dict:
    import requests
    r = requests.get(POLY.format(t=ticker, k=_key()), timeout=20)
    j = r.json()
    if j.get("status") not in ("OK", "DELAYED") or not j.get("results"):
        raise RuntimeError(f"Polygon prev-bar unavailable for {ticker}: {j.get('status')} {j.get('message') or j.get('error') or ''}".strip())
    b = j["results"][0]
    h, l, c, o, v = b["h"], b["l"], b["c"], b["o"], b["v"]
    piv = {k: round(val, 2) for k, val in camarilla(h, l, c).items()}
    return {
        "ticker": ticker, "prior_bar": {"o": o, "h": h, "l": l, "c": c, "v": v},
        "range": round(h - l, 2), "pivots": piv,
        "note": "Camarilla from prior daily bar (Polygon). S4/R4 = breakout, S3/R3 = reversion band.",
    }


def to_markdown(d: dict) -> str:
    p = d["pivots"]
    return (
        f"**Camarilla — {d['ticker']}** _(prior bar O {d['prior_bar']['o']} H {d['prior_bar']['h']} "
        f"L {d['prior_bar']['l']} C {d['prior_bar']['c']}, range {d['range']})_\n"
        f"- Resistance: R3 **{p['R3']}** · R4 **{p['R4']}** (breakout) · R5 {p['R5']}\n"
        f"- Pivot: {p['PP']}\n"
        f"- Support: S3 **{p['S3']}** · S4 **{p['S4']}** (breakdown)\n"
        f"  _{d['note']}_"
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Camarilla pivots from the prior daily bar.")
    ap.add_argument("ticker")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        d = compute(a.ticker.upper())
    except Exception as e:
        print(json.dumps({"error": str(e)}) if a.json else f"[UNAVAILABLE: Camarilla {a.ticker.upper()} — {e}]")
        return 1
    print(json.dumps(d, indent=2) if a.json else to_markdown(d))
    return 0


if __name__ == "__main__":
    sys.exit(main())
