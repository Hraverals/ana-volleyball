# Next commit candidates

Out of scope for the current ANA remake work. Recorded here instead of being done now.

## Remaining Pikachu parts and asset follow-ups

- The original `pikachu/pikachu_*.png` player frames are no longer drawn but still sit in the sprite sheet. Overwrite or drop them (the packer keeps every existing name today).
- The Korean `game_start.png` and the common `ready.png` / `game_end.png` messages still use the original lettering (no Japanese left); restyle them to match the new jelly logo if wanted.
- Title and menu textures are rasterized from Windows fonts (Arial Black, Malgun Gothic). Bundle an open pixel font so `tools/pixelart/titles.py` gives the same output on any OS.
- Sound effects (`WAVE140`–`WAVE144`, Pikachu voices) stay as they are until new sounds are prepared separately; swap the files behind `SOUNDS.*` in `assets_path.js` when they are ready.
- The "playing inside another website" notice links to the GitHub Pages address (https://hraverals.github.io/ana-volleyball/); switch it to the club server's address when the game moves there.

## Character select

- The player markers reuse the score digits "1" and "2". Dedicated "1P" / "2P" label textures (and a "select your character" title) would read better.
- The dimmed room behind the select screen could get a slow idle animation or a spotlight on the slot under each cursor.
- Remember the last picks between games instead of resetting to a_teal / n_blue.

## Indoor effects instead of clouds and wave

Clouds and wave are hidden in the room background (their model still runs so the shared `rand()` sequence is unchanged). Ideas for indoor replacements:

- Dust motes drifting slowly in light from the ceiling lamps, driven by the existing cloud model (same count, positions and speeds), so no extra `rand()` calls are needed
- A faint flicker of one fluorescent ceiling light, reusing the wave model's per-frame values

## Dev tooling

- Starting the dev server runs `CleanWebpackPlugin`, which empties the real `dist/` folder (the dev build itself lives in memory). Run `npm run build` again after `npm run start` if you need `dist/`.
