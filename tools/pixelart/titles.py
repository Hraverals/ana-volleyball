"""Title, logo and menu textures for the ANA remake.

Each texture keeps the name and size of the original one it replaces, so the
layout code does not change:

- messages/{ja,ko}/mark.png              88x110  intro emblem
- messages/{ja,ko}/pokemon.png           200x32  subtitle over the logo
- messages/{ja,ko}/pikachu_volleyball.png 276x79 game logo
- messages/{ja,ko}/fight.png             160x160 burst on the menu
- messages/{ja,ko}/with_computer.png, with_friend.png 120x20 menu options
  (the Korean ones keep their words, redrawn to read on the menu tiles)
- messages/ja/game_start.png             96x24   "GAME START!" (the original
  is Japanese; the Korean one stays)
- messages/common/sachisoft.png          360x20  credit line; the original
  credit stays and "ANA REMAKE" is added
- sitting_pikachu.png and menu/tile_{id}.png 104x104 menu background tiles

The ja textures are also used by the English and Chinese pages, so their text
is English. Text is rasterized without anti-aliasing from fonts that ship
with Windows; set ANA_FONT_DIR to use another font folder.
"""

import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from characters import PALETTES, Pose, build_frame
from pixelkit import Canvas, Part, hex_rgb

FONT_DIR = os.environ.get('ANA_FONT_DIR', r'C:\Windows\Fonts')
FONT_LATIN = 'ariblk.ttf'      # Arial Black
FONT_LATIN_SMALL = 'arialbd.ttf'
FONT_KOREAN = 'malgunbd.ttf'   # Malgun Gothic Bold

YELLOW = ['#7a4a00', '#d99a00', '#f2bd12', '#ffd84a', '#fff1a8']
CORAL = ['#6e1b1f', '#b8343a', '#d94a48', '#f06a5f', '#ffaaa0']
SHADOW = (20, 18, 28, 255)


def _font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def _ramp(character_id):
    """Five-step ramp (outline .. light) from a character palette."""
    p = PALETTES[character_id]
    s, b = np.array(hex_rgb(p['s'])), np.array(hex_rgb(p['b']))
    mid = tuple(int(v) for v in (s + b) / 2)
    return [hex_rgb(p['O']), hex_rgb(p['s']), mid, hex_rgb(p['b']),
            hex_rgb(p['l'])]


def _hex_ramp(hexes):
    return [hex_rgb(h) for h in hexes]


def _text_mask(text, font):
    """1-bit mask of text, cropped to its pixels."""
    l, t, r, b = font.getbbox(text)
    img = Image.new('L', (r - l + 4, b - t + 4), 0)
    draw = ImageDraw.Draw(img)
    draw.fontmode = '1'
    draw.text((2 - l, 2 - t), text, font=font, fill=255)
    mask = np.array(img) > 127
    ys, xs = np.nonzero(mask)
    return mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def _fit_font(text, name, max_w, max_h, start=80):
    for size in range(start, 6, -1):
        mask = _text_mask(text, _font(name, size))
        if mask.shape[1] <= max_w and mask.shape[0] <= max_h:
            return mask
    raise ValueError(f'{text!r} does not fit in {max_w}x{max_h}')


def _dilate(mask, r=1):
    out = mask.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                out |= np.roll(np.roll(mask, dy, 0), dx, 1)
    return out


class Board(Canvas):
    """RGBA canvas with helpers for jelly text and shapes."""

    def place(self, mask, x, y):
        """A full-size mask with `mask` placed at (x, y)."""
        full = np.zeros((self.h, self.w), dtype=bool)
        mh, mw = mask.shape
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + mw, self.w), min(y + mh, self.h)
        full[y0:y1, x0:x1] = mask[y0 - y:y1 - y, x0 - x:x1 - x]
        return full

    def shadow(self, full, dx=2, dy=2, color=SHADOW):
        sh = np.roll(np.roll(_dilate(full), dy, 0), dx, 1)
        self.px[sh] = color

    def jelly(self, full, ramp, radius=3.0):
        """Shaded, outlined jelly fill with a white glint at the upper left."""
        Part(_dilate(full), ramp, radius=radius).draw(self)

    def glints(self, full, n=2):
        """White pixels in the top-left corner of each blob of `full`."""
        ys, xs = np.nonzero(full)
        if not len(xs):
            return
        order = np.argsort(xs + ys)
        for k in order[:n]:
            y, x = ys[k] + 1, xs[k] + 1
            if 0 <= y < self.h and 0 <= x < self.w and full[y, x]:
                self.px[y, x] = (255, 255, 255, 255)



