# Next commit candidates

Out of scope for the current ANA remake work. Recorded here instead of being done now.

## Assets still showing Pokémon / Pikachu

- Replace title and logo textures: `messages/*/pokemon.png`, `pikachu_volleyball.png`, `mark.png`, `fight.png`, `messages/common/sachisoft.png`
- Replace `sitting_pikachu.png` on the menu with the ANA characters
- Reskin the ball and the score numbers. The current ball's gray lower half sits close to the room wall's tone; a new ball should keep a dark outline and a bright, saturated face.
- Replace sound effects (`WAVE140`–`WAVE144`, Pikachu voices)
- Update the icons (`IDI_PIKAICON-*`), HTML titles and the web manifest

## Indoor effects instead of clouds and wave

Clouds and wave are hidden in the room background (their model still runs so the shared `rand()` sequence is unchanged). Ideas for indoor replacements:

- Dust motes drifting slowly in light from the ceiling lamps, driven by the existing cloud model (same count, positions and speeds), so no extra `rand()` calls are needed
- A faint flicker of one fluorescent ceiling light, reusing the wave model's per-frame values

## Dev tooling

- The service worker caches the dev server's assets too, so `npm run start` can show an old build after changes. Consider skipping service worker registration in development builds.
