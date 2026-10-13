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

It checks file hashes, row counts, per-row words, and layout-only newline changes. **It does not patch any file or determine runtime renderer behavior.** It passed a local self-test comparing v9.3.9 action text and v9.3.10 wrapped text: 184/184 rows retain wording, exactly 152 help descriptions changed in wrapping only, 0 content-difference rows. The actual PC `0024.vap` was not included in the current isolated self-test. Copyrighted game files stay outside the repository.
