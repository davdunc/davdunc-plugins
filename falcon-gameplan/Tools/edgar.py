#!/usr/bin/env python3
"""Recent SEC EDGAR filings for a ticker — catalyst + dilution detection for the gameplan.

Free SEC data (no key). Maps ticker->CIK via company_tickers.json, then reads the
company submissions feed. Flags catalyst forms (8-K) and dilution vehicles
(S-3 shelf, 424B prospectus, S-1, ATM-related) — the latter feed the R-S+ATM combo watch.

SEC requires a descriptive User-Agent with contact info or returns 403.
"""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timedelta, timezone

UA = {"User-Agent": "falcon-gameplan/0.1 (davdunc@gmail.com)"}
TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SUBS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"

DILUTION_FORMS = {"S-3", "S-3/A", "S-1", "S-1/A", "424B5", "424B3", "424B4", "424B2", "EFFECT"}
CATALYST_FORMS = {"8-K", "8-K/A", "6-K"}


def ticker_to_cik(ticker: str) -> int:
    import requests
    r = requests.get(TICKERS_URL, headers=UA, timeout=20)
    r.raise_for_status()
    for row in r.json().values():
        if row.get("ticker", "").upper() == ticker:
            return int(row["cik_str"])
    raise RuntimeError(f"ticker {ticker} not found in SEC company_tickers")


def compute(ticker: str, days: int) -> dict:
    import requests
    cik = ticker_to_cik(ticker)
    r = requests.get(SUBS_URL.format(cik=cik), headers=UA, timeout=20)
    r.raise_for_status()
    j = r.json()
    recent = j.get("filings", {}).get("recent", {})
    forms = recent.get("form", []); dates = recent.get("filingDate", [])
    accs = recent.get("accessionNumber", []); docs = recent.get("primaryDocument", [])
    cutoff = (datetime.now(timezone.utc).date() - timedelta(days=days))
    out = []
    for i, form in enumerate(forms):
        try:
            fd = datetime.strptime(dates[i], "%Y-%m-%d").date()
        except (ValueError, IndexError):
            continue
        if fd < cutoff:
            continue
        acc = accs[i].replace("-", "") if i < len(accs) else ""
        doc = docs[i] if i < len(docs) else ""
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{doc}" if acc and doc else ""
        is_dil = form in DILUTION_FORMS
        out.append({
            "form": form, "date": dates[i], "url": url,
            "dilution": is_dil, "catalyst": form in CATALYST_FORMS,
        })
    dil = [f for f in out if f["dilution"]]
    return {
        "ticker": ticker, "cik": cik, "company": j.get("name"),
        "days": days, "count": len(out),
        "dilution_flag": bool(dil),
        "filings": out[:25],
        "note": "S-3/424B/S-1 = dilution vehicles (shelf/ATM/offering); pair with a reverse-split 8-K = R-S+ATM combo → Day-2/Day-3 short watch, NEVER Day-1.",
    }


def to_markdown(d: dict) -> str:
    if not d["count"]:
        return f"**EDGAR — {d['ticker']} ({d['company']})**: no filings in last {d['days']}d."
    lines = []
    for f in d["filings"]:
        tag = " 🚨DILUTION" if f["dilution"] else (" ·catalyst" if f["catalyst"] else "")
        lines.append(f"  - {f['date']}  **{f['form']}**{tag}  {f['url']}")
    hdr = f"**EDGAR — {d['ticker']} ({d['company']}, CIK {d['cik']})** — {d['count']} filing(s) / {d['days']}d"
    if d["dilution_flag"]:
        hdr += "  ⚠️ DILUTION VEHICLE FILED"
    return hdr + "\n" + "\n".join(lines) + f"\n  _{d['note']}_"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Recent SEC EDGAR filings (catalyst + dilution) for a ticker.")
    ap.add_argument("ticker")
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        d = compute(a.ticker.upper(), a.days)
    except Exception as e:
        print(json.dumps({"error": str(e)}) if a.json else f"[UNAVAILABLE: EDGAR {a.ticker.upper()} — {e}]")
        return 1
    print(json.dumps(d, indent=2) if a.json else to_markdown(d))
    return 0


if __name__ == "__main__":
    sys.exit(main())
