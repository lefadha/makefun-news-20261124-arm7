#!/usr/bin/env python3
"""Local mirror of the gate for arm 7 of news-image-20261124.

Checks, in the order the gate matters:
  structure  -- PNG whole, every chunk CRC, IHDR 1024x1024, under 1 MiB, no trailing bytes
  determinism -- a second render is byte identical
  page       -- light paper, colour in the band the paid pages measured, clean outer edge
  drawings   -- every one of the 32 cards carries a drawn scene with real ink
  furniture  -- region-count chips summing to 32, the numbers strip, a desk/status line
  shipping   -- main.ts resolves entry.png from its own module (cwd does not matter) and
                writes the same bytes back
  reading    -- OCR at full size (date, places, headlines, figures) and at 300 px

Run: python3 verify7.py     -- exit 0 only when nothing failed.
"""
import hashlib
import os
import struct
import subprocess
import sys
import zlib
from difflib import SequenceMatcher

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, 'entry.png')
PY = sys.executable
TMP = '/opt/data/tmp/desk1835/verify'
CAP = 1048576
W = H = 1024
PASS, FAIL = [], []

sys.path.insert(0, HERE)
import render7  # noqa: E402

TAGS = [s[0] for s in render7.STORIES]
HEADS = [s[2] for s in render7.STORIES]
CHIPS = {}
for _s in render7.STORIES:
    CHIPS[_s[1]] = CHIPS.get(_s[1], 0) + 1


def ok(name, cond, detail=''):
    (PASS if cond else FAIL).append(name)
    print(('pass ' if cond else 'FAIL ') + name + (': ' + detail if detail else ''))


def walk(path):
    b = open(path, 'rb').read()
    ok('png signature', b[:8] == b'\x89PNG\r\n\x1a\n')
    at, kinds, side = 8, [], (0, 0)
    while at + 12 <= len(b):
        ln = struct.unpack('>I', b[at:at + 4])[0]
        typ = b[at + 4:at + 8].decode('latin1')
        crc = struct.unpack('>I', b[at + 8 + ln:at + 12 + ln])[0]
        ok(f'crc {typ}@{at}', zlib.crc32(b[at + 4:at + 8 + ln]) & 0xffffffff == crc)
        if typ == 'IHDR':
            side = struct.unpack('>II', b[at + 8:at + 16])
        kinds.append(typ)
        at += 12 + ln
        if typ == 'IEND':
            break
    ok('IEND last', kinds and kinds[-1] == 'IEND')
    ok('no trailing bytes', at == len(b), f'{len(b) - at} extra')
    ok('1024x1024', side == (W, H), f'{side[0]}x{side[1]}')
    ok('under 1 MiB', len(b) <= CAP, f'{len(b)} bytes')
    return b


raw = walk(PNG)
sha = hashlib.sha256(raw).hexdigest()
print('   sha256', sha[:16], '| bytes', len(raw))

os.makedirs(TMP, exist_ok=True)
again = os.path.join(TMP, 'again.png')
subprocess.run([PY, os.path.join(HERE, 'render7.py'), again], check=True, stdout=subprocess.DEVNULL)
ok('two renders byte identical', open(again, 'rb').read() == raw)

