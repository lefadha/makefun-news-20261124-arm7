#!/usr/bin/env python3
"""The scene painters for arm 7, written for this build (168 x 46 tiles).

Every picture on the page is drawn here from primitives -- rectangles, polygons,
ellipses, arcs and lines -- with no photograph, no bitmap and no font glyph. Each
painter fills its tile with a sky tinted by the story's region colour, lays a
ground line, and puts one subject on it, so a card reads as a small landscape
rather than a symbol floating on a dark box.

The page calls tile(name, region_colour) and pastes the returned 2x supersampled
tile into the card.
"""
import math

from PIL import Image, ImageDraw

TW, TH = 168, 46
S = 2
NIGHT = (10, 12, 16)


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _sky(d, col, horizon=0.62, steps=9):
    """A banded sky from the region colour at the top down to a darker horizon."""
    hz = TH * horizon
    for i in range(steps):
        y0 = hz * i / steps
        y1 = hz * (i + 1) / steps
        d.rectangle([0, y0, TW, y1 + 1], fill=mix(mix(col, NIGHT, 0.55), mix(col, NIGHT, 0.86),
                                                  i / (steps - 1)))
    return hz


def _ground(d, col, hz, depth=0.72):
    d.rectangle([0, hz, TW, TH], fill=mix(col, NIGHT, depth))
    d.line([(0, hz), (TW, hz)], fill=mix(col, NIGHT, depth - 0.18), width=2)


def _flames(d, x, base, n=3, step=14, h=18):
    for k in range(n):
        bx = x + k * step
        d.polygon([(bx, base), (bx + 6, base - h - k % 2 * 5), (bx + 12, base)],
                  fill=(244, 150, 48))
        d.polygon([(bx + 3, base), (bx + 6, base - h * 0.55), (bx + 9, base)],
                  fill=(255, 226, 150))


def _smoke(d, x, base, col, n=4):
    for k in range(n):
        r = 4 + k
        d.ellipse([x + k * 5 - r, base - 12 - k * 6 - r, x + k * 5 + r, base - 12 - k * 6 + r],
                  fill=mix(col, NIGHT, 0.5 + 0.1 * k))


def fire(d, col):
    hz = _sky(d, col, 0.66)
    _ground(d, col, hz, 0.8)
    for bx, bw, bh in ((14, 34, 18), (58, 26, 14), (120, 30, 20)):
        d.rectangle([bx, TH - bh, bx + bw, TH - 4], fill=mix(col, NIGHT, 0.92))
        d.rectangle([bx + 6, TH - bh - 6, bx + bw - 8, TH - bh], fill=mix(col, NIGHT, 0.84))
    _flames(d, 26, TH - 4, 3, 12, 16)
    _smoke(d, 70, TH - 10, col, 5)


def ship(d, col):
    hz = _sky(d, col, 0.46)
    d.rectangle([0, hz, TW, TH], fill=mix(col, NIGHT, 0.8))
    for i in range(3):
        d.line([(0, hz + 6 + i * 7), (TW, hz + 6 + i * 7)], fill=mix(col, NIGHT, 0.62), width=1)
    d.polygon([(40, hz + 14), (128, hz + 14), (118, hz + 26), (50, hz + 26)],
              fill=mix(col, NIGHT, 0.94))
    d.rectangle([70, hz + 4, 98, hz + 14], fill=mix(col, NIGHT, 0.88))
    d.rectangle([82, hz - 8, 86, hz + 4], fill=mix(col, NIGHT, 0.92))
    d.polygon([(98, hz + 6), (118, hz - 2), (118, hz + 10)], fill=(240, 128, 84))
    _smoke(d, 60, hz, col, 4)


def coffin(d, col):
    hz = _sky(d, col, 0.72)
    _ground(d, col, hz, 0.76)
    d.polygon([(52, TH - 4), (116, TH - 4), (110, TH - 16), (94, TH - 20),
               (74, TH - 20), (58, TH - 16)], fill=mix(col, NIGHT, 0.95))
    for i in range(4):
        d.line([(64 + i * 13, TH - 19), (64 + i * 13, TH - 6)], fill=mix(col, NIGHT, 1.8), width=2)
    for px in (40, 124):
        d.ellipse([px, TH - 14, px + 6, TH - 8], fill=mix(col, NIGHT, 0.6))
        d.rectangle([px + 1, TH - 8, px + 5, TH - 3], fill=mix(col, NIGHT, 0.6))


