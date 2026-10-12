"""Make the page and app icons from the ANA favicon.

    python tools/make_icons.py

Source: src/resources/assets/images/favicon_ana.ico (the ANA logo on a
transparent background, up to 256x256). Writes next to it:

- ana_icon_32.png: the favicon's own 32x32 image, for browsers that take
  a PNG icon
- ana_icon_{48,192,512}.png: the logo centered on white with a margin, for
  the web manifest and the iOS home screen (which turns transparency black)
"""

import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGES = os.path.join(os.path.dirname(HERE), 'src', 'resources', 'assets',
                      'images')
SOURCE = os.path.join(IMAGES, 'favicon_ana.ico')

LOGO_WIDTH = 0.8  # logo width as a share of the icon width


def frame(ico, size):
    ico.size = (size, size)
    return ico.convert('RGBA')


def app_icon(logo, size):
    """Logo (cropped to its pixels) centered on a white square."""
    w = round(size * LOGO_WIDTH)
    h = round(logo.height * w / logo.width)
    scaled = logo.resize((w, h), Image.LANCZOS)
    icon = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    icon.alpha_composite(scaled, ((size - w) // 2, (size - h) // 2))
    return icon.convert('RGB')


def main():
    ico = Image.open(SOURCE)
    frame(ico, 32).save(os.path.join(IMAGES, 'ana_icon_32.png'))
    big = frame(ico, 256)
    logo = big.crop(big.getbbox())
    for size in (48, 192, 512):
        app_icon(logo, size).save(os.path.join(IMAGES,
                                               f'ana_icon_{size}.png'))


if __name__ == '__main__':
    main()
