# Alt views (helix, beatific vision, tree of life, galaxy, sphere, brain)

Views panel in the toolbar (or press V). On load the map opens in a random alt view and glides into the default map (skipped with reduced motion).

Coherence: each view has a time direction (height, ring radius, arm radius, latitude, distance from stem). `__views.check()` verifies parent ≤ child along it for every lineage edge: 0 violations in all 6 views. All edges stay drawn. Families keep one sector, ordered by mean abstraction; inside a sector a child sits next to its parent.

Stretch works in the default map only (button greyed in alt views). Filters, branches, domain and search work in every view. Edge pulses and center glow switch off on low-end devices (≤4 cores or ≤4 GB) or if intro FPS < 40. Headless FPS (software GL): desktop ~13-17, phone ~7, so not a real-device number.

Shots: intro-*, mid-tween-to-tree, one per view, mobile-*, brain-filter-christianity, reduced-motion-start.
