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
