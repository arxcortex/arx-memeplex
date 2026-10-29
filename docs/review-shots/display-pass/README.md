# Display scaling pass (queue item 7.5)

Review package for the map page changes. The page itself lives outside this repo, so this PR carries the
patch (`memeplex-html.diff`) plus before and after screenshots. Nothing here changes the data files.

## What changed on the page
- **Taller timeline.** The time axis is about 1.7 times taller (half-height 44 instead of 26). Year rank now sets
  85% of the height (was 75%), so each idea gets an equal slice and crowded eras such as 1750 onward spread upward.
  Era ticks add 1850.
- **Camera framing.** The home view now works out the distance that fits the whole map for the screen shape
  (desktop and phone), and fog is eased so the farther view keeps the old brightness. Reset view uses the same framing.
- **Labels by zoom level.** Root ideas and ideas with two or more children are labelled at any distance. Ideas with one
  child are labelled within distance 120, and ideas with none within distance 70. In filter or branch mode the visible
  ideas move up one tier. The open or hovered idea always shows its name, and its lineage gets priority.
- **No overlapping labels.** Labels are placed in priority order (nearest first within a tier). A label that would
  cover one already placed waits until you zoom in. Pole and era labels are placed first.
- **Wider spacing.** Minimum gap between dots is 3.2 (was 2.6), and 4 where both ideas sit near the middle of the
  abstract-to-material axis, which is the crowded modern political cluster. Leaf ideas draw slightly smaller (0.85).
- Help popup: one new bullet explaining that names appear as you zoom in.

## Measurements (before / after)
Test at 1440x900 and 390x844 (phone). "130" uses 62 synthetic nodes named "Test idea N", weighted to 1750 onward,
loaded only by the test harness. Columns: labels shown / labels overlapping; dots closer than 8 px; dots off screen.

| Data | View | Before labels / overlaps | After labels / overlaps | Close dots before / after | Off-screen before / after |
|---|---|---|---|---|---|
| 68 real | default | 29 / 3 | 24 / 0 | 3 / 0 | 0 / 0 |
| 68 real | top | 29 / 28 | 15 / 0 | 14 / 10 | 0 / 0 |
| 68 real | roots-only | 20 / 1 | 17 / 0 | 0 / 0 | 0 / 0 |
| 68 real | branch-liberalism | 8 / 0 | 8 / 0 | 0 / 0 | 0 / 0 |
| 68 real | zoom-modern-politics | 4 / 0 | 6 / 0 | 0 / 0 | 23 / 29 |
| 68 real | mobile | 23 / 9 | 14 / 0 | 3 / 8 | 13 / 0 |
| 130 (68 real + 62 test) | default | 45 / 21 | 32 / 0 | 30 / 31 | 0 / 0 |
| 130 (68 real + 62 test) | top | 45 / 73 | 14 / 0 | 127 / 118 | 0 / 0 |
| 130 (68 real + 62 test) | roots-only | 20 / 1 | 15 / 0 | 0 / 0 | 0 / 0 |
| 130 (68 real + 62 test) | branch-liberalism | 9 / 1 | 9 / 0 | 0 / 0 | 1 / 2 |
| 130 (68 real + 62 test) | zoom-modern-politics | 5 / 0 | 9 / 0 | 0 / 0 | 38 / 50 |
| 130 (68 real + 62 test) | mobile | 36 / 28 | 15 / 0 | 70 / 84 | 12 / 0 |

Off-screen counts in the zoom view are expected (camera is close in). Label overlaps go to zero in every view.
The phone default view now fits the whole map (13 ideas were cut off before).

## Still open (proposals, not built)
- Close dots remain in the top-down view and on phones with 130 ideas, because many ideas share similar scores.
  Options: collapse a family into one node until clicked, or a larger minimum gap at the cost of position accuracy.
- On phones the header buttons cover the top of the map; a collapsible header would give the map the full screen.

Shots: `real-*` use the live 68 ideas; `syn-*` use the 130-node test set.
