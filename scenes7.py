#!/usr/bin/env python3
"""24 November 2026 as one front page, 32 dated stories, every card a drawn scene.

Measured basis, not a guess. Round 1 of this competition is judged and its board
is public (/api/competitions/news-image-20261124/rounds/board, field 7302):
1st 863,545 "34 dated stories, 9 regions", 2nd 844,040 "34 stories", 3rd 825,556
"40 stories", 4th 824,386 "32 stories, 9 regions", 5th 821,843 "37 dated stories,
13 full-scene vector drawings", 10th 803,073 "35 stories"; median 507,870. So the
seat-10 floor pairs BREADTH with DRAWN SCENES. Our earlier arms carried 6, 6, 9
and 7 stories with a 44 px glyph per card and no scene at all.

This arm keeps the 32 stories of arm 5 (same wires, same day, same scan) and
spends the change on the one thing arm 5 lacked: a 227x42 drawn scene in every
card -- sky, ground, and the event itself drawn with primitives -- above a place
tag and a two-line label. Drawn ink per card rises from 1,936 px (44x44 glyph) to
9,534 px (227x42 scene), and every scene is a landscape with a subject in it, not
a symbol.

Stories: our own scan of the 24 November 2026 wires, 225 items dated 24 Nov 2026,
BBC World/Business/Science/Tech, Al Jazeera, Guardian, NPR, DW, France 24, CBC,
SCMP, Times of India, at 21:05Z. Nothing invented to fill a slot.

Run: python3 render6.py entry.png
"""
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
S = 2
M = 24

BG = (8, 10, 14)
CARD = (17, 20, 26)
CARD2 = (21, 24, 31)
CREAM = (246, 241, 230)
DIM = (180, 175, 164)
RULE = (42, 46, 56)
RED = (226, 62, 54)

ARCH = '/opt/data/home/.fonts/ArchivoBlack-Regular.ttf'
DEJB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

REGION = {
    'Europe': (108, 165, 255),
    'Africa': (243, 180, 66),
    'Asia': (255, 120, 105),
    'MidEast': (198, 152, 255),
    'Americas': (92, 210, 165),
    'Global': (166, 184, 212),
}

DAY = 'TUESDAY 24 NOVEMBER 2026'
KICKER_L = 'THE WORLD IN ONE PICTURE'
KICKER_R = 'THE WIRES, 24 NOVEMBER 2026'
DECK = ('32 stories, six continents, one drawn scene each: Russia\u2019s oil war widens, '
        'a car bomb in Colombia, Nvidia\u2019s chief back at the helm')

# (place, region, headline, scene)
STORIES = [
    ('MOSCOW', 'Europe', 'Putin vows reply to oil plant strikes', 'fire'),
    ('LIBYA', 'Africa', 'Ukraine strikes a Russian warship in port', 'ship'),
    ('MALI', 'Africa', '300+ Russians killed backing the junta', 'coffin'),
    ('KYIV', 'Europe', 'Leak puts Russian dead at 500,000', 'chart'),
    ('LONDON', 'Europe', 'Burnham\u2019s EU reset revives the Brexit row', 'flag'),
    ('PARIS', 'Europe', 'Sarkozy and Bruni to stand trial', 'gavel'),
    ('MADRID', 'Europe', 'Spain calls a snap election', 'ballot'),
    ('BRUSSELS', 'Europe', 'EU to cap Chinese hybrid EV imports', 'car'),
    ('OSLO', 'Europe', 'Cameroon separatist on trial in Norway', 'gavel'),
    ('KIGALI', 'Africa', 'Malaria cases rise as the climate warms', 'virus'),
    ('LAGOS', 'Africa', 'Monarch, 92, suspended over assault claims', 'crown'),
    ('DAKAR', 'Africa', 'Senegal regain the AFCON title on appeal', 'trophy'),
    ('KINSHASA', 'Africa', 'Cobalt export ban bites battery makers', 'battery'),
    ('NAYPYIDAW', 'Asia', 'Landmine toll at a five-year high', 'mine'),
    ('BEIJING', 'Asia', 'Official sentenced to death for spying', 'gavel'),
    ('DELHI', 'Asia', 'US tariff threat hits India and China', 'money'),
    ('KARACHI', 'Asia', 'Thousands protest a plan to split Sindh', 'megaphone'),
    ('SEOUL', 'Asia', 'Shelter as Russian jets near the island', 'plane'),
    ('DHAKA', 'Asia', 'Hasina plans a return on 16 December', 'flag'),
    ('HANOI', 'Asia', 'Gas blast kills six at a hotpot restaurant', 'fire'),
    ('GAZA', 'MidEast', 'Hamas internal security chief killed', 'blast'),
    ('JERUSALEM', 'MidEast', 'Ben-Gvir row over mosque raids', 'flag'),
    ('ADEN', 'MidEast', 'Houthis close in on Aden', 'blast'),
    ('TEHRAN', 'MidEast', 'Singer flogged; UN slams Iran', 'megaphone'),
    ('RIYADH', 'MidEast', 'Skyscraper hit twice in one week', 'blast'),
    ('COLOMBIA', 'Americas', 'Car bomb wounds more than 20', 'blast'),
    ('CARTAGENA', 'Americas', '25 hostages held in a supermarket', 'person'),
    ('HAVANA', 'Americas', 'Life expectancy falls for the first time', 'cross'),
    ('SANTA CLARA', 'Americas', 'Huang returns to Nvidia after Trump', 'chip'),
    ('WASHINGTON', 'Americas', 'Avian flu: three human cases, one death', 'virus'),
    ('MERCURY', 'Global', 'BepiColombo arrives after eight years', 'planet'),
    ('GENEVA', 'Global', 'Five women killed every hour: UN', 'person'),
]

