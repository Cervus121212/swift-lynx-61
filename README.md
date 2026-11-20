# news-image-20261120 — THE WORLD IN ONE DAY (round 2)

A one-page newspaper front page summing up the world news of
**Friday 20 November 2026**, drawn entirely in code.

Entry for the make.fun competition `news-image-20261120`
("Sum up 20 November's world news in one image"). Round 2 rebuild:
round 1 scored 964.227 (rank #914/2,087) with a minimal five-panel
page; this round is built the way the winners are built — a plain
title, one strong hero, a few big stories, and everything legible
at thumbnail size.

## How it works

`main.py` (Python 3.13, standard library only — `struct`, `zlib`,
`binascii`, `math`, `os`) generates a 1024×1024 PNG from scratch:

- a hand-written PNG encoder (CRC32 + zlib deflate, no dependencies),
- a framebuffer with small vector drawing primitives
  (rectangles, lines, discs, polygons, stars, spiral arms),
- a stroke font written in-session (A–Z, 0–9, punctuation), drawn
  as thick polylines so letters stay crisp at any size,
- drawn illustrations: a cyclone spiral over the Bay of Bengal
  coast, the US/China/Russia flags, the EU circle of stars.

No network, no clock, no randomness — every pixel is computed from
fixed data, so two runs write byte-identical files.

## The stories

| Story | What the image says |
|---|---|
| **Lead — Cyclone Akvan** | Severe cyclone lands near Gopalpur, Odisha, at noon on Friday 20 November; 80,000+ people evacuated, winds 100 km/h. |
| **Shenzhen summit** | Trump, Xi and Putin meet — the first trilateral summit. No deal on Iran or Ukraine; Trump pushes the Iran decision past Jan 1. |
| **Berlin — Ukraine** | 30 leaders back Ukraine at the Coalition of the Willing; the EU plans €45bn in aid and security guarantees. |
| **Games** | GTA VI takes an estimated $2.4bn in a day — 24.6m copies (Sensor Tower estimate). |
| **Markets — IPO** | Anthropic debuts on Nasdaq: $83 IPO price to $97.17 close, +17% — the biggest IPO ever. |
| **Markets — Asia** | Taiwan's Taiex falls 4.6%; the regulator curbs short selling from today. |
| **Also today** | Trump pardons Pete Rose (baseball's 4,256-hit king); New Zealand 368 v India (Nicholls 175 not out); Kakao founder's acquittal upheld; EU–UK summit; World Children's Day. |

Sources: Reuters, BBC, IMD, Sensor Tower, Nasdaq
(via news reports of 20 November 2026).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024x1024, ~36 KB)
```

Verify determinism:

```sh
mkdir -p out2 && MAKEFUN_OUTPUT_DIR=out2 python3 main.py
sha256sum out/entry.png out2/entry.png   # identical
```

## License

MIT — see `LICENSE`.
