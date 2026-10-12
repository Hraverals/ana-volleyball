"""ANA club room background (432x304) and the whiteboard net sprite.

Side view of the room wall. Physics reference points (see CLAUDE.md):
net center x=216 (top y=176), players stand with feet at about y=276, the
ball bottoms out at about y=272, the floor surface starts at y=264.

No people and no readable text: posters, photos and notes are color blocks.
"""

import random

from PIL import Image, ImageEnhance

from pixelkit import Canvas, hex_rgb

W, H = 432, 304
FLOOR_Y = 264

# The net sprite is wider than the pillar so the stand's base fits.
NET_X, NET_Y = 204, 176
NET_W, NET_H = 24, 96


def C(h):
    return hex_rgb(h)


class Painter:
    def __init__(self, w, h):
        self.c = Canvas(w, h, (0, 0, 0, 0))

    def rect(self, x0, y0, x1, y1, col):
        """Fill [x0, x1) x [y0, y1)."""
        x0, x1 = max(0, x0), min(self.c.w, x1)
        y0, y1 = max(0, y0), min(self.c.h, y1)
        if x0 < x1 and y0 < y1:
            self.c.px[y0:y1, x0:x1] = (*col, 255)

    def px(self, x, y, col):
        if 0 <= x < self.c.w and 0 <= y < self.c.h:
            self.c.px[y, x] = (*col, 255)

    def box(self, x0, y0, x1, y1, ramp, outline=True):
        """Lit box: ramp = [outline, dark, base, light]. Light from upper left."""
        o, d, b, l = (C(h) for h in ramp)
        self.rect(x0, y0, x1, y1, b)
        self.rect(x0, y0, x1, y0 + 1, l)
        self.rect(x0, y0, x0 + 1, y1, l)
        self.rect(x0, y1 - 1, x1, y1, d)
        self.rect(x1 - 1, y0, x1, y1, d)
        if outline:
            self.frame(x0 - 1, y0 - 1, x1 + 1, y1 + 1, o)

    def frame(self, x0, y0, x1, y1, col):
        self.rect(x0, y0, x1, y0 + 1, col)
        self.rect(x0, y1 - 1, x1, y1, col)
        self.rect(x0, y0, x0 + 1, y1, col)
        self.rect(x1 - 1, y0, x1, y1, col)

    def image(self):
        return self.c.image()


# --- palettes (already muted; a final pass lowers saturation further) ---
# white wallpaper: [edge line, stripe, base, light]
WALL = ['#b9b5ac', '#e2dfd8', '#ecebe6', '#f6f5f1']
WOOD = ['#5d4c38', '#86704f', '#9e8761', '#b29b73']
WOOD_LIGHT = ['#6a5940', '#9b8661', '#b19b72', '#c2ad84']
METAL = ['#4d5155', '#6f7478', '#878c90', '#a1a5a8']
WHITE_GOODS = ['#6d7173', '#a8abab', '#bcbebd', '#cdcfcd']
DARK = ['#2f3236', '#3d4146', '#4a4f55', '#5d6369']
CARDBOARD = ['#6b573d', '#957a55', '#a88c63', '#b99e74']

POSTER_COLORS = ['#b8a46a', '#b98a62', '#5d6680', '#6c8f8c', '#c4bca6',
                 '#a07c86', '#7f8f6a']
BOOK_COLORS = ['#6f6a8a', '#8a6a5e', '#5f7b78', '#9a8f6a', '#7c7f86',
               '#8d7a8f', '#a0a39a', '#5d6a7c', '#94806a']


def build_background(seed=7):
    rnd = random.Random(seed)
    p = Painter(W, H)
    _wall(p)
    _floor(p)
    _left_half(p, rnd)
    _right_half(p, rnd)
    img = p.image()
    # keep the room calmer than the characters and the ball
    img = ImageEnhance.Color(img.convert('RGB')).enhance(0.8)
    img = ImageEnhance.Contrast(img).enhance(0.88)
    return img.convert('RGBA')


