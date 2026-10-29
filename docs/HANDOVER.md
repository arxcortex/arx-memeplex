# The Memeplex — MemeBot handover

The Memeplex is Chronosphere for ideas. Each idea is a star in a Three.js constellation. Ideas with similar ratings sit near each other, height tracks time, and copper lines run from parent idea to child idea. GSAP drives every camera move and panel transition.

Status (Oct 25, 2026, HST): built and verified on the **local test site only**. Nothing is deployed, and the data repo is `arxcortex/arx-memeplex`.

---

## 1. Hard rules (read first)

- **Never deploy to Netlify.** Never run `netlify deploy`, never trigger a build, never touch Netlify settings.
- **Never post to X, and never send email or messages.** X hooks are written into stories and staged for the owner. The owner posts them.
- **Never put personal names in public files.** No owner name, owner email, or collaborator names in any file, commit, PR, or story (the parent bot holds the exact do-not-use list).
- **Commit identity for arx-memeplex is always** `arxcortex <283871079+arxcortex@users.noreply.github.com>`.
- **Work by PR only.** You may merge your own PR when the owner says "go", the same way the ArxStories flow works.
- **Change only Memeplex files.** Do not edit other site pages. Propose nav changes instead (see the backlog).
- **Facts must match the cited sources.** Never invent quotes. Ratings are judgment, so keep each rationale to one sober line.

## 2. File map

Local test site: the site's `test-site` folder

| Path | What it is |
|---|---|
| `memeplex.html` | The whole page: CSS, markup, and one ES module. Three.js 0.160 and OrbitControls load from a CDN import map. GSAP 3.12.5 loads from jsDelivr. |
| `memeplex/axes.json` | Axis definitions. Add an axis here, and the lens menu and panel pick it up automatically. |
| `memeplex/ideas.json` | The idea records (31 seeded). |
| `memeplex/HANDOVER.md` | This file. |

The page loads its data with `fetch`, so it needs an HTTP server. Opening it as a `file://` page will not work. From `test-site`, run `python -m http.server 8000`, then open `http://localhost:8000/memeplex.html`.

Build workspace on the box: `/workspace/memeplex-build/` (`site/` mirrors the files, `gen.py` regenerates the seed JSON, `t2.py` runs Playwright checks, `shots/` holds screenshots).

## 3. Data schema

### axes.json — array of
```json
{ "id": "platonism", "label": "Platonism", "group": "tradition|register", "description": "one line",
  "plain": "1-2 sentences a newcomer understands (shown in the lens legend and as hover tooltips)" }
```
- `id` is snake_case and never changes, because ideas reference it.
- `group` is either `tradition` (an intellectual lineage) or `register` (a mode or tone: humor or irony). Critical theory is a tradition.

### ideas.json — array of
```json
{
  "id": "hegelian_dialectic",            // snake_case, unique, permanent
  "name": "Hegelian dialectic",
  "root": false,                         // true only for the idea that starts a tradition axis
  "root_axis": null,                     // the tradition id when root is true (exactly one root per tradition)
  "year": 1807,                          // negative = BC; the idea's canonical founding date
  "year_approx": false,                  // true when the year is an estimate (shown as "c.")
  "origin_src": "https://grokipedia.com/page/The_Phenomenology_of_Spirit",  // page that states year/place
  "origin_note": "Phenomenology of Spirit, 1807, finished in Jena",           // what that page says
  "place": "Jena", "lat": 50.93, "lon": 11.59,   // place/lat/lon null when the cited page does not support one
  "thinkers": ["G. W. F. Hegel"],
  "parents": ["neoplatonism", "romanticism"],   // ids of ideas this one descends from
  "plain": "≤200 chars, no jargon (or jargon explained); shown FIRST in the panel",
  "summary": "≤200 chars, plain, active voice, neutral; shown under plain as detail",
  "ratings":   { "platonism": 2, "marxism": 3, ... },   // ALL 13 axes; integers -5..+5; 0 = neutral; null only if a judgment is impossible
  "rationale": { "platonism": "one line", ... },        // one line for EVERY axis, zeros included
  "stories": ["2026-10-25-some-dispatch-slug"],   // arxstories dispatch slugs
  "sources": ["https://grokipedia.com/page/Georg_Wilhelm_Friedrich_Hegel"]  // Grokipedia (https://grokipedia.com/page/<Title>); SEP / IEP allowed as extras
}
```
`children` are computed at load time from `parents`, so never store them. Every id in `parents` must exist, and lineage must run forward in time. `gen.py` asserts the length and id rules, so mirror those checks in CI (see section 9).

