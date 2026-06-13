#!/usr/bin/env python3
"""Huginn: ask the table what it thinks of an origin and prefix.

RPKI validity (valid, invalid_asn, invalid_length, or unknown) via RIPEstat's
public API, so nothing to install or run. For an offline or no-third-party check,
run Routinator locally instead (see the README).

    python huginn/validity.py 65020 203.0.113.0/25
"""
import argparse
import json
import urllib.parse
import urllib.request

API = "https://stat.ripe.net/data/rpki-validation/data.json"


def main():
    ap = argparse.ArgumentParser(description="RPKI validity of an origin and prefix.")
    ap.add_argument("asn", help="origin AS, e.g. 65020 or AS65020")
    ap.add_argument("prefix", help="prefix, e.g. 203.0.113.0/25")
    args = ap.parse_args()

    q = urllib.parse.urlencode({"resource": args.asn, "prefix": args.prefix})
    with urllib.request.urlopen(f"{API}?{q}", timeout=20) as r:
        data = json.load(r)["data"]

    asn = str(args.asn).lstrip("ASas")
    print(f"{args.prefix} from AS{asn}: {data.get('status')}")
    for roa in data.get("validating_roas", []):
        print("  roa origin", roa.get("origin"), "prefix", roa.get("prefix"),
              "maxlen", roa.get("max_length"), roa.get("validity"))


if __name__ == "__main__":
    main()
