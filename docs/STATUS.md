# Development status

Updated: **2026-10-13**. This page records reported findings from iterative local playtests. The source archives and SHA-256 hashes must be reintroduced before a release is claimed verified.

## Local version history

| Version / experiment | Outcome | Decision |
| --- | --- | --- |
| v9.2.x | English text injection and many successful dialogues; long strings caused overflow/truncation, menu widths varied | Historical research |
| v9.2.16 | Experimental attempt to solve multi-page text; broader regression, including wrong character portrait (Terry) | **Rejected. Do not build on this** |
| v9.3.5 | Most recent reported working base for initial menu/title changes | Recover and independently recheck |
| v9.3.6 | Western visual opening `mv002.mp4` with Japanese voice/audio preserved | Preserved in subsequent local builds; files not in repository |
| v9.3.9 | Official Western PC Quick/Slick Control texture labels, save header Log and Playtime | **User validated; safe gameplay rollback** |
| v9.3.10 | Misc and System help wrapping, two newly translated Switch-only settings, Controls/System/Actions titles, Action List wrapping | **Partially validated in Eden**: all listed menu fixes work except one truncated System setting name; Action List descriptions still truncate despite line breaks. Startup black screen was traced to swapped initial-menu vs DQH1 LINKDATA locations, not a proven patch defect. |

GitHub contains documentation and historical read-only analysis utilities, not a verified public game patch. See [PC-to-Switch adaptation log](PC_TO_SWITCH_DIFFERENCES.md) for current user-confirmed changes and open questions.

## Progress by subsystem