## 4. Rating rubric (−5 … +5)

A score answers one question: **"How much does this idea descend from (+) or stand against (−) this tradition or register?"** A score of 0 means neutral or unrelated. Score every axis, zeros included; the panel collapses zeros visually under "Why the zeros".

General anchors, used for every axis:

| Score | Meaning |
|---|---|
| +5 | Founding or defining instance of the tradition, or the idea *is* the tradition |
| +4 | Core descendant; incomprehensible without it |
| +3 | Major, explicit, acknowledged debt |
| +2 | Clear borrowing of key concepts or vocabulary |
| +1 | Faint or indirect echo |
| 0 | Unrelated or neutral |
| −1 | Mild tension |
| −2 | Rejects a key premise |
| −3 | Explicit critique; defines itself partly against it |
| −4 | Programmatic opposition |
| −5 | Its avowed enemy; built to negate it |

Axis-specific anchors:

| Axis | +5 looks like | −5 looks like |
|---|---|---|
| platonism | Theory of Forms; Neoplatonic One | Nominalism or postmodern denial of essences |
| aristotelianism | Teleology, Thomist synthesis | Mechanistic, final-cause-free nature (Descartes, Darwin) |
| stoicism | Logos, apatheia, cosmopolitan duty | Hedonism, passions as the guide |
| christianity | Augustinian grace, Thomism, Calvinism | Nietzsche's "slave morality" attack, militant atheism |
| gnosticism | Demiurge, matter as prison, saving gnosis | World-affirming incarnational orthodoxy |
| hermeticism | As above, so below; the magus; perennial wisdom | Disenchanted positivism |
| enlightenment_liberalism | Natural rights, consent, toleration, progress | Neoreaction, Traditionalism |
| marxism | Class struggle and historical materialism | Neoliberal market order |
| darwinism | Selection and descent with modification; memetics | Fixed essences, design teleology |
| nietzsche | Will to power, revaluation of values | Christian or utilitarian egalitarian morality |
| humor *(register)* | The idea lives in jokes (meme culture) | Humorless solemnity *as a stated principle* (rare; usually use 0) |
| irony *(register)* | Post-irony, Romantic irony | Militant sincerity *as a stated principle* |
| critical_theory | Frankfurt School (root idea), Foucauldian power analysis | Explicit defense of norms as natural and power-neutral |

Review rules:
- Score all 13 axes. Typically 3 to 5 are non-zero; every zero still gets a one-line reason ("Comes before X existed", "No clear debt to, or quarrel with, X"). Use null only when a judgment is genuinely impossible, and say why in the rationale.
- Descent runs forward in time: an idea cannot score positive on a tradition that began after it.
- A +5 must be rare. At most one per idea, unless the idea fuses two traditions, as Thomism does.
- Write each rationale as one line in active voice and cite something checkable.

## 5. How the page works

- **Layout:** the page runs PCA on the 13-dimensional rating vectors, using power iteration in the browser with no library. PC1 maps to x and PC2 to z, each scaled to ±34. Height (y) blends 75% ordinal year rank with 25% signed log year, which keeps the dense modern centuries readable. The whole cloud is centered on the origin. `yPos()` turns any year into a height, and the era spine reuses it.
- **Pole labels:** the edge labels ("toward Platonism · Christianity") name the two strongest loadings at each end of PC1 and PC2. They tell the viewer what the axes mean, which a bare projection never does.
- **Era spine:** a vertical copper rule at (−44, *, −44) carries tick labels at 400 BC, AD 1, 500, 1250, 1600, 1800, 1900, 1950 and 2000.
- **Lineage lines:** quadratic Bézier arcs run parent to child, lifted slightly at the midpoint. Hovering or selecting an idea lights its whole **ancestry in copper** and its **descent in ivory**. Every other line and star dims to about 5–10%. This is the focus+context, degree-of-interest pattern from TimeNets.
- **Panel:** it shows the name, date and place, summary, thinkers, and parents and children (each clickable). Ratings appear as a **diverging bar chart** sorted by strength, with the zeros collapsed into one "Neutral" line. Below that come the one-line rationales, Arx stories and sources.
- **Compare:** the Compare button prompts for a second idea, picked by star or search. Two thin bars per axis appear on one symmetric axis, sorted by the biggest gap. The panel also shows the rating distance and the shared ancestors.
- **Trace lineage:** this button frames the camera on the idea's whole family tree.
- **Lens menu:** pick an axis to recolor the stars, from blue (−5) through grey to copper (+5), with star size set by the strength of the score.
- **Search** matches name, thinkers and summary.
- **Mobile:** on screens up to 760 px wide, the panel becomes a bottom sheet at 62% of the screen height, and the camera offsets so the selected star stays visible above it. On a phone you tap instead of hovering.
- **Motion:** every tween uses GSAP: an intro timeline, camera glides, panel slides, and bar fills. Motion is skipped under `prefers-reduced-motion`. Rendering runs on `gsap.ticker`.

