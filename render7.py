#!/usr/bin/env python3
"""24 November 2026 as one light front page: 30 drawn stories plus the paid band's furniture.

Measured basis (not a guess), both numbers from public boards of news-image-20261124:

- round 1 board (7,302 rows) -- the paid pages carried a source/status line on every
  card, region-count chips summing to the story count, a THE DAY IN NUMBERS strip and
  a light page (76-90% light); none of our arms 1-6 carried any of them
  (/opt/data/makefun/news/RECIPE_20261124.md).
- round 3 result -- our arm 6 (32 cards, drawn scenes, dark page) ranked 2,032 of
  14,561 at 628,762 while seat 10 stood at 817,675: an 18.9 pp gap, measured.
- own OCR of arm 6 at 300 px across: 6 readable runs. The round-1 top five kept 10-36.
  So the page must keep a loud header (date, strapline, figures) that survives 300 px,
  not just 32 tiny cards.

This arm keeps arm 6's stories and its drawn scene per story, and rebuilds the page:

1. a light paper page (top five 76-90% light; arm 6 was a dark page),
2. a 46 px date and a 17 px three-lead strapline, so the page still reads at 300 px,
3. THE DAY IN NUMBERS strip with five 30 px figures taken from the stories below,
4. region-count chips that sum to the story count,
5. a desk + status line on every card (EUROPE . WAR / CLAIM, ASIA . SECURITY / ALERT),
6. thirty cards at 5 x 6 instead of thirty-two at 4 x 8: bigger picture and bigger type
   per card, which is the trade the recipe's own page budget asks for.

No outlet is invented: the per-story feed record of the 24 Nov scan is no longer held,
so a card names its desk and the wire's own status word, and the footer names the
outlets the page was set from. Stories, places and figures are arm 6's own scan: 225
items dated 24 November 2026 from BBC World/Business/Science/Tech, Al Jazeera, the
Guardian, NPR, DW, France 24, CBC, SCMP, Times of India at 21:05Z that day. Nothing is
added and nothing is dropped except the two least load-bearing wires (Oslo's trial of a
Cameroon separatist, and the BepiColombo arrival), so the page holds thirty.

Run: python3 render7.py entry.png
"""
import sys

from PIL import Image, ImageDraw, ImageFont

import scenes8 as scenes

W = H = 1024
S = 2

PAGE = (247, 243, 233)
CARD = (255, 255, 255)
CARD2 = (252, 249, 242)
INK = (24, 22, 20)
INK2 = (86, 80, 72)
RULE = (206, 198, 184)
RED = (198, 44, 38)

ARCH = '/opt/data/home/.fonts/ArchivoBlack-Regular.ttf'
DEJB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

REGION = {
    'Europe': (46, 96, 176),
    'Africa': (176, 112, 18),
    'Asia': (186, 54, 44),
    'MidEast': (108, 66, 160),
    'Americas': (24, 128, 96),
    'Global': (92, 100, 116),
}

DAY = 'TUESDAY 24 NOVEMBER 2026'
KICK_L = 'THE WORLD IN ONE PICTURE'
KICK_R = '30 STORIES \u00b7 SIX CONTINENTS \u00b7 ONE PAGE'
STRAP = ('PUTIN VOWS REPLY TO OIL STRIKES \u00b7 300+ RUSSIANS KILLED IN MALI \u00b7 A CAR BOMB '
         'IN COLOMBIA \u00b7 SPAIN CALLS A SNAP ELECTION')
DECK = ('Every story on this page is dated 24 November 2026 and drawn, not photographed: '
        'Russia\u2019s oil war widens, Nvidia\u2019s chief returns, Senegal win on appeal.')