| Subsystem | Observed results | Open issues |
| --- | --- | --- |
| Story dialogue | Large portions readable in English | Certain long text records are clipped or overflow; line layout inconsistent |
| NPC dialogue | Old Man, Young Lady, Healix, Doric tested in screenshots | One Healix line truncated; soldier dialogue/name clipped; later Doric dialogue regression in experiments |
| Portrait dialogue | Doric and others display expected portraits in successful builds | Erroneous switch to Terry under rejected v9.2.16 |
| Character setup | Text formatting improved in A/B tests; longer strings readable in B | Ensure fixes do not worsen story dialogues |
| Control options | Western PC Quick/Slick art and Controls plaque validated in v9.3.9 / v9.3.10 | Continue general UI checks |
| Camera settings | Most rows translated, including Player Distance | Long descriptions need context-sensitive wrapping |
| Naming/alphabet | Japanese alphabet reported in earlier testing | Verify and document current state |
| Adventure log/save menu | **Log** and **Playtime** labels validated in v9.3.9 | Continue save/load and dynamic substitution regression checks |
| Inventory/shop | Text dynamic substitutions worked in earlier tests | Some names/labels around 10-12 characters and descriptions around 30 visible characters were clipped |
| Intro video | Western opening visual substitution successful in local report | Verify provenance, timing and Japanese audio integrity; **do not publish videos** |
| Other videos | User reviewed all 50 remaining videos and reports no visible textual characters | Retain Japanese video streams; verify external subtitle/audio routing separately |
| System and Misc menus | v9.3.10 English description wrapping validated; two new Switch-specific settings translated and their descriptions fit | **Shorten Special Animations** title clips; proposed **Shorten Specials**, not patched |
| Action List | Official PC 0024.vap byte-identical to the English-transplanted v9.3.9 Switch 0008.vap; **Actions** heading fits; NSO analysis confirms original Japanese Switch renderer allocates **60 × 72-byte character sprites** | 99/184 descriptions exceed 60 characters; offline 58-unit two-page layout preserves all 184 descriptions (77 on one page, 107 on two). **Runtime page switching is not yet built**. Never raise count alone or shorten official text. |
| Skill-point allocation UI | New user screenshot shows `Attribut`, `Requiremen`, `Points Req`, `Skill Po`, `Switch Charac` with unused horizontal room | Verify complete transplanted PC strings and native per-widget sprite budgets; new [issue #10](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/10) |
| Base version | Japanese Switch 1.0.0 used for playtests | 1.03 not assessed |

## Technical hypotheses (not yet proven)

Text layout may be governed by **multiple independent limits**, such as per-record character/byte budget, line count, rendered pixel width, dialogue page handling, and separate UI layout engines. The often-mentioned **128-character limit** is a hypothesis, not a confirmed universal threshold.

A cut-off at the same location after shortening text is not enough to prove its cause. Compare the original record, translated record, control codes, render path, and runtime behavior for each affected text class.

## Non-negotiable acceptance checks

A patch must not truncate previously working dialogue, lose text after a speaker change, change the wrong portrait, corrupt dynamic placeholders, remove Japanese voice acting, or break save-game actions. Compare screenshots and test transcripts against the last validated local build.


## Current executable experiment (not baseline)

**v9.3.11-EXP** is a separately packaged **Action List-only pagination proof** with a 132-byte AArch64 page-selector, tagged dual-page VAP records and unchanged 60-sprite allocation. Five offline integrity tests passed using locally supplied PC/Switch assets, and all 184 PC text entries remain recoverable (77 one-page, 107 two-page). **First Eden gameplay evidence now positive:** physical **X** reveals page 2 for Attack (No MP Used) and both screenshots combine to the full English text. Hold/release behavior, other entries and input conflicts remain unverified. **No approved stable release.** The target main must be the exact Japanese Switch 1.0.0 NSO. Known working rollback is v9.3.9; v9.3.10 menu changes remain partially verified. See [experimental integration guide](ACTION_LIST_PAGEHOOK_EXPERIMENT.md).


## Milestone M1 active: complete Western PC skill labels

Roadmap issue [#11](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/11), pilot [#10](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/10). Six complete Western PC strings have been verified in the PC VAP. Original Japanese Switch 1.0.0 MOD0 symbol analysis located the older DQH1 skill menu registration path. Fourteen font-call checks passed, confirming multiple small native per-call glyph budgets, but exact screenshot-title mapping and safe backing-array extent remain unproven. **No skill-tree executable fix yet.** See [verified static report](M1_SKILL_LABELS_REPORT.md).


### 2026-10-13 M1 follow-up: installed data confirmed, sprite-pool models proven

User supplied `skill_report.json`. All six full PC labels survive into the translated DQH1 4,501-record system VAP, and their record references are documented. Fifteen original Switch instruction signatures verified an **embedded 12-sprite** character-selection draw and a **global reserved seven-sprite** skill-point draw. Draw-operation ↔ screenshot-label mapping is still pending, so **no capacity patch is safe yet**. See [M1 source/pool report](M1_SOURCE_AND_POOL_FOLLOWUP.md).


### New isolated M1 experimental test: v9.3.12-EXP (Eden pending)

Exact label-to-font paths have now been identified for six skill headings. To avoid increasing object memory, an isolated three-instruction NSO patch **rebalances Requirements and Details within the same twenty-sprite region** (Requirements 12, Details 8, totals unchanged). Offline original- and pagehook-combined builds pass with no other executable section changes. This is **not gameplay validated** or a universal capacity fix. See [readme and rollback plan](M1_REQUIREMENTS_POOL_EXPERIMENT.md) and milestone [#11](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/11).


### Eden-confirmed first M1 native renderer fix, v9.3.12-EXP (2026-10-13)

Tester supplied an in-game Luceus skill-tree screenshot and reported **all three checks passed**: `Requirements` fully displayed after reallocating 12 existing sprite slots; adjacent seven-letter `Details` fully rendered with its eight slots; holding X continues to show page 2 in the Action List. This proves a narrowly scoped **20-sprite capacity redistribution works in Eden**, but does not prove all skill labels fixed or all gameplay/regression cases. Other captions (`Attribut`, `Spells a`, `Switch Charac`, `Skill Po`) remain visibly truncated. Next evaluate other adjacent sprite pools independently. Keep v9.3.12 experimental, v9.3.9 rollback.


### v9.3.13-EXP: Points Required pilot packaged (Eden pending)

After v9.3.12's successful Requirements/Details runtime test, a separate five-instruction version-locked prototype reallocates the same 66 embedded sprites to `Points Required=15 / Requirements=12 / Details=8 / dynamic field=31` (formerly 10/12/8/36). Six offline tests pass for both supported v9.3.12 main variants, with unchanged unrelated code, rodata, data and preserved Action List X-hook where used. **The dynamic field loses five reserved sprites, so real long-value tests remain necessary. No user runtime confirmation yet; do not call stable.** Research: [v9.3.13 pilot](M1_POINTS_REQUIRED_V9313_EXPERIMENT.md).

Attributes, Spells and Abilities, Special Effects and Exclusive share just four 8-sprite pools; their source titles exceed that combined capacity. **No safe rebalancing-only solution**, require separate owned storage / relocation study.


### v9.3.13-EXP Eden outcome: heading success with a **new clipping trade-off**

User supplied three screenshots (Luceus and Aurora): full `Points Required`, `Requirements`, `Details` heading now working. However, same **Inferno Slash** description renders **31** visible characters (`Summons a fiery tornado that sw`), versus **35** in the previous v9.3.12 screenshot (`...that sweeps`). This strongly corresponds to the deliberate 36→31 dynamic sprite shrink: v9.3.13 is **not suitable for promotion**. To preserve existing capacities, Points Required 15 + Requirements 12 + Details 8 + dynamic 36 needs **71**, not the original **66** slots. Next design must safely enlarge/relocate the backed sprite region by 5, or use another separately proven lifetime-managed buffer. Retain v9.3.12 rollback. Separate still-clipped headings and skill names from **PC ESC-token grammar incompatibilities** (records 2943, 2944, 2946, 2953). See [M1 #11](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/11), [skill UI #10](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/10), [control-code issue #12](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/12).


### v9.3.14-EXP: extra persistent description sprite pool (offline tested, Eden pending)

This independent experiment starts from **v9.3.12** (not regressing v9.3.13). A four-site AArch64 patch plus 52-byte initialization hook reallocates `Points Required=15, Requirements=12, Details=8`, while keeping the dynamic description at its original **36 glyph sprites** by using an appended 4 KiB BSS page. Six offline test groups passed for both supported v9.3.12 executables, preserving the prior X-held Action List hook when present. **No runtime validation yet.** There are substantial loader/renderer risks with external sprite storage. [Details and Eden test gate](M1_V9314_BSS_DESCRIPTION_EXPERIMENT.md). User-tested v9.3.12 is still last successful M1 checkpoint.


### v9.3.14-EXP: first positive Eden result, 2026-10-14

The user's new **Inferno Slash** screenshot confirms restoration of the original description visibility (`Summons a fiery tornado that sweeps`, as in v9.3.12), reversing v9.3.13's `...that sw` truncation. `Requirements` and `Details` remain complete; title boots. The BSS-backed persistent description pool thus has **positive runtime evidence** for this skill. **Still pending:** simultaneous `Points Required` display (not shown in screenshot), multiple character and locked-skill states, X-held Action List behavior and extended regression checks. Preserve experimental designation and prior v9.3.12 rollback. See [BSS experiment](M1_V9314_BSS_DESCRIPTION_EXPERIMENT.md).


### Startup selector English regression discovered 2026-10-14

**Eden screenshots:** English game-cover artwork and subtitles survive, but the interactive selector question, individual game confirmation prompts, and Yes/No reverted to Japanese. Earlier **v9.3.0/v9.3.1** changed these **in `exefs/main`**, while v9.3.2–v9.3.5 changed separate **common-game LINKDATA artwork**. The original-main rebuild performed for **v9.3.11** did not carry forward the selector executable edits, causing the likely missing functionality in later M1 builds. **Do not install old v9.3.1 main over the new M1 main.** A source-only, conflict-rejecting three-way selector merge diagnostic is packaged in the conversation; genuine v9.3.1 donor and Eden testing are still pending. [Issue #13](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/13). This is a release blocker: **future NSO experiments must explicitly preserve selector patch and newer Action List/M1 hooks simultaneously.**


### 2026-10-14: selector-restored cumulative NSO source fingerprint locked

Uploaded **`main(7)`**, SHA-256 **`47116b6c07abd8dba61c659aac7226a4bb6e221d0ae38fd2963e1ff273f3c745`**. Validated all NSO section digests, seven native instruction sites, Action List X-held pagehook, 52-byte BSS skill description helper and 4 KiB BSS extension. Crucially, resetting just its `rodata` and `data` to original Japanese selector values recreates the *exact known pre-merge v9.3.14+X main* SHA `376acf9e707319edd0c80126c7da53415d78f879b804e9a50ce52f15f906e7fb`. This conclusively verifies prior hooks weren't overwritten by restoring the earlier English selector. User reports selector working. **All future experimental main builds must preserve this selector-restored baseline.** [Provenance and future preflight](M1_MERGED_SELECTOR_EXECUTABLE_BASELINE.md), [resolved selector regression #13](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/13).


### v9.3.15-EXP: isolated Attributes capacity pilot, offline verified (Eden pending)

Using canonical selector-restored main SHA `47116b6c07abd8dba61c659aac7226a4bb6e221d0ae38fd2963e1ff273f3c745`, a two-instruction + 56-byte AArch64 BSS helper changes only `Attributes` drawing from 8 to 10 sprites. Its new externally copied 720-byte pool `0x33B3A20..0x33B3CF0` fits in the unused portion of the already verified v9.3.14 BSS page; previous description sprites `0x33B3000..0x33B3A20` do not overlap. All seven offline test groups pass and original English selector, v9.3.11 Action List hook and v9.3.14 M1 hooks survive byte-for-byte. **Runtime renderer acceptance and multi-character re-entry still untested**, so this is not a stable build. Output experimental main SHA `45d990b3353af457be3d15d6ea964df9e7b45985d27b196f077aa53ae53a65e5`. [Technical report](M1_V9315_ATTRIBUTES_BSS_EXPERIMENT.md).


### 2026-10-15: v9.3.15-EXP failed in Eden; revert to selector-restored v9.3.14

User reports **Attributes completely absent** when running v9.3.15-EXP. Previous v9.3.14 displayed truncated `Attribut`. This is a critical **regression**, not a partial success; v9.3.15 **REJECTED**. Exact input/output NSO SHA checks reproduced. Static postmortem finds that the injected 10-sprite Attributes BSS array is passed only to one font-generation call while other native initialization/registration paths still use the original `this+0xCF8` array, potentially making rendered sprites invisible. Specific pointer registration and draw path not yet proven by live tracing. Use protected selector-restored main(7) `47116b6c07abd8dba61c659aac7226a4bb6e221d0ae38fd2963e1ff273f3c745` as last working checkpoint. [Failure analysis](M1_V9315_ATTRIBUTES_FAILURE.md). No replacement patch yet.


## Correction from 2026-10-15 read-only sprite-owner audit

The prior claim that code addresses 0x209774 / 0x209838 / 0x2C61F0 register the Attributes heading is NOT supported. Those paths use a different 13-sprite, 0x450-stride array layout. The true skill category headers use four 8-sprite arrays at owner offsets 0x878, 0xAB8, 0xCF8, 0xF38 (stride 0x240), with native font call sites 0x326FC0, 0x327118, 0x3272B8 and 0x327450. The failed v9.3.15 helper copied 10 sprites starting at 0xCF8, crossing from 8 Attributes objects into 2 objects of the next heading, whose text is processed later. It is not proven these extra objects were initialized or accepted by the renderer. The actual category render-list registration path remains untraced. No new playable patch has been built. All five read-only audit tests pass for working main(7) and reproduced failed main. See docs/M1_V9316_SPRITE_OWNER_AUDIT.md. Keep v9.3.14 selector-restored main(7) as rollback and baseline.


### v9.3.17-EXP: native Attributes BSS draw-list registration, **Eden pending**

After tracing actual native render-list submission in `0x326388`, a source-only cumulative v9.3.17 builder now pairs the 10-sprite external Attributes font pool with an additional native render-list entry for that exact 720-byte BSS pool. Previous v9.3.15 failed because its external sprite pool wasn't within the original owner registration `this+0xE8..this+0x8E28`; the mismatch is now byte-grounded, though final causality needs Eden. New 132-byte hook at `0x11B7900` extends draw-list at `0x32642C` with original capacity guards; 7 offline test groups pass. SHA-gated input is canonical selector-restored `main(7)` (`47116b...`), experimental output `53020c...`. **Not runtime-tested; don't promote.** [v9.3.17 report](M1_V9317_ATTRIBUTES_DRAWLIST_EXPERIMENT.md). Keep baseline and all LINKDATA untouched for rollback.