def _wall(p):
    o, d, b, l = (C(h) for h in WALL)
    p.rect(0, 0, W, FLOOR_Y, b)
    # wallpaper: faint vertical stripes with a light line beside each
    for x in range(4, W, 12):
        p.rect(x, 0, x + 2, FLOOR_Y, d)
        p.rect(x + 2, 0, x + 3, FLOOR_Y, l)
    # tiny dots between the stripes
    for y in range(14, FLOOR_Y - 10, 12):
        for x in range(10, W, 12):
            p.px(x + (6 if (y // 12) % 2 else 0) % 12, y, d)
    # ceiling molding and a soft shade under it
    p.rect(0, 0, W, 6, C('#f4f3ef'))
    p.rect(0, 6, W, 7, o)
    p.rect(0, 7, W, 9, C('#d9d6cf'))
    p.rect(0, 9, W, 11, d)
    # baseboard
    p.rect(0, FLOOR_Y - 8, W, FLOOR_Y - 7, l)
    p.rect(0, FLOOR_Y - 7, W, FLOOR_Y, C('#a9a59c'))
    p.rect(0, FLOOR_Y - 1, W, FLOOR_Y, C('#8a867d'))


def _floor(p):
    base, line, light = C('#8e9090'), C('#7d7f80'), C('#9c9e9d')
    p.rect(0, FLOOR_Y, W, H, base)
    p.rect(0, FLOOR_Y, W, FLOOR_Y + 1, light)
    for y in (276, 292):
        p.rect(0, y, W, y + 1, line)
    # tile seams lean slightly outward from the center for a hint of depth
    for i in range(-14, 15):
        xt = 216 + i * 32
        for y in range(FLOOR_Y + 1, H):
            x = xt + int(i * (y - FLOOR_Y) * 0.12)
            p.px(x, y, line)


# --------------------------------------------------------------- left half
def _left_half(p, rnd):
    _posters(p, rnd, 12, 38)
    _photo_board(p, rnd, 100, 40)
    _wall_whiteboard(p, rnd, 140, 110)  # low enough for short legs
    _desk(p, 2, 132, 212)
    _laptop(p, 30, 212)
    _book_stack(p, 92, 212, rnd)
    _mug(p, 118, 212)
    _lamp(p, 70, 212)


def _posters(p, rnd, x0, y0):
    pw, ph, gap = 24, 36, 4
    for row in range(2):
        for col in range(3):
            x = x0 + col * (pw + gap)
            y = y0 + row * (ph + gap) + rnd.randint(-1, 1)
            main = C(rnd.choice(POSTER_COLORS))
            paper = C('#c9c4b6')
            p.frame(x - 1, y - 1, x + pw + 1, y + ph + 1, C('#7e7a72'))
            p.rect(x, y, x + pw, y + ph, paper)
            # title band and a big shape, then "text" bars (abstract)
            p.rect(x, y, x + pw, y + 9, main)
            p.rect(x + 3, y + 3, x + pw - 3 - rnd.randint(0, 6), y + 5,
                   C('#e6e1d4'))
            kind = rnd.randint(0, 2)
            if kind == 0:
                p.rect(x + 4, y + 12, x + pw - 4, y + 22, main)
            elif kind == 1:
                for k in range(4):
                    p.rect(x + 4 + k * 4, y + 12 + k * 2, x + 7 + k * 4,
                           y + 22, main)
            else:
                cx, cy = x + pw // 2, y + 17
                for dy in range(-5, 6):
                    hw = int((25 - dy * dy) ** 0.5)
                    p.rect(cx - hw, cy + dy, cx + hw, cy + dy + 1, main)
            for k in range(3):
                bar = pw - 8 - rnd.randint(0, 8)
                p.rect(x + 4, y + 25 + k * 3, x + 4 + bar, y + 26 + k * 3,
                       C('#9d988c'))
            # pins
            p.px(x + 2, y + 1, C('#d6d2c6'))
            p.px(x + pw - 3, y + 1, C('#d6d2c6'))


def _photo_board(p, rnd, x0, y0):
    w, h = 30, 62
    p.box(x0, y0, x0 + w, y0 + h, METAL)
    # pegboard holes
    for yy in range(y0 + 2, y0 + h - 1, 3):
        for xx in range(x0 + 2, x0 + w - 1, 3):
            p.px(xx, yy, C('#73787c'))
    # four-cut photo strips: 4 small frames stacked
    for col in range(5):
        for row in range(3):
            x = x0 + 2 + col * 6 + rnd.randint(0, 1)
            y = y0 + 3 + row * 19 + rnd.randint(0, 2)
            p.rect(x, y, x + 4, y + 16, C('#d7d4cc'))
            for k in range(4):
                tone = C(rnd.choice(['#8f8a9a', '#9a8f86', '#86958f',
                                     '#a39a8a', '#7f8796']))
                p.rect(x + 1, y + 1 + k * 4, x + 3, y + 4 + k * 4, tone)
    # lanyards with name cards (blank)
    for i in range(6):
        x = x0 + 3 + i * 5
        top = y0 + h
        length = 18 + rnd.randint(0, 8)
        strap = C(rnd.choice(['#5d6680', '#7a6a8a', '#4f6f6c', '#8a6a5a']))
        for y in range(top, top + length):
            p.px(x, y, strap)
            p.px(x + 2, y, strap)
        p.rect(x - 1, top + length, x + 4, top + length + 6, C('#cfccc4'))
        p.rect(x, top + length + 1, x + 3, top + length + 2, C('#9a968c'))


def _wall_whiteboard(p, rnd, x0, y0):
    w, h = 62, 58
    p.box(x0, y0, x0 + w, y0 + h, METAL)
    p.rect(x0 + 2, y0 + 2, x0 + w - 2, y0 + h - 2, C('#c8cac7'))
    p.rect(x0 + 2, y0 + 2, x0 + w - 2, y0 + 3, C('#d6d8d5'))
    # faint doodles and notes: wavy strokes and blocks, nothing readable
    ink = [C('#9fa8b8'), C('#a8a0a6'), C('#a3aba0')]
    for k in range(7):
        x = x0 + 5 + rnd.randint(0, 36)
        y = y0 + 6 + k * 6 + rnd.randint(0, 2)
        length = rnd.randint(8, 18)
        col = rnd.choice(ink)
        for i in range(length):
            p.px(x + i, y + (1 if (i // 2) % 2 else 0), col)
    for k in range(3):  # sticky notes
        x = x0 + 44 + (k % 2) * 7
        y = y0 + 8 + k * 9
        p.rect(x, y, x + 6, y + 6, C(rnd.choice(['#c9bf86', '#b9c6a0',
                                                 '#c6a8a8'])))
    # tray and the stand's legs down to the floor
    p.box(x0 + 2, y0 + h, x0 + w - 2, y0 + h + 2, METAL, outline=False)
    for lx in (x0 + 4, x0 + w - 6):
        p.box(lx, y0 + h + 2, lx + 2, FLOOR_Y - 4, METAL, outline=False)
        p.rect(lx - 3, FLOOR_Y - 4, lx + 5, FLOOR_Y - 2, C('#5d6266'))
        p.rect(lx - 2, FLOOR_Y - 2, lx + 1, FLOOR_Y, C('#3e4245'))
        p.rect(lx + 2, FLOOR_Y - 2, lx + 4, FLOOR_Y, C('#3e4245'))


def _desk(p, x0, x1, top):
    p.box(x0, top, x1, top + 5, WOOD_LIGHT)
    # legs (metal) and a modesty panel
    for lx in (x0 + 3, x1 - 6):
        p.box(lx, top + 5, lx + 3, FLOOR_Y, METAL, outline=False)
    p.rect(x0 + 6, top + 6, x1 - 6, top + 7, C('#7a6a55'))


def _laptop(p, x, top):
    # open laptop seen from the side/back: lid and base
    p.box(x, top - 16, x + 22, top - 2, DARK)
    p.px(x + 10, top - 10, C('#6f7479'))  # logo dot
    p.rect(x - 2, top - 2, x + 24, top, C('#5d6369'))


def _book_stack(p, x, top, rnd):
    y = top
    for k in range(3):
        h = 3
        w = 14 - k * 2 + rnd.randint(0, 2)
        col = rnd.choice(BOOK_COLORS)
        p.box(x + k, y - h, x + k + w, y, [col, col, col, '#b0aca2'],
              outline=False)
        y -= h + 1


def _mug(p, x, top):
    p.box(x, top - 7, x + 6, top, WHITE_GOODS, outline=False)
    p.frame(x + 6, top - 6, x + 9, top - 2, C('#a8abab'))


def _lamp(p, x, top):
    # desk lamp: base, arm and shade
    p.rect(x, top - 2, x + 10, top, C('#3d4146'))
    for k in range(12):
        p.px(x + 4 + k // 3, top - 3 - k, C('#4a4f55'))
    p.box(x + 6, top - 18, x + 16, top - 13, DARK)
    p.rect(x + 8, top - 13, x + 14, top - 12, C('#c9c3a4'))


# -------------------------------------------------------------- right half
def _right_half(p, rnd):
    _bookshelf(p, rnd, 230, 128)
    _boxes(p, 280, 112)
    _lockers(p, 278, 112)
    _fridge(p, 350, 178)
    _desk(p, 382, 432, 212)
    _server(p, 392, 212)
    _monitor(p, 414, 212)


def _bookshelf(p, rnd, x0, y0):
    w = 42
    y1 = FLOOR_Y - 1
    p.box(x0, y0, x0 + w, y1, WOOD)
    p.rect(x0 + 3, y0 + 3, x0 + w - 3, y1 - 3, C('#6b5a42'))
    shelf_ys = list(range(y0 + 3, y1 - 3, 27))
    for sy in shelf_ys[1:]:
        p.rect(x0 + 3, sy, x0 + w - 3, sy + 2, C('#9e8761'))
    for i, sy in enumerate(shelf_ys):
        x = x0 + 4
        bottom = (shelf_ys[i + 1] if i + 1 < len(shelf_ys) else y1 - 3)
        while x < x0 + w - 6:
            bw = rnd.randint(2, 4)
            bh = rnd.randint(14, 22)
            col = C(rnd.choice(BOOK_COLORS))
            p.rect(x, bottom - bh, x + bw, bottom, col)
            p.rect(x, bottom - bh, x + 1, bottom, C('#b4b0a6'))
            x += bw + (1 if rnd.random() < 0.3 else 0)


def _lockers(p, x0, y0):
    cols, rows = 3, 5
    cw, rh = 22, 30
    p.box(x0, y0, x0 + cols * cw, FLOOR_Y - 1, WOOD_LIGHT)
    for c in range(cols):
        for r in range(rows):
            x = x0 + c * cw + 1
            y = y0 + r * rh + 1
            p.box(x + 1, y + 1, x + cw - 2, min(y + rh - 2, FLOOR_Y - 3),
                  WOOD_LIGHT, outline=False)
            p.frame(x, y, x + cw - 1, min(y + rh - 1, FLOOR_Y - 2),
                    C('#7a6748'))
            # handle / keyhole
            p.rect(x + cw - 6, y + 6, x + cw - 4, y + 9, C('#5d4c38'))


def _boxes(p, x0, y1):
    p.box(x0 + 4, y1 - 14, x0 + 24, y1 - 1, CARDBOARD)
    p.rect(x0 + 13, y1 - 14, x0 + 15, y1 - 1, C('#8a7250'))
    p.box(x0 + 28, y1 - 9, x0 + 52, y1 - 1, ['#2f3a5a', '#3d4c75',
                                              '#4a5a88', '#5d6c98'])
    p.box(x0 + 54, y1 - 12, x0 + 64, y1 - 1, CARDBOARD)


def _fridge(p, x0, y0):
    w = 28
    p.box(x0, y0, x0 + w, FLOOR_Y - 1, WHITE_GOODS)
    p.rect(x0 + 1, y0 + 24, x0 + w - 1, y0 + 25, C('#8e9192'))
    p.rect(x0 + w - 5, y0 + 6, x0 + w - 3, y0 + 18, C('#8e9192'))
    p.rect(x0 + w - 5, y0 + 30, x0 + w - 3, y0 + 50, C('#8e9192'))
    # a small box on top
    p.box(x0 + 4, y0 - 8, x0 + 20, y0 - 1, CARDBOARD)


def _server(p, x, top):
    # tower PC standing on the desk: the club server
    p.box(x, top - 30, x + 16, top, DARK)
    for k in range(4):
        p.rect(x + 3, top - 26 + k * 3, x + 13, top - 25 + k * 3,
               C('#3a3e43'))
    p.px(x + 12, top - 6, C('#6fb08a'))  # power LED
    p.px(x + 3, top - 6, C('#5d6369'))


def _monitor(p, x, top):
    p.box(x, top - 22, x + 20, top - 6, DARK)
    p.rect(x + 2, top - 20, x + 18, top - 8, C('#56626f'))
    p.rect(x + 3, top - 19, x + 8, top - 18, C('#6e7c8a'))
    p.rect(x + 8, top - 6, x + 12, top - 2, C('#3d4146'))
    p.rect(x + 5, top - 2, x + 15, top, C('#3d4146'))


# --------------------------------------------------------------------- net
def build_net():
    """Movable whiteboard seen edge-on: thin frame, tray, pole, wheeled base.
    Sprite is drawn at (NET_X, NET_Y). The upright part stays inside
    x=213..221 like the original net pillar."""
    p = Painter(NET_W, NET_H)

    def X(x):
        return x - NET_X

    def Y(y):
        return y - NET_Y

    frame = ['#4a4f54', '#8d9296', '#b4b8bb', '#d9dcdd']
    # board, slightly turned so a sliver of its white face shows
    p.box(X(214), Y(177), X(220), Y(237), frame)
    p.rect(X(215), Y(178), X(219), Y(236), C('#e4e7e7'))
    p.rect(X(215), Y(178), X(216), Y(236), C('#f4f6f6'))
    # marker scribbles on the face
    for y, x, col in ((184, 217, '#6f8fc0'), (185, 218, '#6f8fc0'),
                      (192, 216, '#c07070'), (193, 217, '#c07070'),
                      (200, 218, '#6f8fc0'), (207, 216, '#7aa07a'),
                      (208, 217, '#7aa07a'), (216, 218, '#6f8fc0'),
                      (224, 216, '#c07070')):
        p.px(X(x), Y(y), C(col))
    # top cap
    p.rect(X(213), Y(176), X(221), Y(178), C('#4a4f54'))
    p.rect(X(214), Y(176), X(220), Y(177), C('#7d8286'))
    # marker tray under the board
    p.box(X(211), Y(237), X(223), Y(240), frame)
    p.px(X(212), Y(236), C('#5f7fb0'))
    p.px(X(221), Y(236), C('#b06060'))
    # pole
    p.box(X(215), Y(240), X(219), Y(258), ['#3d4145', '#5f6468', '#767b7f',
                                            '#8d9296'])
    # base and wheels
    p.box(X(206), Y(258), X(228), Y(261), ['#3d4145', '#5f6468', '#767b7f',
                                            '#8d9296'])
    for wx in (X(207), X(224)):
        p.rect(wx, Y(262), wx + 4, Y(266), C('#2f3236'))
        p.rect(wx + 1, Y(261), wx + 3, Y(267), C('#2f3236'))
        p.px(wx + 1, Y(263), C('#6d7276'))
    return p.image()


if __name__ == '__main__':
    build_background().save('background.png')
    Image.Image.save(build_net(), 'net.png')
