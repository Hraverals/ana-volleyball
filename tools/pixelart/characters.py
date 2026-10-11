"""Part definitions of the ANA characters (64x64 frames, side view facing
right, like the original Pikachu frames).

Parts: tail, ear, back foot, body (head + snout + torso shaded as one),
front foot, arm, face stamps and jelly highlights. A pose moves, rotates or
swaps those parts, so every frame is drawn from the same definitions and
reads as the same character.
"""

from dataclasses import dataclass

import numpy as np

from pixelkit import Canvas, Part, edge, ellipse, grid, hex_rgb, transform

SIZE = 64

WHITE = hex_rgb('#ffffff')
INK = hex_rgb('#16141f')       # eyes, nose, mouth
MOUTH = hex_rgb('#7a2a3a')     # inside of the mouth
TONGUE = hex_rgb('#ff8fa0')
BLUSH = hex_rgb('#f59aaa')
SWEAT = hex_rgb('#8fd0ff')

# Ramps: [outline, shade 2, shade 1, base, light]
PALETTES = {
    'a_teal': {
        'body': ['#0f6663', '#26a39b', '#3cc2b6', '#62dccf', '#a6f3ea'],
        'ear_inner': '#e6fcf9',
        'eyes': 'open',
    },
    'n_blue': {
        'body': ['#173a86', '#2f5fc0', '#4377dc', '#6595ef', '#a9c8fb'],
        'ear_inner': '#ffb3c1',
        'eyes': 'closed',
    },
    'a_red': {
        'body': ['#7a1f24', '#c23c3c', '#de5650', '#f4766d', '#ffb0a8'],
        'ear_inner': '#ffc4cd',
        'eyes': 'open',
    },
}


@dataclass
class Pose:
    """Placement of the parts for one frame. Angles are degrees, clockwise
    on screen; offsets are pixels relative to the neutral standing pose."""
    dx: float = 0.0            # whole character offset
    dy: float = 0.0
    head_dx: float = 0.0       # head relative to the torso
    head_dy: float = 0.0
    torso_tilt: float = 0.0    # torso rotation around its center
    torso_sx: float = 1.0      # torso scale (squash and stretch)
    torso_sy: float = 1.0
    arm: float = 50.0          # arm angle: 0 = forward, 90 = straight down
    arm_len: float = 7.0
    back_foot: tuple = (0.0, 0.0)
    front_foot: tuple = (0.0, 0.0)
    tail: tuple = (0.0, 0.0)   # tail offset
    tail_scale: float = 1.0
    ear_tilt: float = 0.0      # ear rotation (negative leans back)
    eyes: str = ''             # '' = character default; open | closed |
    #                            wince | dizzy | surprised
    mouth: str = 'smile'       # smile | open | flat | frown | o
    blush: bool = True
    sweat: bool = False
    grounded: bool = True      # keep the feet on the ground line


# Neutral geometry (frame coordinates)
HEAD = (40.0, 23.0, 15.0, 13.5)    # cx, cy, rx, ry
SNOUT = (53.5, 28.0, 5.0, 4.5)
TORSO = (38.0, 44.0, 14.5, 16.0)
EAR = (28.0, 11.0, 6.0, 6.0)
TAIL = (17.0, 45.0, 11.5, 11.0)
BACK_FOOT = (31.0, 59.0, 5.5, 3.2)
FRONT_FOOT = (46.0, 59.0, 5.5, 3.0)
SHOULDER = (45.0, 38.0)


