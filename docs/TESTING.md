# Regression test matrix

This checklist is based on playtest screenshots and notes. **Checked tests are not implied here:** each case must be executed again on the recovered baseline and after every risky engine-level change.

| Test ID | Scene / action | Required outcome |
| --- | --- | --- |
| OPEN-01 | Start a fresh game and play opening `mv002.mp4` | Western/English visual intro plays without desync; Japanese voice/audio remains |
| MENU-01 | Initial game/control menus | Titles and descriptions fit; correct English strings without accidental shortening |
| MENU-02 | Camera Settings options | No Japanese leftover for Player Distance; all descriptions fit the box or wrap cleanly |
| CHAR-01 | Hero selection Luceus/Aurora | Both biographies fit their independent cards |
| CHAR-02 | Narration beneath hero selection | All text displays, no one-line truncation |
| CHAR-03 | Character naming | Requested Latin naming support works; no corrupted glyphs |
| NPC-01 | Talk to Old Man | Every paragraph complete with natural wraps |
| NPC-02 | Talk to Young Lady | Both multi-line entries complete |
| NPC-03 | Talk to Healix | No cut ending such as `it's jus` |
| NPC-04 | Talk to soldier about skill points | Long explanation complete and speaker name not truncated |
| NPC-05 | Talk to Doric at camp | Long messages paginated/reflowed correctly |
| NPC-06 | Group conversation with Doric, Luceus and Terry | **Correct portrait for each speaker**; no spurious Terry portrait |
| NPC-07 | Longer group-conversation follow-up | No overflow beyond dialogue box, no lost ending |
| SHOP-01 | Browse and sell items | Name, price and text placeholders present |
| SHOP-02 | Item descriptions | No truncation at ~30 visible chars; long descriptions stay readable |
| SAVE-01 | Create/delete adventure log | Text and dynamically inserted save slot/level values correct |
| SAVE-02 | Reload saved game | Save integrity preserved |
| AUDIO-01 | Play spoken scenes | Japanese voice acting retained |
| REG-01 | Compare against prior accepted baseline | No previously complete line becomes shorter; no new portrait/placeholder corruption |

## Evidence to record per test

Game title/version, environment (Eden build or real Switch), patch revision/hash, save point, original and expected text, actual screen capture, voice-language confirmation where relevant, and pass/fail with reproducible steps.

## Patch discipline

Change one engine-level hypothesis at a time. Run a small smoke suite before full regression. Failed experiments remain on isolated branches, never overwrite the baseline, and must be clearly identified as unverified.
