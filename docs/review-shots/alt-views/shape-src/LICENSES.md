# Alt-view shape sources

| View | Source | License | How used |
|---|---|---|---|
| Helix | PDB 1BNA (B-DNA dodecamer), https://www.rcsb.org/structure/1BNA | wwPDB data: CC0 1.0 | Phosphate (P) atoms of the central base pairs measured: radius 9.35 Å, rise 3.12 Å/bp, twist 37.2°/bp, strands 131° apart. Page uses the 131° strand offset and radius/pitch 0.31, widened 1.8× for map scale, 4 turns. |
| Brain | "Brain and Skull" by Drummyfish, https://opengameart.org/content/brain-and-skull (head_0.obj, object `brain`) | CC0 1.0 (author: no credit needed; credited anyway) | 3,398 vertices, farthest-point sampled to 420 anchors (anchors.json). Ideas assigned oldest to nearest the brain stem; right hemisphere abstract, left practical. |
| Tree of life | Deterministic L-system in gen_anchors.py | Own code | 420 anchors along branches; ideas assigned by height bands, families by branch angle. |
| Galaxy | Logarithmic spiral in code | Own code | Procedural fallback (no dataset used). |
| Sphere | Latitude = time, longitude = family sector | Own code | Procedural (no dataset needed). |
| Beatific vision | Nine concentric rings after Dante's Paradiso | Own code | Procedural. |

Credits also appear in the page's Views panel under "About the shapes".
