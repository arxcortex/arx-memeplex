# Thrives in

Adds `thrives_in` to every idea: 1-4 places where the idea is strongest today, or, for historical ideas (`historical: true`), where it flourished at its height. Each place has a Grokipedia source and a one-line note. A place was kept only if the cited article names it; places that could not be confirmed were left out, and ideas with no confirmed place are marked `uncertain: true` and show "Not yet sourced".

Page changes (in `memeplex.html` here):
- Idea panel: "Thrives in" (or "Thrived in" for historical ideas) sits beside Key thinkers.
- Memele: new "Where it thrives" clue. Share text and share card are unchanged and stay spoiler-free.
- Thinker Match: rounds 2 and 4 ask which idea thrives in a place; wrong options never list that place.

Checks: `python3 scripts/validate.py`, then `python3 t_thrives.py` from this folder (tour validator, alias search, panel, Memele clue, Thinker Match ambiguity over 300 seeds, screenshots).
