#!/usr/bin/env python3
"""SPY (or any ticker) dealer Gamma Exposure (GEX) snapshot for the morning gameplan.

DIY rebuild of ~/falcon/dashboard/spy_gex_compute.py (memory: spy-gex-tool).
Pulls the options chain from yfinance, computes per-contract gamma via Black-Scholes-Merton,
aggregates dealer net GEX (net = calls - puts).

Data reality (2026-06-09): yfinance's openInterest comes back 0 and impliedVolatility
is broken; Alpha Vantage / Polygon options are paywalled. So:
  --source auto (default): use real OI+IV when present, else fall back to a VOLUME-PROXY.
  --source volume: weight by the day's option VOLUME (flow, not standing positioning) and
                   self-solve IV from each option's mid price via BSM inversion.
  --source oi: force real-OI mode (fails loud if the OI feed is empty).
The VOLUME-PROXY is a documented degradation (flow, not dealer positioning) pending a real
options feed (Tradier/Polygon-Options/ORATS) wired in via cross-agent collaboration.
The REGIME LABEL is the load-bearing output, not the absolute dollar figure.
"""
from __future__ import annotations
import argparse, json, math, sys
from datetime import datetime, timezone

CONTRACT_MULTIPLIER = 100
SANE_IV_FLOOR = 0.02


def _f(x) -> float:
    """NaN/None-safe float (pandas NaN is truthy, so `x or 0` is not enough)."""
    try:
        v = float(x)
        return 0.0 if math.isnan(v) else v
    except (TypeError, ValueError):
        return 0.0


def _norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def bsm_gamma(S, K, T, sigma, r) -> float:
    if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
        return 0.0
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    return _norm_pdf(d1) / (S * sigma * math.sqrt(T))


def bsm_price(S, K, T, sigma, r, is_call) -> float:
    if T <= 0 or sigma <= 0:
        return max(0.0, (S - K) if is_call else (K - S))
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if is_call:
        return S * _norm_cdf(d1) - K * math.exp(-r * T) * _norm_cdf(d2)
    return K * math.exp(-r * T) * _norm_cdf(-d2) - S * _norm_cdf(-d1)


def implied_vol(price, S, K, T, r, is_call):
    """Bisection BSM implied vol from a market price. None if not solvable."""
    intrinsic = max(0.0, (S - K) if is_call else (K - S))
    if price is None or price <= 0 or price < intrinsic - 0.01 or T <= 0:
        return None
    lo, hi = 1e-3, 5.0
    if bsm_price(S, K, T, hi, r, is_call) < price:  # price above model max → unsolvable
        return None
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if bsm_price(S, K, T, mid, r, is_call) < price:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _gex_at_spot(rows, spot, r) -> float:
    """rows: (K,T,iv,weight,sign). Net dealer GEX ($ per 1% move) at a hypothetical spot."""
    return sum(sign * bsm_gamma(spot, K, T, iv, r) * w * CONTRACT_MULTIPLIER * spot * spot * 0.01
               for K, T, iv, w, sign in rows)


