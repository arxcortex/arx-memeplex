# How Memeplex scores are made

This page explains, in plain words, what the numbers on the Memeplex mean and how we choose them. It extends the rating rubric in [RUBRIC.md](RUBRIC.md), which stays the reference for the per-axis anchors.

## What a score is

Every idea gets a score on each of the 23 axes. An axis is one of three kinds:

- **Traditions** (20): Platonism, Christianity, Marxism, Buddhism, Nationalism and the rest. The score says how the idea stands toward that tradition.
- **Stances** (2): hierarchy, and abstract versus material. These ask what the idea itself believes. They are already "opinion" scores, so the two tiers below do not apply to them.
- **Registers** (2): humor and irony. These describe the tone an idea is carried in. The two tiers do not apply to them either.

Scores run from **-5 to +5**, whole numbers only:

| Score | Meaning |
|---|---|
| +5 | The idea is the tradition, or founds it |
| +4 to +3 | Grows straight out of it, with a large, open debt |
| +2 to +1 | Borrows some of its ideas, or faintly echoes it |
| 0 | Neutral, unrelated, or nothing a source can support |
| -1 to -2 | Some tension, or rejects one of its key premises |
| -3 to -4 | Openly attacks it, or is built in opposition to it |
| -5 | Its sworn enemy, made to undo it |

## Two tiers: lineage first, stance as the fallback

### Tier 1: lineage or direct relation (the main method)

First we ask: is there a real, recorded relation between the idea and the tradition? That means one of these:

- the idea **descends from** the tradition (its founders learned from it, cite it, or grew out of it);
- the idea **reacts against** it (its founders or core texts argue against the tradition, or a school inside it, by name);
- the two were **rivals** in the same time and place.

Tier 1 scores use the full -5..+5 scale. Descent only runs forward in time: an idea cannot score positive for descending from a tradition that began after it. Opposition and rivalry can be scored whenever the record shows them.

Example: Mohism attacked the fatalism it tied to Laozi, so it scores -2 on Daoism as a tier 1 score.

### Tier 2: stance and affinity (the fallback)

If there is **no** recorded relation, the score is not automatically 0. We ask two fallback questions:

1. **Stance.** If this idea could judge the tradition, would it favor it or oppose it? We answer from what the idea's core texts and adherents say about the tradition's main claims. Example: Theravada teaches that there is no permanent self, so it would reject Vedanta's teaching that the deep self (Atman) is real and eternal.
2. **Affinity.** How much does the idea resemble the tradition in what it teaches? Example: Pythagoreanism taught rebirth into new bodies and a discipline to escape the cycle, which resembles Buddhism, even with no historical link.

Think of Lenin and Trotsky. They were bitter rivals, but both stand in the Marxist family. Tier 1 captures the family tie. Tier 2 is for the cases with no tie at all, where we still can say how much each side would like or dislike the other.

**Half strength.** Tier 2 scores count half as much as lineage:

1. Rate the stance or affinity on the full -5..+5 scale (the "raw" reading).
2. Halve it, and round **toward zero** to a whole number. That is the stored score.

| Raw reading | Stored score |
|---|---|
| +5 or +4 | +2 |
| +3 or +2 | +1 |
| +1, 0, -1 | 0 |
| -2 or -3 | -1 |
| -4 or -5 | -2 |

So a fallback score is never bigger than ±2, and a faint raw reading of ±1 still stores 0. Keep raw readings to about ±1..±3. Use a raw ±4 or ±5 only when a source states the stance outright (for example, a founding text condemns the tradition by name).

Scores are whole numbers today (the schema and validator require integers). A later option is to store half-points (+0.5, +1.5) instead of rounding. That would need a schema change and the owner's approval; the default stays whole numbers.