def _letters_runs(runs, name, max_w, max_h, gap=2):
    """Render runs [(text, ramp), ...] side by side at one font size that
    fits max_w x max_h. Returns [(mask, ramp)] and the total size."""
    for size in range(90, 6, -1):
        font = _font(name if not isinstance(name, list) else name[0], size)
        masks = []
        for text, ramp, font_name in runs:
            f = _font(font_name, size) if font_name else font
            masks.append((_text_mask(text, f), ramp))
        w = sum(m.shape[1] for m, _ in masks) + gap * (len(masks) - 1)
        h = max(m.shape[0] for m, _ in masks)
        if w <= max_w - 6 and h <= max_h - 6:
            return masks, w, h
    raise ValueError('runs do not fit')


def logo(lang):
    """Big jelly 'ANA' in the three character colors, then 'VOLLEY'
    (ja/en/zh) or '배구' (ko) smaller and bottom-aligned, 276x79."""
    W, H = 276, 79
    b = Board(W, H)
    word, word_font = (('VOLLEY', FONT_LATIN) if lang == 'ja'
                       else ('배구', FONT_KOREAN))
    ramps = [_ramp('a_teal'), _ramp('n_blue'), _ramp('a_red')]
    for size in range(80, 10, -1):
        letters = [_text_mask(c, _font(FONT_LATIN, size)) for c in 'ANA']
        word_mask = _text_mask(word, _font(word_font, int(size * 0.62)))
        gap, space = 2, 8
        w = (sum(m.shape[1] for m in letters) + gap * 2 + space
             + word_mask.shape[1])
        h = max(m.shape[0] for m in letters)
        if w <= W - 10 and h <= H - 10:
            break
    x = (W - w) // 2 - 2
    base = (H + h) // 2 - 2  # common baseline (bottom of the letters)
    parts = []
    for m, ramp in zip(letters, ramps):
        parts.append((b.place(m, x, base - m.shape[0]), ramp))
        x += m.shape[1] + gap
    x += space - gap
    parts.append((b.place(word_mask, x, base - word_mask.shape[0]),
                  _hex_ramp(YELLOW)))
    allm = np.zeros((H, W), dtype=bool)
    for f, _ in parts:
        allm |= f
    b.shadow(allm, 3, 3)
    for f, ramp in parts:
        b.jelly(f, ramp, radius=4.0)
        b.glints(f, 2)
    return b.image()


