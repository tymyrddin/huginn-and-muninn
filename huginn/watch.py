#!/usr/bin/env python3
"""Huginn: a live BGP eye.

Watch every announcement and withdrawal touching a prefix, as seen across RIPE
RIS collectors, streamed from the public RIS Live websocket. It announces
nothing; it only listens.

    python huginn/watch.py 203.0.113.0/24 --more-specific

Needs: pip install websocket-client
"""
import argparse
import json

import websocket  # pip install websocket-client

RIS_LIVE = "wss://ris-live.ripe.net/v1/ws/?client=huginn"


def origin_of(path):
    """Origin AS is the last element of the path. For an AS_SET it may itself be
    a list; return it as-is rather than guessing."""
    return path[-1] if path else None


def main():
    ap = argparse.ArgumentParser(description="Watch a prefix on RIS Live.")
    ap.add_argument("prefix", help="prefix to watch, e.g. 203.0.113.0/24")
    ap.add_argument("--more-specific", action="store_true",
                    help="also report more-specifics (what a hijack would announce)")
    ap.add_argument("--host", help="limit to one RIS collector, e.g. rrc00")
    args = ap.parse_args()

    sub = {"prefix": args.prefix, "moreSpecific": args.more_specific}
    if args.host:
        sub["host"] = args.host

    ws = websocket.create_connection(RIS_LIVE)
    ws.send(json.dumps({"type": "ris_subscribe", "data": sub}))
    print(f"# watching {args.prefix} (more-specific={args.more_specific}); Ctrl-C to stop")
    try:
        while True:
            msg = json.loads(ws.recv())
            if msg.get("type") != "ris_message":
                continue
            d = msg["data"]
            ts, peer, path = d.get("timestamp"), d.get("peer"), d.get("path", [])
            for ann in d.get("announcements", []):
                for pfx in ann.get("prefixes", []):
                    print(ts, "A", pfx, "origin", origin_of(path), "path", path, "seen-by", peer)
            for pfx in d.get("withdrawals", []):
                print(ts, "W", pfx, "seen-by", peer)
    except KeyboardInterrupt:
        print("\n# stopped")
    finally:
        ws.close()


if __name__ == "__main__":
    main()
