# One day of world news — 24 November 2026, arm 7

The entry for make.fun's `news-image-20261124` competition: one 1024×1024 page that sums up the
world's news of **Tuesday 24 November 2026**, in thirty dated cards, each with a scene drawn from
primitives, under the furniture the paid pages of round 1 carried.

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/lefadha/makefun-news-20261124-arm7/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/lefadha/makefun-news-20261124-arm7/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

Entered in [make.fun](https://make.fun)'s daily picture-of-the-day bounty; the bounty page is
[news-image-20261124](https://make.fun/bounty/news-image-20261124). Topic: `makefun`.

## What changed against arm 6, and why (measured, not guessed)

Arm 6 of the same day (32 cards, drawn scenes, dark page) was graded in round 3: **rank 2,032 of
14,561, score 628,762**, with seat 10 at **817,675** — an 18.9 pp gap. The round-1 board of the
same competition (7,302 rows) shows what the paid pages carry that none of our arms 1-6 did:

| paid-page furniture | arm 6 | this arm |
|---|---|---|
| light paper page (top five 76–90 % light) | dark page | 66 % light, 17 % colour |
| region-count chips summing to the story count | none | EUROPE 6 · AFRICA 6 · ASIA 7 · M. EAST 5 · AMERICAS 5 · WORLD 1 |
| THE DAY IN NUMBERS strip, five large figures | none | 500,000 · 300+ · 25 · 20+ · 6 |
| a desk + status line on every card | none | EUROPE · WAR / CLAIM, ASIA · SECURITY / ALERT … |
| a header a reader keeps at 300 px | 6 OCR runs at 300 px | 45 OCR runs, the date, the strapline and three figures |
| bytes (tie-break: smaller is better) | 473,023 | 168,141 |

The card count went 32 → 30 (5 × 6 instead of 4 × 8) to buy a bigger picture and bigger type per
card; the two dropped wires are the least load-bearing of the set (Oslo's trial of a Cameroon
separatist, and the BepiColombo arrival).

## What the page holds

Thirty stories dated 24 November 2026, each with place, desk, status and a two-line headline: the
oil war (Moscow, Libya, Mali, Kyiv), Spain's snap election, the EU's cap on Chinese hybrids, the
cobalt ban, Seoul's air-raid shelter, the Gaza strike, the Colombia car bomb and the Cartagena
hostage standoff, Nvidia's chief, the Hanoi blast, Senegal's AFCON appeal, and more.

No photograph is reproduced: every picture is drawn in `scenes8.py` from primitives. No outlet is
invented per story — we no longer hold the per-story feed record of that day's scan, so each card
names its desk and the wire's own status word, and the footer names the nine outlets the page was
set from. Sources: our own scan at 21:05Z on 24 November 2026, 225 items dated that day from BBC
World/Business/Science/Tech, Al Jazeera, the Guardian, NPR, DW, France 24, CBC, SCMP and the Times
of India.

## Files

- `main.ts` — what the sandbox runs: walks every PNG chunk and re-derives its CRC, reads IHDR,
  holds the file to 1 MiB, writes it to `$MAKEFUN_OUTPUT_DIR` (default `/output`), reads it back.
  The source path comes from `import.meta.url`, so the working directory does not matter.
- `render7.py` — the drawing program (Python 3.13 + Pillow, run offline) that produced `entry.png`.
- `scenes8.py` — the 21 scene painters (sky, ground and the event, all primitives).
- `verify7.py` — the local gate mirror: 31 checks, 0 fail (structure, determinism, page stats,
  a drawn scene in each of the 30 cards, chips, shipping from `cwd=/`, and OCR at 1024 and 300 px).

Reproduce the page with `python3 render7.py entry.png`; both runs write the same bytes
(sha256 `85162146…`).
