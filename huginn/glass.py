#!/usr/bin/env python3
"""Huginn: a snapshot looking glass.

Who is announcing a prefix right now, as seen from RIPE's collectors. Uses
RIPEstat's public API, so it needs nothing installed and nothing running.

    python huginn/glass.py 203.0.113.0/24            # summary, grouped by origin
    python huginn/glass.py 203.0.113.0/24 --verbose  # every peer at every collector

More than one origin AS for a prefix (a MOAS) is the first thing a hijack looks
like, so the summary leads with the origin set and flags it.
"""
import argparse
import json
import urllib.parse
import urllib.request
from collections import defaultdict

API = "https://stat.ripe.net/data/looking-glass/data.json"


def fetch(prefix):
    q = urllib.parse.urlencode({"resource": prefix})
    with urllib.request.urlopen(f"{API}?{q}", timeout=20) as r:
        return json.load(r)["data"]


def main():
    ap = argparse.ArgumentParser(description="Snapshot of who announces a prefix.")
    ap.add_argument("prefix", help="prefix to look up, e.g. 203.0.113.0/24")
    ap.add_argument("--verbose", action="store_true",
                    help="every peer at every collector, not just the summary")
    args = ap.parse_args()

    data = fetch(args.prefix)
    rrcs = data.get("rrcs", [])

    peers_by = defaultdict(int)        # (origin, prefix) -> peer count
    rrcs_by = defaultdict(set)         # (origin, prefix) -> set of collectors
    total_peers = 0
    for rrc in rrcs:
        for peer in rrc.get("peers", []):
            key = (peer.get("asn_origin"), peer.get("prefix"))
            peers_by[key] += 1
            rrcs_by[key].add(rrc.get("rrc"))
            total_peers += 1
            if args.verbose:
                print(rrc.get("rrc"), rrc.get("location", ""),
                      "origin", key[0], "path", peer.get("as_path"), "prefix", key[1])

    if args.verbose:
        return

    if not peers_by:
        print(f"# no collector currently sees {args.prefix}")
        return

    origins = sorted({k[0] for k in peers_by}, key=str)
    print(f"{args.prefix}: {len(origins)} origin AS, {total_peers} peers, {len(rrcs)} collectors")
    if len(origins) > 1:
        print("# MOAS: more than one origin announces this prefix, which is what a hijack looks like")
    for key in sorted(peers_by, key=lambda k: (-peers_by[k], str(k[0]))):
        origin, pfx = key
        print(f"  AS{origin}  {pfx}  seen by {peers_by[key]} peers across {len(rrcs_by[key])} collectors")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # Output was piped into something that closed early (head, grep -m).
        import os
        import sys
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
