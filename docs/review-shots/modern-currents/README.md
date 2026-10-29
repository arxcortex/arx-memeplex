# Modern currents + timeline view + compare search + card footer fix + game reset

Data (+13 ideas, 141 total; validate.py OK):
- Feminism strands: Liberal feminism (1792, London), Socialist feminism (c.1896), Radical feminism (1967, New York), Black feminism (1977, Boston)
- Critical race theory (c.1973), Intersectionality (1989), Social justice (woke) (2014, Ferguson)
- America First (1940; Buchanan 1990s, Trump 2016+, Groypers 2017+), MAGA (2015), Postliberalism (c.2018), National conservatism (2019)
- Renames (ids unchanged): post_vatican_ii_catholicism -> "Vatican II Catholicism"; old_right -> "Old Right" (America First now its own node)
- Script: add_modern.py (run from repo root on main's ideas.json)

Page (memeplex.html here; diff vs games-hub in memeplex-html.diff; assets/sharecard.js updated):
- "Linear timeline" view: time left to right on a piecewise scale (1800+ and 1900+ get more width), year ticks along the bottom, orbitable 3D (abstraction up, hierarchy in depth), lineage lines drawn. Default map unchanged. __views.check(): 0 breaks.
- Compare search box: fuzzy search with aliases (same as Memele); map clicks still work; desktop + phone.
- Memele aliases: woke / social justice, make america great again, groypers, post-vatican ii catholicism.
- Share cards: fixed footer zone (SAFE = H-224); sections dropped or trimmed to fit; at most 2 shared ancestors + "+N more"; game cards shrink rows and cap lines.
- Games hub: "Reset today" (clears today's Memele + hub game state, keeps streak/best) and "Reset all stats", each with a confirm step.

Tests: t_modern.py (views, timeline order, ticks, tours.validate, Memele aliases, hash link, compare search, reset), t_cards.py (12 cards incl. the longest ideas, all PASS: content ends above footer).
- Also: Holiness movement (c.1835, parent Methodism; now a parent of Pentecostalism), Brentano's intentionality (1874, Vienna; now a parent of Phenomenology)
- New edges: Leninism -> Fascism (contested, see PR), Leninism -> Trotskyism, Heidegger's existential phenomenology -> Existentialism
- Selection labels: when an idea is selected (click, deep link, Trace lineage) only its lineage keeps name labels; all return on deselect (t_lbl.py; labels-before/after-*.png).
- Hub games endless: Lineage Ladder, Odd One Out, Thinker Match play random rounds with "Play again"; streak = correct answers in a row (current + best + last 10 rounds in localStorage arxgames-v1.stats). Memele stays daily. Reset today now only resets Memele; Reset all stats clears everything.
- Game share cards show recent rounds (offered ideas, answer, pick, root) with ✓/✗ and streak, no date number; Memele keeps the spoiler-free grid. Captions wrap instead of clipping.

## Fix pass (density axis + weak links)
- Default map height is now pure density rank (TIME_RANK=1, TIME_H=52): each period gets height in proportion to its idea count, so 1800+ and 1900+ open up. Before/after: density-before-default-*.png / density-after-default-*.png.
- Linear timeline is now true to scale (linear years).
- Weak links: removed Radical feminism→Black feminism, New Left→Social justice, New Left→CRT, Frankfurt→CRT. Kept Socialist feminism→Black feminism (Combahee members were socialists; cited). Added Critical legal studies (1977; Kennedy, Unger, Horwitz) between New Left/Frankfurt/Marxism and CRT; CRT dated late 1970s (1979 approx). Social justice ← intersectionality, CRT. Brentano ← Aristotelian teleology, Thomism (sourced: Intentionality, Franz Brentano pages). Patricia Hill Collins verified on the Intersectionality page. Leninism→Fascism kept, flagged contested.
