# M1 v9.3.17R: recovery variant of the Attributes draw-list patch

**2026-10-15. Source-only ZIP reconstructed. Unverified in Eden.**

The original M1 v9.3.17-EXP technical record is preserved in [M1_V9317_ATTRIBUTES_DRAWLIST_EXPERIMENT.md](M1_V9317_ATTRIBUTES_DRAWLIST_EXPERIMENT.md). It records an experimental build SHA-256 **`53020c9e4cace2f34213467ce9ba7c99bcc16b67f0a7cc4eb2b39c30310b6f97`** and seven passing offline test groups. Its ZIP was **conversation-only and is not present** in the currently accessible files or GitHub tree. Do not claim the old source or exact artifact has been recovered.

To avoid losing work, a **new separately named v9.3.17R reconstruction** was independently implemented from the GitHub specification and original Switch binary, using exclusively the user's selector-restored `main(7)` SHA-256 **`47116b6c07abd8dba61c659aac7226a4bb6e221d0ae38fd2963e1ff273f3c745`**.

The new version performs the same principal three native instruction changes: `0x3272B8` redirects the Attributes font buffer through a 56-byte BSS clone helper at `0x11B7880`, `0x3272BC` raises the Attributes font limit from eight to ten sprites, and `0x32642C` branches to a new **132-byte draw-list helper at `0x11B7900`**, preserving the original displaced `ldrb w9,[x21]`. The added renderer entry registers the external 10×72-byte BSS range **`0x33B3A20..0x33B3CF0`** in the original render group, with the same `0x3FE` count guard. The English selector .rodata/data, the Action List and skill description hooks, original BSS size, and all RomFS are preserved.

**The recovered output is NOT byte-identical to the previously recorded v9.3.17 build.** Its new exact output SHA-256 is **`6192870b0a38df44add8dc72cc743fb76692dde4a4aa3549a0c4c35c7b2f1092`**. This is why it is named **v9.3.17R**, not presented as the same original patch. Distinct valid register-save and code-generation sequences can implement the same logical hook, but they have different binary checksums and still require independent gameplay validation.

A new set of **seven strict offline checks passed** on the canonical source: decompression/recompression and three NSO SHA digests; exact three-site patch whitelist; both BL targets and BSS ADRP targeting; preserved prior hooks and displaced instruction; original `0x3FE` capacity guard and LR restoration; wrong-binary refusal; deterministic output. Native 132-byte draw-list helper is assembled with Clang/LLVM and its bytes match the Python builder.

The user-facing source-only package in the conversation is **`DQH1_M1_v9.3.17R_EXP_Attributes_Drawlist_Reconstruction.zip`**, containing builder, AArch64 source, regression tests, manifest and instructions. It contains no compiled game executable. **No Eden success or stable release is claimed.** The last user-tested rollback is still `main(7)`.

First Eden test: game boots past the restored English selector, Attributes appears fully and remains stable when changing characters/reopening Skill Tree, adjacent headings do not regress, previous Points Required / Requirements / Details / description and X-held Action List remain functional; do not save. Any disappearing text or crash means immediately restore `main(7)`.

If the original `DQH1_M1_v9.3.17_EXP_Attributes_Drawlist_Registration.zip` is later supplied, compare its source, instructions, and resulting SHA with this reconstruction instead of silently treating them as the same release.