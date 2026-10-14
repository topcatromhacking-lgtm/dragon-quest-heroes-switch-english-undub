# M1 v9.3.13-EXP: Points Required sprite repacking (Eden test pending)

**Date:** 2026-10-13. **Platform:** original Japanese Switch DQH1 1.0.0 executable with transplanted official Western PC text. **Status:** source-only experimental patcher packaged in the associated conversation, **not validated in Eden**. This is **not** a game-content release; do not commit executable or proprietary LINKDATA assets.

## Rationale

Eden confirmed v9.3.12-EXP fixes `Requirements` by moving existing 20 sprites between that heading and adjacent `Details`, without increasing object size. The next candidate, `Points Required`, is complete in the transplanted Western PC text but clipped on screen as `Points Req`. Its native font call has only **10** sprites, while the full source label requires **15**.

Original Switch v1.0.0 also registers a **36-sprite dynamic status/requirements field** after the Requirements/Details pools. Static code shows this field can resolve source message ID `2876` (`???` in the Western PC text), but **the longest actual runtime expansion is unknown**. That uncertainty is why this patch remains strictly experimental.

## Exact version-locked layout

| Field | v9.3.12 slots | v9.3.13-EXP slots | New relative start / end |
| --- | ---: | ---: | --- |
| Points Required | 10 | **15** | `+0x600..+0xA38` |
| Requirements | 12 | 12 | `+0xA38..+0xD98` |
| Details | 8 | 8 | `+0xD98..+0xFD8` |
| Dynamic requirements/status | 36 | 31 | `+0xFD8..+0x1890` |
| **Total** | **66** | **66** | unchanged endpoint `+0x1890` |

Each sprite is 72 bytes. Both before/after chains have zero gaps/overlaps. Each pair of endpoints denotes a **half-open** memory interval, so no sprite past the original boundary is used.

Exactly five AArch64 words change, relative to the **already patched v9.3.12** executable:

| VA | Before | After | Purpose |
| --- | --- | --- | --- |
| `0x21C050` | `52800143` | `528001E3` | Points Required count 10 → 15 |
| `0x21BFB4` | `91234261` | `9128E261` | Requirements backing start `0x8D0→0xA38` |
| `0x21BF28` | `9130C261` | `91366261` | Details backing start `0xC30→0xD98` |
| `0x21C11C` | `9139C261` | `913F6261` | Dynamic field start `0xE70→0xFD8` |
| `0x21C124` | `52800483` | `528003E3` | Dynamic field count 36 → 31 |

Strict supported input main SHA-256:

- **v9.3.12 original-based:** `7814f92c976fe0e5deb94dab614f7744a9f69740fce9ab3a63402ad0605bd5b1` → output SHA `50c958af73b0d1737a89d9603722db8e925ec7747b579187d25ae3eaacf88c4e`.
- **v9.3.12 + X-held Action List hook:** `bebddffd0352eee6a0a1951379115792545cbb0d15f801d88da7ac8ac6fb1b4e` → output SHA `364c12b9753502748095d03a3941c14ef773e025ec7d23b1697133369e7e2f72`.

The test package contains `build_m1_points_required_pilot.py`, `test_m1_points_required.py`, `README_V9313.md` and detailed research notes. The generated executable is deliberately **not** uploaded or committed.

### Offline test results

**Six checks passed**: AArch64 immediate encoding (cross-checked by LLVM), total 66-sprite layout invariants, five exact-site whitelist, incompatible-input refusal, real NSO roundtrip and readback, and separate source-only verification of **both original-based and pagehook-combined** v9.3.12 source variants. The three NSO sections are integrity-checked; rodata/data and unrelated code remain byte-identical, and the pagehook is preserved when present.

### Required Eden test before promotion

1. Use a **fresh ExeFS override** with only the generated `exefs/main`, keeping the existing compatible v9.3.12 gameplay LINKDATA and separately validated starting-menu LINKDATA.
2. Boot past 30th Anniversary. Confirm full **Points Required**, full **Requirements**, full **Details**, and no visual overlap.
3. **Critical risk test:** select locked, unlocked, low-level, high-level, and multiple-character skills, checking the **dynamic requirements/status field** for truncation after its 36→31 reduction.
4. Confirm **hold X → Action List page 2; release → page 1** if using the pagehook-combined variant.
5. Exit **without saving** in this first experiment. On any anomaly, replace only `exefs/main` with the previous working v9.3.12 build.

### Why Attributes is not in this patch

The four contiguous eight-sprite header arrays at `+0x878,+0xAB8,+0xCF8,+0xF38` render Western PC source records **Spells and Abilities** (20 characters), **ESC-token Exclusive** (10 literal chars plus escapes), **Attributes** (10), and **Special Effects** (15). Their combined pool contains **32 sprites**, but just three plain-English labels require **45**, even before the Exclusive heading. No deficit-preserving redistribution can fix the group. It needs a separate safely owned expanded pool, layout strategy or relocation. Shortening the PC labels or stealing from other clipped headings is not our plan.

**Conclusion:** the v9.3.13 Points Required pilot passed offline but is **awaiting user Eden validation**. Keep v9.3.12-EXP as the last successfully tested M1 build, and v9.3.9 as a separate stable rollback. See [M1 milestone](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/11), [skill UI #10](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/10) and the [living PC-to-Switch changelog](PC_TO_SWITCH_DIFFERENCES.md).


## Eden result and blocking regression, 2026-10-13

**The pilot restores the intended `Points Required` label**, while Requirements and Details headings remain complete; screenshots from Luceus and Aurora confirm this. However, v9.3.13 now shows only **`Summons a fiery tornado that sw` (31 characters)** for Inferno Slash, whereas the v9.3.12 test previously showed **`Summons a fiery tornado that sweeps` (35 characters)**. This matches the attempted dynamic field capacity reduction **36→31**. Therefore the tested trade-off **fails the no-regression requirement**. The status must remain **REJECTED FOR PROMOTION**, despite the headline success. Keep v9.3.12 as the earlier confirmed M1 build and do not save experimental progress until the other fields are regression-tested.

The total needed to retain all original capacities is 15+12+8+36 = **71** glyph slots, not 66. Further redistribution cannot solve this particular layout without sacrificing another field; the next prototype must safely allocate/relocate five additional 72-byte sprite units or use a separate owned buffer, checking the region beyond `+0x1890` before touching it.
