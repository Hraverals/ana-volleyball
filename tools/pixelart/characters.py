"""Part definitions of the ANA characters (64x64 frames, facing right).

A frame is built from parts: back arm, ears, body, front arm, face and
highlights. A pose moves, rotates or swaps those parts, so every frame is
drawn from the same definitions and reads as the same character.
"""

from dataclasses import dataclass, field

import numpy as np

from pixelkit import (Canvas, Part, ellipse, grid, hex_rgb, round_poly,
                      transform)

SIZE = 64

WHITE = hex_rgb('#ffffff')
INK = hex_rgb('#1d1a2b')       # eyes, nose, mouth line
MOUTH = hex_rgb('#7a2a3a')     # inside of the mouth
TONGUE = hex_rgb('#ff8fa0')
BLUSH = hex_rgb('#ff9fb4')

# Ramps: [outline, shade 2, shade 1, base, light]
PALETTES = {
    'a_teal': {
        'body': ['#0b4a4d', '#178a87', '#2fb6ad', '#4fd6c9', '#90f1e5'],
        'ear_inner': ['#0b4a4d', '#d2f7f1', '#e9fcf9', '#ffffff'],
        'letter': 'A',
    },
    'n_blue': {
        'body': ['#14306e', '#2a56b0', '#3c73d6', '#5a91ec', '#9cc0fa'],
        'ear_inner': ['#14306e', '#f59aaa', '#ffb3c1', '#ffd0d9'],
        'letter': 'N',
    },
    'a_red': {
        'body': ['#5e1a1c', '#b23a3a', '#d9534f', '#f2716a', '#ffaaa2'],
        'ear_inner': ['#5e1a1c', '#f59aaa', '#ffb3c1', '#ffd0d9'],
        'letter': 'A',
    },
}


@dataclass
class Pose:
    """Placement of the parts for one frame. Angles are in degrees,
    clockwise on screen; offsets are in pixels."""
    dx: float = 0.0            # whole-body offset
    dy: float = 0.0
    tilt: float = 0.0          # whole-body rotation around the hips
    squash: float = 1.0        # vertical scale of the body (1 = none)
    legs: float = 0.0          # extra spread of the legs
    back_arm: float = 0.0      # rotation of the back (left) arm
    front_arm: float = 0.0     # rotation of the front (right) arm
    ear_tilt: float = 0.0
    eyes: str = 'open'         # open | closed | wince
    mouth: str = 'smile'       # smile | open | flat | frown
    face_dx: float = 0.0       # face shift relative to the body
    face_dy: float = 0.0
    extra: dict = field(default_factory=dict)


# Body geometry in frame coordinates for the neutral pose.
BODY_TOP = 13
BODY_BOTTOM = 62
HIP = (33.0, 53.0)  # rotation pivot of the whole body


def _ramp(hexes):
    return [hex_rgb(h) for h in hexes]


def _body_mask_a(xs, ys, pose):
    """A-shaped body: narrow round top, wide bottom split into two legs."""
    sp = pose.legs
    top = BODY_BOTTOM - (BODY_BOTTOM - BODY_TOP) * pose.squash
    # a round head on a body that widens toward the feet
    pts = [(23, top + 2), (43, top + 2), (56 + sp, BODY_BOTTOM),
           (10 - sp, BODY_BOTTOM)]
    body = round_poly(xs, ys, pts, 7.5)
    head = ellipse(xs, ys, 33.0, top + 11.0, 14.0, 11.5 * pose.squash)
    # the legs split under an arch, like the inside of an A
    gap = ellipse(xs, ys, 33.0, BODY_BOTTOM + 1.0, 4.0 + sp * 0.5,
                  12.0 * pose.squash)
    return (body | head) & ~gap, top


def _body_mask_n(xs, ys, pose):
    """N-shaped body: two pillars joined by a diagonal."""
    sp = pose.legs
    top = BODY_BOTTOM - (BODY_BOTTOM - BODY_TOP) * pose.squash
    left = round_poly(xs, ys, [(13 - sp, top + 4), (25 - sp, top + 4),
                               (25 - sp, BODY_BOTTOM), (13 - sp, BODY_BOTTOM)],
                      5.5)
    right = round_poly(xs, ys, [(41 + sp, top), (53 + sp, top),
                                (53 + sp, BODY_BOTTOM),
                                (41 + sp, BODY_BOTTOM)], 5.5)
    diag = round_poly(xs, ys, [(14, top + 6), (26, top + 4),
                               (52, BODY_BOTTOM - 8), (40, BODY_BOTTOM - 6)],
                      5.0)
    return left | right | diag, top


