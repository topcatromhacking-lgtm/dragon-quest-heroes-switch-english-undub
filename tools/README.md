# Read-only resource analysis tools

These three scripts were recovered from earlier DQH1 investigation. They inspect **user-supplied extracted assets locally** and write CSV/TXT reports. They do not modify the original game files.

They have passed Python syntax compilation and `--help` invocation checks; full scans and outputs have **not** yet been revalidated in this repository.

Run with Python 3:

```bash
python tools/dqh1_resource_mapper.py /path/to/pc_extraction /path/to/switch_extraction /path/to/output_map
python tools/dqh1_signature_census.py /path/to/pc_extraction /path/to/switch_extraction /path/to/output_signatures
python tools/dqh1_gt1_mapper.py /path/to/pc_extraction /path/to/switch_extraction /path/to/output_textures
```

The scripts expect extracted game assets that **you must supply yourself**. They cannot unpack or obtain games. Never commit game files or output dumps containing copyrighted source data. Scanning large extracted trees can take time.


## Western PC ↔ Switch Action List comparison (read-only)

Use [compare_dqh1_action_vaps.py](compare_dqh1_action_vaps.py) with **your own extracted Western PC** `0000000000000024.vap` and **your own already English-patched Switch** `0000000000000008.vap`:

```sh
python compare_dqh1_action_vaps.py /path/to/PC/0000000000000024.vap /path/to/SW/0000000000000008.vap --json action_comparison.json
```

It checks file hashes, row counts, per-row words, and layout-only newline changes. **It does not patch any file or determine runtime renderer behavior.** It passed a local self-test comparing v9.3.9 action text and v9.3.10 wrapped text: 184/184 rows retain wording, exactly 152 help descriptions changed in wrapping only, 0 content-difference rows. The user subsequently supplied the actual Western PC `0024.vap`, and its SHA-256 is an exact match to the **English-transplanted v9.3.9 Switch VAP**: `eaeab8f434085119f9efdc4a0c06a2a7bcd3ef7b5f4b5c759b3db24f76620aa4`. This is expected for a direct data transplant and does **not** imply that the original Japanese Switch VAP shipped with English content. Copyrighted game files stay outside the repository.


## Native Action List sprite allocation audit

The [Action List capacity tool](analyze_action_display_capacity.py) reads the user's own Japanese Switch 1.0.0 NSO `main` and optional transplanted VAP, then verifies **nine executable instruction sites** explaining the **60-sprite limit**. It is read-only and does not contain or emit game assets.

```sh
python -m pip install lz4
python analyze_action_display_capacity.py /path/to/Switch/main --action /path/to/transplanted/0000000000000008.vap
```

See the [technical report](../docs/ACTION_LIST_60_SLOT_LIMIT.md). No gameplay patch for the executable is ready.


## Offline Action List two-page layout planner

The [page planner](plan_action_list_pages.py) and [synthetic unit tests](test_plan_action_pages.py) take the user's **original Western PC** `0000000000000024.vap` and estimate whether each complete English Action List description fits safely in one or two pages of the **existing native 60-primitive buffer**. The source is never modified; the default output is a metadata-only report.

```sh
python tools/plan_action_list_pages.py /path/to/PC/0000000000000024.vap --summary /tmp/action_page_stats.json
python -m unittest discover -s tools -p 'test_plan_action_pages.py' -v
```

Full-corpus offline result: **77 one-page, 107 two-page, 0 three-page; complete wording preserved in all 184 cases**, with 58 estimated units per page and 39 per line. Seven synthetic tests pass. These are **not measurements of actual Switch font sprite use**, and no executable hook or in-game page control has yet been developed. Optional `--local-preview` writes copyrighted game text; **do not commit/upload the generated preview**. See [pagination engineering design](../docs/ACTION_LIST_PAGINATION_DESIGN.md).


## Milestone M1: original Switch skill UI capacity audit

Use the [source-only, read-only skill audit](audit_skill_ui_capacity.py) with your original Japanese Switch DQH1 v1.0.0 NSO and the Western PC extracted `0000000000000001.vap`:

```sh
python -m pip install lz4
python tools/audit_skill_ui_capacity.py /path/to/original-exefs/main /path/to/PC/0000000000000001.vap --output skill_audit.json
```

All **14 fixed-budget instruction/BL pairs** were checked against the original NSO. Six complete English PC strings were located. This is **not a patch tool**; do not modify cap immediates until the corresponding backing sprite pools are proven safe. See [M1 findings](../docs/M1_SKILL_LABELS_REPORT.md).


## M1 skill label: inspect a running English-transplanted DQH1 RomFS

After performing the Switch original-code audit, use [inspect_transplanted_skill_text.py](inspect_transplanted_skill_text.py) to check where the **full** strings actually live in the installed English DQH1 LINKDATA. This reads only; no source file is modified. A synthetic 4501-record VAP/IDX mapping test passed.

```powershell
python -X utf8 tools/inspect_transplanted_skill_text.py "C:\\path\\to\\english-romfs\\dqh1" --scan-all --output skill_report.json
```

Send only the small `skill_report.json` output, not the multi-GB LINKDATA archive. The optional full scan checks **uncompressed** entries only; absence in these entries does not prove the string is absent from compressed/indirect resources. The default scan checks just system slot 3.
