"""Render the Phase 3 art drafts into tools/pixelart/out/.

    python tools/pixelart/make_draft.py

Outputs a_teal state 0 frame 0, the room background and the whiteboard net,
each at 1x and 4x, the original pikachu frame for comparison, and an
in-game mockup.
"""

import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from background import NET_X, NET_Y, build_background, build_net  # noqa: E402
from characters import Pose, build_frame  # noqa: E402
from pixelkit import upscale  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
SHEET = os.path.join(ROOT, 'src', 'resources', 'assets', 'images')
OUT = os.path.join(HERE, 'out')


def original_frame(name):
    sheet = Image.open(os.path.join(SHEET, 'sprite_sheet.png')).convert('RGBA')
    with open(os.path.join(SHEET, 'sprite_sheet.json'), encoding='utf-8') as f:
        r = json.load(f)['frames'][name]['frame']
    return sheet.crop((r['x'], r['y'], r['x'] + r['w'], r['y'] + r['h']))


def save(img, name):
    img.save(os.path.join(OUT, name + '.png'))
    upscale(img, 4).save(os.path.join(OUT, name + '_x4.png'))


def main():
    os.makedirs(OUT, exist_ok=True)
    save(build_frame('a_teal', Pose()), 'a_teal_0_0')
    save(original_frame('pikachu/pikachu_0_0.png'), 'pikachu_0_0')

    bg = build_background()
    net = build_net()
    save(bg, 'background')
    save(net, 'net')
    composed = bg.copy()
    composed.alpha_composite(net, (NET_X, NET_Y))
    save(composed, 'background_with_net')

    # in-game mockup at the physics positions: players centered at
    # (36, 244) and (396, 244), shadows at y=273, ball in the air
    mock = composed.copy()
    shadow = original_frame('objects/shadow.png')
    player = Image.open(os.path.join(OUT, 'a_teal_0_0.png'))
    ball = original_frame('ball/ball_0.png')
    for cx in (36, 396, 150):
        mock.alpha_composite(shadow, (cx - 16, 273 - 3))
    mock.alpha_composite(player, (36 - 32, 244 - 32))
    mock.alpha_composite(player.transpose(Image.FLIP_LEFT_RIGHT),
                         (396 - 32, 244 - 32))
    mock.alpha_composite(ball, (150 - 20, 90 - 20))
    save(mock, 'mockup')


if __name__ == '__main__':
    main()