def build_frame(character_id, pose):
    pal = PALETTES[character_id]
    body_ramp = _ramp(pal['body'])
    inner_ramp = _ramp(pal['ear_inner'])
    canvas = Canvas(SIZE, SIZE)

    gx, gy = grid(SIZE, SIZE)
    # sample points for the whole body (tilt around the hips, then offset)
    bx, by = transform(gx, gy, HIP[0], HIP[1], pose.tilt, pose.dx, pose.dy)

    body_fn = _body_mask_a if pal['letter'] == 'A' else _body_mask_n
    body, top = body_fn(bx, by, pose)

    # ears sit on the top corners of the letter
    if pal['letter'] == 'A':
        ear_l, ear_r = (22.5, top - 0.5), (43.5, top - 1.0)
    else:
        ear_l, ear_r = (17.0, top + 4.0), (48.0, top + 0.5)
    ears = np.zeros_like(body)
    inners = np.zeros_like(body)
    for (ex, ey), toward in ((ear_l, 1), (ear_r, -1)):
        ex2, ey2 = transform(bx, by, ex, ey, pose.ear_tilt * -toward)
        ears |= ellipse(ex2, ey2, ex, ey, 5.5, 5.2)
        inners |= ellipse(ex2, ey2, ex + toward * 0.5, ey - 0.8, 2.6, 2.3)

    # arms are short nubs pivoting at the shoulders
    sh_y = top + 21
    back_shoulder = (18.0, sh_y)
    front_shoulder = (48.0, sh_y)
    ax, ay = transform(bx, by, *back_shoulder, angle=pose.back_arm)
    back_arm = ellipse(ax, ay, back_shoulder[0] - 4.5, back_shoulder[1] + 4.0,
                       6.5, 3.6)
    ax, ay = transform(bx, by, *front_shoulder, angle=pose.front_arm)
    front_arm = ellipse(ax, ay, front_shoulder[0] + 4.5,
                        front_shoulder[1] + 4.0, 6.5, 3.6)

    Part(back_arm, body_ramp, radius=3.0, bias=-0.1).draw(canvas)
    Part(ears, body_ramp, radius=4.0).draw(canvas)
    Part(inners & ~body, inner_ramp, outline=False, flat=2).draw(canvas)
    Part(body, body_ramp, radius=6.0, bias=0.05).draw(canvas)
    Part(front_arm, body_ramp, radius=3.0).draw(canvas)

    # face: stamped pixel patterns, placed on the body after the transform
    fx = 36 + pose.face_dx
    fy = top + 13 + pose.face_dy
    _stamp_face(canvas, pose, fx, fy)

    # jelly highlights on the upper left of the head and the near ear
    hx, hy = 24, top + 3
    for px, py in ((hx, hy), (hx + 1, hy), (hx - 1, hy + 1)):
        _put(canvas, pose, px, py, WHITE)

    return canvas.image()


def _place(pose, x, y):
    """Forward-map a body-space point to frame space."""
    a = np.radians(pose.tilt)
    cx, cy = HIP
    rx = (x - cx) * np.cos(a) - (y - cy) * np.sin(a) + cx + pose.dx
    ry = (x - cx) * np.sin(a) + (y - cy) * np.cos(a) + cy + pose.dy
    return int(round(rx - 0.5)), int(round(ry - 0.5))


def _put(canvas, pose, x, y, color):
    px, py = _place(pose, x + 0.5, y + 0.5)
    if 0 <= px < SIZE and 0 <= py < SIZE:
        canvas.px[py, px] = (*color, 255)


def _stamp(canvas, pose, x0, y0, rows, colors):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in colors:
                _put(canvas, pose, x0 + i, y0 + j, colors[ch])


EYE_OPEN = ['.WWW.',
            'WWHKW',
            'WWKKW',
            '.WWW.']
EYE_CLOSED = ['.KK.',
              'K..K']
EYE_WINCE = ['K..',
             '.KK',
             'K..']

MOUTHS = {
    'smile': ['K.....K',
              '.KMMMK.',
              '.KMTTK.',
              '..KKK..'],
    'open': ['.KKK.',
             'KMMMK',
             'KMTMK',
             '.KKK.'],
    'flat': ['.KKK.'],
    'frown': ['.KKK.',
              'K...K'],
}


def _stamp_face(canvas, pose, fx, fy):
    colors = {'W': WHITE, 'H': WHITE, 'K': INK, 'M': MOUTH, 'T': TONGUE,
              'B': BLUSH}
    fx, fy = int(fx), int(fy)
    if pose.eyes == 'open':
        eye = EYE_OPEN
        _stamp(canvas, pose, fx - 9, fy - 3, eye, colors)
        _stamp(canvas, pose, fx + 4, fy - 3, eye, colors)
    elif pose.eyes == 'closed':
        _stamp(canvas, pose, fx - 7, fy - 1, EYE_CLOSED, colors)
        _stamp(canvas, pose, fx + 3, fy - 1, EYE_CLOSED, colors)
    else:
        _stamp(canvas, pose, fx - 6, fy - 2, EYE_WINCE, colors)
        _stamp(canvas, pose, fx + 3, fy - 2,
               [r[::-1] for r in EYE_WINCE], colors)
    # nose
    _stamp(canvas, pose, fx - 1, fy + 1, ['KK'], colors)
    # mouth
    m = MOUTHS[pose.mouth]
    _stamp(canvas, pose, fx - len(m[0]) // 2, fy + 2, m, colors)
    # blush
    _stamp(canvas, pose, fx - 12, fy + 2, ['BBB', 'BBB'], colors)
    _stamp(canvas, pose, fx + 9, fy + 2, ['BBB', 'BBB'], colors)
