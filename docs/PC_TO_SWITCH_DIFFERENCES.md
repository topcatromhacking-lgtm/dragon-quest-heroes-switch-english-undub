# Western PC vs Japanese Switch: localization differences and adaptations

**Updated:** 2026-10-13  
**Scope:** *Dragon Quest Heroes I*, Japanese Nintendo Switch release 1.0.0, English-undub project.  
**Working build:** v9.3.10 (partially gameplay-tested) applied on validated v9.3.9; **do not declare v9.3.10 final** while Action List truncation remains.

This is a **living user-visible changelog**, not an assertion that the Switch release was officially localized into English. **Every English string previously observed in our Switch screenshots was introduced by our English-undub transplant or later patch, not originally present as English in the Japanese Switch game.** It documents intentional departures from the *official English Western PC release*, distinguishes genuine new Switch options from official translations, and records why modifications are needed to fit the Switch UI.

**Status terms:** `Confirmed working` = user validated in Eden; `Partial` = some affected rows still broken; `Proposal` = not installed or tested; `Investigation` = source/renderer behavior unproven. Wording listed under "Switch project" may be custom even when based on an official PC text source.

## 1. Deliberate differences from Western PC wording

| Screen / element | Official Western PC source or original Switch | Switch English-undub adaptation | Why | Validation |
| --- | --- | --- | --- | --- |
| Save menu heading | **Adventure Log** (PC) | **Log** | The Switch save plaque clips longer titles | Confirmed working, v9.3.9 |
| Save slot time label | **Play Time** (PC) | **Playtime** | Fits the Switch's narrow field | Confirmed working, v9.3.9 |
| System settings plaque | **System Settings** (PC) | **System** | Switch title renders only `System S` | Confirmed working, v9.3.10 |
| Control selection plaque | **Control Method** (PC) | **Controls** | Fits the Switch plaque and retains a natural English name | Confirmed working, v9.3.10 |
| Action List plaque | **Action List** (PC) | **Actions** | Avoids displayed truncation `Action L` | Confirmed working, v9.3.10 |
| Control style images | Japanese **かんたん操作 / ガッツリ操作** in Switch | Official PC **Quick Controls / Slick Controls**, selected gold + unselected gray | Original Western PC graphic sprites copied at compressed block level into Switch texture atlas | Confirmed working, v9.3.9 |
| Misc. option help (3 entries) | Official PC English description text | **Same complete wording**, with explicit line breaks | Switch help-panel width differs | Confirmed working, v9.3.10 |
| System option help (5 English entries) | Official PC English description text | **Same complete wording**, with explicit line breaks | Prevent horizontal overrun | Confirmed working, v9.3.10 |
| Action List help (184 entries) | Western PC English action-table descriptions | Same complete wording, explicit wraps added to 152 of 184 entries | Initial Switch display clipped at the panel's right boundary | **Partial:** text still truncated; investigate layout/renderer rather than abbreviate |

**The Control labels are official Western PC image assets**, not community re-creations. The two new Switch settings below are a different case.

## 2. Settings present on Switch but absent in Western PC

The Western PC system-message resource `0000000000000001.vap` has no English counterparts in the two corresponding records (both slots empty). The Switch `0000000000000003.vap` contains these Japanese options (IDs 3282 and 3283). The English here is **new translation from the Japanese, not official PC wording**.

| Switch Japanese label | Meaning / setting | English in v9.3.10 | Result and next decision |
| --- | --- | --- | --- |
| **必殺技演出の短縮** | Shorten the *animations/presentation* of special moves | **Shorten Special Animations** | **Truncated:** user sees `Shorten Special Anim`. **Proposal:** `Shorten Specials` (shorter, grammatical, preserves that it shortens presentation); not yet installed |
| **アクション中のカメラ演出** | Cinematic camera effects during battle actions | **Action Camera Effects** | User reports working |

- Both original Japanese help texts have been translated faithfully and manually wrapped. **Both descriptions display correctly** in the v9.3.10 user test.
- Do **not** claim the proposed short label above is already in any release.
- Alternative proposed by tester: **Short Special Moves**. It is a reasonable short label, but can misleadingly suggest shorter *moves* instead of shorter *animations* and is longer than `Shorten Specials`. Prefer the latter if its pixel width is confirmed to fit.
- Before changing the label, check whether the menu column/font size can be safely expanded. Prefer a short understandable label if that would require intrusive renderer changes; preserve explanatory wording in the already working help text.

## 3. Action List: preserve full PC text, investigate actual renderer limits

**Current observation:** user reports v9.3.10 inserts line breaks, but Action List help is **still truncated**. This is a *runtime display issue*, not evidence that words were removed from the translation. **Do not shorten Action List strings yet.**

**Important PC-to-Switch resource discovery:**

| Western PC | Japanese Switch | Evidence |
| --- | --- | --- |
| `0000000000000024.vap` | `0000000000000008.vap` | Earlier two-platform extraction audit: **both 184 rows, 12-byte records, PC file 19,256 bytes**; sampled move names and descriptions match the English translation at the same IDs. Original Japanese Switch resource was 18,412 bytes. |