def chart(d, col):
    hz = _sky(d, col, 0.88)
    ox, oy = 18, TH - 6
    d.line([(ox, 6), (ox, oy)], fill=mix(col, NIGHT, 0.7), width=2)
    d.line([(ox, oy), (TW - 10, oy)], fill=mix(col, NIGHT, 0.7), width=2)
    pts = [(ox + 6, oy - 8), (ox + 34, oy - 12), (ox + 62, oy - 10),
           (ox + 90, oy - 22), (ox + 118, oy - 26), (ox + 140, oy - 4)]
    d.line(pts, fill=(240, 104, 92), width=3, joint='curve')
    for px, py in pts:
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 230, 218))


def flag(d, col):
    hz = _sky(d, col, 0.74)
    _ground(d, col, hz, 0.76)
    for px in (34, 84, 134):
        d.line([(px, 8), (px, TH - 3)], fill=mix(col, NIGHT, 0.82), width=2)
        for k in range(3):
            d.polygon([(px + 2, 10 + k * 10), (px + 40 - k * 3, 7 + k * 10),
                       (px + 38 - k * 3, 16 + k * 10), (px + 2, 19 + k * 10)],
                      fill=col if k % 2 == 0 else mix(col, (250, 246, 236), 0.4))
    for px in (16, 72, 128, 154):
        d.ellipse([px, TH - 10, px + 6, TH - 4], fill=mix(col, NIGHT, 0.55))


def gavel(d, col):
    hz = _sky(d, col, 0.82)
    _ground(d, col, hz, 0.74)
    d.rectangle([96, TH - 16, 158, TH - 9], fill=mix(col, NIGHT, 0.92))
    d.rectangle([112, TH - 9, 142, TH - 4], fill=mix(col, NIGHT, 0.78))
    d.polygon([(52, 10), (86, 17), (83, 27), (49, 20)], fill=mix(col, (250, 246, 236), 0.55))
    d.line([(66, 22), (80, TH - 12)], fill=mix(col, NIGHT, 0.9), width=3)
    for k in range(3):
        d.line([(94 + k * 8, 6), (89 + k * 8, 13)], fill=mix(col, NIGHT, 0.62), width=2)


def ballot(d, col):
    hz = _sky(d, col, 0.82)
    _ground(d, col, hz, 0.74)
    bx, by = 56, TH - 24
    d.polygon([(bx, by), (bx + 76, by), (bx + 68, TH - 3), (bx + 8, TH - 3)],
              fill=mix(col, NIGHT, 0.94))
    d.rectangle([bx + 28, by - 3, bx + 48, by + 2], fill=NIGHT)
    d.polygon([(bx + 32, by - 18), (bx + 58, by - 13), (bx + 55, by - 2), (bx + 29, by - 7)],
              fill=mix(col, (250, 246, 236), 0.7))
    d.line([(bx + 36, by - 10), (bx + 40, by - 5), (bx + 50, by - 14)],
           fill=(46, 132, 84), width=3)


def car(d, col):
    hz = _sky(d, col, 0.72)
    _ground(d, col, hz, 0.72)
    by = TH - 14
    d.rectangle([30, by - 8, 132, by], fill=mix(col, NIGHT, 0.92))
    d.polygon([(52, by - 8), (68, by - 18), (104, by - 18), (114, by - 8)],
              fill=mix(col, NIGHT, 0.86))
    for wx in (48, 104):
        d.ellipse([wx, by - 1, wx + 12, by + 11], fill=mix(col, NIGHT, 0.6))
        d.ellipse([wx + 3, by + 2, wx + 9, by + 8], fill=NIGHT)
    d.line([(138, by - 26), (138, by - 4)], fill=col, width=3)
    d.line([(138, by - 26), (150, by - 20), (142, by - 14)], fill=col, width=2)


def virus(d, col):
    _sky(d, col, 0.9)
    for cx, cy, r in ((48, 18, 9), (96, 13, 6), (128, 24, 5)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=mix(col, (250, 246, 236), 0.5))
        for k in range(8):
            a = k * math.pi / 4
            d.line([(cx + r * 0.9 * math.cos(a), cy + r * 0.9 * math.sin(a)),
                    (cx + (r + 5) * math.cos(a), cy + (r + 5) * math.sin(a))],
                   fill=mix(col, (250, 246, 236), 0.7), width=2)
    d.rectangle([0, TH - 10, TW, TH], fill=mix(col, NIGHT, 0.7))


def crown(d, col):
    hz = _sky(d, col, 0.84)
    _ground(d, col, hz, 0.76)
    cx = 58
    d.polygon([(cx, TH - 8), (cx + 60, TH - 8), (cx + 55, TH - 22), (cx + 40, TH - 15),
               (cx + 30, TH - 24), (cx + 20, TH - 15), (cx + 5, TH - 22)], fill=(232, 190, 82))
    d.rectangle([cx, TH - 8, cx + 60, TH - 5], fill=(196, 152, 54))
    d.ellipse([cx + 26, TH - 10, cx + 30, TH - 6], fill=(150, 60, 60))