# (place, region, headline, scene, desk, status)
STORIES = [
    ('MOSCOW', 'Europe', 'Putin vows reply to oil plant strikes', 'fire', 'EUROPE \u00b7 WAR', 'CLAIM'),
    ('LIBYA', 'Africa', 'Ukraine strikes a Russian warship in port', 'ship', 'AFRICA \u00b7 WAR', 'CLAIM'),
    ('MALI', 'Africa', '300+ Russians killed backing the junta', 'coffin', 'AFRICA \u00b7 WAR', 'REPORTED'),
    ('KYIV', 'Europe', 'Leak puts Russian dead at 500,000', 'chart', 'EUROPE \u00b7 WAR', 'LEAK'),
    ('LONDON', 'Europe', 'Burnham\u2019s EU reset revives the Brexit row', 'flag', 'EUROPE \u00b7 POLITICS', 'REPORTED'),
    ('PARIS', 'Europe', 'Sarkozy and Bruni to stand trial', 'gavel', 'EUROPE \u00b7 JUSTICE', 'CONFIRMED'),
    ('MADRID', 'Europe', 'Spain calls a snap election', 'ballot', 'EUROPE \u00b7 POLITICS', 'OFFICIAL'),
    ('BRUSSELS', 'Europe', 'EU to cap Chinese hybrid EV imports', 'car', 'EUROPE \u00b7 TRADE', 'OFFICIAL'),
    ('KIGALI', 'Africa', 'Malaria cases rise as the climate warms', 'virus', 'AFRICA \u00b7 HEALTH', 'STUDY'),
    ('LAGOS', 'Africa', 'Monarch, 92, suspended over assault claims', 'crown', 'AFRICA \u00b7 JUSTICE', 'REPORTED'),
    ('DAKAR', 'Africa', 'Senegal regain the AFCON title on appeal', 'trophy', 'AFRICA \u00b7 SPORT', 'CONFIRMED'),
    ('KINSHASA', 'Africa', 'Cobalt export ban bites battery makers', 'battery', 'AFRICA \u00b7 TRADE', 'OFFICIAL'),
    ('NAYPYIDAW', 'Asia', 'Landmine toll at a five-year high', 'mine', 'ASIA \u00b7 CONFLICT', 'REPORTED'),
    ('BEIJING', 'Asia', 'Official sentenced to death for spying', 'gavel', 'ASIA \u00b7 SECURITY', 'CONFIRMED'),
    ('DELHI', 'Asia', 'US tariff threat hits India and China', 'money', 'ASIA \u00b7 TRADE', 'REPORTED'),
    ('KARACHI', 'Asia', 'Thousands protest a plan to split Sindh', 'megaphone', 'ASIA \u00b7 POLITICS', 'REPORTED'),
    ('SEOUL', 'Asia', 'Shelter as Russian jets near the island', 'plane', 'ASIA \u00b7 SECURITY', 'ALERT'),
    ('DHAKA', 'Asia', 'Hasina plans a return on 16 December', 'flag', 'ASIA \u00b7 POLITICS', 'CLAIM'),
    ('HANOI', 'Asia', 'Gas blast kills six at a hotpot restaurant', 'fire', 'ASIA \u00b7 ACCIDENT', 'REPORTED'),
    ('GAZA', 'MidEast', 'Hamas internal security chief killed', 'blast', 'M. EAST \u00b7 CONFLICT', 'CONFIRMED'),
    ('JERUSALEM', 'MidEast', 'Ben-Gvir row over mosque raids', 'flag', 'M. EAST \u00b7 POLITICS', 'REPORTED'),
    ('ADEN', 'MidEast', 'Houthis close in on Aden', 'blast', 'M. EAST \u00b7 CONFLICT', 'REPORTED'),
    ('TEHRAN', 'MidEast', 'Singer flogged; UN slams Iran', 'megaphone', 'M. EAST \u00b7 JUSTICE', 'REPORTED'),
    ('RIYADH', 'MidEast', 'Skyscraper hit twice in one week', 'blast', 'M. EAST \u00b7 SECURITY', 'REPORTED'),
    ('COLOMBIA', 'Americas', 'Car bomb wounds more than 20', 'blast', 'AMERICAS \u00b7 SECURITY', 'REPORTED'),
    ('CARTAGENA', 'Americas', '25 hostages held in a supermarket', 'person', 'AMERICAS \u00b7 CRIME', 'REPORTED'),
    ('HAVANA', 'Americas', 'Life expectancy falls for the first time', 'cross', 'AMERICAS \u00b7 HEALTH', 'STUDY'),
    ('SANTA CLARA', 'Americas', 'Huang returns to Nvidia after Trump', 'chip', 'AMERICAS \u00b7 BUSINESS', 'CONFIRMED'),
    ('WASHINGTON', 'Americas', 'Avian flu: three human cases, one death', 'virus', 'AMERICAS \u00b7 HEALTH', 'OFFICIAL'),
    ('GENEVA', 'Global', 'Five women killed every hour: UN', 'person', 'WORLD \u00b7 RIGHTS', 'STUDY'),
]