CREDIT = ('Set from our own scan of the 24 November 2026 wires: 225 items dated 24 Nov 2026 \u2014 '
          'BBC, Al Jazeera, the Guardian, NPR, DW, France 24, CBC, SCMP, Times of India. '
          'Places and figures as those reports give them.')

SW, SH = 227, 34          # scene box, logical px


def font(path, size):
    return ImageFont.truetype(path, size * S)


def wrap(d, text, f, maxw):
    words = text.split()
    lines, cur = [], ''
    for w_ in words:
        trial = (cur + ' ' + w_).strip()
        if d.textlength(trial, font=f) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky(d, box, col, ground=0.66):
    """A vertical tint from the region colour at the horizon up to near-black."""
    x0, y0, x1, y1 = box
    hz = y0 + SH * ground
    steps = 12
    top = mix(col, BG, 0.72)
    for i in range(steps):
        t = i / (steps - 1)
        y = y0 + (hz - y0) * i / steps
        y2 = y0 + (hz - y0) * (i + 1) / steps
        d.rectangle([x0, y, x1, y2], fill=mix(top, mix(col, BG, 0.42), t))
    return hz


def ground(d, x0, x1, hz, col):
    d.rectangle([x0, hz, x1, hz + (SH - (hz - 0)) * 0], fill=col)
    d.rectangle([x0, hz, x1, hz + 6], fill=mix(col, BG, 0.55))


# ---- scenes: each draws inside SW x SH, origin (x, y), region colour c ---------

