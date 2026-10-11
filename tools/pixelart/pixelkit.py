"""Small pixel-art toolkit for the "3D pixel" style.

Shapes are boolean masks on a pixel grid. A part is a mask plus a color ramp;
it is shaded as a soft dome lit from the upper left and outlined with the
darkest tone of its ramp.
"""

import numpy as np
from PIL import Image

# Light comes from the upper left, slightly toward the viewer.
LIGHT = np.array([-0.6, -0.7, 0.9])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


class Canvas:
    """RGBA pixel canvas of size w x h."""

    def __init__(self, w, h, fill=(0, 0, 0, 0)):
        self.w, self.h = w, h
        self.px = np.zeros((h, w, 4), dtype=np.uint8)
        self.px[:, :] = fill

    def paint(self, mask, color):
        rgba = color if len(color) == 4 else (*color, 255)
        self.px[mask] = rgba

    def image(self):
        return Image.fromarray(self.px, 'RGBA')


def grid(w, h):
    """Pixel center coordinates."""
    ys, xs = np.mgrid[0:h, 0:w]
    return xs + 0.5, ys + 0.5


def transform(xs, ys, cx=0.0, cy=0.0, angle=0.0, dx=0.0, dy=0.0):
    """Inverse-map sample points so a shape is rotated by `angle` degrees
    (clockwise on screen) around (cx, cy) and then moved by (dx, dy)."""
    a = np.radians(angle)
    x = xs - dx - cx
    y = ys - dy - cy
    return (x * np.cos(a) + y * np.sin(a) + cx,
            -x * np.sin(a) + y * np.cos(a) + cy)


def ellipse(xs, ys, cx, cy, rx, ry):
    return ((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2 <= 1.0


def polygon(xs, ys, pts):
    """Even-odd point-in-polygon test."""
    inside = np.zeros(xs.shape, dtype=bool)
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        cond = (y1 > ys) != (y2 > ys)
        with np.errstate(divide='ignore', invalid='ignore'):
            xint = (x2 - x1) * (ys - y1) / (y2 - y1) + x1
        inside ^= cond & (xs < xint)
    return inside


def rect(xs, ys, x0, y0, x1, y1):
    return (xs >= x0) & (xs < x1) & (ys >= y0) & (ys < y1)


def round_poly(xs, ys, pts, r):
    """Polygon with corners rounded by radius r (offset of a shrunk polygon)."""
    shrunk = polygon(xs, ys, _inset(pts, r))
    return dilate(shrunk, r)


def _inset(pts, r):
    pts = np.array(pts, dtype=float)
    c = pts.mean(axis=0)
    out = []
    n = len(pts)
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        e1 = p1 - p0
        e2 = p2 - p1
        n1 = np.array([e1[1], -e1[0]]) / np.linalg.norm(e1)
        n2 = np.array([e2[1], -e2[0]]) / np.linalg.norm(e2)
        # normals should point inward (toward centroid)
        if np.dot(n1, c - p1) < 0:
            n1 = -n1
        if np.dot(n2, c - p1) < 0:
            n2 = -n2
        bis = n1 + n2
        bis /= np.linalg.norm(bis)
        cos_half = np.dot(bis, n1)
        out.append(tuple(p1 + bis * r / max(cos_half, 0.2)))
    return out


def dilate(mask, r):
    out = mask.copy()
    ri = int(np.ceil(r))
    for dy in range(-ri, ri + 1):
        for dx in range(-ri, ri + 1):
            if dx * dx + dy * dy <= r * r + 0.25:
                out |= shift(mask, dx, dy)
    return out


def shift(mask, dx, dy):
    out = np.zeros_like(mask)
    h, w = mask.shape
    xs0, xs1 = max(0, dx), min(w, w + dx)
    ys0, ys1 = max(0, dy), min(h, h + dy)
    out[ys0:ys1, xs0:xs1] = mask[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
    return out


def edge(mask):
    """Pixels of mask that touch the outside (4-neighborhood)."""
    inner = (mask & shift(mask, 1, 0) & shift(mask, -1, 0)
             & shift(mask, 0, 1) & shift(mask, 0, -1))
    return mask & ~inner


def distance_inside(mask, limit=12):
    """Chamfer-ish distance from each mask pixel to the outside."""
    dist = np.zeros(mask.shape, dtype=float)
    cur = mask.copy()
    for i in range(limit):
        dist[cur] += 1
        cur = cur & ~edge(cur)
        if not cur.any():
            break
    return dist


def shade_levels(mask, levels, radius=7.0, bias=0.0):
    """Quantized dome lighting. Returns an int array: 0 = darkest ramp tone
    (just inside the outline) ... levels-1 = brightest."""
    d = distance_inside(mask, limit=int(radius) + 2)
    hgt = np.sqrt(np.clip(d / radius, 0, 1)) * radius
    gy, gx = np.gradient(hgt)
    nz = np.ones_like(hgt) * 1.2
    norm = np.sqrt(gx ** 2 + gy ** 2 + nz ** 2)
    nx, ny, nzz = -gx / norm, -gy / norm, nz / norm
    lam = nx * LIGHT[0] + ny * LIGHT[1] + nzz * LIGHT[2]
    # a little extra light toward the top-left of the part as a whole
    ys, xs = np.nonzero(mask)
    if len(xs):
        yy, xx = np.mgrid[0:mask.shape[0], 0:mask.shape[1]]
        span = max(xs.max() - xs.min(), ys.max() - ys.min(), 1)
        tilt = -((xx - xs.mean()) + (yy - ys.mean())) / span * 0.2
        lam = lam + tilt
    lam = lam + bias
    q = np.clip(((lam - 0.35) / 0.6) * levels, 0, levels - 1).astype(int)
    return q


class Part:
    """A shaded, outlined layer."""

    def __init__(self, mask, ramp, outline=True, radius=7.0, bias=0.0,
                 flat=None):
        self.mask = mask
        self.ramp = ramp  # [outline, darkest, ..., brightest]
        self.outline = outline
        self.radius = radius
        self.bias = bias
        self.flat = flat  # index into ramp to fill flat instead of shading

    def draw(self, canvas):
        m = self.mask
        if not m.any():
            return
        body = m & ~edge(m) if self.outline else m
        if self.flat is not None:
            canvas.paint(body, self.ramp[self.flat])
        else:
            lv = shade_levels(m, len(self.ramp) - 1, self.radius, self.bias)
            for i, col in enumerate(self.ramp[1:]):
                canvas.paint(body & (lv == i), col)
        if self.outline:
            canvas.paint(edge(m), self.ramp[0])


def upscale(img, k):
    return img.resize((img.width * k, img.height * k), Image.NEAREST)
