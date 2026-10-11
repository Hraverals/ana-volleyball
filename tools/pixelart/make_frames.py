"""Render all 27 frames of each character into tools/pixelart/out/frames/.

    python tools/pixelart/make_frames.py [character_id ...]

Writes players/{id}/{id}_{state}_{frame}.png plus, for review, a contact
sheet per character (1x and 4x, one row per state), a 4x strip per state
and an animated GIF per state played with the game's frame timing.
"""

import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from characters import PALETTES, build_frame  # noqa: E402
from pixelkit import upscale  # noqa: E402
from poses import FRAME_COUNTS, POSES  # noqa: E402

OUT = os.path.join(HERE, 'out', 'frames')
CELL = 64
GAP = 4


BG = (226, 224, 218, 255)

# (frame order, ms per frame, ms to hold the last frame) as physics.js
# plays them at 25 fps
PLAYBACK = {
    0: ([0, 1, 2, 3, 4, 3, 2, 1], 160, 160),
    1: ([0, 1, 2], 40, 40),
    2: ([0, 1, 2, 3, 4], 40, 600),
    3: ([0, 1], 120, 120),
    4: ([0], 1000, 1000),
    5: ([0, 1, 2, 3, 4], 200, 1200),
    6: ([0, 1, 2, 3, 4], 200, 1200),
}


def review_files(character_id, frames):
    for state, count in enumerate(FRAME_COUNTS):
        strip = Image.new('RGBA', (count * (CELL + GAP) + GAP, CELL + 2 * GAP),
                          BG)
        for f in range(count):
            strip.alpha_composite(frames[(state, f)],
                                  (GAP + f * (CELL + GAP), GAP))
        upscale(strip, 4).save(
            os.path.join(OUT, f'{character_id}_state{state}_x4.png'))

        order, ms, hold = PLAYBACK[state]
        imgs = []
        for f in order:
            cell = Image.new('RGBA', (CELL, CELL), BG)
            cell.alpha_composite(frames[(state, f)])
            imgs.append(upscale(cell, 4).convert('RGB'))
        durations = [ms] * (len(order) - 1) + [hold]
        imgs[0].save(os.path.join(OUT, f'{character_id}_state{state}.gif'),
                     save_all=True, append_images=imgs[1:], loop=0,
                     duration=durations, disposal=2)


def render(character_id):
    folder = os.path.join(OUT, 'players', character_id)
    os.makedirs(folder, exist_ok=True)
    sheet = Image.new('RGBA', (5 * (CELL + GAP) + GAP,
                               len(FRAME_COUNTS) * (CELL + GAP) + GAP),
                      (226, 224, 218, 255))
    frames = {}
    for (state, frame), pose in POSES.items():
        img = build_frame(character_id, pose)
        frames[(state, frame)] = img
        img.save(os.path.join(folder,
                              f'{character_id}_{state}_{frame}.png'))
        sheet.alpha_composite(img, (GAP + frame * (CELL + GAP),
                                    GAP + state * (CELL + GAP)))
    sheet.save(os.path.join(OUT, f'{character_id}_sheet.png'))
    upscale(sheet, 4).save(os.path.join(OUT, f'{character_id}_sheet_x4.png'))
    review_files(character_id, frames)


def main():
    ids = sys.argv[1:] or list(PALETTES)
    for character_id in ids:
        render(character_id)


if __name__ == '__main__':
    main()
