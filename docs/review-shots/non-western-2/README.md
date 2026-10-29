# Non-Western batch 2 (+ absolute sovereignty)

Six new ideas (158 total). Every fact was checked against the cited Grokipedia pages, which all return 200.

| id | year | place | parents |
|---|---|---|---|
| jainism | c. 557 BCE | Bihar, India | none (parent_note: arose among the sramana movements, which are not a node) |
| samkhya | c. 350 | India | upanishadic_brahman |
| yogacara | c. 350 | Purushapura (Peshawar) | buddhas_dharma |
| illuminationism | c. 1186 | Aleppo | avicennism, neoplatonism, sufism |
| absolute_sovereignty | 1576 | France | aristotelian_teleology |
| transcendent_theosophy | c. 1628 | Kahak, near Qom | avicennism, illuminationism, sufism |

New edges on existing ideas, each sourced in edge_notes:
- absolute_sovereignty → divine_right_of_kings. Grokipedia, Divine right of kings: Bodin's Six Books "synthesized absolutist theory".
- absolute_sovereignty → social_contract. Grokipedia, Jean Bodin: his doctrine influenced later absolutists such as Hobbes.

Each new idea carries `thrives_in` in the format PR #4's validator expects, and passes that validator. No idea names contain parentheticals; alternate names go in `aliases`. No new axes were added.

Merged or held back rather than duplicated:
- Mohism is already on main.
- Mu'tazila is already covered by the Kalam node (origin note, thinkers, sources).
- Tibetan Buddhism overlaps Vajrayana, which Yungdrung Bon already uses as its parent.
- Nyaya is left for a later run.

Tests (`t_nw2.py`, which serves the page from ../youtube-link with this branch's data):
- `__views.check()`: 0 order violations in all 9 views.
- `__tours.validate()`: 0 bad edges, and the negative control is caught.
- The panel opens for every new idea on desktop and phone.
- 0 console or page errors.

Note: adding ideas changes future Memele daily answers, because the answer is picked by index into the id-sorted list.
