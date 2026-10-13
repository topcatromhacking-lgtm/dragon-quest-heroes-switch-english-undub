# Development status

Updated: **2026-10-13**. This page records reported findings from iterative local playtests. The source archives and SHA-256 hashes must be reintroduced before a release is claimed verified.

## Local version history

| Version / experiment | Outcome | Decision |
| --- | --- | --- |
| v9.2.x | English text injection and many successful dialogues; long strings caused overflow/truncation, menu widths varied | Historical research |
| v9.2.16 | Experimental attempt to solve multi-page text; broader regression, including wrong character portrait (Terry) | **Rejected. Do not build on this** |
| v9.3.5 | Most recent reported working base for initial menu/title changes | Recover and independently recheck |
| v9.3.6 | Reported Western visual opening `mv002.mp4` with Japanese voice/audio preserved | **Latest reported local baseline; files not yet in repository** |

Exact archived ZIP names, build manifests, scripts and hashes remain to be verified. GitHub currently contains documentation only.

## Progress by subsystem

| Subsystem | Observed results | Open issues |
| --- | --- | --- |
| Story dialogue | Large portions readable in English | Certain long text records are clipped or overflow; line layout inconsistent |
| NPC dialogue | Old Man, Young Lady, Healix, Doric tested in screenshots | One Healix line truncated; soldier dialogue/name clipped; later Doric dialogue regression in experiments |
| Portrait dialogue | Doric and others display expected portraits in successful builds | Erroneous switch to Terry under rejected v9.2.16 |
| Character setup | Text formatting improved in A/B tests; longer strings readable in B | Ensure fixes do not worsen story dialogues |
| Control options | English descriptions displayed; manual wrapping tested | Japanese labels still reported in earlier tests; text should remain source-faithful |
| Camera settings | Most rows translated, including Player Distance | Long descriptions need context-sensitive wrapping |
| Naming/alphabet | Japanese alphabet reported in earlier testing | Verify and document current state |
| Adventure log/save menu | Navigation works | Some title/label truncation and malformed variable substitutions/pointers observed in tests |
| Inventory/shop | Text dynamic substitutions worked in earlier tests | Some names/labels around 10-12 characters and descriptions around 30 visible characters were clipped |
| Intro video | Western opening visual substitution successful in local report | Verify provenance, timing and Japanese audio integrity; **do not publish videos** |
| Other videos | ~50 files remain to audit | Classify visual-language content, do not replace blindly |
| Base version | Japanese Switch 1.0.0 used for playtests | 1.03 not assessed |

## Technical hypotheses (not yet proven)

Text layout may be governed by **multiple independent limits**, such as per-record character/byte budget, line count, rendered pixel width, dialogue page handling, and separate UI layout engines. The often-mentioned **128-character limit** is a hypothesis, not a confirmed universal threshold.

A cut-off at the same location after shortening text is not enough to prove its cause. Compare the original record, translated record, control codes, render path, and runtime behavior for each affected text class.

## Non-negotiable acceptance checks

A patch must not truncate previously working dialogue, lose text after a speaker change, change the wrong portrait, corrupt dynamic placeholders, remove Japanese voice acting, or break save-game actions. Compare screenshots and test transcripts against the last validated local build.
