#!/usr/bin/env python3
"""SPY Gamma Exposure (GEX) snapshot for the morning gameplan.

Pulls the options chain (open interest + IV) from CBOE's public delayed-quotes
CDN (free; no API key) and computes gamma via Black-Scholes-Merton on CBOE's IV.
yfinance was retired 2026-08-11 — its openInterest returned 0 across all expiries;
Massive/Polygon options are a plan tier not entitled here. CBOE carries real OI.
Aggregates per-strike GEX, identifies the zero-gamma flip level, ranks
top strikes by magnitude, and prints a regime label.

Why this exists:
  Dealer net gamma position drives intraday tape character.
  - Positive GEX regime: dealers buy dips + sell rips → mean-reversion, chop, pin
  - Negative GEX regime: dealers sell dips + buy rips → trends extend, breakouts work
  - Zero-gamma flip: the price where MM positioning crosses sign → magnet/repellent

Usage:
  python spy_gex_compute.py [--ticker SPY] [--max-dte 30] [--rate 0.0525]

Output:
  Markdown block suitable for paste into MorningGamePlan macro context section.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import urllib.request
from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy.stats import norm

# CBOE publishes index roots under an underscore prefix (SPX -> _SPX, etc.)
CBOE_ROOT = {"SPX": "_SPX", "NDX": "_NDX", "RUT": "_RUT", "VIX": "_VIX"}
CBOE_URL = "https://cdn.cboe.com/api/global/delayed_quotes/options/{sym}.json"


def bsm_gamma(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Black-Scholes-Merton gamma. T in years, sigma annualized."""
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return 0.0
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    return float(norm.pdf(d1) / (S * sigma * np.sqrt(T)))


@dataclass
class StrikeGEX:
    strike: float
    call_gex: float
    put_gex: float
    net_gex: float

    @property
    def total_magnitude(self) -> float:
        return abs(self.call_gex) + abs(self.put_gex)


def _fetch_cboe(ticker: str) -> dict:
    """CBOE delayed-quotes JSON: {current_price, options:[{option, open_interest, iv, gamma, ...}]}."""
    sym = CBOE_ROOT.get(ticker.upper(), ticker.upper())
    req = urllib.request.Request(CBOE_URL.format(sym=sym), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)["data"]


def _parse_occ(sym: str):
    """Right-anchored OCC parse (root length varies): <root><YYMMDD><C|P><strike*1000, 8 digits>."""
    strike = int(sym[-8:]) / 1000.0
    cp = sym[-9].upper()
    exp = dt.date(2000 + int(sym[-15:-13]), int(sym[-13:-11]), int(sym[-11:-9]))
    return exp, cp, strike