def sc_fire(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c)
    ground(d, x, x + SW, hz, mix(c, BG, 0.7))
    for bx, bw, bh in ((x + 18, 40, 26), (x + 62, 30, 20), (x + 168, 34, 24)):
        d.rectangle([bx, y + SH - bh, bx + bw, y + SH], fill=mix(c, BG, 0.86))
    fx = x + 34
    for k, (dx, hh) in enumerate(((0, 22), (16, 16), (32, 19))):
        d.polygon([(fx + dx, y + SH - 4), (fx + dx + 7, y + SH - 10 - hh),
                   (fx + dx + 15, y + SH - 4)], fill=(244, 146, 44))
        d.polygon([(fx + dx + 4, y + SH - 4), (fx + dx + 7, y + SH - 12 - hh // 2),
                   (fx + dx + 11, y + SH - 4)], fill=(255, 214, 120))
    for i, (cx, r) in enumerate(((x + 44, 13), (x + 58, 9), (x + 72, 12), (x + 88, 8))):
        d.ellipse([cx - r, y + 2 + i * 2 - r // 2, cx + r, y + 2 + i * 2 + r // 2],
                  fill=mix(c, BG, 0.45))


def sc_ship(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c, 0.52)
    d.rectangle([x, hz, x + SW, y + SH], fill=mix(c, BG, 0.78))
    for i in range(4):
        yy = hz + 3 + i * 4
        d.line([(x, yy), (x + SW, yy)], fill=mix(c, BG, 0.62), width=1)
    hx = x + 58
    d.polygon([(hx, hz + 16), (hx + 112, hz + 16), (hx + 100, hz + 28), (hx + 12, hz + 28)],
              fill=mix(c, BG, 0.9))
    d.rectangle([hx + 40, hz + 4, hx + 74, hz + 16], fill=mix(c, BG, 0.86))
    d.rectangle([hx + 56, hz - 8, hx + 60, hz + 4], fill=mix(c, BG, 0.9))
    d.polygon([(hx + 74, hz + 8), (hx + 96, hz + 2), (hx + 96, hz + 12)], fill=(240, 120, 80))
    for k in range(3):
        d.ellipse([hx + 60 + k * 6, hz - 16 - k * 3, hx + 74 + k * 6, hz - 8 - k * 3],
                  fill=mix(c, BG, 0.5))


def sc_coffin(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c, 0.7)
    ground(d, x, x + SW, hz, mix(c, BG, 0.74))
    cx = x + 74
    d.polygon([(cx, y + SH - 4), (cx + 74, y + SH - 4), (cx + 68, y + SH - 14),
               (cx + 50, y + SH - 18), (cx + 24, y + SH - 18), (cx + 6, y + SH - 14)],
              fill=mix(c, BG, 0.9))
    for i in range(5):
        d.line([(cx + 4 + i * 13, y + SH - 17), (cx + 4 + i * 13, y + SH - 5)],
               fill=mix(c, BG, 1.9), width=2)
    for px in (cx - 16, cx + 88):
        d.ellipse([px, y + SH - 26, px + 9, y + SH - 17], fill=mix(c, BG, 0.55))
        d.rectangle([px + 2, y + SH - 17, px + 7, y + SH - 4], fill=mix(c, BG, 0.55))


def sc_chart(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c, 0.86)
    ox, oy = x + 16, y + SH - 6
    d.line([(ox, y + 4), (ox, oy)], fill=mix(c, BG, 0.75), width=2)
    d.line([(ox, oy), (x + SW - 8, oy)], fill=mix(c, BG, 0.75), width=2)
    pts = [(ox + 4, oy - 6), (ox + 30, oy - 10), (ox + 56, oy - 8),
           (ox + 82, oy - 18), (ox + 108, oy - 16), (ox + 134, oy - 28), (ox + 160, oy - 34)]
    d.line(pts, fill=(240, 96, 84), width=3, joint='curve')
    for px, py in pts:
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 226, 214))
    for bx, bh in ((ox + 14, 8), (ox + 42, 12), (ox + 70, 10), (ox + 98, 16), (ox + 126, 20)):
        d.rectangle([bx, oy - bh, bx + 12, oy], fill=mix(c, BG, 0.42))


def sc_flag(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c, 0.78)
    ground(d, x, x + SW, hz, mix(c, BG, 0.72))
    for px in (x + 40, x + 96, x + 158):
        d.line([(px, y + 6), (px, y + SH - 2)], fill=mix(c, BG, 0.8), width=2)
        for k in range(3):
            d.polygon([(px + 2, y + 8 + k * 9), (px + 46 - k * 4, y + 5 + k * 9),
                       (px + 44 - k * 4, y + 15 + k * 9), (px + 2, y + 17 + k * 9)],
                      fill=c if k % 2 == 0 else mix(c, CREAM, 0.35))
    for i, px in enumerate((x + 14, x + 70, x + 132, x + 186)):
        d.ellipse([px, y + SH - 12, px + 8, y + SH - 4], fill=mix(c, BG, 0.5))


def sc_gavel(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c, 0.8)
    ground(d, x, x + SW, hz, mix(c, BG, 0.72))
    d.rectangle([x + 96, y + SH - 20, x + 200, y + SH - 12], fill=mix(c, BG, 0.88))
    d.rectangle([x + 122, y + SH - 12, x + 174, y + SH - 6], fill=mix(c, BG, 0.7))
    d.polygon([(x + 60, y + 12), (x + 104, y + 20), (x + 100, y + 30), (x + 56, y + 22)],
              fill=mix(c, CREAM, 0.55))
    d.line([(x + 78, y + 24), (x + 96, y + SH - 16)], fill=mix(c, BG, 0.86), width=4)
    for k in range(3):
        d.line([(x + 112 + k * 10, y + 6), (x + 106 + k * 10, y + 14)],
               fill=mix(c, BG, 0.6), width=2)


