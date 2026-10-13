# Roadmap

## Phase 0: recover and lock the known-good baseline

Recover the actual v9.3.5 and v9.3.6 local build archives and the input manifest. Record SHA-256 for the source data and produced output, changes from v9.3.5 to v9.3.6, Switch game version, region, emulator/hardware, test locations, and installation instructions. Confirm that the game starts, saves/loads, plays Japanese voices, and displays the updated opening and initial menu.

**Do not** merge the failed experimental v9.2.16 dialogue pagination code.

## Phase 1: opening and movie audit

Inventory the remaining ~50 movies, including relative paths, durations, codecs, subtitle/text content, language, audio tracks and any UI references. Group by (a) Japanese text on screen, (b) language-neutral video, (c) unknown. For each localization candidate, document an English-visual/Japanese-audio approach and test syncing, playback and transitions.

Do not replace every movie automatically; do not redistribute the source videos.

## Phase 2: dialogue engine investigations

Reproduce long-dialogue failures, preferably with one minimal English record per UI class. Identify text delimiters, variable/placeholders, any explicit newline/page markers, buffer sizes, text measurement, pagination behavior and portrait metadata. Compare short and long cases to determine whether the constraint is bytes, glyph count, pixel width, or page state. Apply isolated fixes to a separate test branch and measure against the preserved baseline.

Maintain a source-faithful script and apply shortening **only** for labelled diagnosis or where no functional alternative exists.

## Phase 3: menu and naming completeness

Check control scheme names, camera settings descriptions, character naming alphabet/keyboard, adventure log/save slot text, shop names/prices/descriptions, other HUD labels, and portrait overlays. Confirm dynamic tokens and markers are preserved.

## Phase 4: compatibility, validation, distribution

Only after baseline stability, compare Switch update 1.03 with 1.0.0. Determine whether patch paths, resource layouts or executables have changed. Complete extended playtesting, create installation/rollback instructions, and distribute source-free tools or legally reviewed patch/delta files rather than copyrighted game content.

## Release gate

Do not publish a release until build inputs, reproducibility, hashes, patch contents, regressions, installation and rollback have been verified.
