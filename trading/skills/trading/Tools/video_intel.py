#!/usr/bin/env python3
"""Pull the evening video layer for a date — the news source automated feeds miss.

Reads channel IDs straight out of the trading skill's AnalystSources.md, so
registering a new channel there is the only step needed to add it here.

Usage:
    video_intel.py                     # yesterday's videos, all channels
    video_intel.py --date 2026-07-27
    video_intel.py --channel StockedUp
    video_intel.py --list              # show registered channels
    video_intel.py --urls-only         # just print video URLs
    video_intel.py --all               # skip title filtering
    video_intel.py VIDEO_ID [...]      # fetch specific videos directly

Channels that post many videos a day (TraderTV Live) declare a
'**Filter keywords:**' line in AnalystSources.md listing backticked title
fragments. Only matching videos are transcribed; the rest are reported as
skipped, never dropped silently. Channels without that line are unfiltered.

Transcripts are cached under $VIDEO_INTEL_DIR (default
~/.claude/LifeOS/USER/TRADING/Intelligence/transcripts/) so the same video is
never fetched twice.

Why this exists: automated news APIs routinely return zero items for small caps
and can go silent market-wide for hours, including on days when a genuine
sector-moving catalyst is circulating. Evening recap videos carry those stories,
and they also carry pre-specified levels worth more than the narrative. Treat a
quiet newsfeed as absence of coverage, never as absence of news.

Requires `fabric` on PATH for transcript extraction.
"""

import argparse
import html
import os
import re
import subprocess
import sys
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

# Resolution order, first hit wins: explicit override, the copy shipped beside
# this file inside the plugin, then a locally-installed trading skill. Keeping
# all three means the tool works whether it is run from a plugin checkout or
# from a personal ~/.claude skill directory.
SOURCE_CANDIDATES = [
    Path(p) for p in [os.environ.get("ANALYST_SOURCES", "")] if p
] + [
    Path(__file__).resolve().parent.parent / "Reference" / "AnalystSources.md",
    Path.home() / ".claude" / "skills" / "Trading" / "AnalystSources.md",
]

OUTDIR = Path(os.environ.get(
    "VIDEO_INTEL_DIR",
    Path.home() / ".claude" / "LifeOS" / "USER" / "TRADING"
    / "Intelligence" / "transcripts"))
RSS = "https://www.youtube.com/feeds/videos.xml?channel_id={}"


def registered_channels() -> dict[str, dict]:
    """Parse '### Name' blocks out of AnalystSources into {name: {id, keywords}}.

    A block becomes a channel only if it carries a '**Channel ID:**' line, so the
    '### [SourceName]' format template is skipped. '**Filter keywords:**' is
    optional and may sit either side of the Channel ID line. Only backtick-quoted
    fragments count as keywords — Blue Cloud's line mixes one backticked phrase
    with prose ("ticker + date in title"), and treating that prose as a keyword
    would silently exclude the entire channel.
    """
    sources = next((p for p in SOURCE_CANDIDATES if p.exists()), None)
    if sources is None:
        return {}
    blocks, name = {}, None
    for line in sources.read_text().splitlines():
        m = re.match(r"^###\s+(.+?)\s*$", line)
        if m:
            name = m.group(1).strip()
            blocks.setdefault(name, {"id": None, "keywords": []})
            continue
        if not name:
            continue
        m = re.search(r"\*\*Channel ID:\*\*\s*`?(UC[A-Za-z0-9_-]{22})`?", line)
        if m:
            blocks[name]["id"] = m.group(1)
        if "**Filter keywords:**" in line:
            blocks[name]["keywords"] = [k.lower()
                                        for k in re.findall(r"`([^`]+)`", line)]
    return {n: b for n, b in blocks.items() if b["id"]}


def matches_filter(title: str, keywords: list[str]) -> bool:
    """A channel with no declared keywords is unfiltered — everything passes."""
    return not keywords or any(k in title.lower() for k in keywords)


VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{5,32}$")


def safe_id(video_id: str) -> bool:
    """Video IDs reach filename construction, so keep them to the YouTube charset."""
    return bool(VIDEO_ID.match(video_id))


def feed(channel_id: str) -> list[dict]:
    req = urllib.request.Request(RSS.format(channel_id),
                                 headers={"User-Agent": "Mozilla/5.0"})
    xml = urllib.request.urlopen(req, timeout=30).read().decode(errors="replace")
    vids = []
    for e in re.findall(r"<entry>(.*?)</entry>", xml, re.S):
        def grab(tag):
            m = re.search(rf"<{tag}>(.*?)</{tag}>", e, re.S)
            return m.group(1).strip() if m else ""
        if not safe_id(grab("yt:videoId")):
            continue
        # Unescape: RSS carries &amp;/&quot; literally, which both uglifies the
        # printed title and silently breaks keyword matching against it.
        vids.append({"id": grab("yt:videoId"),
                     "title": html.unescape(grab("title")),
                     "published": grab("published")})
    return vids


