# DQH1 Action List: 60-slot-safe pagination feasibility

Date: 2026-10-13. **Status: offline design and tests, NOT a runtime/gameplay patch.**

## Confirmed native renderer path (original Japanese Switch 1.0.0)

- `NActProj::CMenuBtlAction::OnRegister` retrieves the selected Action description pointer at `0x251B10`, returns it as `x21`.
- `0x251C0C..0x251C14` obtains persistent per-menu sprite buffer `x22 = this + 0x33F8`.
- `0x251C1C` sets `w3=60`; `0x251C30` calls `CFont::SetStrPrim(x20, x22, x21, 60, ...)`.
- `0x251CDC` writes the **start pointer** `x22` into the render-registration queue; `0x251CE4..0x251CE8` writes the **end pointer** `x22 + count*primitive_stride`. The queued sprites need their original persistent lifetime; a temporary stack/heap allocation freed before the draw is unsafe.
- The constructor initializes 60 embedded sprites of 72 bytes at `this+0x33F8..this+0x44D7`; the next menu member starts at `this+0x44D8`.

## Offline feasibility result

Using the exact 184 descriptions extracted from the English Western PC `0000000000000024.vap`, SHA-256 `eaeab8f434085119f9efdc4a0c06a2a7bcd3ef7b5f4b5c759b3db24f76620aa4`:

| Constraint / outcome | Result |
| --- | ---: |
| Maximum **estimated** visible units on one page | 58 |
| Maximum units per formatted line | 39 |
| Source descriptions preserved in full | 184 / 184 |
| Fit on one page | 77 |
| Need two pages | 107 |
| Need three pages | 0 |
| Total pages | 291 |
| Original wording, names, punctuation and controller-token order lost | 0 |

The two extra sprite slots below 60 are a **margin**, not a validated count of all possible rendered control-code sequences. Font widths, escaped button glyphs, accented character handling, and line breaks still require runtime testing. The planner preserves the official text even when a label is not yet supported by Switch font lookup.

Python tools: `tools/plan_action_list_pages.py` (source only) and `test_plan_action_pages.py` (synthetic unit tests). The script reads a user-supplied PC VAP, writes only summary statistics by default, and never alters game resources. **Never commit text-bearing generated previews to the public repo.**

## Safer initial runtime design

1. Retain the original 60-sprite pool and `SetStrPrim` limit; do **not** enlarge the count or move adjacent menu objects.
2. Store display-page strings in persistent VAP-backed memory or another clearly owned long-lived buffer. A 2-page entry has two NUL-terminated strings, but pointer metadata and the existing VAP reader must be validated first.
3. Add a narrow hook only to the Action List description selection path so the renderer receives the currently selected page's pointer. **Never hook the shared `CFont::SetStrPrim` globally.**
4. Select page 1 by default; when the user changes the selected action/character/control mode, reset to page 1. Page 2 needs a discoverable, non-conflicting input plus a visible page indicator.
5. Before distributing any runtime build, map the chosen input against existing controls, identify stable per-menu state storage, and audit `OnInit`/`OnTerm`/destructor state transitions. Test page 1, page 2, fast scroll, menu close/reopen and repeated transitions for at least Attack (No MP Used), Inferno Slash, the 116-character shockwave description, and button-coded descriptions.
6. Treat an expanded dynamic sprite pool as a separate, higher-risk option requiring successful heap ownership, 128 sprite constructors, render registration and cleanup auditing. No allocation hook has been implemented or runtime validated.

## Safety and rollback

Do not change the translated v9.3.10 gameplay LINKDATA, the v9.3.9 rollback, the common starting-menu LINKDATA or Japanese audio as part of this offline research. No ROM/NSO patch is released here. The game engine's true sprite consumption may differ from the planner's estimate.