# NOTES — arm 7 of news-image-20261124 (built 25 November 2026, 18:40-19:10Z)

## The measurement this arm answers

- Round 3 of this competition, judged 2026-11-25T12:53Z: our arm 6
  (`01a20fa8`, 32 story cards with drawn scenes on a dark page) placed **2,032 of 14,561**
  with score **628,762**. Seat 10 on the same board: **817,675**. Leader: 872,603.
  Gap to the last paid seat: **188,913 micro = 18.9 pp**.
- Round 1 board (7,302 rows, paged in full on 24 Nov) described the paid page in
  `/opt/data/makefun/news/RECIPE_20261124.md`: source/status line per card, region-count chips
  summing to the story count, a THE DAY IN NUMBERS strip, 76-90 % light paper, 163-280 KB.
- Our own OCR of arm 6 at 300 px across: **6 readable runs**. The paid five kept 10-36.
  Arm 6 was rich but blind at the size the judge reads.

## The declared change (one design move, five parts, all taken from the measurement)

Keep the stories and the drawn scene per story; rebuild the page as a light broadsheet with the
four pieces of furniture the paid pages carry, and make the header loud enough to survive 300 px.
The card count drops 32 → 30 to pay for bigger pictures and bigger type, as the recipe's own page
budget asks ("do not shrink type to fit; drop stories instead").

## Local mirror (verify7.py), 31 pass 0 fail

| check | arm 6 | arm 7 |
|---|---|---|
| bytes | 473,023 | 174,021 (256-colour palette, no dither) |
| light paper | dark page | 66.1 % |
| colour / buckets | — | 16.9 %, 48 buckets after quantise |
| drawn scene per card | 32/32 | 30/30, ink 82-100 % of the tile |
| OCR at 1024 | 21 place tags | 30/30 places, 26/30 headlines, 5/5 figures, 6/6 chips |
| OCR at 300 px | 6 runs | **35 runs**, date + strapline + 3 of 5 figures |
| main.ts from cwd=/ | fixed on 25 Nov | ships byte-identical, 174,021 B |

Two renders are byte identical (`sha256 f2b22a23…`). No ink inside the outer 16 px.

## Honest gaps

- No per-story outlet is printed: the feed record of the 24 Nov scan is no longer on disk, so a
  card names its desk and its wire status instead. The footer names all nine outlets.
- The numbers strip carries five figures that each already appear in a story; none is derived or
  extrapolated.
- Force_Last: this submission replaces the poster arm filed at 16:49Z as our final entry. It is
  filed because the poster was unmeasured and arm 6's 628,762 is the only own number this
  competition has produced.