**Direct verification (user-supplied Western PC extraction, 2026-10-13):** the PC `0024.vap` has SHA-256 `eaeab8f434085119f9efdc4a0c06a2a7bcd3ef7b5f4b5c759b3db24f76620aa4`, **byte-identical to the already transplanted English Switch v9.3.9 Action List VAP** (19,256 bytes). **This does NOT mean the original Japanese Switch release contained English text**: the original Japanese Switch `0008.vap` was a different 18,412-byte resource. v9.3.10 then adds explicit line breaks, retaining the same wording but no longer byte-identical. The PC `0000000000000001.vap` is the *system menu text*, **not** the Action List descriptions resource.

Examples of complete source descriptions already present in Switch `0008.vap`:

| Entry | Stored source length (characters) | Beginning of source text |
| --- | ---: | --- |
| Attack (No MP Used), row 0 | 81 | Uses appropriate attacks for the situation... |
| Attack (Uses MP), row 1 | 77 | Uses appropriate attacks for the situation... |
| Inferno Slash, row 9 | 68 | A swirling firestorm summoned by the swing... |
| Mid-Air Combo, row 7 | 83 | Swings the sword from side to side while airborne... |

**Next investigation before any text edits:**

1. Compare the full PC `0000000000000024.vap` with the translated Switch `0000000000000008.vap` at byte, record, punctuation, control-code and newline levels. The repo contains a [read-only comparison tool](../tools/compare_dqh1_action_vaps.py); direct SHA-256 comparison of the newly supplied PC file against the **transplanted v9.3.9 Switch English VAP** has confirmed byte identity, not original-platform text equivalence.
2. Capture an actual **Western PC Action List help window** for the same long records at a known resolution. **The PC text resource alone cannot prove that its Windows renderer wraps automatically or has more glyph capacity.**
3. For the Switch, measure **visible cutoff position**, rendered line count and whether a forced newline changes total visible glyph count. Distinguish **per-line pixel clipping, hard total-glyph budget, escape-code parsing and line-count limitations**.
4. Only then decide among safer explicit wrapping, label/layout scaling, adjusted text viewport, or narrowly isolated renderer changes. Avoid a mass rewrite and do not reduce the official wording.
5. Validate the changed entries in Eden (Attack No MP / Uses MP, Inferno Slash, Recovery, longer descriptions), leaving v9.3.9 as rollback.

Offline control test: comparing the local v9.3.9 Switch action table with the v9.3.10 wrapped table returns **184/184 content-equal records, 152 help descriptions with wrapping-only differences, and zero wording changes**. This tests the *patcher*, not Western PC rendering.

### Switch renderer allocation: confirmed root cause

The original Japanese Switch **1.0.0 executable** creates exactly **60 glyph/primitive slots (60 × 72 bytes)** for Action List help. `CMenuBtlAction::OnRegister()` passes `60` to `CFont::SetStrPrim()`, which stops at that sprite-count limit. **The next menu object immediately follows the 60-slot array in memory**, so increasing the constant alone would corrupt menu state. Of the 184 transplanted official PC descriptions, 99 exceed 60 Unicode characters (longest 116). The character cap is independent of the text panel's pixel width and line wrapping. **This explains the v9.3.10 truncation after wrapping.**

Read the [verified NSO disassembly report](ACTION_LIST_60_SLOT_LIMIT.md). Preserve the complete PC text and pursue a safe larger sprite pool or paged help window as an isolated executable experiment, not an abbreviated language rewrite.

The v9.3.10 patcher conserves text content and modifies only LINKDATA DQH1 slots `0x3` and `0x8`. Its checksums and simulated archive tests do **not** establish runtime layout correctness.

## 4. Separate open problems, not yet changed

- **Coup de Grâce:** the correct Western PC UTF-8 spelling contains `â`, but the Switch Action List UI renders it as `Gr**ce`. Do not silently replace it with unaccented ASCII; inspect the font/character mapping in a separate experiment. Deferred while Action List layout is investigated.
- **Other clipped dialogue:** menu fixes are not proof that narrative dialogue or variable-substitution buffers can safely be expanded. Reject the failed v9.2.16 multi-page experiment; preserve full official text.

## 5. Installation: two distinct LINKDATA pairs

This is a recurring source of confusion:

- **Starting/menu application LINKDATA.BIN and LINKDATA.IDX:** keep the separately validated startup menu assets (v9.3.5 UI base).
- **DQH1 gameplay LINKDATA.BIN and LINKDATA.IDX:** apply v9.3.9/v9.3.10 **only** to the DQH1 game subdirectory.

During v9.3.10 testing a black screen after the 30th Anniversary screen was traced by the tester to putting the gameplay LINKDATA in the **startup-menu location**, not to a confirmed v9.3.10 program defect. Treat startup behavior as tested again only after proper placement. Always preserve a working rollback pair.

## 6. Policy for future deviations from Western PC

For every new change, append a row recording **source (official PC / Japanese-only Switch / new experimental), displayed old and new label, purpose, affected resource/message ID, version, and user-test status**.

Priority: **official Western PC wording/assets > faithful new translation for genuinely Switch-only features > minimum required screen-space adaptation**. Never mark a proposed change as tested. Preserve Japanese voice/audio. Do not include copyrighted assets in this repository.

See [STATUS](STATUS.md), [RESOURCE_MAPPING](RESOURCE_MAPPING.md), [issue #8 (Action List and menus)](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/8) and [issue #9 (accented glyph)](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/9).
