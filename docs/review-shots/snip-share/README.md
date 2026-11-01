# Snip & share

The toolbar has a **Snip** button (shortcut **S**). Press it and the cursor turns into a crosshair. Drag a box over any part of the map; touch works too. Esc cancels.

- **Capture:** the WebGL frame is rendered on demand and read in the same task, so `preserveDrawingBuffer` isn't needed. The visible idea and axis labels (DOM) inside the box are redrawn onto the 2D canvas at their screen positions.
- **Card:** the card always has the shape you snipped. There are no size presets. It is drawn at about 2× CSS pixels, at least 640 px wide, with the longest side capped at 4096 px. An Arx strip goes along the bottom edge and never crops the snip: the sigil, ARX CORTEX · THE MEMEPLEX, an optional title (the selected idea's name or "Memeplex") and the link text. It is rendered by `ArxShareCard.snip()` in `assets/sharecard.js` with the same fonts and colours as the game cards.
- **Link:** `https://arxcortex.io/memeplex.html#i=<id>&v=…&ax=<axis>&cam=x,y,z,tx,ty,tz`. When the page loads it restores the view, the axis colouring, the selected idea, and then the exact camera. Older `#i=` links still work, and the live URL hash doesn't carry `cam`.
- **Actions:** Download PNG; Copy image (`navigator.clipboard.write` with a ClipboardItem, where the browser supports it); Copy link; Share (`navigator.share` with the file where possible, otherwise it opens an X post intent with the text and link for you to post yourself). Nothing is ever posted automatically.
- **Phone:** the idea panel is hidden while you snip, so the map can be captured.

Test: `python3 t_snip.py` (desktop and phone). Screenshots: `snip-*-overlay.png`, `snip-*-card.png`, `snip-phone-restored.png`.
`assets/brand/` is included only so the review page renders the marks; the live site already has it.

# Menu and chart views

The toolbar keeps only the controls that change the default map: **Menu**, Search, Color, Filter, Stretch, Snip, Hide politics, Light/Dark, the Impact slider, Lines, Hide UI and Reset. Everything else is in the **Menu** button (shortcut **M**; **V** opens it too): the chart views below, the map shapes (Helix, Tree of life, Choose your axes, National and the rest), Random, Tours, Games, Copy link, the map key, Help and About the symbols. The menu works with the keyboard (arrow keys, Tab, Esc returns focus to the button) and becomes a bottom sheet on phones. The page still opens on the default map.

Chart views are flat SVG drawings over the map, computed in the page from the same data. Each one keeps its state in the link (`#v=<view>&f=…&g=…`), follows light and dark mode, and works with Snip & share (the visible part of the chart is rasterised into the card). Searching for an idea while a view that follows one idea is open retargets that view; **Open idea page** shows the usual panel. Older links (`v=axes&x=…&y=…`, `v=national&ns=…`, `ui=0`, `i=…`) work as before.

- **Family tree** (`v=family&f=<id>`): the idea, every mapped ancestor above it and every descendant below, one band per generation. A generation is the fewest lineage steps between two ideas. Inside a band, ideas sit near the ideas they connect to. Click an idea to center the tree on it. Also on every idea page.
- **Fingerprint** (`v=fingerprint&f=<id>&g=<id>`): the idea's scores as a radar shape. The center is −5, the bold ring 0, the rim +5. A second idea is drawn dashed on top, with the score gap and the biggest differences below. As on the idea page, tone scores are left out when a root idea is involved. Also on every idea page, and as Fingerprints on a comparison.

Test: `python3 t_views.py` (desktop and phone). Screenshots: `views-*-menu.png`, `views-*-family*.png`, `views-*-fingerprint*.png`.