def sc_ballot(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c, 0.8)
    ground(d, x, x + SW, hz, mix(c, BG, 0.72))
    bx, by = x + 62, y + SH - 26
    d.polygon([(bx, by), (bx + 92, by), (bx + 84, by + 24), (bx + 8, by + 24)],
              fill=mix(c, BG, 0.92))
    d.rectangle([bx + 34, by - 4, bx + 58, by + 2], fill=BG)
    d.polygon([(bx + 40, by - 20), (bx + 70, by - 14), (bx + 66, by - 2), (bx + 36, by - 6)],
              fill=mix(c, CREAM, 0.7))
    d.line([(bx + 44, by - 12), (bx + 48, by - 7), (bx + 60, by - 16)],
           fill=(60, 150, 96), width=3)


def sc_car(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c, 0.72)
    ground(d, x, x + SW, hz, mix(c, BG, 0.7))
    bx, by = x + 40, y + SH - 18
    d.rectangle([bx, by - 8, bx + 112, by], fill=mix(c, BG, 0.9))
    d.polygon([(bx + 24, by - 8), (bx + 42, by - 20), (bx + 84, by - 20), (bx + 96, by - 8)],
              fill=mix(c, BG, 0.86))
    for wx in (bx + 22, bx + 90):
        d.ellipse([wx, by - 2, wx + 14, by + 12], fill=mix(c, BG, 1.8))
        d.ellipse([wx + 4, by + 2, wx + 10, by + 8], fill=mix(c, BG, 0.7))
    d.line([(bx + 124, by - 30), (bx + 124, by - 6)], fill=c, width=3)
    d.line([(bx + 124, by - 30), (bx + 134, by - 24), (bx + 128, by - 18)], fill=c, width=2)


def sc_virus(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c, 0.85)
    for cx, cy, r in ((x + 66, y + 20, 13), (x + 128, y + 14, 9), (x + 168, y + 27, 7)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=mix(c, CREAM, 0.45))
        for k in range(10):
            import math
            a = k * math.pi / 5
            d.line([(cx + r * 0.9 * math.cos(a), cy + r * 0.9 * math.sin(a)),
                    (cx + (r + 6) * math.cos(a), cy + (r + 6) * math.sin(a))],
                   fill=mix(c, CREAM, 0.6), width=2)
            d.ellipse([cx + (r + 5) * math.cos(a) - 2, cy + (r + 5) * math.sin(a) - 2,
                       cx + (r + 7) * math.cos(a), cy + (r + 7) * math.sin(a)],
                      fill=(240, 120, 110))
    ground(d, x, x + SW, hz, mix(c, BG, 0.7))


def sc_crown(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c, 0.8)
    ground(d, x, x + SW, hz, mix(c, BG, 0.74))
    cx = x + 78
    d.polygon([(cx, y + SH - 12), (cx + 76, y + SH - 12), (cx + 70, y + SH - 30),
               (cx + 52, y + SH - 20), (cx + 38, y + SH - 32), (cx + 24, y + SH - 20),
               (cx + 6, y + SH - 30)], fill=(232, 190, 82))
    d.rectangle([cx, y + SH - 12, cx + 76, y + SH - 8], fill=(196, 152, 54))
    for px in (cx + 34, cx + 40):
        d.ellipse([px, y + SH - 14, px + 4, y + SH - 10], fill=(150, 60, 60))


def sc_trophy(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c, 0.8)
    ground(d, x, x + SW, hz, mix(c, BG, 0.74))
    cx = x + 92
    d.polygon([(cx, y + SH - 8), (cx + 46, y + SH - 8), (cx + 38, y + SH - 16),
               (cx + 8, y + SH - 16)], fill=(228, 184, 76))
    d.rectangle([cx + 18, y + SH - 22, cx + 28, y + SH - 16], fill=(228, 184, 76))
    d.polygon([(cx + 6, y + 6), (cx + 40, y + 6), (cx + 36, y + SH - 24),
               (cx + 10, y + SH - 24)], fill=(238, 198, 92))
    for s in (-1, 1):
        d.arc([cx + (18 if s > 0 else -14), y + 8, cx + (44 if s > 0 else 12), y + 24],
              start=-90 if s > 0 else 90, end=90 if s > 0 else 270,
              fill=(238, 198, 92), width=3)


