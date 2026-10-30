# World politics view: review shots

Test: `python3 t_world.py` (from this folder). It runs desktop 1440x900 and phone 390x844, over http and file://, and checks:
- no console or page errors;
- the Politics key lists US, UK, France, Germany, Russia, China and Japan, and each country's key and factions render;
- Russia and China use bloc mode; China's three judgment shades read "Proposed shade, no party color";
- the CDU swatch is drawn #5c5c5c with an outline;
- the Hide politics toolbar button (also in Filter, and the H key) hides all 41 modern_politics ideas, their labels and their links, and restores them;
- the selected-idea highlight and panel still work;
- a Snip & share card renders with the brand strip.

Results are in `results.json`. Screenshots: `world-<proto>-<desk|phone>-<country|selected|hidden|snip>.png`.
