# DQH1 Switch English Undub v9.3.11-EXP: Action List page-switch hook

**Research-grade executable experiment. NOT gameplay-validated. NOT the stable v9.3.10 release.**

This test attempts to show every word of the official Western PC Action List help without changing the original Japanese Switch game's **60 × 72-byte** embedded sprite pool. It uses a hold-to-show-page-2 input candidate. Releasing the input shows page 1. The physical controller button for the candidate PAD bit **20** is **not proven**; do not describe it as a verified ZL or ZR binding.

## Inputs: files from your own game copies

- Original **Japanese Switch DQH1 1.0.0** ExeFS `main` (exact SHA-256 `cc9dfbc99f1a60120fd30b3e82dc98a17e6b2754f9cad6acfd5be329cbe63e4d`). **Do not use a different update/version/region.**
- Official Western PC extracted `0000000000000024.vap` (SHA-256 `eaeab8f434085119f9efdc4a0c06a2a7bcd3ef7b5f4b5c759b3db24f76620aa4`).
- Your **already patched v9.3.10** DQH1 gameplay folder containing `LINKDATA.BIN` and `LINKDATA.IDX` (not the separate smaller startup-menu archive).
- Python 3.10+ and Python module `lz4` (`python -m pip install lz4`). The patcher uses built-in original AArch64 hook machine code generated from `page_selector.S`. **No native compiler is required on Windows**.

## Build (Windows PowerShell)

```powershell
python -X utf8 build_action_pagehook.py --pc-action "C:\DQH_PC\0000000000000024.vap" --switch-main "C:\DQH_Switch_100\exefs\main" --gameplay-dqh1 "C:\DQH_v9310\romfs\dqh1" --output "C:\DQH_Action_Page_Exp"
```

This writes **new, isolated copies** under:

- `C:\DQH_Action_Page_Exp\romfs\dqh1\LINKDATA.BIN` and `.IDX`
- `C:\DQH_Action_Page_Exp\exefs\main`
- `C:\DQH_Action_Page_Exp\VALIDATION.json`

**Never copy the DQH1 gameplay LINKDATA into the starting menu's LINKDATA location.** Keep the v9.3.5 starting-menu archive and v9.3.6 movie/audio overrides in their existing directories. When testing, install the output as a single separate test mod/profile; avoid overlapping duplicate game-archive overrides. Back up your known-good v9.3.9 profile.

## Controlled Eden test

1. Confirm the game progresses past the 30th Anniversary splash. Abort and restore the working profile if it does not.
2. Open Actions (formerly Action List), select **Attack (No MP Used)**. Confirm that the first description page displays without reaching past the box border.
3. With the cursor on that entry, **try holding ZL** to see whether the remainder appears. If not, try ZR. These are **diagnostic guesses**, not established button identities. Record the result, and do not remap unrelated game controls to make this work. The hook actually tests PAD bit 20 via `GetLevel(0)`.
4. Release the input and check page 1 returns. Change entries/characters, close and reopen the menu, and confirm normal L/R and Y functions still work. Try Inferno Slash, Recovery, a description with a controller icon, and short entries (these have no page 2).
5. Check that Japanese audio, existing Control graphics, menu names, saves and original startup screen are unchanged.

**Do not treat a failed ZL/ZR test as evidence that pagination is impossible.** It may only mean the game maps those buttons to different PAD bits. The `--button-bit` option allows a *new separate experiment* with a different known bit, but arbitrary values should not be distributed as fixes.

## Technical implementation

- Verified `NActProj::STR_GetBtlActionExplanation` (`0x55B18`) forwards to `CXLSBinary::GetString` (`0xE8F28`), which returns a pointer into the loaded VAP. The original Japanese Switch text was separate; it **never shipped with the PC English data**.
- A new VAP has **77 single-page** and **107 double-page** entries, all 184 official PC descriptions recoverable. Second pages use a NUL-separated marker `0x1F DQH2 0x1F` recognized **only** by our code.
- Original `CMenuBtlAction::OnRegister` instruction at `0x251C28` is changed from `mov x2,x21` to a near `bl` targeting a new 132-byte routine at `0x11B7700`, within the original gap before `.rodata` (starts `0x11B8000`). The text section is extended to precisely the next page boundary; **other sections retain identical decompressed bytes and hashes**.
- The hook preserves x0/x1/x3/x4 and callee-saved registers, calls the original `CPadManager::GetInstance` and `GetLevel`, and chooses page 2 only with the held candidate input and a matching resource marker. The font still receives the original **60** limit and original persistent sprite buffer. No global font hook, heap allocation, or custom persistent menu state.
- Rebuild `main` by recompressing and verifying all three NSO segments, recalculating affected header offsets, segment lengths, and checksums; verify six source instruction signatures and original executable SHA-256.
- Rebuild VAP pointers with full source words preserved. Append the rebuilt resource to the end of the **gameplay** `LINKDATA.BIN`; update **only** Action VAP IDX entry #8. This avoids overwriting the next packed resource. The system VAP and Western PC Control atlas are SHA-256 protected.

### Remaining caveats

The physical PAD bit 20 has **not** been measured in Eden. The NSO changed its text section size while preserving original rodata/data and load addresses; static integrity checks cannot guarantee the loader supports the change. The VAP loader may impose resource size/offset constraints not encountered in synthetic tests. Font pixel widths, UTF-8 accented `â`, input repeat, page indicator, and real renderer behavior still need live validation. This does **not** solve the separate Coup de Grâce accented-glyph problem.

## Offline tests

Five independent tests passed using a supplied original Switch NSO, Western PC VAP and a locally rebuilt v9.3.10 Action VAP. They covered all 184 records and markers, version rejection, multiple button-bit configurations, lossless NSO roundtrips and a synthetic IDX/BIN append-and-readback.

To run equivalent tests locally, extract your patched Action VAP and set `DQH_PC_ACTION_PATH`, `DQH_MAIN_PATH`, and `DQH_V9310_ACTION_PATH` environment variables, then run `python -m unittest discover -s . -p test_pagehook.py -v`. Without those variables the tests correctly skip rather than fetch assets.

## Rollback and distribution

All patch scripts are source-only, without any PC/Switch binary/text asset. Do **not** upload generated NSO, `.vap`, `LINKDATA.BIN`, movies, audio, or ROMFS to GitHub. Revert by removing the **entire v9.3.11-EXP override** and restoring the complete original v9.3.10 test profile (or v9.3.9 gameplay-validated profile). Never mix and match the patched executable with older/non-tagged Action VAP sources while testing this hook.