def fetch_and_report(video_id: str, label: str, path: Path) -> bool:
    """Transcribe one video to `path` and print the standard three-line block."""
    ok, note = transcript(video_id, path)
    print(f"{'✓' if ok else '✗'} {label}")
    print(f"    https://www.youtube.com/watch?v={video_id}")
    print(f"    {path if ok else note}")
    return ok


def transcript(video_id: str, out_path: Path) -> tuple[bool, str]:
    if out_path.exists() and out_path.stat().st_size > 500:
        return True, "cached"
    try:
        r = subprocess.run(
            ["fabric", "-y", f"https://www.youtube.com/watch?v={video_id}",
             "--transcript"],
            capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except FileNotFoundError:
        return False, "fabric not installed"
    if r.returncode != 0 or len(r.stdout) < 500:
        return False, f"empty (rc={r.returncode})"
    out_path.write_text(r.stdout)
    return True, f"{len(r.stdout):,} chars"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video_ids", nargs="*",
                    help="fetch these video IDs directly, skipping RSS discovery")
    ap.add_argument("--date", help="YYYY-MM-DD (default: most recent weekday before today)")
    ap.add_argument("--channel", help="limit to one registered channel (substring match)")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--urls-only", action="store_true")
    ap.add_argument("--all", action="store_true",
                    help="transcribe every video in the window, ignoring title filters")
    args = ap.parse_args()

    chans = registered_channels()
    if args.list:
        if not chans:
            print("No channels with a **Channel ID:** line in AnalystSources.md")
            return 1
        for n, b in chans.items():
            kw = (f"{len(b['keywords'])} filter keyword(s)"
                  if b["keywords"] else "unfiltered")
            print(f"  {n:<24} {b['id']}  {kw}")
        return 0

    OUTDIR.mkdir(parents=True, exist_ok=True)

    # Direct fetch bypasses RSS, the date window and the title filters entirely —
    # the operator naming a video ID has already decided it is the one they want.
    if args.video_ids:
        stamp = args.date or date.today().isoformat()
        for vid in args.video_ids:
            if not safe_id(vid):
                print(f"✗ {vid}: not a valid YouTube video ID", file=sys.stderr)
                continue
            if args.urls_only:
                print(f"https://www.youtube.com/watch?v={vid}")
                continue
            fetch_and_report(vid, vid, OUTDIR / f"{stamp}_direct_{vid}.txt")
        return 0

    if not chans:
        print("No channels registered in AnalystSources.md", file=sys.stderr)
        return 1
    if args.channel:
        chans = {n: b for n, b in chans.items()
                 if args.channel.lower() in n.lower()}
        if not chans:
            print(f"No registered channel matching {args.channel!r}", file=sys.stderr)
            return 1

    if args.date:
        target = args.date
    else:
        d = date.today() - timedelta(days=1)
        while d.weekday() > 4:
            d -= timedelta(days=1)
        target = d.isoformat()

    found_any = False
    for name, meta in chans.items():
        try:
            vids = feed(meta["id"])
        except Exception as exc:
            print(f"✗ {name}: feed failed ({type(exc).__name__})", file=sys.stderr)
            continue
        # Evening posters record after the close ET, so a "07/27" recap can carry a
        # UTC published stamp of 07-28. Accept the next calendar day up to 10:00 UTC
        # (05:00 ET) — anything later that day is genuinely the NEXT session's video.
        nxt = (datetime.strptime(target, "%Y-%m-%d") + timedelta(days=1)).date().isoformat()

        def in_window(v):
            p = v["published"]
            if p[:10] == target:
                return True
            return p[:10] == nxt and p[11:13] < "10"

        in_win = [v for v in vids if in_window(v)]
        hits = in_win
        if in_win and meta["keywords"] and not args.all:
            hits = []
            for v in in_win:
                if matches_filter(v["title"], meta["keywords"]):
                    hits.append(v)
                else:
                    print(f"    {name}: skipped (title filter) {v['title'][:56]}",
                          file=sys.stderr)
        if not hits:
            if in_win:
                # Distinguish "filtered everything out" from "nothing published" —
                # conflating them is how a missed catalyst reads as a quiet day.
                print(f"— {name}: {len(in_win)} video(s) for {target}, none matched "
                      f"the title filter (re-run with --all to take them anyway)")
            else:
                latest = vids[0]["published"][:10] if vids else "none"
                print(f"— {name}: nothing published for the {target} session "
                      f"(latest {latest})")
            continue
        found_any = True
        for v in hits:
            if args.urls_only:
                print(f"https://www.youtube.com/watch?v={v['id']}")
                continue
            fetch_and_report(
                v["id"], f"{name}: {v['title'][:64]}",
                OUTDIR / f"{target}_{name.replace(' ', '')}_{v['id']}.txt")
    if not found_any:
        print(f"\nNo videos found for {target}. Channels may not have posted yet, "
              "or the date is a market holiday.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
