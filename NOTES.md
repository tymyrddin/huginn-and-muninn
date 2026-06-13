# Notes: findings and choices

A short record of why Huginn and Muninn are built the way they are, and what was
actually checked. Validation done 2026-06-13.

## Design choices

- Local and zero-cloud. Observation only reads public data, so there is nothing to
  provision. A laptop or a small box runs all of it.
- Public APIs over running infrastructure where it can be helped. `glass`,
  `validity` and `recall` use RIPEstat and need only the standard library. The one
  dependency, `websocket-client`, belongs to the live stream (`watch`) alone.
- RIS Live for the live eye. `watch` streams from RIPE's public websocket and
  announces nothing.
- RIPEstat, not pybgpstream, for the quick paths. An early sketch used pybgpstream
  with `from_time=0` for "most recent", which actually reads from 1970. Dropped.
  Live data comes from RIS Live; current and historical snapshots come from
  RIPEstat; raw MRT parsing is a heavier offline option for later.
- Routinator is the offline validity option. `validity` asks RIPEstat by default;
  for a no-third-party answer, run Routinator locally (see the README), which needs
  its trust anchors initialised once before it serves.
- `glass` defaults to a summary, not a dump. The raw per-peer view (every peer at
  every collector) buries the signal. The summary leads with the origin set and
  flags a MOAS (more than one origin), which is what a hijack looks like.
  `--verbose` keeps the full per-peer view.
- `validity` reports RIPEstat's real verdicts: valid, invalid_asn, invalid_length,
  unknown, rather than a flattened valid/invalid.

## What was checked, 2026-06-13

- `glass`: live against RIPEstat. 1.1.1.0/24 shows one origin (AS13335) across 23
  collectors and about 372 peers; summary and `--verbose` both correct.
- `validity`: live. AS13335 / 1.1.1.0/24 is valid; a wrong origin returns
  invalid_asn.
- `watch`: the RIS Live message shape it reads (`timestamp`, `peer`, `path`,
  `announcements[].prefixes`, `withdrawals`) confirmed against a live stream. The
  origin AS is taken from `path[-1]`; the separate `origin` field is the BGP origin
  attribute, not the origin AS. `watch` needs `websocket-client` installed and is a
  streaming tool, so run it from a terminal.
- `recall` (Muninn): live. 1.1.1.0/24 returns 46 origins over time and 282 timeline
  rows from RIPEstat's routing history, the long pre-Cloudflare story of that
  prefix.

## Honest scope

- Partial vantage. A single set of collectors sees the table their peers offered,
  not the table everyone sees. More sight comes from more feeds, never from
  inventing routes.
- The footprint moves, it does not vanish. RIPEstat and RIS Live queries leave from
  your own address unless something sits in front of them.
- Public data only. No ASN of your own, no peering, no BMP from your own routers;
  those are the heavier embedded-eyes tier, for later.

## Status

- Huginn: `watch`, `glass`, `validity`. Done and checked.
- Muninn: `recall`. Done and checked. Raw MRT parsing (mrtparse or bgpdump) over
  the RouteViews and RIS archives is a possible heavier addition.
- No licence chosen yet.
