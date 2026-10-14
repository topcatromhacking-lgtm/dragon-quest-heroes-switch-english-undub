# Roadmap

## Next active milestone: M1 — complete Western PC labels in Japanese Switch menus

**Started 2026-10-13.** [Milestone tracking issue](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/11); [pilot: skill tree #10](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/10); [related Action List #8](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/8).

Prioritize identifying and safely expanding per-widget **native Switch glyph/text capacity** where English has already been transplanted but clips despite available visual room. Preserve complete official Western PC terminology instead of repeatedly abbreviating. Pilot screenshot: `Attribut`, `Requiremen`, `Points Req`, `Skill Po`, `Switch Charac`, `Spells a`. Confirm the official source and storage of each; derive exact limits in the Japanese Switch 1.0.0 executable; prototype **one** isolated safe field fix, then test all related fields in Eden. Keep Japanese audio, saves, and the separate starting-menu archive unchanged; preserve v9.3.9 rollback.

After this pilot, address other verified text-capacity classes (including Action List single-window parity) without conflating their allocations. **No full-label executable patch is yet validated.**

---


## Phase 0: recover and lock the known-good baseline

Recover the actual v9.3.5 and v9.3.6 local build archives and the input manifest. Record SHA-256 for the source data and produced output, changes from v9.3.5 to v9.3.6, Switch game version, region, emulator/hardware, test locations, and installation instructions. Confirm that the game starts, saves/loads, plays Japanese voices, and displays the updated opening and initial menu.

**Do not** merge the failed experimental v9.2.16 dialogue pagination code.

## Phase 1: verify movie visuals; locate cutscene subtitle and audio resources

The user reviewed the **50 videos after the opening** (`mv003.mp4`–`mv052.mp4`) and reports **no visible textual characters**. The video streams therefore have no known visual-language localization requirement, and the plan is to **retain the Japanese originals**. The exception remains the reportedly localized opening `mv002.mp4`. This is a user visual assessment, not an independent file-by-file technical verification.

Audio and subtitles are suspected to be stored/controlled by **other assets**. Prior resource mapping identified the PC-Western `00000000000000bc.vap` ↔ Switch-JP `0000000000000064.vap` pair as **cutscene subtitles**. Revalidate that correspondence and investigate how subtitle calls, timing, speaker metadata, and audio are dispatched; do not assume all movies use this resource or that audio is necessarily outside the MP4 container.

Before changing files, establish one small runtime case: (1) identify the cutscene, (2) locate the corresponding subtitle record, (3) verify the Japanese line and official English equivalent, (4) determine where voiced audio comes from, and (5) confirm any patch preserves Japanese audio and synchronization. Do not alter video assets when the video has no Japanese text; do not redistribute copyrighted media.

Movie filename audit record: [MOVIE_INVENTORY.csv](MOVIE_INVENTORY.csv).

## Phase 2: dialogue engine investigations

Reproduce long-dialogue failures, preferably with one minimal English record per UI class. Identify text delimiters, variable/placeholders, any explicit newline/page markers, buffer sizes, text measurement, pagination behavior and portrait metadata. Compare short and long cases to determine whether the constraint is bytes, glyph count, pixel width, or page state. Apply isolated fixes to a separate test branch and measure against the preserved baseline.

Maintain a source-faithful script and apply shortening **only** for labelled diagnosis or where no functional alternative exists.

## Phase 3: menu and naming completeness

Check control scheme names, camera settings descriptions, character naming alphabet/keyboard, adventure log/save slot text, shop names/prices/descriptions, other HUD labels, and portrait overlays. Confirm dynamic tokens and markers are preserved.

## Phase 4: compatibility, validation, distribution

Only after baseline stability, compare Switch update 1.03 with 1.0.0. Determine whether patch paths, resource layouts or executables have changed. Complete extended playtesting, create installation/rollback instructions, and distribute source-free tools or legally reviewed patch/delta files rather than copyrighted game content.

## Release gate

Do not publish a release until build inputs, reproducibility, hashes, patch contents, regressions, installation and rollback have been verified.
