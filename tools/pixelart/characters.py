"""Part definitions of the ANA characters (64x64 frames, side view facing
right, like the original Pikachu frames).

The base drawing is the approved side-view design, kept pixel for pixel in
parts/base_side.txt (34x57). It is split into parts:

- body: head, ear and torso (silhouette, rim lights, nose)
- back foot, front foot
- arm: drawn as a flat paddle from the shoulder, so it can swing
- face: eye, blush and mouth stamps, swapped per expression

A pose squashes, leans or turns the body, moves the feet, swings the arm
and swaps the face stamps, so every frame is built from the same parts.

Grid characters: '.' empty, O outline, s shade, b base, l light, W white,
K eye, P blush, e inside of the ear, N nose and mouth line, M inside of the
mouth, T tongue, S sweat drop.
"""

import os
from dataclasses import dataclass, replace

import numpy as np
from PIL import Image

from pixelkit import hex_rgb

SIZE = 64
HERE = os.path.dirname(os.path.abspath(__file__))

# Body colors per character: outline, shade, base, light, inside of the ear
PALETTES = {
    'a_teal': {
        'O': '#20726a', 's': '#34baae', 'b': '#64d8ce', 'l': '#c0f4ea',
        'e': '#34baae',
        'eyes': 'open', 'mouth': 'smile',
    },
    'n_blue': {
        'O': '#1d3f8f', 's': '#3e72d8', 'b': '#6797f0', 'l': '#c3d8fd',
        'e': '#f4a6b6',
        'eyes': 'closed', 'mouth': 'open',
    },
    'a_red': {
        'O': '#7f2328', 's': '#d8504c', 'b': '#f4776e', 'l': '#ffc8c0',
        'e': '#f9b3c0',
        'eyes': 'open', 'mouth': 'smile',
    },
}
COMMON = {
    'W': '#ffffff', 'K': '#0b0b10', 'P': '#ef98aa', 'N': '#14121c',
    'M': '#7a2a3a', 'T': '#ff8fa0', 'S': '#8fd0ff',
}

# Placement of the 34x57 base drawing in the 64x64 frame (standing)
X0, Y0 = 15, 6

# Base coordinates used by the poses
NECK_ROW = 24      # rows removed here lower the head (slump)
TORSO_ROW = 40     # rows removed / repeated here squash / stretch the body
SHOULDER = (17.0, 31.0)
EYE_AT = (20, 10)
BLUSH_AT = (16, 17)
MOUTH_AT = (27, 20)
SWEAT_AT = (14, 4)


def _load_base():
    path = os.path.join(HERE, 'parts', 'base_side.txt')
    with open(path, encoding='utf-8') as f:
        rows = [line.rstrip('\r\n') for line in f if line.strip()]
    return np.array([list(r) for r in rows])


def _inner(mask):
    pad = np.pad(mask, 1, constant_values=False)
    return pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]


def _outline(grid):
    """Turn every filled pixel that touches empty space into outline."""
    filled = grid != '.'
    out = grid.copy()
    out[filled & ~_inner(filled)] = 'O'
    return out


def _split_parts():
    base = _load_base()
    h, w = base.shape
    ys, xs = np.mgrid[0:h, 0:w]

    body = base.copy()
    # inside of the ear: the shaded blob on the back of the head
    ear = (ys >= 3) & (ys <= 9) & (xs >= 2) & (xs <= 11) & (base == 's')
    body[ear] = 'e'

    # face features come off the body and go back on as stamps
    eye_box = (ys >= 10) & (ys <= 16) & (xs >= 20) & (xs <= 26)
    eye_px = eye_box & np.isin(base, ['K', 'W'])
    eye = np.where(eye_px, base, '.')
    body[eye_px] = 'b'
    blush_box = (ys >= 17) & (ys <= 22) & (xs >= 16) & (xs <= 21)
    body[blush_box & (base == 'P')] = 'b'
    for y, x in ((20, 27), (21, 28), (21, 29), (21, 30), (21, 31)):
        body[y, x] = 'b'
    # a clear, dark nose at the tip of the face
    nose = ((ys >= 15) & (ys <= 16) & (xs >= 31)) | ((ys == 17) & (xs >= 32))
    nose &= base == 'O'

    # the arm is redrawn per pose
    arm_box = (ys >= 28) & (ys <= 39) & (xs >= 14) & (xs <= 26)
    body[arm_box & np.isin(base, ['O', 'l', 's'])] = 'b'

    # feet
    front = (ys >= 52) & (xs >= 17)
    for y, x in {47: 27, 48: 27, 49: 26, 50: 25, 51: 23}.items():
        front |= (ys == y) & (xs >= x)
    back = (ys >= 52) & (xs <= 10)
    front_foot = np.where(front, base, '.')
    back_foot = np.where(back, base, '.')
    body[front | ((ys >= 53) & (xs <= 11))] = '.'
    body = _outline(body)
    body[nose] = 'N'
    return body, back_foot, front_foot, eye


