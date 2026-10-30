# Snip & share

The toolbar has a **Snip** button (shortcut **S**). Press it and the cursor turns into a crosshair. Drag a box over any part of the map; touch works too. Esc cancels.

- **Capture:** the WebGL frame is rendered on demand and read in the same task, so `preserveDrawingBuffer` isn't needed. The visible idea and axis labels (DOM) inside the box are redrawn onto the 2D canvas at their screen positions.
- **Card:** the card always has the shape you snipped. There are no size presets. It is drawn at about 2× CSS pixels, at least 640 px wide, with the longest side capped at 4096 px. An Arx strip goes along the bottom edge and never crops the snip: the sigil, ARX CORTEX · THE MEMEPLEX, an optional title (the selected idea's name or "Memeplex") and the link text. It is rendered by `ArxShareCard.snip()` in `assets/sharecard.js` with the same fonts and colours as the game cards.
- **Link:** `https://arxcortex.io/memeplex.html#i=<id>&v=…&ax=<axis>&cam=x,y,z,tx,ty,tz`. When the page loads it restores the view, the axis colouring, the selected idea, and then the exact camera. Older `#i=` links still work, and the live URL hash doesn't carry `cam`.
- **Actions:** Download PNG; Copy image (`navigator.clipboard.write` with a ClipboardItem, where the browser supports it); Copy link; Share (`navigator.share` with the file where possible, otherwise it opens an X post intent with the text and link for you to post yourself). Nothing is ever posted automatically.
- **Phone:** the idea panel is hidden while you snip, so the map can be captured.

Test: `python3 t_snip.py` (desktop and phone). Screenshots: `snip-*-overlay.png`, `snip-*-card.png`, `snip-phone-restored.png`.
`assets/brand/` is included only so the review page renders the marks; the live site already has it.
