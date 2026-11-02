# Arx Memeplex data

Data for the Arx Memeplex (arxcortex.io/memeplex.html): a 3D constellation map of ideas and where they came from. Plain JSON, served via GitHub Pages at https://arxcortex.github.io/arx-memeplex/.

## Goal: readable by a beginner

Anyone with no background in philosophy should be able to read every idea, tradition and score here and understand it. Every idea carries a `plain` explanation written for a newcomer, every tradition has a plain description, and every score has a one-line reason in everyday words.

## Files

| File | What it holds |
|---|---|
| `axes.json` | The 23 axes: 19 traditions (Platonism, Christianity, Marxism, critical theory, Confucianism, Daoism, Buddhism, Vedanta, Islam, Judaism...), 2 registers (humor, irony) and 2 stances (hierarchy; abstract vs material). Registers are stored for every idea but not shown for root ideas. The stances show on every idea, roots included. |
| `ideas.json` | The ideas: date, place, thinkers, parent ideas, plain explanation, scores on every axis with reasons, and sources. |
| `thinkers.json` | Optional. Maps a thinker name, exactly as written in `ideas.json`, to its Grokipedia page, or its English Wikipedia page when Grokipedia has no correct one. Only names with a checked, matching page are listed; the map shows the rest as plain text. |
| `schema/idea.schema.json` | JSON Schema for one idea record. |
| `scripts/validate.py` | Checks the data (standard-library Python). Runs on every push and pull request. |
| `docs/RUBRIC.md` | How scores from -5 to +5 are assigned. |
| `docs/METHODOLOGY.md` | Plain-language scoring method: lineage first, then a half-strength stance or affinity fallback. |
| `docs/HANDOVER.md` | Full build notes for maintainers. |

## How an idea is scored

Each score answers: how much does this idea descend from (+) or stand against (-) this tradition? 0 means neutral or unrelated. The hierarchy stance asks a different question: does the idea favor (+) or oppose (-) ranked order? The abstraction stance asks whether reality is ideas or spirit (+) or matter (-). Every idea is scored on all 23 axes. The map places ideas on fixed directions: abstract vs material left-right, hierarchy front-back, time up (see docs/RUBRIC.md). Root ideas (`root: true`) are the starting point of a tradition. Lineage runs forward in time: a parent idea is never later than its child.

Facts (dates, places, thinkers) follow the cited sources. Sources are Grokipedia pages (`https://grokipedia.com/page/<Title>`); SEP or IEP may be added alongside. Wikipedia is not used. Scores are editorial judgments, each with its stated reason. Where an idea has no recorded relation to a tradition, a half-strength stance or affinity reading may be used instead (see docs/METHODOLOGY.md).

## Check locally

```
python scripts/validate.py
```

Changes come in by pull request only. Data is MIT licensed.
