# Huginn and Muninn

![Huginn and Muninn](assets/tree-eyes.png)

Odin's ravens, Thought and Memory. They fly out over the routing world each day
and report back what they saw. This is a small, local BGP observation toolkit: it
reads public data and announces nothing. No cloud, no peering, no ASN of your own.
A laptop or a small always-on box is plenty.

Two ravens, two jobs:

- Huginn, thought, the now. Live and current observation: what is being
  announced, by whom, and whether the table believes it.
- Muninn, memory, the then. The history of who announced a prefix and when, from
  RIPE's routing archive.

## Install

```bash
pip install -r requirements.txt
```

Only `watch.py` needs that (the RIS Live websocket). The other two use the
standard library.

## Huginn: the now

Watch a prefix live, every announcement and withdrawal touching it, across RIPE's
collectors. Add `--more-specific` to catch the kind of announcement a hijack
makes:

```bash
python huginn/watch.py 203.0.113.0/24 --more-specific
```

A snapshot of who is announcing a prefix right now, grouped by origin and flagging
a MOAS (more than one origin, what a hijack looks like). Add `--verbose` for every
peer at every collector:

```bash
python huginn/glass.py 203.0.113.0/24
python huginn/glass.py 203.0.113.0/24 --verbose
```

Ask the table what it thinks of an origin and prefix:

```bash
python huginn/validity.py 65020 203.0.113.0/25     # valid | invalid_asn | invalid_length | unknown
```

`watch.py` streams from RIS Live. `glass.py` and `validity.py` call RIPEstat's
public API and need nothing beyond Python.

## Validity without a third party

The check above asks RIPEstat. For an offline or no-third-party verdict, run
Routinator locally. It initialises its trust anchors once, then serves:

```bash
docker run --rm -v "$PWD/routinator:/home/routinator/.rpki-cache" \
  nlnetlabs/routinator init --accept-arin-rpa
docker run -d --name routinator -p 9556:9556 \
  -v "$PWD/routinator:/home/routinator/.rpki-cache" nlnetlabs/routinator server
curl 'http://localhost:9556/api/v1/validity/AS65020/203.0.113.0/25'
```

Check the exact flags against Routinator's own docker quickstart; the bare image
needs the init step above before the server has anything to validate against.

## Muninn: the then

The history of who announced a prefix and when, from RIPE's routing archive. An
origin change in the timeline is where a past hijack, or a legitimate handover,
shows:

```bash
python muninn/recall.py 203.0.113.0/24
python muninn/recall.py 203.0.113.0/24 --max-rows 100
```

Standard library only, like `glass` and `validity`.

## Scope

A single eye sees the table its collectors' peers offered, not the one everyone
sees. Partial vantage is the honest state of one eye; more sight comes from more
feeds, never from inventing routes the collectors did not receive. Queries leave
from your own address unless you put something in front of them, so the footprint
moves rather than vanishes.

## Status

Huginn (`watch`, `glass`, `validity`) and Muninn (`recall`) are built and checked
live against RIPEstat and RIS Live; see `NOTES.md` for what was verified and why
the choices were made. `watch.py` needs `websocket-client` and is a streaming
tool, so run it from a terminal. Raw MRT parsing over the archives is a possible
heavier addition. No licence chosen yet.
