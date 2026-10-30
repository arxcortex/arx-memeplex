# Modern politics view

Views → **Modern politics** (URL `#v=politics`; a non-default country adds `pc=<id>`). It uses the default map layout and recolours it.

- **Data:** `politics.json` (repo root) lists countries. Each names the idea field that holds its alignment (`party_alignment` for the United States), the party colours (R `#d62828`, D `#1d4ed8`, mixed `#7b3fb0`), how strength words map to intensity, and the ancestor decay. To add a country, add an entry there and an alignment field on the ideas; the picker and key are built from the data.
- **Factions** (ideas with an alignment) take their party colour; weaker strength fades toward the dim colour. `lean R`/`lean D` on a mixed faction tilts its share 65/35 for ancestor mixing, while the faction itself stays purple.
- **Ancestors:** lineage is walked up from every faction. Each ancestor collects red and blue weight (strength × 0.7 per step), and its colour runs red → purple → blue by the blue share, brighter the more it feeds in. Shared ancestry comes out purple.
- **Unrelated ideas** are dimmed and shrunk. Faction labels are always shown.
- **Key** (bottom left; on phones above the toolbar, hidden while an idea is open): country picker, party swatches, the red–purple–blue mix bar and the faction list with party and strength. Click a faction to open it.
- **Panel:** any idea with an alignment shows a "Modern politics" box with party, strength, the note and the source link.
- Leaving the view restores the normal colouring; Snip, tours, filters and other views are unchanged.

Test: `python3 t_politics.py` (desktop and phone). Screenshots: `politics-*-view.png`, `politics-*-panel.png`, `politics-desk-snip.png`; numbers in `results.json`.
