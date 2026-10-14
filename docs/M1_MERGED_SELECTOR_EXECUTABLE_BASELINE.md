# DQH1 executable checkpoint: 2026-10-14

**What this contains:** the user-confirmed English game selector **and** the
previous v9.3.14-EXP Skill Tree BSS + v9.3.11 Action List X-held hook, in the
same working `exefs/main` executable. This ZIP **does not** distribute the
Nintendo executable or any extracted game assets.

## Immutable fingerprint

The currently uploaded `main(7)` has SHA-256:

`47116b6c07abd8dba61c659aac7226a4bb6e221d0ae38fd2963e1ff273f3c745`

Its exact provenance has been established by reconstituting the prior unmerged
v9.3.14-EXP + X-held Action List main **only by restoring original Japanese
rodata/data**, then reconstructing the original NSO compression and section
hashes. The resulting SHA-256 is exactly:

`376acf9e707319edd0c80126c7da53415d78f879b804e9a50ce52f15f906e7fb`

Thus the selector restoration did **not modify any of the executable code**
from the previous known v9.3.14+Action List build. It changes 159 bytes of
rodata and 257 bytes of data compared with the *original* Japanese executable.

Protected checks include:

- The Action List page selector (132 bytes at VA `0x11B7700`).
- The BSS skill description initializer (52 bytes at VA `0x11B7800`).
- Seven original code-site modifications for the prior M1/pagehook fixes.
- The extra BSS page (size `0xD43FF8`).
- English game-selection prompt and both game-specific confirmation strings,
  plus `Yes` and `No` string data.
- NSO section decompression and embedded SHA-256 checks.

**Runtime qualification:** the user reports the starting menu's English
restored, and previously demonstrated the v9.3.14 Inferno Slash description
capacity restoration. This binary audit cannot confirm every skill/character
interaction, save/load, Japanese voices, or all control sequences. The English
selector and skill scripts should be tested again together after further edits.

## Verify on Windows

Extract the source-only ZIP and run:

```powershell
python -m pip install lz4
python -X utf8 verify_merged_main.py `
  "C:\PATH\TO\ORIGINAL_SWITCH_1.0.0\exefs\main" `
  "C:\PATH\TO\CURRENT_WORKING\exefs\main" `
  --report baseline_report.json
```

The original Japanese 1.0.0 main and the merged working main must have the
exact hashes above. For a **future** executable built on this baseline,
include `--candidate "C:\PATH\TO\NEW_BUILD\exefs\main"` to detect accidental
loss of the selector or overwriting of previously validated hooks. The future
candidate mode intentionally rejects changing protected hook locations: if a
future feature deliberately replaces one, it requires a new reviewed baseline
and updated checks rather than skipping verification silently.

**This tool does not edit or generate any game executable.** It emits only
integrity metadata, without game strings or copyrighted assets.
## Hash verification in development container

The hash-gated verifier independently decompressed all three NSO sections, confirmed the seven protected native instruction sites, both helper-code hashes and the extended BSS, and repacked the original selector-free rodata/data to exactly match previously recorded pre-merge v9.3.14+X SHA-256. The verifier and a JSON evidence manifest are supplied in the [source-only chat ZIP], not as a game binary.