def subtitle(lang):
    """Small subtitle above the logo, 200x32."""
    b = Board(200, 32)
    text, font = (('CNU ANA', FONT_LATIN) if lang == 'ja'
                  else ('충남대 ANA', FONT_KOREAN))
    m = _fit_font(text, font, 190, 24)
    full = b.place(m, (200 - m.shape[1]) // 2, (32 - m.shape[0]) // 2)
    b.shadow(full, 2, 2)
    b.jelly(full, _ramp('a_teal'), radius=2.0)
    return b.image()


def burst(lang):
    """A jelly burst with 'VS!' or '대결!', 160x160."""
    b = Board(160, 160)
    ys, xs = np.mgrid[0:160, 0:160]
    ang = np.arctan2(ys + 0.5 - 76, xs + 0.5 - 76)
    rad = np.hypot(ys + 0.5 - 76, xs + 0.5 - 76)
    spikes = 13
    t = (ang / (2 * np.pi) * spikes) % 1.0
    edge = 52 + 18 * np.abs(1 - 2 * t)  # star outline radius
    star = rad <= edge
    b.shadow(star, 6, 6)
    b.jelly(star, _hex_ramp(CORAL), radius=10.0)
    text, font = (('VS!', FONT_LATIN) if lang == 'ja'
                  else ('대결!', FONT_KOREAN))
    m = _fit_font(text, font, 92, 52)
    full = b.place(m, 76 - m.shape[1] // 2, 76 - m.shape[0] // 2)
    b.shadow(full, 2, 2)
    b.jelly(full, _hex_ramp(YELLOW), radius=3.0)
    b.glints(full, 2)
    return b.image()


def mark():
    """Intro emblem: a_teal over jelly 'ANA' on a dark card, 88x110."""
    b = Board(88, 110)
    card = b.place(np.ones((106, 84), dtype=bool), 2, 2)
    b.px[_dilate(card)] = (*hex_rgb('#3a3d48'), 255)
    b.px[card] = (*hex_rgb('#262833'), 255)
    ch = np.array(build_frame('a_teal', Pose()))
    char = ch[6:63, 15:49]  # the 34x57 drawing
    y0 = 6
    region = b.px[y0:y0 + 57, 27:61]
    a = char[..., 3] > 0
    region[a] = char[a]
    runs = [('A', _ramp('a_teal'), FONT_LATIN),
            ('N', _ramp('n_blue'), FONT_LATIN),
            ('A', _ramp('a_red'), FONT_LATIN)]
    masks, w, h = _letters_runs(runs, FONT_LATIN, 80, 38, gap=1)
    x = (88 - w) // 2
    for m, ramp in masks:
        full = b.place(m, x, 104 - m.shape[0])
        b.shadow(full, 1, 2)
        b.jelly(full, ramp, radius=3.0)
        b.glints(full, 1)
        x += m.shape[1] + 1
    return b.image()


def with_who(text, size, font=FONT_LATIN):
    """Menu option in the original style: yellow fill, red edge, white rim."""
    b = Board(120, 20)
    m = _text_mask(text, _font(font, size))
    full = b.place(m, (120 - m.shape[1]) // 2, (20 - m.shape[0]) // 2)
    b.px[_dilate(full, 2)] = (255, 255, 255, 255)
    b.px[_dilate(full, 1)] = (220, 20, 20, 255)
    b.px[full] = (255, 224, 0, 255)
    return b.image()


def game_start():
    """Round start message in the original style: red letters with a dark
    rim and a drop shadow, 96x24."""
    b = Board(96, 24)
    m = _fit_font('GAME START!', FONT_LATIN, 90, 16)
    full = b.place(m, (96 - m.shape[1]) // 2 - 1, (24 - m.shape[0]) // 2 - 1)
    b.px[np.roll(np.roll(_dilate(full), 2, 0), 2, 1)] = SHADOW
    b.px[_dilate(full)] = (40, 0, 0, 255)
    b.px[full] = (255, 32, 32, 255)
    return b.image()


def credit():
    """The original credit line plus the remake, 360x20."""
    b = Board(360, 20)
    text = '(C) 1997 SACHISOFT / SAWAYAKAN Programmers  -  ANA REMAKE'
    m = _fit_font(text, FONT_LATIN_SMALL, 354, 14)
    full = b.place(m, (360 - m.shape[1]) // 2, (20 - m.shape[0]) // 2)
    b.px[np.roll(np.roll(full, 1, 0), 1, 1)] = (60, 60, 60, 255)
    b.px[full] = (255, 255, 255, 255)
    return b.image()


# dark, low-saturation tints so the menu text on top stays readable
TILE_BG = {'a_teal': '#2f4f4c', 'n_blue': '#2f3b5a', 'a_red': '#553634'}


def menu_tile(character_id):
    """Menu background tile: the character smiling on a soft color."""
    b = Board(104, 104)
    b.px[:, :] = (*hex_rgb(TILE_BG[character_id]), 255)
    frame = np.array(build_frame(character_id, Pose(arm=20, eyes='closed',
                                                    mouth='open')))
    region = b.px[20:84, 20:84]
    a = frame[..., 3] > 0
    region[a] = frame[a]
    return b.image()


def textures():
    out = {}
    for lang in ('ja', 'ko'):
        out[f'messages/{lang}/mark.png'] = mark()
        out[f'messages/{lang}/pokemon.png'] = subtitle(lang)
        out[f'messages/{lang}/pikachu_volleyball.png'] = logo(lang)
        out[f'messages/{lang}/fight.png'] = burst(lang)
    # one font size for both options, set by the longer one
    size = next(s for s in range(30, 6, -1)
                if _text_mask('VS COMPUTER', _font(FONT_LATIN, s)).shape[1]
                <= 112 and _text_mask('VS COMPUTER',
                                      _font(FONT_LATIN, s)).shape[0] <= 14)
    out['messages/ja/with_computer.png'] = with_who('VS COMPUTER', size)
    out['messages/ja/with_friend.png'] = with_who('VS FRIEND', size)
    # same words as the original Korean options, redrawn so they read on the
    # darker menu tiles
    size = next(s for s in range(30, 6, -1)
                if _text_mask('혼자서 재미있게~', _font(FONT_KOREAN, s)).shape[1]
                <= 112 and _text_mask('혼자서 재미있게~',
                                      _font(FONT_KOREAN, s)).shape[0] <= 14)
    out['messages/ko/with_computer.png'] = with_who('혼자서 재미있게~', size,
                                                    FONT_KOREAN)
    out['messages/ko/with_friend.png'] = with_who('둘이서 같이~', size,
                                                  FONT_KOREAN)
    out['messages/ja/game_start.png'] = game_start()
    out['messages/common/sachisoft.png'] = credit()
    for character_id in PALETTES:
        out[f'menu/tile_{character_id}.png'] = menu_tile(character_id)
    out['sitting_pikachu.png'] = menu_tile('a_teal')
    return out


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(here, 'out', 'titles')
    for name, img in textures().items():
        path = os.path.join(folder, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        img.save(path)
        print(name, img.size)