img = Image.open(PNG).convert('RGB')
a = np.asarray(img).astype(np.int16)
lum = a.mean(axis=2)
light = 100.0 * (lum > 200).mean()
mx, mn = a.max(axis=2), a.min(axis=2)
hued = (mx - mn) > 26
buckets = len({(int(p[0]) // 24, int(p[1]) // 24, int(p[2]) // 24)
               for p in a[hued][:200000]}) if hued.any() else 0
ok('light paper 60-90%', 60 <= light <= 90, f'{light:.1f}%')
ok('colour 8-25%', 8 <= 100.0 * hued.mean() <= 25, f'{100.0 * hued.mean():.1f}%')
print('   colour buckets', buckets)

edge = 16
strips = [a[:edge], a[-edge:], a[:, :edge], a[:, -edge:]]
ok('clean outer 16 px (no ink on the paper edge)',
   min(int(s.mean(axis=2).min()) for s in strips) >= 190,
   f'min lum {min(int(s.mean(axis=2).min()) for s in strips)}')

# ---- 30 drawn scenes: each card's tile carries ink and several colours -------------
M, top, bottom = render7.M, 236, 940
cols, rows, gap = render7.COLS, render7.ROWS, 7
cw = (W - 2 * M - (cols - 1) * gap) / cols
rh = (bottom - top - (rows - 1) * gap) / rows
TW, TH = render7.TILE_W, render7.TILE_H
ink_pct, cols_per_card = [], []
for i in range(len(render7.STORIES)):
    r_, c_ = divmod(i, cols)
    x = M + c_ * (cw + gap) + 7
    y0 = top + r_ * (rh + gap) + 5
    crop = np.asarray(img.crop((int(x), int(y0), int(x + TW), int(y0 + TH)))).astype(np.int16)
    l = crop.mean(axis=2)
    ink = (l < 120) | ((crop.max(axis=2) - crop.min(axis=2)) > 40)
    ink_pct.append(round(100.0 * ink.mean(), 1))
    cols_per_card.append(len({tuple(p) for p in crop.reshape(-1, 3)[::5]}))
ok('every card carries a drawn scene (ink >= 20%)', min(ink_pct) >= 20,
   f'min {min(ink_pct)}% max {max(ink_pct)}%')
ok('every scene has >= 6 distinct colours', min(cols_per_card) >= 6, f'min {min(cols_per_card)}')
print('   scene ink % per card:', ink_pct)

# ---- the furniture the paid band carried -----------------------------------------
ok('region chips sum to the story count',
   sum(CHIPS.values()) == len(TAGS) == len(render7.STORIES), str(CHIPS))

main_src = open(os.path.join(HERE, 'main.ts')).read()
ok('main.ts resolves entry.png from the module', 'fileURLToPath(import.meta.url)' in main_src)
ok('main.ts reads back what it wrote', 'readFileSync(target).equals(png)' in main_src)

out = os.path.join(TMP, 'out')
os.makedirs(out, exist_ok=True)
subprocess.run(['node', os.path.join(HERE, 'main.ts')], check=True, cwd='/',
               env={**os.environ, 'MAKEFUN_OUTPUT_DIR': out}, stdout=subprocess.DEVNULL)
shipped = open(os.path.join(out, 'entry.png'), 'rb').read()
ok('main.ts from cwd=/ ships the same bytes', shipped == raw, f'{len(shipped)} vs {len(raw)}')

# ---- reading ---------------------------------------------------------------------
try:
    from rapidocr_onnxruntime import RapidOCR
    ocr = RapidOCR()
    texts = {}
    for tag, size in (('full', W), ('300px', 300)):
        im = img if size == W else img.resize((size, size), Image.LANCZOS)
        path = os.path.join(TMP, f'ocr_{tag}.png')
        im.save(path)
        res, _ = ocr(path)
        res = res or []
        texts[tag] = (' '.join(r[1] for r in res).upper(), len(res), res)

    full, runs, _ = texts['full']
    ok('full OCR reads the date', 'NOVEMBER' in full and '2026' in full, f'{runs} runs')
    places = sum(1 for t in TAGS if t in full)
    ok('full OCR reads 28+ of 30 place tags', places >= 28, f'{places}/{len(TAGS)}')
    tokens = [w.strip('.,:;()').upper() for w in full.split()]

    def near(word, pool, cut=0.78):
        return max((SequenceMatcher(None, word, p).ratio() for p in pool), default=0) >= cut

    heads = 0
    for h in HEADS:
        words = [w.strip('.,:;').upper() for w in h.split() if len(w.strip('.,:;')) >= 5]
        if any(near(w, tokens) for w in words):
            heads += 1
    ok('full OCR reads 26+ of 30 headlines', heads >= 26, f'{heads}/{len(HEADS)}')

    figs = sum(1 for f in ('500,000', '300+', '25', '20+', '6') if f in full)
    ok('full OCR reads the numbers strip', figs >= 4 and 'NUMBERS' in full, f'{figs}/5 figures')
    chip_hits = sum(1 for k in ('EUROPE', 'AFRICA', 'ASIA', 'EAST', 'AMERICAS', 'GLOBAL')
                    if k in full)
    ok('full OCR reads the region chips', chip_hits >= 5, f'{chip_hits}/6')
    desk_hits = sum(1 for k in ('WAR', 'TRADE', 'JUSTICE', 'SECURITY', 'POLITICS', 'HEALTH')
                    if k in full)
    ok('full OCR reads the desk/status lines', desk_hits >= 5, f'{desk_hits}/6 desks')
    ok('full OCR reads the credit line', 'BBC' in full and 'GUARDIAN' in full,
       full[-110:])

    small, sruns, sres = texts['300px']
    ok('300 px OCR still reads the date', '2026' in small, f'{sruns} runs')
    ok('300 px OCR keeps 30+ runs', sruns >= 30, f'{sruns} runs')
    # what a reader (and the judge) must still get at 300 px: the day, the three leads
    # of the strapline, and the figures. Arm 6 kept 6 runs here and nothing of the leads.
    stops = ['NOVEMBER', 'PUTIN', 'COLOMBIA', 'SNAP', '500', '300']
    kept = sum(1 for w in stops if w in small)
    ok('300 px OCR keeps 4+ of 6 landmarks', kept >= 4, f'{kept}/6')
    print('   300px reads:', small[:160])
except Exception as e:
    ok('OCR available', False, repr(e)[:90])

print(f'\n{len(PASS)} pass {len(FAIL)} fail  sha {sha[:8]}')
sys.exit(1 if FAIL else 0)