def compute(ticker: str, max_dte: int, r: float, source: str) -> dict:
    import yfinance as yf
    tk = yf.Ticker(ticker)
    try:
        spot = float(tk.fast_info["lastPrice"])
    except Exception:
        try:
            spot = float(tk.history(period="1d")["Close"].iloc[-1])
        except Exception as e:
            raise RuntimeError(f"could not fetch spot for {ticker}: {e}")
    if not spot or spot <= 0:
        raise RuntimeError(f"invalid spot for {ticker}: {spot}")

    exps = list(getattr(tk, "options", []) or [])
    if not exps:
        raise RuntimeError(f"no option expirations returned for {ticker}")
    today = datetime.now(timezone.utc).date()

    raw = []  # (K,T,sign,oi,vol,mid,iv_yf,is_call)
    used_exps = 0
    for exp in exps:
        try:
            dte = (datetime.strptime(exp, "%Y-%m-%d").date() - today).days
        except ValueError:
            continue
        if dte < 0 or dte > max_dte:
            continue
        T = max(dte, 0.5) / 365.0
        try:
            chain = tk.option_chain(exp)
        except Exception:
            continue
        used_exps += 1
        for df, sign, is_call in ((chain.calls, +1.0, True), (chain.puts, -1.0, False)):
            for _, row in df.iterrows():
                K = _f(row.get("strike"))
                if K <= 0:
                    continue
                oi = _f(row.get("openInterest"))
                vol = _f(row.get("volume"))
                iv_yf = _f(row.get("impliedVolatility"))
                bid = _f(row.get("bid")); ask = _f(row.get("ask"))
                last = _f(row.get("lastPrice"))
                mid = (bid + ask) / 2 if (bid > 0 and ask > 0) else last
                raw.append((K, T, sign, oi, vol, mid, iv_yf, is_call))

    if not raw:
        raise RuntimeError(f"no option rows for {ticker} within {max_dte} DTE")

    # decide effective source
    usable_oi = sum(1 for x in raw if x[3] > 0 and x[6] > SANE_IV_FLOOR)
    total_oi = sum(x[3] for x in raw)
    if source == "auto":
        eff = "oi" if (usable_oi >= 20 and total_oi >= 500) else "volume"
    else:
        eff = source
    if eff == "oi" and (usable_oi < 20 or total_oi < 500):
        raise RuntimeError(
            f"--source oi requested but OI feed unusable (rows={usable_oi}, OI={total_oi:.0f}). "
            "yfinance OI=0/IV broken; need a real options feed (Tradier/Polygon-Options/ORATS)."
        )

    per_strike, rows = {}, []
    for K, T, sign, oi, vol, mid, iv_yf, is_call in raw:
        weight = oi if eff == "oi" else vol
        if weight <= 0:
            continue
        iv = iv_yf if (eff == "oi" and iv_yf > SANE_IV_FLOOR) else implied_vol(mid, spot, K, T, r, is_call)
        if not iv or iv <= 0:
            continue
        g = bsm_gamma(spot, K, T, iv, r)
        gex = sign * g * weight * CONTRACT_MULTIPLIER * spot * spot * 0.01
        per_strike[K] = per_strike.get(K, 0.0) + gex
        rows.append((K, T, iv, weight, sign))

    if len(rows) < 20:
        raise RuntimeError(f"too few usable rows ({len(rows)}) for {ticker} via source={eff}")

    net = sum(per_strike.values())
    gross = sum(abs(v) for v in per_strike.values()) or 1.0
    ratio = abs(net) / gross
    sign_label = "POSITIVE" if net >= 0 else "NEGATIVE"
    strength = "strong" if ratio >= 0.35 else "moderate"
    regime = f"{sign_label} ({strength})"
    if sign_label == "POSITIVE":
        tape = ("Mean-reversion + fade setups preferred; breakouts fail more often; pinning toward magnets."
                if strength == "strong" else "Mild dampening; ranges hold; lower-conviction trend trades.")
    else:
        tape = ("Chase breakouts; momentum extends; fade only at multi-TF confirm."
                if strength == "strong" else "Mild amplification; trends extend; breakouts more reliable.")

    flip, lo, hi, steps = None, spot * 0.85, spot * 1.15, 120
    prev_s, prev_v = lo, _gex_at_spot(rows, lo, r)
    for i in range(1, steps + 1):
        s = lo + (hi - lo) * i / steps
        v = _gex_at_spot(rows, s, r)
        if prev_v == 0 or (prev_v < 0) != (v < 0):
            flip = prev_s if (v - prev_v) == 0 else prev_s + (s - prev_s) * (-prev_v) / (v - prev_v)
            break
        prev_s, prev_v = s, v

    magnets = sorted(per_strike.items(), key=lambda kv: abs(kv[1]), reverse=True)[:5]
    proxy = eff == "volume"
    return {
        "ticker": ticker, "spot": round(spot, 2), "source": eff, "is_proxy": proxy,
        "net_gex_musd": round(net / 1e6, 1), "directionality": round(ratio, 3),
        "regime": regime, "tape_read": tape,
        "zero_gamma_flip": round(flip, 2) if flip else None,
        "flip_vs_spot_pct": round((flip / spot - 1) * 100, 2) if flip else None,
        "magnet_strikes": [{"strike": k, "net_gex_musd": round(v / 1e6, 1)} for k, v in magnets],
        "expiries_used": used_exps, "max_dte": max_dte, "rows_used": len(rows),
        "asof_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": ("VOLUME-PROXY: weighted by option VOLUME (flow, not standing OI) with IV self-solved from price — "
                 "yfinance OI/IV broken. Upgrade to a real OI feed pending. Regime label is the load-bearing output."
                 if proxy else
                 "Real-OI mode; naive net=calls-puts; free 15-min-delayed data."),
    }


def to_markdown(d: dict) -> str:
    src = "⚠️ VOLUME-PROXY" if d["is_proxy"] else "OI"
    flip = (f"${d['zero_gamma_flip']} ({d['flip_vs_spot_pct']:+}% vs spot)"
            + ("  ← within $5, magnet/repellent" if d["zero_gamma_flip"] and abs(d["zero_gamma_flip"] - d["spot"]) <= 5 else "")
            ) if d["zero_gamma_flip"] else "no flip in ±15% band (regime stable)"
    mag = "\n".join(f"  - ${m['strike']:g}  ({m['net_gex_musd']:+} $M)" for m in d["magnet_strikes"])
    return (
        f"**SPY GEX — {d['ticker']} @ ${d['spot']}**  [{src}]  _(asof {d['asof_utc']}, ≤{d['max_dte']} DTE, "
        f"{d['expiries_used']} exp, {d['rows_used']} rows)_\n"
        f"- Net dealer GEX: **{d['net_gex_musd']:+,} $M**  |  regime: **{d['regime']}**  (directionality {d['directionality']})\n"
        f"- Tape read: {d['tape_read']}\n"
        f"- Zero-gamma flip: {flip}\n"
        f"- Top magnet strikes (intraday targets/triggers):\n{mag}\n"
        f"  _{d['note']}_"
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Dealer Gamma Exposure (GEX) snapshot for the gameplan macro block.")
    ap.add_argument("--ticker", default="SPY")
    ap.add_argument("--max-dte", type=int, default=30)
    ap.add_argument("--rate", type=float, default=0.043)
    ap.add_argument("--source", choices=["auto", "oi", "volume"], default="auto",
                    help="auto=OI if available else volume-proxy; oi=force real OI; volume=force volume-proxy")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        d = compute(a.ticker.upper(), a.max_dte, a.rate, a.source)
    except Exception as e:
        print(json.dumps({"error": str(e)}) if a.json else f"[UNAVAILABLE: SPY GEX — {e}]")
        return 1
    print(json.dumps(d, indent=2) if a.json else to_markdown(d))
    return 0


if __name__ == "__main__":
    sys.exit(main())
