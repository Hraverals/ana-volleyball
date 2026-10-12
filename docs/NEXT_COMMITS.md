# Next commit candidates

Out of scope for the current ANA remake work. Recorded here instead of being done now.

## Assets still showing Pokémon / Pikachu

- The original `pikachu/pikachu_*.png` player frames are no longer drawn but still sit in the sprite sheet. Overwrite or drop them (the packer keeps every existing name today).
- The Korean `game_start.png` and the common `ready.png` / `game_end.png` messages still use the original lettering (no Japanese left); restyle them to match the new jelly logo if wanted.
- Title and menu textures are rasterized from Windows fonts (Arial Black, Malgun Gothic). Bundle an open pixel font so `tools/pixelart/titles.py` gives the same output on any OS.
- Replace sound effects (`WAVE140`–`WAVE144`, Pikachu voices)
- Update the icons (`IDI_PIKAICON-*`), HTML titles and the web manifest

## Character select

- The player markers reuse the red score digits "1" and "2". Dedicated "1P" / "2P" label textures (and a "select your character" title) would read better.
- The dimmed room behind the select screen could get a slow idle animation or a spotlight on the slot under each cursor.
- Remember the last picks between games instead of resetting to a_teal / n_blue.

## Indoor effects instead of clouds and wave

Clouds and wave are hidden in the room background (their model still runs so the shared `rand()` sequence is unchanged). Ideas for indoor replacements:

- Dust motes drifting slowly in light from the ceiling lamps, driven by the existing cloud model (same count, positions and speeds), so no extra `rand()` calls are needed
- A faint flicker of one fluorescent ceiling light, reusing the wave model's per-frame values

## Dev tooling

- The service worker caches the dev server's assets too, so `npm run start` can show an old build after changes. Consider skipping service worker registration in development builds.