def trophy(d, col):
    hz = _sky(d, col, 0.84)
    _ground(d, col, hz, 0.76)
    cx = 62
    d.polygon([(cx, TH - 5), (cx + 44, TH - 5), (cx + 36, TH - 12), (cx + 8, TH - 12)],
              fill=(228, 184, 76))
    d.rectangle([cx + 18, TH - 18, cx + 26, TH - 12], fill=(228, 184, 76))
    d.polygon([(cx + 6, 8), (cx + 38, 8), (cx + 34, TH - 19), (cx + 10, TH - 19)],
              fill=(238, 198, 92))
    for s, span in ((1, (36, 50)), (-1, (0, 14))):
        d.arc([cx + span[0], 10, cx + span[1], 24], start=-90 if s > 0 else 90,
              end=90 if s > 0 else 270, fill=(238, 198, 92), width=3)


def battery(d, col):
    hz = _sky(d, col, 0.86)
    _ground(d, col, hz, 0.74)
    bx, by = 44, 8
    d.rectangle([bx, by, bx + 40, by + 22], fill=mix(col, NIGHT, 0.9), outline=col, width=2)
    d.rectangle([bx + 40, by + 7, bx + 45, by + 15], fill=col)
    for i in range(3):
        d.rectangle([bx + 4 + i * 11, by + 4, bx + 12 + i * 11, by + 18],
                    fill=mix(col, (250, 246, 236), 0.35))
    d.line([(bx + 6, by + 4), (bx + 32, by + 18)], fill=(226, 62, 54), width=3)
    for i, hh in enumerate((8, 14, 19)):
        d.rectangle([112 + i * 16, TH - 8 - hh, 123 + i * 16, TH - 8], fill=mix(col, NIGHT, 0.5))


def mine(d, col):
    hz = _sky(d, col, 0.7)
    _ground(d, col, hz, 0.72)
    cx, cy = 92, TH - 9
    d.ellipse([cx - 12, cy - 6, cx + 12, cy + 6], fill=mix(col, NIGHT, 0.95))
    for k in range(8):
        a = k * math.pi / 4
        d.line([(cx + 11 * math.cos(a), cy + 5 * math.sin(a)),
                (cx + 17 * math.cos(a), cy + 9 * math.sin(a))], fill=(226, 62, 54), width=2)
    d.polygon([(18, hz + 4), (150, hz + 4), (144, hz + 9), (24, hz + 9)],
              fill=mix(col, NIGHT, 0.58))


def money(d, col):
    _sky(d, col, 0.86)
    d.rectangle([26, 12, 114, 32], fill=mix(col, (150, 206, 158), 0.5))
    d.ellipse([62, 16, 82, 28], outline=NIGHT, width=2)
    for px in (34, 96):
        d.rectangle([px, 17, px + 10, 27], outline=NIGHT, width=1)
    for i, px in enumerate((124, 138, 152)):
        d.ellipse([px, 16 - i * 3, px + 12, 28 - i * 3], fill=(232, 194, 88), outline=NIGHT)


def megaphone(d, col):
    _sky(d, col, 0.88)
    d.polygon([(36, 16), (84, 5), (84, 31), (36, 23)], fill=mix(col, (250, 246, 236), 0.55))
    d.rectangle([27, 17, 37, 22], fill=mix(col, (250, 246, 236), 0.4))
    for k in range(3):
        d.arc([88 + k * 8, 4 - k * 2, 112 + k * 8, 34 + k * 2], start=-50, end=50,
              fill=mix(col, (250, 246, 236), 0.2 + 0.25 * k), width=3)
    for px in (128, 142, 156):
        d.ellipse([px, TH - 12, px + 6, TH - 6], fill=mix(col, NIGHT, 0.55))
        d.polygon([(px, TH - 6), (px + 6, TH - 6), (px + 7, TH - 1), (px - 1, TH - 1)],
                  fill=mix(col, NIGHT, 0.55))


def plane(d, col):
    hz = _sky(d, col, 0.9)
    cx, cy = 72, 16
    d.polygon([(cx, cy), (cx + 44, cy + 5), (cx + 44, cy + 10), (cx, cy + 8)],
              fill=mix(col, (250, 246, 236), 0.6))
    d.polygon([(cx + 16, cy + 4), (cx + 4, cy - 8), (cx + 14, cy - 8), (cx + 28, cy + 4)],
              fill=mix(col, (250, 246, 236), 0.5))
    d.polygon([(cx + 20, cy + 8), (cx + 10, cy + 19), (cx + 20, cy + 19), (cx + 32, cy + 9)],
              fill=mix(col, (250, 246, 236), 0.45))
    for k in range(3):
        d.line([(cx - k * 12, cy + 8), (cx - 34 - k * 8, cy + 10 + k * 2)],
               fill=mix(col, (250, 246, 236), 0.15), width=2)
    d.rectangle([0, TH - 8, TW, TH], fill=mix(col, NIGHT, 0.76))