## 6. How to add an idea

1. Pick an `id` and confirm the canonical year, place and thinkers against the Grokipedia page (https://grokipedia.com/page/<Title>; confirm it returns HTTP 200). Never rely on memory for these.
2. Set `parents` to existing ids only. If a parent is missing, add the parent first.
3. Write the summary in active voice with named actors, 200 characters or fewer.
4. Rate it with the rubric in section 4 and write one rationale line per non-zero score.
5. Add at least one source URL.
6. Run `python3 memeplex/validate.py memeplex/` (ids unique, parents exist and are older, ranges, lengths, all axes scored with rationale, one root per tradition, `plain` present).
7. Open the page locally (or the deploy preview, once the repo exists) and click the new star.
8. Open a PR using the arxcortex identity.

## 7. Linking stories

- `stories[]` holds **arxstories dispatch slugs**, for example `2026-10-25-machado-returns-trump-backs-rodriguez`.
- The page builds each link as `https://arxcortex.github.io/arxstories/dispatches/<slug>/`.
- When MemeBot writes an idea story, publish it in arxstories (same flow, same voice rules), then add the slug to every idea it materially discusses.
- Tag existing dispatches too. Tag only when the piece actually engages the idea, never on a keyword match alone.

## 8. Switching to the GitHub Pages data source

At the top of the module in `memeplex.html`:
```js
const MEMEPLEX_DATA_BASE = './memeplex/';
// const MEMEPLEX_DATA_BASE = 'https://arxcortex.github.io/arx-memeplex/';
```
Once the repo is live and Pages is serving `axes.json` and `ideas.json` from the repo root, swap the comment. The URL must keep its trailing slash. This follows the same pattern as `CHRONO_DATA_BASE` in `chronosphere.html`, so data updates never cost a Netlify deploy. The site change itself still needs the owner's deploy.

## 9. Planned repo: `arxcortex/arx-memeplex`

```
arx-memeplex/
  axes.json
  ideas.json
  README.md               # what this is, schema link, no personal names
  docs/HANDOVER.md        # this file (names scrubbed)
  docs/RUBRIC.md          # section 4, split out
  schema/idea.schema.json # JSON Schema for CI
  scripts/validate.py     # ids unique, parents exist, years ordered, ranges, lengths
  .github/workflows/validate.yml   # runs validate.py on every PR
  .nojekyll               # Pages serves the JSON raw
```
- Serve from GitHub Pages on the `main` branch, at the repo root.
- **PR only.** Every change goes through a branch and a PR, CI must pass, and merging follows the owner's "go".
- Commit as `arxcortex <283871079+arxcortex@users.noreply.github.com>`.
- **Status:** live. Data lives at the repo root and is served by GitHub Pages at https://arxcortex.github.io/arx-memeplex/.

## 10. Voice rules (stories, hooks, summaries)

- Use active voice and name the actor. Write "Hegel argues", never "it is argued".
- Keep it plain: short sentences and no throat-clearing. Avoid "not X, it's Y" constructions and AI tells.
- Titles are 90 characters or fewer. Summaries are 200 characters or fewer.
- **X hooks are under 280 characters** with no `>` markers. **The hook is the story's lead paragraph**, verbatim.
- Stay neutral on ideas. Describe what an idea claims and who holds it, not whether it is right.
- After publishing, stage the card and hook for the owner, following the existing x-staging folder convention. Never post them.

## 11. Research findings (Oct 2026) and what was applied

| Finding | Source | Applied? |
|---|---|---|
| Radar charts mislead: polygon area depends on axis order and grows with the square of values, and they handle negative values badly. Use diverging bars for ± data on a symmetric, centered axis, with distinct colors per direction (blue/orange is colorblind-safe). | Few, *Keep Radar Graphs Below the Radar* (perceptualedge.com/articles/dmreview/radar_graphs.pdf); usefuldatatips.com radar alternatives; Domo divergent bar guide | **Yes**: the panel uses diverging bars in blue (−) and copper (+), sorted by strength, with zeros collapsed. No radar. |
| Genealogies are lattices, not trees. Use degree-of-interest focus+context: keep the selected node's ancestry and descent lit and fade the rest. | Kim et al., *Tracing Genealogical Data with TimeNets* (homes.cs.washington.edu/~jheer/files/genvis.pdf); GeneaQuilts (doi 10.1109/tvcg.2010.159) | **Yes**: hover or select lights the full ancestry in copper and descent in ivory. Multiple parents are supported. |
| Humanities data is incomplete and interpretive. Tools should help users filter, contextualize, **compare**, and see the gaps rather than smooth them over. | Stanford *Mapping the Republic of Letters* / Palladio (hdlab.stanford.edu/palladio/about; NEH feature; AHR doi 10.1093/ahr/122.2.400) | **Yes**: compare mode, plus "Neutral" and "None mapped yet" shown explicitly. Still to do: show "unrated" versus "0". |
| Projections are unreadable without axis meaning. Label each pole by its top loadings. | Standard PCA biplot practice | **Yes**: pole labels on PC1 and PC2. |
| Time needs an explicit scale when it is one axis of the layout. | TimeNets; Republic of Letters timeline views | **Yes**: the era spine. |
| Edge bundling (Holten hierarchical edge bundles) cuts clutter in dense graphs. | d3 bundle docs; Holten 2006; Luo et al. 2012 (doi 10.1109/TVCG.2011.104) | **Not yet.** With 31 nodes and roughly 45 edges it isn't needed. Revisit past about 150 ideas. |
| UMAP preserves local clusters better than PCA, but its axes have no meaning and it needs a library. | umap-learn docs | **Deferred.** PCA keeps meaningful axes and has no dependency. Revisit at about 200 ideas, and precompute positions in the repo rather than in the browser. |
| Parallel coordinates suit many-axis comparison across many items. | General visualization literature | **Backlog**: a possible "table / parallel view" toggle for power users. |

## 12. Backlog

1. **Story tagging:** every `stories[]` is empty. Tag existing arxstories dispatches where the idea is actually engaged, then write idea stories.
2. **Rating review:** the owner should review all 31 seeds against the rubric, especially the register axes and Traditionalism, Neoreaction and Accelerationism.
3. **Source depth:** add SEP or IEP entries next to the Grokipedia links, and double-check dates (canonical year choices such as Existentialism 1943 and Accelerationism 1994 are judgment calls).
4. **Site integration (needs the owner's OK; it touches other files):**
   - `index.html`: add a "VII · THE MEMEPLEX" card next to the Chronosphere card (around line 3506), plus a nav link next to line 3992.
   - `sitemap.xml`: add `https://arxcortex.io/memeplex.html`.
   - Social preview: add og and twitter meta tags to memeplex.html, plus `assets/og/memeplex.png` (1200×630).
5. **Data source switch:** the repo exists; the page switch in section 8 still needs the owner's OK and deploy.
6. **Data growth:** go from 31 to about 150 ideas, covering Confucianism, Buddhism, Islamic philosophy (Avicenna, Averroes), the Kabbalah, Spinoza, utilitarianism, pragmatism, fascism, liberation theology and transhumanism. Non-Western roots need new axes, which you add in axes.json with the owner's approval.
7. **Display ideas:** an unrated-versus-zero distinction, a parallel-coordinates view, deep links (`memeplex.html#hegelian_dialectic`), and edge bundling once the graph is past about 150 ideas.
8. **Validation CI** for the repo (section 9).

## 13. v3 changes (Oct 25, 2026)

- Beginner layer: "What am I looking at?" overlay (opens on first visit, `?` button or `?` key), plain-language legend and pole labels ("leans on X and Y"), `plain` field on every axis and idea, scale explained in the panel, axis tooltips, root-idea badge, "c." for approximate years, zero-score reasons under a collapsible "Why the zeros".
- Full scoring on all 13 axes; `root`/`root_axis`, `year_approx`, `origin_src`, `origin_note` added. Christianity and Social Darwinism added (33 ideas).
- Origin facts re-checked against the cited pages; see `CORRECTIONS-v3.log`.
- Fixed: compare-view heading covered the panel close button.

## Register display rule

Registers (`group: "register"`: **humor** and **irony**) describe the tone an idea is carried in, not a school of thought. They are scored for every idea and stay in the data, but the site never shows them for root ideas (`root: true`):

- Side panel: no register bars, rationales or "Why the zeros" entries on a root idea. Non-root ideas show registers grouped below the traditions under a "Tone / register" label with a one-line explainer.
- Share card: no register rows on a root idea's card; a comparison omits register rows whenever either idea is a root.
- Lens coloring: when a register is the active lens, root stars render neutral grey.

Critical theory is a **tradition**, not a register. Its root idea is the Frankfurt School (`root_axis: "critical_theory"`). A root's `root_axis` does not have to match its own id.
