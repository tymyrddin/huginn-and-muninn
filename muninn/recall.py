#!/usr/bin/env python3
"""Muninn: the memory raven.

The history of who announced a prefix, and when, from RIPE's routing archive.
Uses RIPEstat's public API, so nothing to install or run. A change of origin in
the timeline is where a past hijack, or a legitimate handover, shows itself.

    python muninn/recall.py 203.0.113.0/24
    python muninn/recall.py 203.0.113.0/24 --max-rows 100
"""
import argparse
import json
import urllib.parse
import urllib.request

API = "https://stat.ripe.net/data/routing-history/data.json"


def main():
    ap = argparse.ArgumentParser(description="History of who announced a prefix.")
    ap.add_argument("prefix", help="prefix, e.g. 203.0.113.0/24")
    ap.add_argument("--max-rows", type=int, default=50,
                    help="cap the number of timeline rows printed (default 50)")
    args = ap.parse_args()

    q = urllib.parse.urlencode({"resource": args.prefix})
    with urllib.request.urlopen(f"{API}?{q}", timeout=30) as r:
        data = json.load(r)["data"]

    by_origin = data.get("by_origin", [])
    if not by_origin:
        print(f"# no routing history for {args.prefix}")
        return

    rows = []
    for entry in by_origin:
        origin = entry.get("origin")
        for pfx in entry.get("prefixes", []):
            for tl in pfx.get("timelines", []):
                rows.append((tl.get("starttime"), tl.get("endtime"), origin, pfx.get("prefix")))
    rows.sort(key=lambda r: str(r[0]))

    origins = sorted({e.get("origin") for e in by_origin}, key=str)
    print(f"{args.prefix}: {len(origins)} origin(s) in the record, {len(rows)} timeline rows")
    if len(origins) > 1:
        print(f"# {len(origins)} distinct origins over time {origins}; an origin change is the thing to look at")
    for start, end, origin, pfx in rows[:args.max_rows]:
        print(f"  {start} -> {end}  AS{origin}  {pfx}")
    if len(rows) > args.max_rows:
        print(f"  ... {len(rows) - args.max_rows} more (raise --max-rows)")


if __name__ == "__main__":
    main()
