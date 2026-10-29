# Tours v3 with tour kinds

**Based on `feat/modern-currents`. Merge that PR first.** The Aristotle-to-Sartre and Jerusalem-to-Azusa Street tours use ideas and links that branch adds: Holiness movement, Brentano's intentionality, existential phenomenology → existentialism, and Leninism → Trotskyism.

- The five placeholder tours are replaced by five researched tours. Every caption comes with a source.
  - From Plato's Academy to the Ming court (**transmission**, 7 stops)
  - From Kant to the CPUSA (**genealogy**, 6 stops)
  - From Jerusalem to Azusa Street (**genealogy**, 7 stops)
  - From the Bolsheviks to the neoconservatives (**genealogy**, 5 stops)
  - From Aristotle to Sartre (**genealogy**, 5 stops)
- Each tour has a new `kind` field: genealogy, transmission or narrative.
  - A colored badge shows the kind in the tour picker and in the tour bar.
  - The picker gives a one-line meaning for each kind it shows.
  - The first stop of a tour shows the badge and its meaning.
- Every pair of consecutive stops is a direct parent/child link in ideas.json. `build_tours.py` checks this and stops if one isn't, and `__tours.validate()` checks it again in the page.
- Files:
  - `memeplex.html` is the page.
  - `tours-v3.json` is the source data.
  - `build_tours.py` builds the tours into the page.
  - `t_tours_v3.py` is the browser test.
- Screenshots: tour-picker-kinds.png, tour-start-header.png, tour-in-progress.png and tour-in-progress-narrow.png.
