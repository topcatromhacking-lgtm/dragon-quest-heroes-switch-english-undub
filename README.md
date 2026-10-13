# Dragon Quest Heroes I: Nintendo Switch English Undub

**Work in progress. Not a downloadable release.**

A community localization project for the Japanese Nintendo Switch edition of **Dragon Quest Heroes: The World Tree's Woe and the Blight Below**. The goal is to make the on-screen experience available in English **while preserving Japanese voice acting**.

This is an **English undub**, not an English-dub conversion or a redistribution of the commercial game.

## Project principles

- **Faithful first.** Retain the source material's meaning, characterisation, and complete dialogue. Do not shorten text merely for convenience. Temporary abbreviations may be used for explicitly labelled diagnostics, then reverted.
- **No regressions.** Work incrementally from a known-good baseline. Never combine speculative text-engine experiments with routine translation fixes.
- **Context-sensitive layout.** Dialogue windows, character portraits, menu descriptions, item names, and selection screens have different width/line constraints; test each independently.
- **Japanese voice track.** Keep the Japanese in-game voices and movie audio. Where a Western video variant is useful for English visuals, preserve the original Japanese audio.
- **Reproducible changes.** Maintain source-free scripts, manifests, test cases, and SHA-256 hashes before distributing patch tools.

## Current state (13 October 2026)

The work described below was completed and tested during earlier local development, **but its patch files and verification hashes have not yet been committed to this repository**. These are historical working-version labels, **not GitHub releases**.

| Area | Status |
| --- | --- |
| Japanese Switch base game | Development/test target: **1.0.0** |
| English dialogue and menus | Playable in reported tests; multiple remaining text/layout defects |
| Hero selection, initial menu | Changes reported validated in local testing |
| Western opening visuals | `mv002.mp4` substitution reported validated, with Japanese audio preserved |
| Latest reported local working baseline | **v9.3.6** (video change layered on reported v9.3.5 UI baseline) |
| Remaining movie assets | Inventory and localization audit pending |
| Long dialogue pagination / clipping | Unresolved; **do not use failed v9.2.16 experiment** |
| Japanese game update 1.03 | Compatibility assessment deferred |
| Switch hardware testing | Not yet documented in this repository |

See [development status](docs/STATUS.md), [roadmap](docs/ROADMAP.md), and [test matrix](docs/TESTING.md).

## Known critical regression

An earlier experimental dialogue pagination change (v9.2.16) led to widespread dialogue truncation/overflow and at least one **incorrect portrait switch to Terry**. This build is **not** a development baseline. Future text-engine changes must be isolated and tested against the regression cases before acceptance.

## Repository contents

Initially this repository contains documentation only. Patch scripts and reproducible manifests will be added after the local baseline files are recovered and independently checked. There is **no verified release ZIP here yet**.

## Distribution and legal notice

**Do not upload** copyrighted game dumps, decrypted game files, game executables, extracted ROMFS/EXEFS, proprietary DAT/VAP resources, voice recordings, Western opening MP4 files, or other original Square Enix/Koei Tecmo assets to this repository.

Any future public release should distribute only original tooling and appropriately reviewed patch/delta data that require users to provide their own legitimate game files. This is an unofficial fan project and is not affiliated with or endorsed by the rights holders.
