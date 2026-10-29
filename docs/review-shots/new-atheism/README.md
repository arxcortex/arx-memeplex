# New Atheism to the online right (tour + 7 ideas)

`build_new_atheism.py <research.json>` adds the seven fact-checked ideas to `ideas.json` and appends the narrative tour to this folder's `memeplex.html` (`TOUR_DATA`) and `tours.json` (tours-v3 format). `t_new_atheism.py` loads the page with the new data, runs the in-page tour validator, checks every consecutive stop is a real parent/child edge, runs the search checks and takes the screenshots.

- `tour-start.png`: the tour's first stop
- `tour-middle-stop.png`: stop 4 of 6 (Gamergate)
- `lineage-gamergate.png`: Gamergate selected, lineage view

Page change in this copy: the top search bar also matches `aliases` and ignores accents (so "Atheism+" finds Atheism Plus and "Ásatrú" finds Heathenry).
