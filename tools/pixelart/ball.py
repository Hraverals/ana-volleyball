"""Ball, ball effects and score digits for the ANA remake.

Same names and sizes as the original textures:

- ball/ball_{0..4}.png   40x40  a beach volleyball in the three character
  colors; the frames turn it 72 degrees each, like the original ball
- ball/ball_hyper.png    40x40  dithered copy of the ball (power hit)
- ball/ball_trail.png    40x40  dithered trail circle (power hit)
- ball/ball_punch.png    40x40  burst where the ball is hit
- number/number_{0..9}.png 32x32 score digits in the logo's yellow jelly
"""

import numpy as np
from PIL import Image

from pixelkit import hex_rgb
from titles import (FONT_LATIN, SHADOW, YELLOW, Board, _dilate, _font,
                    _hex_ramp, _ramp, _text_mask)

SIZE = 40
R = 19.5
OUTLINE = hex_rgb('#1d2430')
WHITE_RAMP = [hex_rgb(h) for h in ('#9aa3ad', '#c9d0d6', '#eef2f4', '#ffffff')]

# Light from the upper left, a little toward the viewer
LIGHT = np.array([-0.55, -0.65, 0.75])
LIGHT /= np.linalg.norm(LIGHT)


def _color_ramp(character_id):
    """Four tones (dark .. light) of a character color."""
    r = _ramp(character_id)
    return [r[1], r[2], r[3], r[4]]


SEGMENTS = [WHITE_RAMP, None, WHITE_RAMP, None, WHITE_RAMP, None]
COLOR_IDS = ['a_teal', 'n_blue', 'a_red']


def ball_frame(k):
    """Beach volleyball turned by k * 72 degrees in the screen plane."""
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    x = (xs + 0.5 - SIZE / 2) / R
    y = (ys + 0.5 - SIZE / 2) / R
    rr = x * x + y * y
    inside = rr <= 1.0
    z = np.sqrt(np.clip(1 - rr, 0, 1))

    # six curved panels: the seams swirl a little toward the rim
    ang = np.arctan2(y, x) + np.radians(72 * k) + 0.7 * np.sqrt(rr)
    seg = np.floor((ang % (2 * np.pi)) / (np.pi / 3)).astype(int) % 6

    lam = x * LIGHT[0] + y * LIGHT[1] + z * LIGHT[2]
    # mostly the base tone; the lightest one only near the glint
    level = np.digitize(lam, [0.2, 0.5, 0.93])

    px = np.zeros((SIZE, SIZE, 4), dtype=np.uint8)
    for s in range(6):
        ramp = (WHITE_RAMP if s % 2 == 0
                else _color_ramp(COLOR_IDS[s // 2]))
        for lv in range(4):
            m = inside & (seg == s) & (level == lv)
            px[m] = (*ramp[lv], 255)

    # seams between panels, then the outline
    seam = np.zeros_like(inside)
    seam[:, 1:] |= seg[:, 1:] != seg[:, :-1]
    seam[1:, :] |= seg[1:, :] != seg[:-1, :]
    seam &= inside & (rr < 0.92)
    px[seam] = (*hex_rgb('#5b6470'), 255)
    pad = np.pad(inside, 1, constant_values=False)
    inner = pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]
    px[inside & ~inner] = (*OUTLINE, 255)

    # jelly glint on the upper left
    for gx, gy in ((11, 9), (12, 9), (10, 10), (11, 10), (10, 11)):
        px[gy, gx] = (255, 255, 255, 255)
    return Image.fromarray(px, 'RGBA')


def _dither(img, keep_even=True):
    px = np.array(img)
    ys, xs = np.mgrid[0:px.shape[0], 0:px.shape[1]]
    drop = ((xs + ys) % 2 == 0) != keep_even
    px[drop, 3] = 0
    return Image.fromarray(px, 'RGBA')


def ball_hyper():
    """Dithered ball, drawn one frame behind the ball on a power hit."""
    return _dither(ball_frame(0))


def ball_trail():
    """Dithered pale circle, drawn two frames behind the ball."""
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    rr = ((xs + 0.5 - 20) ** 2 + (ys + 0.5 - 20) ** 2) / R ** 2
    px = np.zeros((SIZE, SIZE, 4), dtype=np.uint8)
    px[rr <= 1] = (*hex_rgb('#8fb4f6'), 255)
    return _dither(Image.fromarray(px, 'RGBA'), keep_even=False)


def ball_punch():
    """Yellow jelly burst; the game scales it with the punch radius."""
    b = Board(SIZE, SIZE)
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    ang = np.arctan2(ys + 0.5 - 20, xs + 0.5 - 20)
    rad = np.hypot(ys + 0.5 - 20, xs + 0.5 - 20)
    t = (ang / (2 * np.pi) * 9) % 1.0
    star = rad <= 12 + 6.5 * np.abs(1 - 2 * t)
    b.jelly(star & (rad < 19), _hex_ramp(YELLOW), radius=4.0)
    return b.image()


def number(n):
    """Score digit in the logo's yellow jelly, 32x32."""
    b = Board(32, 32)
    m = _text_mask(str(n), _font(FONT_LATIN, 30))
    if m.shape[0] > 26:  # keep every digit the same height
        m = _text_mask(str(n), _font(FONT_LATIN, 28))
    full = b.place(m, (32 - m.shape[1]) // 2 - 1, (32 - m.shape[0]) // 2 - 1)
    b.shadow(full, 2, 2, SHADOW)
    b.jelly(full, _hex_ramp(YELLOW), radius=3.0)
    b.glints(full, 1)
    return b.image()


def textures():
    out = {f'ball/ball_{k}.png': ball_frame(k) for k in range(5)}
    out['ball/ball_hyper.png'] = ball_hyper()
    out['ball/ball_trail.png'] = ball_trail()
    out['ball/ball_punch.png'] = ball_punch()
    for n in range(10):
        out[f'number/number_{n}.png'] = number(n)
    return out
