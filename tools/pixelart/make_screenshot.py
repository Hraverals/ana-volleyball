"""Compose the page's game screenshot from the game textures.

    python tools/pixelart/make_screenshot.py

Writes src/resources/assets/images/screenshot.png (1728x1216, the 432x304
game screen at 4x) with the room, the whiteboard net, a_teal jumping on the
left, n_blue standing on the right, the ball and the score digits, placed at
the game's own coordinates.
"""

import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from background import NET_X, NET_Y, build_background, build_net  # noqa: E402
from ball import ball_frame, number  # noqa: E402
from characters import build_frame  # noqa: E402
from pixelkit import upscale  # noqa: E402
from poses import POSES  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'src', 'resources', 'assets', 'images',
                   'screenshot.png')


def shadow():
    """The game's player/ball shadow: a 32x7 dithered ellipse."""
    img = Image.new('RGBA', (32, 7), (0, 0, 0, 0))
    px = img.load()
    for y in range(7):
        for x in range(32):
            inside = ((x + 0.5 - 16) / 16) ** 2 + ((y + 0.5 - 3.5) / 3.5) ** 2
            if inside <= 1 and (x + y) % 2 == 0:
                px[x, y] = (0, 0, 0, 255)
    return img


def main():
    screen = build_background()
    screen.alpha_composite(build_net(), (NET_X, NET_Y))

    # shadows sit at y = 273, centered on each x
    sh = shadow()
    for cx in (76, 360, 170):
        screen.alpha_composite(sh, (cx - 16, 273 - 3))

    # player centers: a_teal mid-jump at (76, 200), n_blue at (360, 244)
    p1 = build_frame('a_teal', POSES[(1, 0)])
    p2 = build_frame('n_blue', POSES[(0, 2)]).transpose(Image.FLIP_LEFT_RIGHT)
    screen.alpha_composite(p1, (76 - 32, 200 - 32))
    screen.alpha_composite(p2, (360 - 32, 244 - 32))

    # the ball in the air, centered at (170, 120)
    screen.alpha_composite(ball_frame(1), (170 - 20, 120 - 20))

    # score boards like GameView: 14 px from each side, y = 10
    for x0, score in ((14, 7), (432 - 32 - 32 - 14, 5)):
        tens, ones = divmod(score, 10)
        if tens:
            screen.alpha_composite(number(tens), (x0, 10))
        screen.alpha_composite(number(ones), (x0 + 32, 10))

    upscale(screen.convert('RGBA'), 4).convert('RGB').save(OUT,
                                                            optimize=True)
    print(OUT)


if __name__ == '__main__':
    main()
