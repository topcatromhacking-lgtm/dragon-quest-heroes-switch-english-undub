# Historical PC-Western ↔ Switch-JP resource mapping

The earlier **read-only** investigation recorded these statistics (not re-run or independently verified in this repository):

| Measure | Reported result |
| --- | ---: |
| PC-Western resources scanned | 2,728 |
| Switch-JP resources scanned | 2,096 |
| Unique exact-hash pairs | 751 |
| Strong structured candidates | 64 |

Reported confirmed pairs (**PC-Western** on left, **Switch-JP** on right):

| PC-Western resource | Switch-JP resource | Category |
| --- | --- | --- |
| `0000000000000001.vap` | `0000000000000003.vap` | Menu/system text |
| `0000000000000008.dat` | `0000000000000004.dat` | Gameplay/story text |
| `00000000000000bc.vap` | `0000000000000064.vap` | Cutscene subtitles |

These correspondences are useful for narrowing the next extraction/mapping experiments, **not** proof that resources can be substituted without conversion. The original source archives and output CSVs need to be matched and rechecked. See [resource mapper](../tools/dqh1_resource_mapper.py) and [signature census](../tools/dqh1_signature_census.py).


## Action List text (newly rechecked against the archived extraction audit)

The historical `vap_family_report.txt` from the extracted **Western PC** and **original Japanese Switch** releases records:

| Western PC candidate | Japanese Switch counterpart | Structural evidence |
| --- | --- | --- |
| `0000000000000024.vap` | `0000000000000008.vap` | Both have 184 rows, 12-byte (three-column) pointer records, base 0x20. Original PC 19,256 bytes and original Japanese Switch 18,412 bytes. |

The Western PC first rows are **Attack (No MP Used)** / **Attack (Uses MP)**, followed by **Slash Combo**, **Charging Slash**, **Rising Slice** with the same full English descriptions as the current translated Switch `0008.vap`. The translated Switch baseline `0008.vap` is also **19,256 bytes**, with source SHA-256 `eaeab8f434085119f9efdc4a0c06a2a7bcd3ef7b5f4b5c759b3db24f76620aa4`.

**Direct PC file hash verified 2026-10-13:** user-supplied PC `0000000000000024.vap` SHA-256 `eaeab8f434085119f9efdc4a0c06a2a7bcd3ef7b5f4b5c759b3db24f76620aa4` is exactly the hash of the **already transplanted Western-English Switch v9.3.9 VAP**, so those two *modified/localized* assets are byte-identical. **The original Japanese Switch `0008.vap` is a separate 18,412-byte asset containing Japanese**, and has not thereby been proven equivalent. v9.3.10 changes line wrapping only and is no longer byte-identical to PC. Full Western PC text proves neither automatic PC wrapping nor how the original Japanese Switch executable renders/wraps transplanted longer English Action List help. The actual difference to investigate is **PC English content versus Japanese Switch UI engine/layout**. Do not shorten Switch action text before comparing both renderers. See [PC-to-Switch Differences](PC_TO_SWITCH_DIFFERENCES.md).