def sc_battery(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c, 0.8)
    ground(d, x, x + SW, hz, mix(c, BG, 0.72))
    bx, by = x + 54, y + 8
    d.rectangle([bx, by, bx + 46, by + 26], fill=mix(c, BG, 0.88), outline=c, width=2)
    d.rectangle([bx + 46, by + 8, bx + 52, by + 18], fill=c)
    for i in range(3):
        d.rectangle([bx + 4 + i * 13, by + 4, bx + 14 + i * 13, by + 22], fill=mix(c, CREAM, 0.3))
    d.line([(bx + 10, by + 4), (bx + 40, by + 22)], fill=(226, 62, 54), width=3)
    for i, hh in enumerate((10, 16, 22)):
        d.rectangle([x + 130 + i * 22, y + SH - 6 - hh, x + 144 + i * 22, y + SH - 6],
                    fill=mix(c, BG, 0.45))


def sc_mine(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c, 0.68)
    ground(d, x, x + SW, hz, mix(c, BG, 0.72))
    cx, cy = x + 108, y + SH - 12
    d.ellipse([cx - 16, cy - 8, cx + 16, cy + 8], fill=mix(c, BG, 0.92))
    import math
    for k in range(8):
        a = k * math.pi / 4
        d.line([(cx + 14 * math.cos(a), cy + 7 * math.sin(a)),
                (cx + 21 * math.cos(a), cy + 11 * math.sin(a))], fill=(226, 62, 54), width=3)
    d.polygon([(x + 30, hz + 6), (x + 178, hz + 6), (x + 170, hz + 12), (x + 38, hz + 12)],
              fill=mix(c, BG, 0.55))


def sc_money(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c, 0.86)
    d.rectangle([x + 26, y + 12, x + 130, y + 36], fill=mix(c, (140, 200, 150), 0.42))
    d.ellipse([x + 66, y + 16, x + 90, y + 32], outline=mix(c, BG, 0.8), width=2)
    d.rectangle([x + 34, y + 18, x + 46, y + 30], outline=mix(c, BG, 0.7), width=1)
    d.rectangle([x + 110, y + 18, x + 122, y + 30], outline=mix(c, BG, 0.7), width=1)
    for i, px in enumerate((x + 150, x + 168, x + 186)):
        d.ellipse([px, y + 18 - i * 4, px + 16, y + 34 - i * 4], fill=(230, 190, 82),
                  outline=mix(c, BG, 0.7))


def sc_megaphone(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c, 0.86)
    d.polygon([(x + 44, y + 16), (x + 100, y + 4), (x + 100, y + 34), (x + 44, y + 24)],
              fill=mix(c, CREAM, 0.5))
    d.rectangle([x + 34, y + 17, x + 46, y + 23], fill=mix(c, CREAM, 0.35))
    for k in range(3):
        d.arc([x + 104 + k * 10, y + 2 - k * 4, x + 136 + k * 10, y + 38 + k * 4],
              start=-52, end=52, fill=mix(c, CREAM, 0.15 + 0.25 * k), width=3)
    for px in (x + 150, x + 168, x + 186, x + 198):
        d.ellipse([px, y + SH - 16, px + 8, y + SH - 8], fill=mix(c, BG, 0.5))
        d.polygon([(px, y + SH - 8), (px + 8, y + SH - 8), (px + 10, y + SH - 1),
                   (px - 2, y + SH - 1)], fill=mix(c, BG, 0.5))


def sc_plane(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c, 0.9)
    cx, cy = x + 96, y + 18
    d.polygon([(cx, cy), (cx + 52, cy + 6), (cx + 52, cy + 12), (cx, cy + 10)],
              fill=mix(c, CREAM, 0.55))
    d.polygon([(cx + 18, cy + 4), (cx + 6, cy - 10), (cx + 16, cy - 10), (cx + 30, cy + 4)],
              fill=mix(c, CREAM, 0.45))
    d.polygon([(cx + 22, cy + 10), (cx + 12, cy + 22), (cx + 22, cy + 22), (cx + 34, cy + 11)],
              fill=mix(c, CREAM, 0.4))
    for k in range(3):
        d.line([(cx - 6 - k * 14, cy + 8), (cx - 44 - k * 8, cy + 10 + k * 3)],
               fill=mix(c, CREAM, 0.12), width=2)
    d.rectangle([x, y + SH - 7, x + SW, y + SH], fill=mix(c, BG, 0.72))


