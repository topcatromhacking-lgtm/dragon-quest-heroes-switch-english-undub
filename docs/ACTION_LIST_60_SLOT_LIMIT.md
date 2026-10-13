# DQH1 Switch Action List truncation: verified executable allocation

**Date:** 2026-10-13. **Status:** root cause identified offline; no gameplay patch created or validated. **Target:** Japanese Nintendo Switch 1.0.0 NSO `main` SHA-256 `cc9dfbc99f1a60120fd30b3e82dc98a17e6b2754f9cad6acfd5be329cbe63e4d`.

## Separate the three assets

- **Original Switch**: Japanese Action List VAP, 18,412 bytes, designed for the original Japanese menu renderer.
- **Western PC**: English Action List `0000000000000024.vap`, 19,256 bytes, SHA-256 `eaeab8f434085119f9efdc4a0c06a2a7bcd3ef7b5f4b5c759b3db24f76620aa4`.
- **Our v9.3.9 transplanted Switch Action List**: `0000000000000008.vap`, byte-for-byte identical to the PC file; the original Japanese Switch never contained the English descriptions.
- **v9.3.10 experimental Switch Action List**: 152 descriptions changed in line-break layout only (184/184 unchanged wording); screenshot still clips text.

## Proven native Switch limit

1. The gameplay NSO includes symbol `NActProj::CMenuBtlAction::OnRegister` at virtual address `0x002516D0`. At `0x00251C1C` it loads `w3 = 0x3C` (60), then calls `NActProj::CFont::SetStrPrim(...)` at `0x00251C30`, with `x2` pointing to the selected Action List description. `w3` is **the number of preallocated character sprites**.
2. `NActProj::CFont::SetStrPrim` (`0x001DB8E4`) moves `w3` to internal `w20` (`0x001DB918`), then compares drawn character/sprite count `w24` against `w20` (`0x001DBE14`, `0x001DC6C4` among other paths). This is a **hard bound** distinct from the rendered pixel width and number of lines.
3. The menu constructor at `0x0024F838` creates exactly **60 entries, 72 bytes each**: `0x10E0` bytes, at offsets `+0x33F8` through `+0x44D7`. The constructor initializes its next object at `+0x44D8`. Thus increasing the `60` constant alone **would overwrite adjacent menu state**.
4. Verified exact machine-code patterns at nine sites against the supplied original NSO with a read-only script; all passed.

**Corpus audit:** 99 of the 184 v9.3.10 Action List descriptions exceed 60 Unicode characters; 98 exceed 60 characters even when four-byte button tokens are counted as single render units. Maximum text length is 116 characters. These are *screening counts*, not exact glyph totals; buttons, newlines and spaces may consume sprites differently. Some shorter descriptions may also overflow horizontally due to pixel width.

**Observed test case:** `Attack (No MP Used)` has an 81-character official PC description. Manual wrapping changes its layout but cannot force a 60-sprite pool to hold the complete explanation. There is no evidence that the text disappeared from VAP data.

## What the Western PC file establishes (and what it does not)

The PC VAP and the v9.3.9 English-transplanted Switch VAP are byte-identical. PC descriptions have **no manual newlines**; PC uses a different rendering/layout path, or otherwise renders that content in its own environment. The file alone does **not** prove its exact runtime sprite capacity. A real PC Action List screenshot or executable comparison would be required for that.

## Engineering implications

- **Do not** abbreviate official descriptions, reuse the failed v9.2.16 story pagination patch, or replace all line breaks again.
- **Do not** increase the `0x3C` immediate to 80/120 by itself. The next object starts where the allocated 60 sprites end.
- A complete fix preserving official wording requires a **larger safe primitive pool** with matching construction, registration, rendering and cleanup changes; or explicit **two-page/scrolling help** with separate valid sprites per page. Any such executable change needs isolated experimental testing and rollback, not the cumulative menu-text patch.
- Another independent issue is the text panel's pixel width: after increasing capacity, retain appropriate word wrapping and verify all 3 help lines stay within the panel.
- Leave the accented `Coup de Grâce` glyph issue separate.

## Reproduce audit

Use [`analyze_action_display_capacity.py`](../tools/analyze_action_display_capacity.py) with the user's own Switch 1.0.0 `main` NSO and optionally their translated Action VAP. Requires Python 3 + `lz4` package for a compressed NSO (`pip install lz4`). Script is **read-only** and contains no copyrighted data or patch bytes beyond public instruction signatures.