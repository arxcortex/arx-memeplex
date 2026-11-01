# Memeplex quizzes

Three quizzes on the Memeplex page (Menu > Explore & share > Quizzes): **Politics**, **Philosophy** and **Combined**.

- `quiz-bank.json`: the questions. The page reads it from GitHub Pages (`https://arxcortex.github.io/arx-memeplex/quiz/quiz-bank.json`), the same way it reads `ideas.json`, with `./memeplex/quiz/quiz-bank.json` and `./quiz/quiz-bank.json` beside the page as fallbacks. To update the questions, replace this file; the page reads the counts from it, so no code change is needed.
- `score.py`: the reference scorer. The page runs the same steps in JavaScript (the `QUIZ SCORE` block in `docs/review-shots/snip-share/memeplex.html`), and `t_quiz.py` in that folder checks both give identical results.

## How a quiz runs

- Politics and Philosophy offer **Full** (every question in the bank) or **Short** (50 drawn at random). When a bank has 50 or fewer, only one option shows.
- **Combined** draws 50: 25 from Politics and 25 from Philosophy. The bank's own `combined` list is used only if a bank lacks one of the two quizzes.
- A random draw first covers both directions (+ and −) on every axis the pool has, up to 2 questions each (3 for abstraction and hierarchy), taking at each step the question that covers the most open needs. It then fills the rest, each time picking the candidate that keeps the summed weight on every axis closest to 0.
- Each statement has five buttons, from Strongly agree (+2) to Strongly disagree (−2). Scenario questions (`"type": "scenario"`) are labelled "Scenario". If a question has a separate `setting` field, that line shows above the statement.

## Scoring (same as `scoring` in the bank)

1. Subtract the respondent's mean answer from each answer, so agreeing with everything gives no signal.
2. For each axis, u = clamp(5 × Σ(centered answer × weight) / (Σ 2|weight| + 8), −5, 5). An axis counts only once at least 2 answered questions touch it.
3. Rank ideas by cosine similarity between u and the idea's `ratings` in `ideas.json`, using only the axes in u. Ratings are used exactly as stored. Fallback (stance or affinity) scores are already stored at half strength under [METHODOLOGY.md](../docs/METHODOLOGY.md), so they count less automatically.
4. If every |u| ≤ 0.25, the result is "not enough signal". If the best match is below 0.30, it is a "weak match".
5. Results show the top 5 ideas, the abstraction and hierarchy position in the map's own −5..+5 units (with how many answers it rests on), the strongest leanings on the other axes, and, for each country, the closest `modern_politics` idea that carries that country's party alignment.

## Share links and cards

- Results links look like `memeplex.html#quiz=politics&qa=p4310…-f2…`. Each prefix group lists answers by question number (0 = strongly disagree … 4 = strongly agree, `.` = not asked). Question ids must therefore stay `letters + number`, which the validator checks. Opening the link recomputes the results and lights the matched ideas on the map.
- Share cards are 9:16 PNGs drawn by `assets/sharecard.js` (`ArxShareCard.quiz`), the same code as the idea and Snip cards.

## Checks

`scripts/validate.py` checks the bank: unique ids, every weight on an axis in `axes.json` and a non-zero number from −5 to +5, every listed id exists, each question appears in its own quiz list, and the scale has five steps. A `lean` idea that is not on the map gives a warning.
