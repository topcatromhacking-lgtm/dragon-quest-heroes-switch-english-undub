# M1 v9.3.15-EXP: Attributes with an independent BSS sprite pool

**Prepared 2026-10-14. Status: offline-verified, Eden gameplay testing pending.**

This prototype follows the user's restored English-selector `main(7)`, SHA-256 `47116b6c07abd8dba61c659aac7226a4bb6e221d0ae38fd2963e1ff273f3c745`, now the **only accepted input** for this experiment. It preserves the translated game selector, v9.3.11 X-held Action List page selector, v9.3.12 Requirements/Details, the full v9.3.14 Points Required heading and its 36-sprite restored skill-description BSS pool. **No LINKDATA or copyrighted game resource is changed.**

## Native finding

Japanese Switch 1.0.0 uses message ID **2954** (`Attributes` in transplanted official Western PC data), fetched at VA `0x327274`. Its glyph draw operation passes the original backing pointer **`this+0xCF8`** at VA `0x3272B8`, and an **8-sprite** limit at VA `0x3272BC` to `CFont::SetStrPrim` at VA `0x32731C`. The next heading sprite block begins at `this+0xF38`, exactly **8×72** bytes later, so increasing the immediate cap alone would corrupt its neighbor.

## Isolated experiment

The v9.3.14 main already reserved one page of additional BSS:

| Resource | Memory interval (half-open) | Bytes |
| --- | --- | ---: |
| Existing skill-description sprites | `0x33B3000 .. 0x33B3A20` | 2,592 |
| **New Attributes sprites** | **`0x33B3A20 .. 0x33B3CF0`** | **720** |
| Remaining BSS slack | `0x33B3CF0 .. 0x33B4000` | 784 |

No increase in BSS or segment size is needed. A **56-byte** helper resides at `0x11B7880`, separate from previously installed Action List `0x11B7700` and description `0x11B7800` helpers. It copies **10 previously initialized 72-byte sprite objects**, returns the BSS sprite address in `x1`, and preserves temporary AArch64 registers. The source template spans ten contiguous initialized objects beginning at `this+0xCF8`, including two objects from the adjacent heading; **those original objects are read only, never overwritten**. The game still uses its normal font routine. It is *not yet proven* that the renderer registers the two additional external objects correctly.

**Exactly two original AArch64 instructions change**:

| VA | Original word | New word | Reason |
| --- | --- | --- | --- |
| `0x3272B8` | `0x9133E261` | `0x943A4172` | `add x1, x19, #0xCF8` → branch to new helper |
| `0x3272BC` | `0x321D03E3` | `0x52800143` | Original limit 8 → 10 sprites |

AArch64 `BL` and `ADRP` targets have been independently decoded; the 56-byte code also matches the assembly source built with Clang/LLVM.

## Verified inputs, output and automated tests

- Input selector-restored `main(7)` SHA-256: `47116b6c07abd8dba61c659aac7226a4bb6e221d0ae38fd2963e1ff273f3c745`.
- **Experimental output** SHA-256: `45d990b3353af457be3d15d6ea964df9e7b45985d27b196f077aa53ae53a65e5`.
- Source-only test package, distributed in the user's conversation: `DQH1_M1_v9.3.15_EXP_Attributes_BSS_Test.zip`. Contains builder, AArch64 source, seven automated tests, README, metadata. No game binary.
- **Seven offline test groups passed** with the exact current `main(7)`: digest/version gate; unchanged previous patches and both helpers; exactly two changed original instructions; 10-sprite BSS space and copy-loop math; incorrect-input refusal; reproducible deterministic NSO output; unchanged `rodata`, `data`, BSS size and code section size.
- ZIP integrity checked. `lz4` is the only Python dependency.

## Installation and required Eden test

On the user's own Windows machine:

```powershell
python -X utf8 build_m1_attributes_bss.py `
  --input-main "C:\PATH\TO\YOUR\main(7)" `
  --output "M1_ATTR_TEST\exefs\main"
```

Use only one `exefs/main` override. Keep separate common/starting-menu and DQH1 gameplay RomFS assets unchanged. **Do not save during this test.**

Verify **Attributes** completely displays (10 letters), including after character switching and menu re-entry; **Special** and the other existing headings do not regress; selector and Yes/No remain English; `Points Required`, `Requirements`, `Details` remain complete; Inferno Slash shows at least previously visible `Summons a fiery tornado that sweeps`; hold X to show Action List page 2 and release to show page 1. On missing sprites, flicker or crashes, restore the exact backed-up main.

## Explicit unresolved risks and remaining M1 work

This is a single-heading proof, **not** a blanket UI expansion. The external BSS pool is global and may be shared by concurrently open panels; per-widget sprite ownership/registration and reentry require real Eden confirmation. Other headings (`Spells and Abilities`, `Switch Character`, `Skill Points`), long skill names/descriptions, and Western PC escape tokens (`ESC F/I/G`) are unchanged and remain open under skill UI issue #10 and ESC decoder issue #12.

**Release gate:** no stable promotion until the user validates runtime behavior and prior translations remain intact.


## EDEN OUTCOME 2026-10-15 — FAILED, DO NOT INSTALL

User reports **Attributes disappears entirely** with this experiment. This supersedes the earlier “Eden pending” status. Restore protected selector-restored v9.3.14+X main(7) SHA `47116b6c07abd8dba61c659aac7226a4bb6e221d0ae38fd2963e1ff273f3c745` and leave both LINKDATA archives intact. The 10-sprite external buffer was passed into only one `CFont::SetStrPrim` call; unmodified native paths still use `this+0xCF8` for original array registration/drawing. It was incorrect to infer complete renderer integration from successful code/NSO integrity tests. **No replacement build is approved.** See [full failure analysis](M1_V9315_ATTRIBUTES_FAILURE.md).
