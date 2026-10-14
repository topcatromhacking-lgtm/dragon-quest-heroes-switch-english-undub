# M1 follow-up: complete skill strings and verified native sprite pools

**2026-10-13; read-only reverse engineering, no executable or data patch.**

## Actual installed Switch English resources

User-supplied `skill_report.json` identifies **gameplay DQH1** slot #3 SHA-256 `17ffe261da8bbcc8301acf71cb057a619e318460b79071530b26f6f244cb271f` (226,080 bytes, 4,501 records). It finds full English source text **within the installed archive**. **This does not yet prove which of several text records the screenshot widgets actually request.** The original Western PC `0000000000000001.vap` was also inspected at those record IDs. All confirmed source records:

| Source text | Message records and caveats |
| --- | --- |
| **Attributes** | 2954, 3044, 4439: exact label |
| **Requirements** | 2942: exact label |
| **Points Required** | 2949: exact label |
| **Skill Points** | 2877: exact label; **2951 / 3794 / 3823 / 3825 are substring matches within longer phrases**, not four copies of this label |
| **Switch Character** | 4304: exact wording **preceded by controller-icon escapes** `ESC PB` and `ESC PC`; do not remove them |
| **Spells and Abilities** | 2956, 4410: exact; 3251 is a controller-code-bearing variant |
| **Exclusive (left-panel display artifact)** | 2953: source `ESC F4` + `ESC I040` + `-Exclusive`; visible `F4I040-E` is potentially an **escape-interpreter issue**, not necessarily character-slot clipping |

The report is **metadata about the installed translated resource**, not an uploaded copy of its underlying 226 KB payload. Likewise, the above PC message indices do **not** mean these strings existed in the original Japanese Switch release.

## Additional native allocation evidence (verified against original NSO)

Japanese Switch 1.0.0 `main` SHA-256: `cc9dfbc99f1a60120fd30b3e82dc98a17e6b2754f9cad6acfd5be329cbe63e4d`. **Fifteen independent AArch64 machine-word signatures** checked on the original decompressed code.

**Embedded pool: `CMenuSkillCharaSelect::OnRegister`**
- VA `0xBF58BC`: `w3 = 12`, passed to `CFont::SetStrPrim` at `0xBF59E4`.
- VA `0xBF59DC`: `x22 = this + 0xA320`, passed as the font sprite pool.
- VA `0xBF5A98`: sprite range begins at `x22`. VA `0xBF5AA0`: range ends at `x22 + 0x360`.
- `0x360 = 12 × 72 bytes` and VA `0xBF5AD8` accounts for exactly that range.
- **Do not enlarge** until neighboring object storage is mapped.

**Dynamically allocated pool: `CUISkillEditWnd::RegisterPoint`**
- VA `0xCA64B8`: global sprite reservation increments by **7**; VA `0xCA64BC` checks remaining capacity.
- VA `0xCA650C`: primitive start = `pool_base + used_count × 72`; `0xCA6510` commits the increased count.
- VA `0xCA65C8`: `w3 = 7` passed to the same font routine at `0xCA668C`.
- VA `0xCA66BC`: registered range end = start + `0x1F8 = 7 × 72 bytes`.
- This is structurally **different from the embedded Action List or character-select pools**. An enlargement would have to change allocator reservation, renderer count, pointer end **and prove spare global pool capacity**. Never change only one immediate.

### Important limitation

**Neither font call has yet been unambiguously mapped to one of the six specific screenshot headings**. The seven-sprite operation could render some other text. The screenshot shows clipping consistent with limits but does not identify which draw call. We must trace the selected record through the resource lookup path before creating an isolated test; this prevents accidentally fixing the wrong UI text or overwriting another widget.

## Next action

Map the unique text records **2942 (Requirements)** and **2949 (Points Required)** through `CUISkillInfoBoard::RegisterLearn/RegisterPoint` and verify their exact backing sprite ranges. Use these as candidate pilots, not pre-selected patch addresses. Investigate record **2953**'s escape interpretation separately. Preserve v9.3.9 rollback and keep v9.3.11-EXP X-held Action List pagination separate.

See [Milestone M1 #11](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/11), [skill menu #10](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/10), and [PC-to-Switch differences](PC_TO_SWITCH_DIFFERENCES.md).
