# Milestone M1: skill-tree label renderer investigation

Date: 2026-10-13. Target: Japanese Nintendo Switch DQH1 1.0.0 with **Western PC English transplanted**. This is a **static diagnostic**, not a game patch or a successful in-game display change.

## User-visible defects

The skill-point allocation screenshot clips `Attribut`, `Requiremen`, `Points Req`, `Skill Po`, `Switch Charac`, and `Spells a` despite some visually unused room. The small-left-panel header also shows `F4I040-E`, consistent with a potential text escape-code interpretation issue; **neither its exact origin nor meaning in that widget has been proven**.

The Western PC `0000000000000001.vap` provided by the user (SHA-256 `05982ef0729b4245321b9b86a468f0a9bd36728da25793fd7b52fd5c5f1c74ec`) contains complete source strings **Attributes**, **Requirements**, **Points Required**, **Skill Points**, **Switch Character**, and **Spells and Abilities**. Its raw file contains multiple string regions; raw occurrence alone **does not locate a unique message-record ID or prove a 1:1 message map to Switch**. Verify actual transplanted Switch records separately when the exact DQH1 archive is available.

## Original Switch executable: reproducible function discovery

Examined unchanged Japanese Switch 1.0.0 `main` (SHA-256 `cc9dfbc99f1a60120fd30b3e82dc98a17e6b2754f9cad6acfd5be329cbe63e4d`). The NSO has a valid MOD0 dynamic table and 96,661 exported/imported symbol records. DQH1-specific skill UI methods are present in the older (non-`NActProj`) namespace:

| Native method | Address / size | Relevance |
| --- | --- | --- |
| `CMenuSkillCharaSelect::OnRegister()` | `0xBF57D8` / `0x4E0` | Character-choice menu registration |
| `CUISkillEditWnd::OnRegister()` | `0xCA4320` / `0x494` | Skill-tree layout, dispatches subordinate draw routines |
| `CUISkillInfoBoard::RegisterSkill()` | `0xB38A04` / `0x424` | Selected skill name / info panel |
| `CUISkillInfoBoard::RegisterEffect()` | `0xB38E2C` / `0x954` | Effect descriptions |
| `CUISkillInfoBoard::RegisterLearn()` | `0xB39780` / `0xC34` | Requirements / learn status |
| `CUISkillInfoBoard::RegisterPoint()` | `0xB3A3B4` / `0x868` | Skill-point requirements/values |
| `CUISkillEditWnd::RegisterPoint()` | `0xCA6380` / `0x8B0` | Skill-point UI labels/values |
| `CFont::SetStrPrim()` | `0xAEDDD0` | Builds glyph primitives; receives count/flags in `w3` |

Unlike the `NActProj`/DQH2-like UI, this path calls **the original non-`NActProj` font renderer**. This distinction matters: an Action List fix or primitive allocation for a different menu class must not be copied blindly.

### Bounded font registration confirmed

Fourteen exact call-site instruction fingerprints were checked against the unmodified Switch NSO. Examples:

| Registration routine | Example local immediate | SetStrPrim call |
| --- | ---: | --- |
| `CMenuSkillCharaSelect::OnRegister` | 12 | `0xBF59E4` |
| `CUISkillInfoBoard::RegisterSkill` | 18 | `0xB38DA8` |
| `CUISkillInfoBoard::RegisterEffect` | 5; 48 elsewhere | `0xB39294`; `0xB394EC` |
| `CUISkillInfoBoard::RegisterLearn` | 6; 2; 48 | `0xB39BD4`; `0xB3A0BC`; `0xB39EC0` |
| `CUISkillInfoBoard::RegisterPoint` | 6; 4; 1 | `0xB3A5E4`; `0xB3A844`; `0xB3AAC4` |
| `CUISkillEditWnd::RegisterPoint` | 7; 4; 1 | `0xCA668C`; `0xCA6960`; `0xCA6BB0` |

These are **code-path capacity candidates**, not a verified 1:1 assignment to the screenshot's six clipped labels. Some assignments are separated from calls by branches or other work; determining their actual reaching value, exact persistent primitive-pool allocation and geometric width is still required. The older font routine at `0xAEDDD0` moves `w3` into an internal count variable and iterates glyph primitives, supporting the general fixed-budget hypothesis.

**Do not patch the immediate constants yet.** Earlier Action List research proved adjacent memory corruption is possible when the render budget exceeds a backing glyph pool. The skill UI's constructor, glyph pool ownership and all direct/indirect references must be mapped first.

## Remaining work for an isolated, safe test

1. Obtain/identify the actual localized gameplay DQH1 `LINKDATA` system/skill text records in v9.3.10/v9.3.11. Determine if all six *full* official PC strings are stored; inspect escape tokens.
2. Link each screenshot widget to its actual call site using system-text IDs, register/dataflow traces, or a strictly isolated diagnostic. Avoid assuming the font-immediate values correspond to label length.
3. Trace embedded `CPrimSprt` buffers in constructors, adjacent object boundaries and renderer registration; determine whether there is safe padding or whether a separately allocated persistent pool is needed.
4. Validate one full label in Eden without changing skills, Japanese voices, button handling or unrelated strings. Test all characters and skill menus before extending the change.
5. Update the [living PC-to-Switch differences](PC_TO_SWITCH_DIFFERENCES.md) and [M1 milestone issue](https://github.com/topcatromhacking-lgtm/dragon-quest-heroes-switch-english-undub/issues/11) with verified results only.

A **read-only, version-locked tool** `tools/audit_skill_ui_capacity.py` checks source hashes, Western PC label occurrences and the fourteen AArch64 call-site pairs. It emits metadata only, never outputs or modifies game executables.