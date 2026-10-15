# M1 v9.3.17-EXP: Register the Attributes BSS sprite pool in the native draw list

**2026-10-15 — Source-only patch and 7/7 offline tests passed; Eden user test PENDING. Not a stable release.**

## Finding that explains the failed v9.3.15 experiment

The native menu's registration function starts at **VA `0x326388`**, and calls `0x3269F8` at `0x3263A4` to update its display state and skill category heading glyphs. In the same registration function, the native sequence at **`0x3263D8..0x32642C`** appends a 24-byte draw-list entry for the **contiguous, owner-embedded sprite range**:

- `0x3263DC`: `add x9,x19,#0xE8`, the original draw range **start**;
- `0x3263E4`: `mov w10,#0x8D40`, followed by `0x3263E8: add x9,x9,x10`, which gives draw range **end `this+0x8E28`**;
- `0x3263E0` / `0x3263F0`: write entry **start and end** pointers;
- `0x326414..0x326428`: advance the renderer's 24-byte entry pointer, increment its count;
- preceding code checks the **`0x3FE` maximum count**, and conditionally skips registration if disabled.

The real native **Attributes** array is `this+0xCF8` (eight 72-byte primitives), and therefore resides **inside the registered owner range**. The failed v9.3.15 BSS clone filled glyphs at `0x33B3A20`, **outside the submitted owner range**, but redirected only the font-writing call. That mismatch is directly verified in executable disassembly and provides a much stronger account of the **observed complete disappearance** than the earlier guess about unrelated `+0xCF8` registration references. The exact runtime renderer behavior still requires Eden.

## v9.3.17 experimental change

Starting **exclusively** from the user's restored-selector cumulative v9.3.14+X `main(7)`, SHA-256 `47116b6c07abd8dba61c659aac7226a4bb6e221d0ae38fd2963e1ff273f3c745`:

1. Preserve the prior font destination experiment: `0x3272B8` branches to a 56-byte helper at `0x11B7880` that clones ten 72-byte native sprites into spare BSS `0x33B3A20..0x33B3CF0`; `0x3272BC` sets font cap **8→10**, without overwriting neighboring original heading objects.
2. **New:** branch from `0x32642C`, which originally executed `ldrb w9,[x21]`, to a **132-byte registration helper** at `0x11B7900`. Immediately following the original successful owner sprite registration, this appends one **additional** render-list entry with start `0x33B3A20`, end `0x33B3CF0`, and the same native render-group selection as the surrounding code.
3. The new helper uses the original list's capacity check `count ≤ 0x3FE`, preserves x8–x15, reproduces `ldrb w9,[x21]` and returns to the original `cbnz w9` branch. Existing renderer list entries and original heading arrays stay untouched.
4. Existing 4 KiB BSS extension is reused (description pool ends at `0x33B3A20`). No new BSS size, LINKDATA changes, text rewrites, or font-system global changes.

### Cumulative instruction sites

| VA | Native old | Experimental |
| --- | --- | --- |
| `0x3272B8` | `add x1,x19,#0xCF8` | BL the 10-sprite BSS font helper |
| `0x3272BC` | 8 glyphs | **10 glyphs** |
| `0x32642C` | `ldrb w9,[x21]` | BL the registration helper, restoring the displaced instruction before return |

No other previously existing native instructions are changed, and the Action List and description hooks in `0x11B7700..0x11B7850` remain byte-for-byte intact. The English selector's `.rodata` and `.data` sections, all original game/starting-menu assets and original audio are untouched.

## Exact build fingerprints

- Accepted source: `47116b6c07abd8dba61c659aac7226a4bb6e221d0ae38fd2963e1ff273f3c745`.
- Expected experimental output: `53020c9e4cace2f34213467ce9ba7c99bcc16b67f0a7cc4eb2b39c30310b6f97`.
- Source-only test package: `DQH1_M1_v9.3.17_EXP_Attributes_Drawlist_Registration.zip` (distributed in the conversation only, **no game binary**), with `build_m1_attributes_registration.py`, the local source sub-builder, AArch64 source and exact helper bytes, test suite, README and research notes.
- **7/7 offline groups pass**: protected source/output SHA, NSO section digest and layout validation, exact changed-instruction whitelist, no collisions with preexisting helpers or description BSS, exact pointer arithmetic and native guard, unknown-binary refusal, LLVM byte-for-byte helper assembly, deterministic command-line repacking and manifest.
- A generated main has not yet been runtime-tested in Eden. All caps and precise expected behavior are therefore **experimental**.

## Required Eden acceptance

Install only the generated `exefs/main` in a separate Eden override, preserving user-validated `main(7)` for instant rollback. Leave gameplay and startup LINKDATA pairs unchanged. Boot through English game selector, open Luceus Skill Tree: **Attributes must be full and visible (10 letters)**; adjacent **Special Effects**, **Spells and Abilities**, and Exclusive headings must not be corrupted or overlapped. Switch characters repeatedly and reenter menus. Confirm `Points Required`, `Requirements`, `Details`, at least the earlier visible Inferno Slash text through `that sweeps`, and X-held Action List pagination. Avoid saving in first test. On disappearance/corruption restore `main(7)`.

**Remaining risk:** font sprite buffers are externally shared in BSS. A concurrent menu instance may collide with them; two extra sprite templates were cloned from the next heading's original array, with no runtime proof of initialization suitability. The extra renderer entry may interact with draw order or group sorting. No full game QA yet. One screenshot proving ten-letter Attributes would establish just that state, not complete stability.

Prior [v9.3.15 failure](M1_V9315_ATTRIBUTES_FAILURE.md), owner analysis [v9.3.16](M1_V9316_SPRITE_OWNER_AUDIT.md), tracked in [M1 issue #11](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/11) and [skill issue #10](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/10).
