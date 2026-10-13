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