def blast(d, col):
    hz = _sky(d, col, 0.66)
    _ground(d, col, hz, 0.74)
    for bx, bw, bh in ((4, 20, 16), (28, 14, 22), (140, 18, 19), (160, 8, 12)):
        d.rectangle([bx, TH - bh, bx + bw, TH], fill=mix(col, NIGHT, 0.9))
    cx, cy = 88, TH - 20
    for k in range(9):
        a = k * 2 * math.pi / 9
        r1, r2 = 6, 18 + (k % 3) * 6
        d.polygon([(cx + r1 * math.cos(a - 0.18), cy + r1 * math.sin(a - 0.18)),
                   (cx + r2 * math.cos(a), cy + r2 * math.sin(a)),
                   (cx + r1 * math.cos(a + 0.18), cy + r1 * math.sin(a + 0.18))],
                  fill=(246, 176, 66) if k % 2 else (240, 120, 90))
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(255, 240, 206))


def person(d, col):
    hz = _sky(d, col, 0.82)
    _ground(d, col, hz, 0.76)
    for i, px in enumerate(range(14, 154, 20)):
        top = 14 + (i % 3) * 4
        d.ellipse([px, top, px + 8, top + 8], fill=mix(col, (250, 246, 236), 0.45))
        d.polygon([(px - 3, TH - 2), (px + 11, TH - 2), (px + 9, top + 10), (px - 1, top + 10)],
                  fill=mix(col, NIGHT, 0.9))


def cross(d, col):
    hz = _sky(d, col, 0.8)
    _ground(d, col, hz, 0.74)
    bx, by = 56, 8
    d.rectangle([bx, by + 6, bx + 64, TH], fill=mix(col, NIGHT, 0.92))
    d.rectangle([bx + 6, by, bx + 16, by + 10], fill=mix(col, NIGHT, 0.74))
    d.rectangle([bx + 48, by, bx + 58, by + 10], fill=mix(col, NIGHT, 0.74))
    cx, cy = bx + 32, by + 20
    d.rectangle([cx - 4, cy - 13, cx + 4, cy + 13], fill=(236, 92, 84))
    d.rectangle([cx - 12, cy - 4, cx + 12, cy + 4], fill=(236, 92, 84))


def chip(d, col):
    _sky(d, col, 0.88)
    bx, by = 56, 10
    d.rectangle([bx, by, bx + 56, by + 26], fill=mix(col, NIGHT, 0.9), outline=col, width=2)
    d.rectangle([bx + 12, by + 6, bx + 44, by + 20], fill=mix(col, NIGHT, 0.62), outline=col)
    for k in range(4):
        for yy in (by, by + 26):
            d.line([(bx + 10 + k * 12, yy), (bx + 10 + k * 12, yy + (-5 if yy == by else 5))],
                   fill=col, width=2)
    d.line([(bx + 56, by + 13), (150, by + 13), (150, TH - 8)], fill=mix(col, NIGHT, 0.4), width=2)


def planet(d, col):
    _sky(d, col, 0.96)
    cx, cy, r = 84, 22, 11
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=mix(col, (216, 196, 172), 0.4),
              outline=mix(col, (250, 246, 236), 0.3))
    d.arc([cx - 21, cy - 7, cx + 21, cy + 7], start=190, end=350,
          fill=mix(col, (250, 246, 236), 0.55), width=2)
    d.arc([cx - 21, cy - 7, cx + 21, cy + 7], start=10, end=170,
          fill=mix(col, (250, 246, 236), 0.3), width=2)
    for px, py in ((24, 9), (46, 30), (140, 8), (154, 28), (118, 6)):
        d.ellipse([px, py, px + 2, py + 2], fill=mix(col, (250, 246, 236), 0.65))


PAINTERS = {
    'fire': fire, 'ship': ship, 'coffin': coffin, 'chart': chart, 'flag': flag,
    'gavel': gavel, 'ballot': ballot, 'car': car, 'virus': virus, 'crown': crown,
    'trophy': trophy, 'battery': battery, 'mine': mine, 'money': money,
    'megaphone': megaphone, 'plane': plane, 'blast': blast, 'person': person,
    'cross': cross, 'chip': chip, 'planet': planet,
}


def tile(name, region_colour):
    """Draw one scene at TW x TH, then hand back the supersampled tile."""
    im = Image.new('RGB', (TW, TH), NIGHT)
    PAINTERS[name](ImageDraw.Draw(im), region_colour)
    return im.resize((TW * S, TH * S), Image.NEAREST)
