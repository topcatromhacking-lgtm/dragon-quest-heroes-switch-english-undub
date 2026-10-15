# M1 v9.3.16: sprite-owner disambiguation (read-only, no game build)

**Date:** 2026-10-15. **Input:** exact user-validated selector-restored v9.3.14+X `main(7)` SHA-256 `47116b6c07abd8dba61c659aac7226a4bb6e221d0ae38fd2963e1ff273f3c745`. **User QA:** after v9.3.15 made Attributes disappear, restoring this baseline caused the former truncated `Attribut` to reappear.

## Critical correction to the earlier failure report

The prior report associated native `this+0xCF8` references at VA `0x207D8C`, `0x209774`, `0x209838`, `0x209840`, and `0x2C61F0` with the Attributes category-heading renderer. **That association was speculative and is unsupported. The offsets are not proof of a shared object owner.** Specifically, the other code operates on lists initialized at object offsets `0x458`, `0x8A8`, `0xCF8`, a **0x450-byte stride**, and one routine calls the font renderer with **13** glyph sprites and submits a **0x3A8-byte** range (13×72). In contrast the actual skill category headings are separate contiguous **0x240-byte** (8×72) pools:

| Label | English PC message ID | Code VA for backing pointer | Original offset | Original sprites |
| --- | ---: | --- | --- | ---: |
| Spells and Abilities | 2956 | `0x326FC0` | `this+0x878` | 8 |
| ESC-coded Exclusive | 2953 | `0x327118` | `this+0xAB8` | 8 |
| Attributes | 2954 | `0x3272B8` | `this+0xCF8` | 8 |
| Special Effects | 2952 | `0x327450` | `this+0xF38` | 8 |

The complete heading group is exactly 32 sprites from `this+0x878..this+0x1178`; the same font dispatcher `0x1DB8E4` receives each pointer/count. All these original instruction bytes are verified from the actual baseline and from the reproducible failed v9.3.15 executable.

### Second problem revealed by the failed copy hook

The failed v9.3.15 helper copied **10×72-byte** objects from `this+0xCF8..this+0xFC8` to BSS `0x33B3A20`. Its first eight source objects belong to Attributes, but the remaining two belong to the **next heading's** original `this+0xF38` pool. The next heading is populated **after** the Attributes font call in the known native code. We cannot assume those two extra objects were in a valid, fully initialized/registered state when copied. Constructor-level initialization may nevertheless exist, so this is a **plausible risk, not a proven cause**.

The earlier v9.3.14 36-slot description BSS helper worked in Eden, but identical copy-loop mechanics do not establish the proper primitive ownership or submit/draw linkage in this *different* category header renderer.

### Revised root-cause status

**Confirmed:** v9.3.15 caused Attributes to disappear; rollback restored visible (still truncated) `Attribut`; all 4 category heading source pools and their limits are tightly packed; the failed copy crosses category boundaries; same-offset references in unrelated 0x450-stride object layouts must not be blindly rewritten.

**Not confirmed:** which precise path registers/submits the 4 category heading pools, whether a BSS clone can be registered, or which missing registration/initializer feature caused the heading to vanish. Previous claims that the 0x209838 path was **the** Attributes registration should be treated as superseded.

## Completed source-only offline audit

A read-only verifier `audit_m1_sprite_ownership.py` checks the entire compressed NSO (all 3 SHA-256 section digests), strict input hashes, each message ID and pointer/count instruction, alternative 0x450-stride list ownership, and original M1 hook guards. The verifier was tested with both exact known binaries: protected input SHA `47116b6...` and reproduced failed output SHA `45d990b...`. Five test groups passed: NSO integrity, category layout, independent layout disambiguation, copy boundary, unknown-version refusal. No copyrighted game binary shipped or committed.

## Next release gate

Before another playable patch, trace the **actual** category-header owner from initialization → `CFont::SetStrPrim` at `0x32731C` → render-list pointer/count submission → teardown and reentry, identifying the owning pointer rather than matching a numeric offset alone. A new safely allocated sprite buffer must be properly initialized and registered with compatible lifetime and must preserve selector-restored v9.3.14's English UI, X-held Action List pagination and 36-sprite description. **Do not release a second speculative pointer-only experiment.**

See [failed v9.3.15 report](M1_V9315_ATTRIBUTES_FAILURE.md), [M1 milestone #11](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/11), [skill issue #10](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/10).