def build_frame(character_id, pose):
    pal = PALETTES[character_id]
    ramp = [hex_rgb(h) for h in pal['body']]
    canvas = Canvas(SIZE, SIZE)
    gx, gy = grid(SIZE, SIZE)
    x0, y0 = gx - pose.dx, gy - pose.dy

    # head group (head, snout, ear, face) moves without rotating
    hx, hy = x0 - pose.head_dx, y0 - pose.head_dy
    head = ellipse(hx, hy, *HEAD)
    snout = ellipse(hx, hy, *SNOUT)

    # torso: rotate and scale around its center
    tcx, tcy = TORSO[0], TORSO[1]
    tx, ty = transform(x0, y0, tcx, tcy, pose.torso_tilt)
    tx = (tx - tcx) / pose.torso_sx + tcx
    ty = (ty - tcy) / pose.torso_sy + tcy
    torso = ellipse(tx, ty, *TORSO)

    def torso_point(px, py):
        """Torso-space point -> frame point."""
        a = np.radians(pose.torso_tilt)
        vx = (px - tcx) * pose.torso_sx
        vy = (py - tcy) * pose.torso_sy
        return (vx * np.cos(a) - vy * np.sin(a) + tcx + pose.dx,
                vx * np.sin(a) + vy * np.cos(a) + tcy + pose.dy)

    body = head | snout | torso

    # ear on the back of the head, pivoting at its base
    ex, ey, erx, ery = EAR
    eax, eay = transform(hx, hy, ex + 2, ey + 5, pose.ear_tilt)
    ear = ellipse(eax, eay, ex, ey, erx, ery)
    inner = ellipse(eax, eay, ex + 0.4, ey + 0.4, 2.6, 2.6)

    # tail behind the torso
    tlx, tly = torso_point(TAIL[0], TAIL[1])
    tlx += pose.tail[0]
    tly += pose.tail[1]
    tail = ellipse(gx, gy, tlx, tly, TAIL[2] * pose.tail_scale,
                   TAIL[3] * pose.tail_scale)

    feet = []
    for base, off in ((BACK_FOOT, pose.back_foot),
                      (FRONT_FOOT, pose.front_foot)):
        fx, fy = torso_point(base[0], base[1])
        if pose.grounded:
            fy = base[1]
        feet.append(ellipse(gx, gy, fx + off[0], fy + off[1],
                            base[2], base[3]))

    # arm: a flat paddle hanging from the shoulder
    sx, sy = torso_point(*SHOULDER)
    a = np.radians(pose.arm)
    acx = sx + np.cos(a) * pose.arm_len * 0.75
    acy = sy + np.sin(a) * pose.arm_len * 0.75
    ax, ay = transform(gx, gy, acx, acy, -pose.arm)
    arm = ellipse(ax, ay, acx, acy, pose.arm_len, 2.8)

    # draw back to front
    Part(tail, ramp, radius=6.0, bias=-0.12).draw(canvas)
    Part(ear, ramp, radius=3.5, bias=-0.35).draw(canvas)
    canvas.paint(inner & ear & ~edge(ear) & ~body, hex_rgb(pal['ear_inner']))
    Part(feet[0] & ~body, ramp, radius=2.5, bias=-0.15).draw(canvas)
    Part(body, ramp, radius=7.0, bias=-0.12).draw(canvas)
    Part(feet[1], ramp, radius=2.5).draw(canvas)
    Part(arm, ramp, radius=2.0, bias=0.1).draw(canvas)

    # face follows the head and stays upright
    ox, oy = pose.dx + pose.head_dx, pose.dy + pose.head_dy
    _stamp_face(canvas, pose, pal, ox, oy)

    # jelly highlights on the upper left of the head and the tail
    for px, py in ((33, 12), (34, 12), (32, 13)):
        _put(canvas, px + ox, py + oy, WHITE)
    s = pose.tail_scale
    for px, py in ((-5, -8), (-4, -9)):
        _put(canvas, tlx + px * s, tly + py * s, WHITE)

    return canvas.image()


def _put(canvas, x, y, color):
    """Paint one pixel, only on top of already drawn pixels."""
    x, y = int(round(x)), int(round(y))
    if 0 <= x < SIZE and 0 <= y < SIZE and canvas.px[y, x, 3]:
        canvas.px[y, x] = (*color, 255)


def _stamp(canvas, x0, y0, rows, colors):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in colors:
                _put(canvas, x0 + i, y0 + j, colors[ch])


# (vertical offset, pattern) per eye type
EYES = {
    # big round eye with highlight pixels toward the upper left
    'open': (0, ['.KKK.',
                 'KKWWK',
                 'KKWWK',
                 'KKKKK',
                 'KWKKK',
                 '.KKK.']),
    'closed': (2, ['.KKK.',
                   'K...K']),
    'wince': (0, ['K....',
                  '.KK..',
                  '...K.',
                  '.KK..',
                  'K....']),
    'dizzy': (0, ['KKKK.',
                  '...K.',
                  '.K.K.',
                  '.KKK.']),
    'surprised': (0, ['.KKK.',
                      'KWWWK',
                      'KWKWK',
                      'KWWWK',
                      '.KKK.']),
}

MOUTHS = {
    'smile': ['K...',
              '.KKK'],
    'open': ['KKKK',
             '.KMT',
             '..KK'],
    'flat': ['.KKK.'],
    'frown': ['.KKK.',
              'K...K'],
    'o': ['.KK.',
          'KMMK',
          '.KK.'],
}


def _stamp_face(canvas, pose, pal, ox, oy):
    colors = {'W': WHITE, 'H': WHITE, 'K': INK, 'M': MOUTH, 'T': TONGUE,
              'B': BLUSH, 'S': SWEAT}
    eyes = pose.eyes or pal['eyes']
    if eyes == 'open' and pal['eyes'] == 'closed':
        eyes = 'closed'
    dy, rows = EYES[eyes]
    _stamp(canvas, 45 + ox, 16 + dy + oy, rows, colors)
    _stamp(canvas, 57 + ox, 25 + oy, ['KK', 'KK'], colors)  # nose
    _stamp(canvas, 51 + ox, 30 + oy, MOUTHS[pose.mouth], colors)
    if pose.blush:
        _stamp(canvas, 40 + ox, 25 + oy, ['.BBB.', 'BBBBB', '.BBB.'], colors)
    if pose.sweat:
        _stamp(canvas, 36 + ox, 12 + oy, ['.S', 'SS', 'SS'], colors)