Stance readings may reach traditions that began after the idea (a 3rd-century-BCE school can be asked how it would judge Islam's creator God). Affinity may compare ideas with no contact at all. Neither counts as descent.

### When 0 is still right

A 0 is the correct answer when:

- the idea is genuinely neutral on what the tradition cares about (a theory of money says nothing about the Buddhist self);
- the idea's own record is mixed or split, with real voices on both sides;
- the stance can't be supported from a source, only guessed;
- the raw reading is only ±1, which halves to 0.

Most zeros will stay. The fallback is for real stances and resemblances, not for filling every cell.

## Writing the reason

Every score keeps a one-line reason (up to 160 characters) in active voice that names something checkable.

- Tier 1 reasons say what the relation is: "Mayr's 1959 essay attacked Platonic essentialism in biology (Grokipedia, Ernst Mayr)."
- Tier 2 reasons begin with **"Stance:"** or **"Affinity:"**, so readers can see the score is a fallback reading: "Stance: its cosmos has no creator deity (Grokipedia, Theravada), so it would reject Christianity's Creator God."
- A raw reading that halves to 0 can say "Stance too weak to score: ..." so the work isn't lost.
- Zeros keep a short reason, as before.

## Sources

- Grokipedia first (`https://grokipedia.com/page/<Title>`), then the Stanford Encyclopedia of Philosophy and primary texts (for example, the Federalist Papers or a scripture verse).
- Wikipedia is not used; the validator rejects it.
- Never invent quotes, dates or numbers. Only quote words you have read in the source.
- Write in a neutral voice for a reader with no background, and don't use "pseudo-" labels.

## Marking fallback scores (proposal)

To let the page show fallback scores lighter than lineage scores, this change proposes two optional fields on an idea. Both are new, optional and backward compatible; ideas without them read as all tier 1. **They need approval before they are rolled out further.**

```json
"basis":      { "vedanta": "stance", "christianity": "stance" },
"stance_raw": { "vedanta": -3, "christianity": -2 }
```

- `basis` marks which axes are tier 2. A missing axis means lineage (tier 1).
- `stance_raw` keeps the full-scale reading before halving, so the scores can be recomputed if the rule changes (for example, to half-points).
- The validator checks that each stored score equals the raw reading halved and rounded toward zero, that tier 2 scores stay within ±2, and that tier 2 reasons start with "Stance:" or "Affinity:".

A possible display, not built yet: draw tier 2 bars in a lighter tint in the side panel, with a small "fallback" label and a tooltip linking here. No new axes are added by this method.

## Zero counts (snapshot)

Run `python3 scripts/zero_report.py` to recount. At main `cb3b170` (256 ideas, 24 axes):

- 4,893 of 6,144 scores were 0 (79.6%). On the 20 tradition axes, 84.7% were 0.
- Worst tradition axes: Daoism 96%, Hermeticism, Vedanta and Islamic philosophy 96%, Stoicism and Islam 93%, Nietzsche 93%, Romanticism 92%. The best were Christianity and Enlightenment liberalism, at about 47% zeros.
- The two stance axes are mostly filled (13 to 16% zeros); humor and irony are 92 to 97% zeros, which is expected for tone.
- A typical non-root idea has 16 to 18 zeros out of 20 traditions. Ancient ideas are worst (89% zeros), then medieval (87%); ideas after 1900 are 81 to 85%.
- About 3,400 zero reasons say "no real link" or similar; about 800 say the idea "comes before" the tradition.

## Pilot (12 ideas)

Twelve non-root ideas with the most zeros, spread across eras and domains, were rescored with this method. Their tradition zeros went from 231 to 208. Three of the changes turned out to be missed tier 1 relations; the rest are tier 2 fallbacks at half strength.

| Idea | Axis | Tier | Raw stance | Before | Stored now |
|---|---|---|---|---|---|
| Mohism | Daoism | 1 lineage | n/a | 0 | -2 |
| Pythagoreanism | Gnosticism | 2 fallback | +2 | 0 | +1 |
| Pythagoreanism | Buddhism | 2 fallback | +2 | 0 | +1 |
| Pythagoreanism | Vedanta | 2 fallback | +2 | 0 | +1 |
| Theravada | Vedanta | 2 fallback | -3 | 0 | -1 |
| Theravada | Christianity | 2 fallback | -2 | 0 | -1 |
| Theravada | Islam | 2 fallback | -2 | 0 | -1 |
| Theravada | Judaism | 2 fallback | -2 | 0 | -1 |
| Kalam | Gnosticism | 1 lineage | n/a | 0 | -2 |
| Kalam | Marxism | 2 fallback | -3 | 0 | -1 |
| Kalam | Christianity | 2 fallback | -2 | 0 | -1 |
| Kalam | Judaism | 2 fallback | +2 | 0 | +1 |
| Liberal feminism | Marxism | 2 fallback | -3 | 0 | -1 |
| Liberal feminism | Romanticism | 2 fallback | -2 | 0 | -1 |
| Liberal feminism | Critical theory | 2 fallback | -2 | 0 | -1 |
| Federalists | Marxism | 2 fallback | -3 | 0 | -1 |
| Agrarian greenbackism | Marxism | 2 fallback | +1 | 0 | 0 (too weak) |
| Holiness movement | Darwinism | 2 fallback | -3 | 0 | -1 |
| Phenomenology | Platonism | 2 fallback | +2 | 0 | +1 |
| Phenomenology | Darwinism | 2 fallback | +1 | 0 | 0 (too weak) |
| Modern synthesis | Platonism | 1 lineage | n/a | 0 | -3 |
| Modern synthesis | Aristotelianism | 2 fallback | -3 | 0 | -1 |
| Chan culture | Enlightenment liberalism | 2 fallback | +2 | 0 | +1 |
| Chan culture | Critical theory | 2 fallback | -2 | 0 | -1 |
| Modern Stoicism | Nationalism | 2 fallback | -2 | 0 | -1 |