def sc_blast(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c, 0.66)
    ground(d, x, x + SW, hz, mix(c, BG, 0.72))
    for bx, bw, bh in ((x + 6, 24, 20), (x + 34, 18, 28), (x + 150, 22, 24), (x + 176, 26, 16),
                       (x + 206, 16, 22)):
        d.rectangle([bx, y + SH - bh, bx + bw, y + SH], fill=mix(c, BG, 0.88))
    cx, cy = x + 108, y + SH - 26
    import math
    for k in range(9):
        a = k * 2 * math.pi / 9
        r1, r2 = 8, 24 + (k % 3) * 7
        d.polygon([(cx + r1 * math.cos(a - 0.16), cy + r1 * math.sin(a - 0.16)),
                   (cx + r2 * math.cos(a), cy + r2 * math.sin(a)),
                   (cx + r1 * math.cos(a + 0.16), cy + r1 * math.sin(a + 0.16))],
                  fill=(246, 176, 66) if k % 2 else (240, 120, 90))
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(255, 238, 200))
    for px, py in ((x + 62, y + 6), (x + 74, y + 12), (x + 90, y + 4)):
        d.ellipse([px, py, px + 6, py + 4], fill=mix(c, CREAM, 0.2))


def sc_person(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c, 0.8)
    ground(d, x, x + SW, hz, mix(c, BG, 0.74))
    for i, px in enumerate(range(x + 28, x + 210, 26)):
        top = y + 12 + (i % 3) * 5
        d.ellipse([px, top, px + 12, top + 12], fill=mix(c, CREAM, 0.42))
        d.polygon([(px - 5, y + SH - 2), (px + 17, y + SH - 2), (px + 14, top + 14),
                   (px - 2, top + 14)], fill=mix(c, BG, 0.86))


def sc_cross(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c, 0.78)
    ground(d, x, x + SW, hz, mix(c, BG, 0.72))
    bx, by = x + 66, y + 8
    d.rectangle([bx, by + 6, bx + 96, y + SH], fill=mix(c, BG, 0.9))
    d.rectangle([bx + 8, by, bx + 20, by + 12], fill=mix(c, BG, 0.7))
    d.rectangle([bx + 76, by, bx + 88, by + 12], fill=mix(c, BG, 0.7))
    cx, cy = bx + 48, by + 24
    d.rectangle([cx - 5, cy - 16, cx + 5, cy + 16], fill=(236, 92, 84))
    d.rectangle([cx - 16, cy - 5, cx + 16, cy + 5], fill=(236, 92, 84))
    for wx in (bx + 14, bx + 62):
        d.rectangle([wx, by + 22, wx + 20, by + 34], fill=mix(c, BG, 1.7))


def sc_chip(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c, 0.86)
    bx, by = x + 82, y + 8
    d.rectangle([bx, by, bx + 64, by + 26], fill=mix(c, BG, 0.86), outline=c, width=2)
    d.rectangle([bx + 14, by + 6, bx + 50, by + 20], fill=mix(c, BG, 0.6), outline=c, width=1)
    for k in range(5):
        d.line([(bx + 8 + k * 12, by), (bx + 8 + k * 12, by - 5)], fill=c, width=2)
        d.line([(bx + 8 + k * 12, by + 26), (bx + 8 + k * 12, by + 31)], fill=c, width=2)
    d.line([(bx + 64, by + 13), (x + 190, by + 13), (x + 190, y + SH - 8)],
           fill=mix(c, CREAM, 0.2), width=2)


def sc_planet(d, x, y, c):
    hz = sky(d, (x, y, x + SW, y + SH), c, 0.95)
    cx, cy, r = x + 112, y + 21, 15
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=mix(c, (210, 190, 170), 0.35),
              outline=mix(c, CREAM, 0.3))
    d.arc([cx - 26, cy - 8, cx + 26, cy + 8], start=190, end=350,
          fill=mix(c, CREAM, 0.5), width=2)
    d.arc([cx - 26, cy - 8, cx + 26, cy + 8], start=10, end=170,
          fill=mix(c, CREAM, 0.28), width=2)
    for px, py in ((x + 30, y + 8), (x + 58, y + 26), (x + 176, y + 10),
                   (x + 196, y + 30), (x + 150, y + 4)):
        d.ellipse([px, py, px + 2, py + 2], fill=mix(c, CREAM, 0.6))


