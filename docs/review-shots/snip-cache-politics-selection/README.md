# Snip cache fix, Politics button, selected-idea highlight

- Snip card showed a broken image on a local test server: the browser kept a cached `assets/sharecard.js` from before Snip & share, which has no `snip()`. The page now loads `assets/sharecard.js?v=20261029` and, if `snip()` is still missing, shows a "reload with Ctrl+F5" message instead of a broken image.
- Modern politics was only reachable inside the Views menu (and Views is hidden on phones). It now has its own **Politics** toolbar button (key P), shown on desktop and phone, that toggles the view and key.
- Selected idea: its label is always shown as a bright amber pill on top of other labels, and its node gets a glowing ring, until deselected. The ring is a non-interactive overlay, so picking and zoom are unchanged (pick-fix and smooth-zoom tests give the same results as main).

Test: serve `../snip-share/` and run `python3 t_fix.py`. Results in `results.json`.

## Follow-up: opening the page as a file
- Snip card was blank when the page is opened straight from disk (file://): the Arx logo PNGs count as cross-origin there, so the canvas was tainted and `toBlob` failed. On file:// the card now uses small embedded copies of the logos, and a failed export now shows an error instead of a broken image.
- Politics config now falls back from Pages to a `politics.json` beside the page, then to a copy embedded in the page, so the view and key always appear.
- Test both ways: `python3 t_fix.py` (http) and `MODE=file python3 t_fix.py` (file://, Pages politics.json blocked). Results in `fix.json` and `file-fix.json`.
