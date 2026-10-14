# M1 v9.3.14-EXP: persistent sprite pool for full Points Required and no description-budget loss

**Status: OFFLINE VERIFIED; EDEN PENDING.** Japanese DQH1 Switch 1.0.0 with official Western PC text transplanted.

This experimental source-only release follows **v9.3.13-EXP's unsuccessful sprite trade-off**: its Points Required (15) heading worked but its dynamic skill description was reduced 36→31, visibly shortening Inferno Slash. The **required previous Eden-tested base is v9.3.12-EXP**, with Requirements (12), Details (8), and optionally X-held Action List pagination. Do **not** apply the patch on top of v9.3.13.

## Capacity layout

| Field | v9.3.12 | v9.3.13 rejected | v9.3.14-EXP |
| --- | ---: | ---: | ---: |
| Points Required | 10 | 15 | **15** |
| Requirements | 12 | 12 | **12** |
| Details | 8 | 8 | **8** |
| Dynamic Details description | 36 | 31 | **36**, relocated into appended BSS |

Three headings use precisely **35 native slots** at object offsets `+0x600..+0xFD8`: Points `+0x600..+0xA38`, Requirements `+0xA38..+0xD98`, Details `+0xD98..+0xFD8`. The dynamic field retains its original **36×72-byte = 0xA20-byte** limit but uses a new memory-backed pool at virtual address `0x33B3000`. The NSO `bss_size` grows one page, **0xD42FF8 → 0xD43FF8**, leaving space through `0x33B4000`. BSS is zero on startup, so a 52-byte isolated AArch64 helper clones the **existing initialized 36 native sprite objects** from `this+0xE70` (324 eight-byte words) into the new BSS page before passing its pointer to `CFont::SetStrPrim`.

Four original AArch64 instruction sites are modified: `0x21BF28`, `0x21BFB4`, `0x21C050`, `0x21C11C`. The last site is a `BL` to helper VA `0x11B7800`. Its sole `ADRP` resolves to the new BSS page at `0x33B3000` after the module is loaded. The existing code area is padded only into its original gap before rodata at `0x11B8000`. When present, the earlier Action List pagehook occupies `0x11B7700..0x11B7784` and remains byte-identical; the new helper starts at `0x11B7800`.

No game texts, scripts, LINKDATA, original Japanese voices, movies, or save files are modified.

## Strict input and output provenance

| Exact v9.3.12 source | Source main SHA-256 | Expected experimental main SHA-256 |
| --- | --- | --- |
| Requirements/Details only | `7814f92c976fe0e5deb94dab614f7744a9f69740fce9ab3a63402ad0605bd5b1` | `27887e3bb16b25a641efc22419d5a3c9083a8dbc5b1e6d024c47820f4b839311` |
| Requirements/Details **plus** X pagehook | `bebddffd0352eee6a0a1951379115792545cbb0d15f801d88da7ac8ac6fb1b4e` | `376acf9e707319edd0c80126c7da53415d78f879b804e9a50ce52f15f906e7fb` |

The Python patcher **refuses all other input hashes** (including v9.3.13). Generated mains are excluded from the GitHub repository. Source-only experimental ZIP supplied in the conversation: `DQH1_M1_v9.3.14_EXP_BSS_Description_Recovery.zip` (builder, isolated hook assembly, six-test suite, usage README).

## Offline verification

Six test groups passed using reconstructed versions of both exact source executables:
- original and modified code instructions, BSS alignment/bounds and AArch64 `ADRP` / `BL` targets;
- 52-byte helper's 324-word copy loop (36 sprites), preservation of live registers;
- complete NSO section compression/decompression/hash roundtrip, with rodata and data byte-identical;
- unchanged original font limit **36**, Points Required **15**, Requirements **12**, Details **8**;
- exact X pagehook and corresponding text bytes untouched in the combined build;
- byte-for-byte deterministic output and refusal to patch unrelated executable revisions.

**Critical remaining runtime risks:** Switch NSO loader accepting increased BSS allocation; the sprite renderer registering externally stored glyph objects; concurrent skill instances sharing one new static pool; font style correctness after cloning existing initialized sprites. Static tests cannot establish these behaviors. The allocated pool is persistent (not transient stack or prematurely freed heap memory), but not yet proven safe across all gameplay states.

## Eden acceptance test

Use the current installed **compatible v9.3.11/v9.3.12 gameplay LINKDATA**, with the independently preserved starting-menu LINKDATA. Install the new `exefs/main` in a separate override, **never overwrite the v9.3.12 rollback**, and do not save on first launch.

1. Boot successfully past the Anniversary opening and enter Skill Tree.
2. Verify complete **Points Required**, **Requirements**, **Details** headings.
3. **Primary regression test:** Inferno Slash should recover at least its previously visible `Summons a fiery tornado that sweeps` (v9.3.12), not v9.3.13's `...that sw`. A longer description is still not guaranteed to display completely because this experiment restores only 36 slots, not the full PC sentence.
4. Switch characters and select unlocked/locked skills; check for blank glyphs, missing fonts, flicker, memory/display overlap or crashing.
5. In the combined X-pagehook version, holding X should show Action List page 2, releasing should restore page 1.
6. Restore the v9.3.12 `exefs/main` immediately if anomalies appear.

Other category headings (`Attributes`, `Spells and Abilities`, `Switch Character`, `Skill Points`), long skill names, and `ESC F/I/G` variable/code interpretation remain **unmodified and tracked separately** in [#10](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/10) and [#12](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/12).

**No Eden confirmation or stable release is claimed for v9.3.14.**


## First Eden result (2026-10-14): primary description-regression recovery confirmed

The user tested v9.3.14-EXP in Eden and supplied a Luceus **Inferno Slash** skill screenshot. The description again shows `Summons a fiery tornado that sweeps` (same visible text as in v9.3.12, versus v9.3.13's `...that sw`). Both `Details` and `Requirements` headings are complete and there is no obvious missing sprite or corruption in this single screen. This is a successful **focused runtime demonstration** of the newly allocated/restored 36-slot capacity, **not a complete proof of concurrent-state safety or layout correctness**.

`Points Required` was not displayed in this specific screenshot; verify it on a point-costing/locked skill. Recheck Aurora/other characters, open/close transitions, the prior X-held Action List pagination, and repeated selection for any external static BSS pool conflict. Keep v9.3.14-EXP experimental until these checks pass. The full official Inferno Slash description extends beyond `sweeps`, so **description remains incomplete** even though the regression was reversed.
