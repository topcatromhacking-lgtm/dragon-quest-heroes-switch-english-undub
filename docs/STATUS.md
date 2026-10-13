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
| Base version | Japanese Switch 1.0.0 used for playtests | 1.03 not assessed |

## Technical hypotheses (not yet proven)

Text layout may be governed by **multiple independent limits**, such as per-record character/byte budget, line count, rendered pixel width, dialogue page handling, and separate UI layout engines. The often-mentioned **128-character limit** is a hypothesis, not a confirmed universal threshold.

A cut-off at the same location after shortening text is not enough to prove its cause. Compare the original record, translated record, control codes, render path, and runtime behavior for each affected text class.

## Non-negotiable acceptance checks

A patch must not truncate previously working dialogue, lose text after a speaker change, change the wrong portrait, corrupt dynamic placeholders, remove Japanese voice acting, or break save-game actions. Compare screenshots and test transcripts against the last validated local build.