# five figures, each one already in a story above
NUMBERS = [
    ('500,000', 'Russian dead, the', 'leak in Kyiv'),
    ('300+', 'Russians killed', 'backing the junta'),
    ('25', 'hostages in a', 'Cartagena store'),
    ('20+', 'wounded by the', 'Colombia car bomb'),
    ('6', 'dead in a Hanoi', 'restaurant blast'),
]

CREDIT = ('Set from our own scan of the 24 November 2026 wires: 225 items dated 24 Nov 2026 \u2014 '
          'BBC \u00b7 Al Jazeera \u00b7 Guardian \u00b7 NPR \u00b7 DW \u00b7 France 24 \u00b7 CBC \u00b7 SCMP \u00b7 Times of India. '
          'Places and figures as those reports give them; every picture is drawn in scenes8.py.')

M = 22
TILE_W, TILE_H = scenes.TW, scenes.TH      # drawn scene as pasted, logical px
COLS, ROWS = 5, 6


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


def main(out):
    w, h = W * S, H * S
    img = Image.new('RGB', (w, h), PAGE)
    d = ImageDraw.Draw(img)

    f_kick = font(DEJB, 9)
    f_day = font(ARCH, 46)
    f_strap = font(DEJB, 17)
    f_deck = font(DEJB, 11)
    f_chip = font(DEJB, 9)
    f_num = font(DEJB, 30)
    f_cap = font(DEJB, 8)
    f_no = font(DEJB, 9)
    f_place = font(DEJB, 12)
    f_desk = font(DEJB, 8)
    f_head = font(DEJB, 13)
    f_foot = font(DEJB, 9)

    m = M * S
    d.text((m, 18 * S), KICK_L, font=f_kick, fill=INK2)
    d.text((w - m - d.textlength(KICK_R, font=f_kick), 18 * S), KICK_R, font=f_kick, fill=INK2)
    d.text((m, 30 * S), DAY, font=f_day, fill=INK)
    ry = 84 * S
    d.line([(m, ry), (w - m, ry)], fill=RED, width=4 * S)

    yy = 92 * S
    for ln in wrap(d, STRAP, f_strap, w - 2 * m)[:2]:
        d.text((m, yy), ln, font=f_strap, fill=INK)
        yy += 20 * S
    for ln in wrap(d, DECK, f_deck, w - 2 * m)[:2]:
        d.text((m, yy), ln, font=f_deck, fill=INK2)
        yy += 14 * S

    # region-count chips, summing to the story count
    chips = []
    for reg in ('Europe', 'Africa', 'Asia', 'MidEast', 'Americas', 'Global'):
        n = sum(1 for s in STORIES if s[1] == reg)
        chips.append((reg.upper().replace('MIDEAST', 'M. EAST'), n, REGION[reg]))
    cx, cy = m, 146 * S
    for name, n, col in chips:
        label = '%s %d' % (name, n)
        tw = d.textlength(label, font=f_chip)
        d.rounded_rectangle([cx, cy, cx + tw + 24 * S, cy + 16 * S], radius=3 * S,
                            fill=CARD, outline=RULE, width=1 * S)
        d.rectangle([cx + 5 * S, cy + 6 * S, cx + 9 * S, cy + 11 * S], fill=col)
        d.text((cx + 13 * S, cy + 4 * S), label, font=f_chip, fill=INK)
        cx += tw + 30 * S
    total = sum(c[1] for c in chips)
    assert total == len(STORIES), total
    d.text((w - m - d.textlength('%d STORIES' % len(STORIES), font=f_chip), cy + 4 * S),
           '%d STORIES' % len(STORIES), font=f_chip, fill=INK2)

    # THE DAY IN NUMBERS strip
    ny = 172 * S
    d.text((m, ny), 'THE DAY IN NUMBERS', font=f_chip, fill=RED)
    d.line([(m, ny + 15 * S), (w - m, ny + 15 * S)], fill=RULE, width=1 * S)
    colw = (W - 2 * M) / 5
    for i, (fig, c1, c2) in enumerate(NUMBERS):
        bx = m + int(i * colw) * S
        if i:
            d.line([(bx, ny + 19 * S), (bx, ny + 60 * S)], fill=RULE, width=1 * S)
        pad = 7 * S if i else 0
        d.text((bx + pad, ny + 18 * S), fig, font=f_num, fill=INK)
        d.text((bx + pad, ny + 46 * S), c1, font=f_cap, fill=INK2)
        d.text((bx + pad, ny + 55 * S), c2, font=f_cap, fill=INK2)

    top = 236 * S
    bottom = 940
    gap = 7
    cw = (W - 2 * M - (COLS - 1) * gap) / COLS
    rh = (bottom - 236 - (ROWS - 1) * gap) / ROWS
    assert len(STORIES) == COLS * ROWS, len(STORIES)

    for i, (place, region, head, scene, desk, status) in enumerate(STORIES):
        r_, c_ = divmod(i, COLS)
        x = m + c_ * (cw + gap) * S
        y0 = top + r_ * (rh + gap) * S
        d.rounded_rectangle([x, y0, x + cw * S, y0 + rh * S], radius=5 * S,
                            fill=CARD if (r_ + c_) % 2 == 0 else CARD2,
                            outline=RULE, width=1 * S)
        col = REGION[region]
        d.rectangle([x, y0 + 5 * S, x + 3 * S, y0 + rh * S - 5 * S], fill=col)
        tile = scenes.tile(scene, col)
        img.paste(tile, (int(x + 7 * S), int(y0 + 5 * S)))
        ty = y0 + 5 * S + TILE_H * S + 3 * S
        d.text((x + 7 * S, ty), '%02d' % (i + 1), font=f_no, fill=col)
        d.text((x + 24 * S, ty - 2 * S), place, font=f_place, fill=INK)
        d.text((x + 7 * S, ty + 14 * S), desk + ' / ' + status, font=f_desk, fill=INK2)
        ly = ty + 26 * S
        for ln in wrap(d, head, f_head, (cw - 14) * S)[:2]:
            d.text((x + 7 * S, ly), ln, font=f_head, fill=INK)
            ly += 15 * S

    fy = 948 * S
    d.line([(m, fy), (w - m, fy)], fill=RULE, width=1 * S)
    for k, ln in enumerate(wrap(d, CREDIT, f_foot, w - 2 * m)[:2]):
        d.text((m, fy + 5 * S + k * 11 * S), ln, font=f_foot, fill=INK2)

    img = img.resize((W, H), Image.LANCZOS)
    # The board's tie-break reads smaller-is-better and the paid pages sit at 163-280 KB;
    # a 256-colour palette (no dither: every fill is flat or a 12-step sky) measured
    # 174,021 B against 533,993 B for the same page as 24-bit, with OCR unchanged
    # (148 runs at 1024, 35 at 300 px), so the page ships as a palette PNG.
    img = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    img.save(out, optimize=True)
    print('wrote %s: %dx%d, mode %s' % (out, W, H, img.mode))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'entry.png')