BODY, BACK_FOOT, FRONT_FOOT, EYE_OPEN = _split_parts()


def _rows(rows):
    return np.array([list(r) for r in rows])


BLUSH = _rows(['.PPP..',
               'PPPPP.',
               'PPPPPP',
               'PPPPPP',
               'PPPPPP',
               '.PPPP.'])

EYES = {
    'open': EYE_OPEN[10:17, 20:27],
    'closed': _rows(['.......',
                     '.......',
                     '..KKK..',
                     '.K...K.',
                     'K.....K',
                     '.......',
                     '.......']),
    'wince': _rows(['.......',
                    '.KK....',
                    '...KK..',
                    '.....K.',
                    '...KK..',
                    '.KK....',
                    '.......']),
    'surprised': _rows(['..KKK..',
                        '.KWWWK.',
                        'KWWWWWK',
                        'KWWKWWK',
                        'KWWWWWK',
                        '.KWWWK.',
                        '..KKK..']),
    'dizzy': _rows(['.KKKK..',
                    'K....K.',
                    'K.KK.K.',
                    'K.K..K.',
                    'K..KK..',
                    '.K.....',
                    '.......']),
}

MOUTHS = {
    'smile': _rows(['N....',
                    '.NNNN']),
    'open': _rows(['N....',
                   '.NNNN',
                   '.NMTN',
                   '..NN.']),
    'flat': _rows(['.....',
                   '.NNNN']),
    'frown': _rows(['.....',
                    '.NNNN',
                    'N....']),
    'o': _rows(['.....',
                '..NN.',
                '.NMMN',
                '..NN.']),
}

SWEAT = _rows(['.S',
               'SS',
               'SS'])


@dataclass
class Pose:
    """One frame. Offsets are pixels; angles are degrees clockwise on
    screen (0 = forward, 90 = down)."""
    dx: int = 0                # whole character offset
    dy: int = 0
    squash: int = 0            # rows removed at the waist (< 0 stretches)
    neck: int = 0              # rows removed at the neck (head sinks)
    lean: int = 0              # top of the body shifted by this many px
    arm: float = 45.0
    arm_len: float = 11.0
    back_foot: tuple = (0, 0)
    front_foot: tuple = (0, 0)
    eyes: str = ''             # '' = character default
    mouth: str = ''            # '' = character default
    blush: bool = True
    sweat: bool = False
    dive: int = 0              # 1 = body turned flat (diving), 2 = lying


class Figure:
    """The standing character composited into a frame grid, with a map from
    base coordinates to frame coordinates for the arm and the stamps."""

    def __init__(self, pose):
        self.pose = pose
        self.rows = self._row_map()
        self.top = BODY.shape[0] - len(self.rows)
        self.grid = np.full((SIZE, SIZE), '.', dtype='<U1')
        self._paste(BACK_FOOT, pose.back_foot)
        self._paste_body()
        self._paste(FRONT_FOOT, pose.front_foot)

    def _row_map(self):
        """Source rows of the body after the squash/neck edits; the bottom
        stays put so the feet stay on the ground."""
        rows = list(range(BODY.shape[0]))
        for at, n in ((TORSO_ROW, self.pose.squash),
                      (NECK_ROW, self.pose.neck)):
            i = rows.index(at)
            if n > 0:
                del rows[i:i + n]
            elif n < 0:
                rows[i:i] = [at] * (-n)
        return rows

    def shear(self, fy):
        """Horizontal shift of frame row fy for the lean (0 at the hips)."""
        if not self.pose.lean:
            return 0
        bottom = Y0 + self.pose.dy + 50
        top = Y0 + self.pose.dy + self.top
        t = (bottom - fy) / max(bottom - top, 1)
        return int(round(self.pose.lean * min(max(t, 0.0), 1.0)))

    def to_frame(self, x, y):
        """Base coordinates -> frame coordinates."""
        p = self.pose
        yi = int(round(y))
        k = min(range(len(self.rows)), key=lambda i: abs(self.rows[i] - yi))
        fy = Y0 + p.dy + self.top + k + (y - yi)
        return X0 + p.dx + x + self.shear(fy), fy

    def _put(self, fx, fy, ch):
        if 0 <= fx < SIZE and 0 <= fy < SIZE and ch != '.':
            self.grid[fy, fx] = ch

    def _paste_body(self):
        p = self.pose
        for k, sy in enumerate(self.rows):
            fy = Y0 + p.dy + self.top + k
            sh = self.shear(fy)
            for sx, ch in enumerate(BODY[sy]):
                self._put(X0 + p.dx + sx + sh, fy, ch)

    def _paste(self, part, off):
        p = self.pose
        for y, x in zip(*np.nonzero(part != '.')):
            self._put(X0 + p.dx + x + off[0], Y0 + p.dy + y + off[1],
                      part[y, x])

    def stamp(self, stamp, at):
        """Stamp onto body pixels only."""
        fx0, fy0 = (int(round(v)) for v in self.to_frame(*at))
        for j, row in enumerate(stamp):
            for i, ch in enumerate(row):
                x, y = fx0 + i, fy0 + j
                if (ch != '.' and 0 <= x < SIZE and 0 <= y < SIZE
                        and self.grid[y, x] != '.'):
                    self.grid[y, x] = ch


