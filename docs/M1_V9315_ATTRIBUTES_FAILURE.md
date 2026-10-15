**Important correction, 2026-10-15:** The earlier attribution of x19+0xCF8 references at 0x209774 / 0x209838 / 0x2C61F0 to the Attributes owner is NOT justified. That code uses a 13-sprite, 0x450-stride layout, versus the real category heading's 8-sprite, 0x240-stride layout. v9.3.15 also copied two objects from the next category's original sprite array. The real cause of the disappearance is still not proven; do not redirect any unrelated registration paths based on an identical offset. Superseding analysis: [M1 v9.3.16 sprite-owner audit](M1_V9316_SPRITE_OWNER_AUDIT.md).

# v9.3.15 Attributes disappeared: root-cause investigation (October 15, 2026)

**Eden report:** Attributes completely disappeared when using v9.3.15-EXP. **Status: FAILED. REJECT THIS BUILD.** Restore the user-confirmed selector-restored v9.3.14+X `main(7)`, SHA-256 `47116b6c07abd8dba61c659aac7226a4bb6e221d0ae38fd2963e1ff273f3c745`. Do not change either gameplay or startup LINKDATA pair for this rollback.

## Byte-verified findings

The v9.3.15 builder was executed against the exact user-supplied `main(7)` and reproduced output SHA-256 `45d990b3353af457be3d15d6ea964df9e7b45985d27b196f077aa53ae53a65e5`. The two NSO code sections were decompressed and key instruction words inspected.

| Native instruction VA | Previous | v9.3.15 |
| --- | --- | --- |
| `0x3272B8` | `add x1,x19,#0xCF8` passes original Attributes backing pool | **Changed** to `BL` a BSS copy/redirect helper |
| `0x3272BC` | Font cap **8** | **Changed** to **10** |
| `0x207D8C` | Another font path passes `x19+0xCF8` | **Unchanged** |
| `0x209774` | Another UI path retains `x19+0xCF8` | **Unchanged** |
| `0x209838` | That path stores the original pointer into a structure | **Unchanged** |
| `0x209840` | That path addresses a range ending at `pointer+0x3A8` | **Unchanged** |
| `0x2C61F0` | Original backing sprite array initialization/registration | **Unchanged** |

The new helper copies 10 initialized 72-byte sprite objects into BSS `0x33B3A20..0x33B3CF0`, but only **one font call** was redirected. The renderer/registration code still has paths using the original `this+0xCF8` array. This **incomplete relocation** is a strong technical explanation for the missing heading. It is **not a full runtime trace**, and some alternate paths may serve other states; do not redirect all references indiscriminately.

## Why seven offline tests missed it

They established allocation size, adjacent-array nonoverlap, helper encoding, checksums and retained earlier NSO hooks/English selector. They did **not** trace actual sprite registration, drawing and object lifetime. A valid buffer and larger glyph count do not guarantee the game will use that buffer for display.

## Before any new version

1. Trace message ID 2954 from resource lookup to **font creation AND actual renderer sprite-range submission** for the skill-category header.
2. Identify which `this+0xCF8` references are genuinely part of Attributes, versus other widgets or modes.
3. Redirect and initialize all relevant paths consistently with explicit buffer ownership and registered span; validate no overlap or stale pointers across menu reentry and characters.
4. Require the selector-restored canonical `main(7)` SHA; preserve X-held Action List, v9.3.14 BSS description recovery, Requirements/Details/Points Required, and all common/title art and texts.
5. Provide **one isolated Eden test**, rollback on black/missing labels, and test character switching plus repeat entry. **Do not promote as stable without runtime acceptance.**

A read-only check script plus this report were produced in the chat as `DQH1_v9.3.15_Attributes_Failure_Diagnostic.zip`. No playable replacement binary was built.

**Milestone M1 (#11):** blocked on native sprite registration analysis, not on adding more text.