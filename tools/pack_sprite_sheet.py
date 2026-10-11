"""Regenerate sprite_sheet.png / sprite_sheet.json with the ANA assets.

    python tools/pack_sprite_sheet.py

Every frame already in the sheet is kept under its name (the pikachu frames,
messages, ball, ...). The ANA textures are rendered from tools/pixelart and
added or replaced by name:

- players/{id}/{id}_{state}_{frame}.png for each character
- objects/background.png (432x304) and objects/net.png
- title, logo and menu textures from tools/pixelart/titles.py (replacing the
  Pokémon / Pikachu ones under the same names)

The whole sheet is then repacked with a simple shelf packer and written in
the same TexturePacker "JSON Hash" format, so running this again gives the
same result.
"""

import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'pixelart'))

from background import build_background, build_net  # noqa: E402
from characters import PALETTES, build_frame  # noqa: E402
from poses import POSES  # noqa: E402
from titles import textures as title_textures  # noqa: E402

ROOT = os.path.dirname(HERE)
SHEET_DIR = os.path.join(ROOT, 'src', 'resources', 'assets', 'images')
SHEET_PNG = os.path.join(SHEET_DIR, 'sprite_sheet.png')
SHEET_JSON = os.path.join(SHEET_DIR, 'sprite_sheet.json')

SHEET_WIDTH = 1024
PAD = 2


def load_existing():
    with open(SHEET_JSON, encoding='utf-8') as f:
        data = json.load(f)
    sheet = Image.open(SHEET_PNG).convert('RGBA')
    frames = {}
    for name, info in data['frames'].items():
        if info['rotated'] or info['trimmed']:
            raise ValueError(f'{name}: rotated/trimmed frames are not supported')
        r = info['frame']
        frames[name] = sheet.crop((r['x'], r['y'], r['x'] + r['w'],
                                   r['y'] + r['h']))
    return data['meta'], frames


def ana_textures():
    out = {}
    for character_id in PALETTES:
        for (state, frame), pose in POSES.items():
            name = (f'players/{character_id}/'
                    f'{character_id}_{state}_{frame}.png')
            out[name] = build_frame(character_id, pose)
    out['objects/background.png'] = build_background()
    out['objects/net.png'] = build_net()
    out.update(title_textures())
    return out


def pack(images):
    """Shelf packing, tallest first. Returns {name: (x, y)} and height."""
    order = sorted(images, key=lambda n: (-images[n].height,
                                          -images[n].width, n))
    pos = {}
    x, y, shelf = PAD, PAD, 0
    for name in order:
        w, h = images[name].size
        if x + w + PAD > SHEET_WIDTH:
            x, y = PAD, y + shelf + PAD
            shelf = 0
        pos[name] = (x, y)
        x += w + PAD
        shelf = max(shelf, h)
    return pos, y + shelf + PAD


def main():
    meta, frames = load_existing()
    frames.update(ana_textures())
    pos, height = pack(frames)

    sheet = Image.new('RGBA', (SHEET_WIDTH, height), (0, 0, 0, 0))
    out_frames = {}
    for name in frames:  # keep the existing names first, in their order
        img = frames[name]
        x, y = pos[name]
        sheet.alpha_composite(img, (x, y))
        w, h = img.size
        out_frames[name] = {
            'frame': {'x': x, 'y': y, 'w': w, 'h': h},
            'rotated': False,
            'trimmed': False,
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': w, 'h': h},
            'sourceSize': {'w': w, 'h': h},
        }

    meta = {k: v for k, v in meta.items() if k != 'smartupdate'}
    meta['size'] = {'w': SHEET_WIDTH, 'h': height}
    sheet.save(SHEET_PNG, optimize=True)
    with open(SHEET_JSON, 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'frames': out_frames, 'meta': meta}, f, indent='\t')
        f.write('\n')
    print(f'{len(out_frames)} frames, sheet {SHEET_WIDTH}x{height}')


if __name__ == '__main__':
    main()