def _draw_arm(grid, sx, sy, angle, length, r=2.6):
    """Flat jelly paddle from (sx, sy): outline, base fill and a light line
    along its upper edge."""
    a = np.radians(angle)
    d = np.array([np.cos(a), np.sin(a)])
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    px, py = xs + 0.5 - sx, ys + 0.5 - sy
    t = np.clip(px * d[0] + py * d[1], 0, length)
    qx, qy = px - t * d[0], py - t * d[1]
    mask = np.hypot(qx, qy) <= r
    inner = mask & _inner(mask)
    n = np.array([d[1], -d[0]])     # a normal of the paddle...
    if n[1] > 0 or (n[1] == 0 and n[0] > 0):
        n = -n                      # ...the one pointing up
    side = qx * n[0] + qy * n[1]
    raw = np.clip(px * d[0] + py * d[1], -r, None)
    # leave the shoulder end open where the arm joins the body
    joined = (raw < 1.0) & (grid != '.')
    grid[mask] = 'b'
    grid[inner & (side > r * 0.35) & (raw > 1.0)] = 'l'
    grid[mask & ~inner & ~joined] = 'O'


def build_grid(character_id, pose):
    pal = PALETTES[character_id]
    eyes = pose.eyes or pal['eyes']
    if pal['eyes'] == 'closed' and eyes == 'open':
        eyes = 'closed'
    mouth = pose.mouth or pal['mouth']

    if not pose.dive:
        fig = Figure(pose)
        if pose.blush:
            fig.stamp(BLUSH, BLUSH_AT)
        fig.stamp(EYES[eyes], EYE_AT)
        fig.stamp(MOUTHS[mouth], MOUTH_AT)
        if pose.sweat:
            fig.stamp(SWEAT, SWEAT_AT)
        _draw_arm(fig.grid, *fig.to_frame(*SHOULDER), pose.arm, pose.arm_len)
        return fig.grid

    # diving / lying: the standing body turned flat, head first, with the
    # face put back on the front of the head so it looks ahead
    fig = Figure(replace(pose, dx=0, dy=0))
    fig.grid[np.isin(fig.grid, ['N'])] = 'O'
    flat = np.rot90(fig.grid, k=-1)
    ys, xs = np.nonzero(flat != '.')
    flat = flat[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    if pose.dive == 2:  # lying: a little flatter
        mid = flat.shape[0] // 2
        flat = np.delete(flat, [mid, mid + 1], axis=0)
    grid = np.full((SIZE, SIZE), '.', dtype='<U1')
    h, w = flat.shape
    ox = (SIZE - w) // 2 + pose.dx
    oy = SIZE - 2 - h + pose.dy
    for y, x in zip(*np.nonzero(flat != '.')):
        if 0 <= x + ox < SIZE and 0 <= y + oy < SIZE:
            grid[y + oy, x + ox] = flat[y, x]

    def put(stamp, x0, y0):
        for j, row in enumerate(stamp):
            for i, ch in enumerate(row):
                x, y = ox + x0 + i, oy + y0 + j
                if ch != '.' and 0 <= x < SIZE and 0 <= y < SIZE                         and grid[y, x] != '.':
                    grid[y, x] = ch

    # arm reaching forward under the chin, then the face over it
    _draw_arm(grid, ox + w - 20, oy + h - 7, pose.arm, pose.arm_len)
    if pose.blush:
        put(BLUSH, w - 17, h - 17)
    put(EYES[eyes], w - 12, h - 22)
    put(_rows(['NN', 'NN']), w - 3, h - 15)
    put(MOUTHS[mouth], w - 7, h - 11)
    return grid


def build_frame(character_id, pose):
    colors = {k: hex_rgb(v) for k, v in {**COMMON,
                                         **PALETTES[character_id]}.items()
              if len(k) == 1}
    grid = build_grid(character_id, pose)
    px = np.zeros((SIZE, SIZE, 4), dtype=np.uint8)
    for ch, rgb in colors.items():
        px[grid == ch] = (*rgb, 255)
    return Image.fromarray(px, 'RGBA')