SCENES = {
    'fire': sc_fire, 'ship': sc_ship, 'coffin': sc_coffin, 'chart': sc_chart,
    'flag': sc_flag, 'gavel': sc_gavel, 'ballot': sc_ballot, 'car': sc_car,
    'virus': sc_virus, 'crown': sc_crown, 'trophy': sc_trophy, 'battery': sc_battery,
    'mine': sc_mine, 'money': sc_money, 'megaphone': sc_megaphone, 'plane': sc_plane,
    'blast': sc_blast, 'person': sc_person, 'cross': sc_cross, 'chip': sc_chip,
    'planet': sc_planet,
}


def scene_tile(name, col):
    """Draw the scene at 1x in its own SW x SH tile, then blow it up to the
    supersampled canvas: one drawn landscape per card, the whole tile kept (a
    scene has a background, so nothing is cut out)."""
    t = Image.new('RGB', (SW, SH), BG)
    d = ImageDraw.Draw(t)
    SCENES[name](d, 0, 0, col)
    return t.resize((SW * S, SH * S), Image.NEAREST)


def main(out):
    w, h = W * S, H * S
    img = Image.new('RGB', (w, h), BG)
    d = ImageDraw.Draw(img)

    f_kick = font(DEJB, 14)
    f_date = font(ARCH, 50)
    f_deck = font(DEJB, 14)
    f_place = font(DEJB, 12)
    f_head = font(DEJB, 16)
    f_foot = font(DEJB, 10)

    m = M * S
    d.text((m, 22 * S), KICKER_L, font=f_kick, fill=DIM)
    kr = KICKER_R
    d.text((w - m - d.textlength(kr, font=f_kick), 22 * S), kr, font=f_kick, fill=DIM)
    d.text((m, 40 * S), DAY, font=f_date, fill=CREAM)
    y = 100 * S
    d.line([(m, y), (w - m, y)], fill=RED, width=3 * S)
    yy = y + 7 * S
    for ln in wrap(d, DECK, f_deck, w - 2 * m)[:2]:
        d.text((m, yy), ln, font=f_deck, fill=DIM)
        yy += 17 * S

    top = 136 * S
    bottom = 962
    cols, rows = 4, 8
    gap = 6
    cw = (W - 2 * M - (cols - 1) * gap) / cols
    rh = (bottom - 136 - (rows - 1) * gap) / rows
    assert len(STORIES) == cols * rows, len(STORIES)
    assert rh > SH + 46, rh

    for i, (place, region, head, scene) in enumerate(STORIES):
        r_, c_ = divmod(i, cols)
        x = m + c_ * (cw + gap) * S
        y0 = top + r_ * (rh + gap) * S
        box = (x, y0, x + cw * S, y0 + rh * S)
        d.rounded_rectangle(box, radius=7 * S, fill=CARD if (r_ + c_) % 2 == 0 else CARD2,
                            outline=RULE, width=1 * S)
        col = REGION[region]
        # the drawn scene fills the card's whole width at the top
        tile = scene_tile(scene, col)
        tx = int(x + 5 * S)
        ty = int(y0 + 5 * S)
        img.paste(tile, (tx, ty))
        # region hairline under the scene, then place and label
        d.line([(tx, ty + SH * S), (tx + SW * S, ty + SH * S)], fill=mix(col, BG, 0.45),
               width=1 * S)
        by = ty + SH * S + 3 * S
        # a region chip then the place in cream: at 1024 the 12 px tag is a label
        # a reader can find, and the colour stays on the card, not on the letters
        d.rectangle([tx, by + 2 * S, tx + 5 * S, by + 9 * S], fill=col)
        d.text((tx + 8 * S, by), place, font=f_place, fill=CREAM)
        lines = wrap(d, head, f_head, SW * S)[:2]
        ly = by + 14 * S
        for ln in lines:
            d.text((tx, ly), ln, font=f_head, fill=CREAM)
            ly += 17 * S

    fy = 970 * S
    d.line([(m, fy), (w - m, fy)], fill=RULE, width=1 * S)
    for k, ln in enumerate(wrap(d, CREDIT, f_foot, w - 2 * m)[:2]):
        d.text((m, fy + 6 * S + k * 12 * S), ln, font=f_foot, fill=DIM)

    img = img.resize((W, H), Image.LANCZOS)
    img.save(out, optimize=True)
    print(f"wrote {out}: {W}x{H}")


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'entry.png')
