# Memeplex rating rubric

The plain-language method, including the half-strength stance and affinity fallback for ideas with no recorded relation to a tradition, is in [METHODOLOGY.md](METHODOLOGY.md).

## Rating rubric (−5 … +5)

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
| hierarchy *(stance)* | Strongly favors ranked order: Neoplatonic chain of being, Neoreaction, Counter-Reformation Catholicism | Strongly opposes ranked order: Marxism, anarchism |
| abstraction *(stance)* | Reality is fundamentally ideas, mind or spirit: Platonic Forms, Neoplatonism, Hegel | Reality is fundamentally matter: Epicurean atomism, Marxism |

Review rules:
- Score all 14 axes. Typically 3 to 5 are non-zero; every zero still gets a one-line reason ("Comes before X existed", "No clear debt to, or quarrel with, X"). Use null only when a judgment is genuinely impossible, and say why in the rationale.
- Descent runs forward in time: an idea cannot score positive on a tradition that began after it.
- A +5 must be rare. At most one per idea, unless the idea fuses two traditions, as Thomism does.
- Write each rationale as one line in active voice and cite something checkable.
- Sources and `origin_src` must be Grokipedia pages (`https://grokipedia.com/page/<Title>`). SEP or IEP may be added as extras. Do not cite Wikipedia.


## Register display rule

Registers (`group: "register"`: **humor** and **irony**) describe the tone an idea is carried in, not a school of thought. They are scored for every idea and stay in the data, but the site never shows them for root ideas (`root: true`):

- Side panel: no register bars, rationales or "Why the zeros" entries on a root idea. Non-root ideas show registers grouped below the traditions under a "Tone / register" label with a one-line explainer.
- Share card: no register rows on a root idea's card; a comparison omits register rows whenever either idea is a root.
- Lens coloring: when a register is the active lens, root stars render neutral grey.

Critical theory is a **tradition**, not a register. Its root idea is the Frankfurt School (`root_axis: "critical_theory"`). A root's `root_axis` does not have to match its own id.

## Hierarchy stance

`hierarchy` (`group: "stance"`) is a position an idea takes, not a family it descends from. It asks: does this idea hold that some people, beings or powers rightly stand above others, socially, politically or cosmically? +5 strongly favors hierarchy, 0 is neutral or internally split (accelerationism, for example), and -5 strongly opposes it. Unlike registers, the stance is shown on every idea, root ideas included, under its own "Stance" group. The forward-in-time rule for traditions does not apply, since a stance is not descent.

## Non-Western root traditions

Five traditions added 2026-10-25, each with a root idea (`root: true`): Confucianism (Confucian ethics, c. 500 BCE), Daoism (the Tao Te Ching, c. 300 BCE, dated by the Guodian strips), Buddhism (the Buddha's Middle Way, c. 5th century BCE), Vedanta (Brahman and Atman in the Upanishads, c. 700 BCE), Islamic philosophy / falsafa (al-Kindi in Baghdad, c. 814 CE). Score them like any tradition: +5 grows straight from it, 0 no real link, −5 built against it; ideas earlier than a root score 0 ("comes before"). Real cross-links are scored, e.g. Thomism +2 on Islamic philosophy (Avicenna's essence-existence distinction), Perennialist Traditionalism +3 on Vedanta.

## Abstraction stance

`abstraction` (`group: "stance"`, label "Abstract vs material") asks what reality is made of at bottom. +5 means it is ideas, mind, spirit or abstract forms (idealism); -5 means it is matter and material conditions (materialism); 0 is neutral, mixed, or simply silent on the question (most political and cultural ideas). Mind-matter dualism (Descartes) is 0. Like hierarchy, it is shown on every idea, roots included, and the forward-in-time rule does not apply. Sources: https://grokipedia.com/page/Idealism, https://grokipedia.com/page/Materialism.

## Map layout (fixed directions)

The map no longer derives its floor from the data (the old PCA layout). Directions are fixed and named:
- left-right (x) = `abstraction`: material on the left, abstract/ideal on the right;
- front-back (z) = `hierarchy`: favors hierarchy at the front, opposes at the back;
- height (y) = year rank (time runs up).
Ideas with identical stance scores get a small deterministic jitter (hashed from the id) plus collision spreading, so they never stack. Because the layout reads these two axes directly, the validator requires every idea to have integer scores for both. Tradition scores do not move ideas on the floor; they drive color-by, compare and the score gap.

## Later-era update nodes

Long-lived traditions get later-era nodes that show how they moved over time, such as Counter-Reformation Catholicism and Vatican II Catholicism. An update node:
- is a separate idea with its own year, scores and reasons;
- lists the earlier form of the tradition in `parents`, so the line on the map shows the drift;
- uses a documented turning point (a council, a founding text, a named movement) with a Grokipedia source.

Score it fresh on every axis; do not copy the parent's scores. The difference between the two is the point.