def compute_gex(ticker: str, max_dte: int, rate: float) -> dict:
    data = _fetch_cboe(ticker)
    spot = float(data["current_price"])

    today = dt.date.today()
    horizon = today + dt.timedelta(days=max_dte)

    # Aggregate per strike across all valid expiries (BSM gamma on CBOE's IV — same math as before)
    strikes: dict[float, StrikeGEX] = {}
    contracts_scanned = 0
    expiries_seen: set[dt.date] = set()

    for o in data.get("options", []):
        sym = o.get("option", "")
        if len(sym) < 15:
            continue
        try:
            exp, cp, K = _parse_occ(sym)
        except (ValueError, IndexError):
            continue
        if exp < today or exp > horizon:  # skip expired + beyond DTE horizon
            continue
        oi_raw = o.get("open_interest", 0) or 0
        iv_raw = o.get("iv", 0) or 0
        try:
            oi = int(float(oi_raw))
            iv = float(iv_raw)
        except (TypeError, ValueError):
            continue
        if K <= 0 or iv <= 0 or oi <= 0:
            continue
        T = max((exp - today).days, 0) / 365.0
        g = bsm_gamma(spot, K, T, rate, iv)
        # gamma × OI × 100 (shares per contract) × spot² → $ per 1% move
        # Then normalize: divide by 100 to express as $ per 1pt move ≈ standard convention
        gex_contract = g * oi * 100 * spot * spot / 100.0
        if K not in strikes:
            strikes[K] = StrikeGEX(strike=K, call_gex=0.0, put_gex=0.0, net_gex=0.0)
        if cp == "C":
            # Public convention: report calls as POSITIVE (dealer assumed short, customer long)
            strikes[K].call_gex += gex_contract
        else:
            # Customers typically long puts, dealers short → dealer gamma negative on puts
            strikes[K].put_gex += gex_contract
        contracts_scanned += 1
        expiries_seen.add(exp)

    if not strikes:
        raise SystemExit(f"No usable option data for {ticker} (OI/IV empty) — check CBOE feed")

    # Net dealer GEX = calls (assumed dealer short) - puts (assumed dealer short)
    # Standard SpotGamma-style convention: net = call_gex - put_gex
    for s in strikes.values():
        s.net_gex = s.call_gex - s.put_gex

    # Sort by strike for zero-gamma flip walk
    sorted_strikes = sorted(strikes.values(), key=lambda s: s.strike)

    # Total net GEX
    total_net_gex = sum(s.net_gex for s in sorted_strikes)

    # Zero-gamma flip: walk strikes near spot, find where cumulative net flips sign
    # Use a window around spot ±15% to keep noise out
    flip = None
    near_strikes = [s for s in sorted_strikes if 0.85 * spot <= s.strike <= 1.15 * spot]
    if near_strikes:
        cumulative = 0.0
        for s in near_strikes:
            prev = cumulative
            cumulative += s.net_gex
            if prev != 0 and ((prev < 0 < cumulative) or (prev > 0 > cumulative)):
                flip = s.strike
                break

    # Top 5 strikes by magnitude
    top5 = sorted(sorted_strikes, key=lambda s: s.total_magnitude, reverse=True)[:5]

    # Regime label
    if total_net_gex > 100_000_000:
        regime = "POSITIVE (strong)"
        implication = "mean-reversion, chop, strike-pinning; fade extremes"
    elif total_net_gex > 0:
        regime = "POSITIVE (moderate)"
        implication = "mild dampening; ranges hold; trends weaker than they look"
    elif total_net_gex > -100_000_000:
        regime = "NEGATIVE (moderate)"
        implication = "mild amplification; trends extend; breakouts more likely to follow through"
    else:
        regime = "NEGATIVE (strong)"
        implication = "amplified moves; momentum extends; chase breakouts, fade fades only at multi-TF confirm"

    return {
        "ticker": ticker,
        "spot": spot,
        "expiries_scanned": len(expiries_seen),
        "contracts_scanned": contracts_scanned,
        "max_dte": max_dte,
        "total_net_gex": total_net_gex,
        "zero_gamma_flip": flip,
        "top5_strikes": top5,
        "regime": regime,
        "implication": implication,
    }


def format_markdown(result: dict) -> str:
    flip_str = f"${result['zero_gamma_flip']:.2f}" if result["zero_gamma_flip"] else "no flip in ±15% band (consistent regime)"
    distance = ""
    if result["zero_gamma_flip"]:
        d = result["zero_gamma_flip"] - result["spot"]
        d_pct = (d / result["spot"]) * 100
        distance = f" ({d:+.2f} from spot = {d_pct:+.2f}%)"

    lines = []
    lines.append(f"### 🌐 GEX Snapshot — {result['ticker']} (max {result['max_dte']} DTE)")
    lines.append("")
    lines.append(f"- **Spot:** ${result['spot']:.2f}")
    lines.append(f"- **Net dealer GEX:** ${result['total_net_gex']/1e6:+,.1f}M  →  **{result['regime']}**")
    lines.append(f"- **Zero-gamma flip:** {flip_str}{distance}")
    lines.append(f"- **Tape-read implication:** {result['implication']}")
    lines.append(f"- **Coverage:** {result['contracts_scanned']:,} contracts across {result['expiries_scanned']} expiries")
    lines.append("")
    lines.append("**Top 5 magnet strikes (by gamma magnitude):**")
    lines.append("")
    lines.append("| Strike | Call GEX ($M) | Put GEX ($M) | Net ($M) |")
    lines.append("|--------|---------------|--------------|----------|")
    for s in result["top5_strikes"]:
        lines.append(f"| ${s.strike:.2f} | {s.call_gex/1e6:+.1f} | {s.put_gex/1e6:+.1f} | {s.net_gex/1e6:+.1f} |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker", default="SPY")
    ap.add_argument("--max-dte", type=int, default=30, help="Include expiries within N days (default 30)")
    ap.add_argument("--rate", type=float, default=0.0525, help="Risk-free rate (default 0.0525)")
    ap.add_argument("--json", action="store_true", help="Emit raw JSON instead of markdown")
    args = ap.parse_args()

    result = compute_gex(args.ticker, args.max_dte, args.rate)

    if args.json:
        import json
        # Convert StrikeGEX dataclasses to dicts
        out = {k: v for k, v in result.items() if k != "top5_strikes"}
        out["top5_strikes"] = [
            {"strike": s.strike, "call_gex": s.call_gex, "put_gex": s.put_gex, "net_gex": s.net_gex}
            for s in result["top5_strikes"]
        ]
        print(json.dumps(out, indent=2, default=str))
    else:
        print(format_markdown(result))


if __name__ == "__main__":
    main()
