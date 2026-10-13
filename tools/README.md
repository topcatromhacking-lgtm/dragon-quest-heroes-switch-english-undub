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
