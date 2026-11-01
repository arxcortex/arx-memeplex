"""Reference scorer for the Memeplex quizzes. memeplex.html runs the same steps in JavaScript (the QUIZ SCORE block);
docs/review-shots/snip-share/t_quiz.py checks the two give the same results.

Usage: python3 quiz/score.py [answers.json] [repo_dir] [bank]
  answers.json = {"p01": 2, "f11": -1, ...}, each answer -2..+2 (strongly disagree .. strongly agree)
Steps (also in quiz-bank.json "scoring"):
  1. Center: subtract the respondent's mean answer from each answer.
  2. User vector: u[a] = clamp(5 * sum(centered * w[a]) / (sum(2*|w[a]|) + 2K), -5, 5), K = 4 phantom neutral answers;
     an axis enters only once >= 2 answered questions touch it.
  3. Match: cosine(u, idea.ratings) over the axes present in u.
  4. Gates: every |u[a]| <= 0.25 -> 'not enough signal'; best cosine < 0.30 -> 'weak match'.
  5. Output: top 5 ideas; per country the best modern_politics idea carrying that country's party_alignment field;
     the abstraction / hierarchy position with n and confidence W/(W+8).
Originally written by ResearchBot (v2); file paths made relative for the repo."""
import json, math, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
K = 4        # shrinkage: K phantom neutral answers per axis (adds 2K=8 to each denominator)
MIN_N = 2    # an axis needs >=2 answered questions to enter the user vector
GATE = 0.25  # if every |u[a]| <= GATE: "not enough signal"
WEAK = 0.30  # top cosine below this: show as weak match
CC = ["us", "gb", "fr", "de", "ru", "cn", "jp"]
AX = IDEAS = B = QS = None
def load(repo=os.path.join(HERE, ".."), bank=os.path.join(HERE, "quiz-bank.json")):
    global AX, IDEAS, B, QS
    AX = [a["id"] for a in json.load(open(os.path.join(repo, "axes.json")))]
    IDEAS = json.load(open(os.path.join(repo, "ideas.json")))
    B = json.load(open(bank)); QS = {q["id"]: q for q in B["questions"]}
def center(ans):
    v = [x for x in ans.values() if x is not None]
    m = sum(v) / len(v) if v else 0
    return {k: (None if x is None else x - m) for k, x in ans.items()}
def user_vector(ans):
    ans = center(ans); num = {a: 0.0 for a in AX}; den = {a: 0.0 for a in AX}; n = {a: 0 for a in AX}; W = {a: 0.0 for a in AX}
    for qid, v in ans.items():
        if v is None: continue
        for a, w in QS[qid]["weights"].items():
            num[a] += v * w; den[a] += 2 * abs(w); n[a] += 1; W[a] += abs(w)
    u = {a: max(-5, min(5, 5 * num[a] / (den[a] + 2 * K))) for a in AX if n[a] >= MIN_N}
    return u, n, W
def conf(n, W): return round(W / (W + 8), 2) if n >= MIN_N else 0.0
def cos(u, r):
    ks = list(u); d = sum(u[k] * r.get(k, 0) for k in ks)
    nu = math.sqrt(sum(u[k] ** 2 for k in ks)); nr = math.sqrt(sum(r.get(k, 0) ** 2 for k in ks))
    return d / (nu * nr) if nu and nr else 0.0
def score(ans, ideas=None, top=5):
    ideas = ideas or IDEAS
    u, n, W = user_vector(ans)
    plane = {"abstraction": {"x": round(u.get("abstraction", 0), 2), "n": n["abstraction"], "confidence": conf(n["abstraction"], W["abstraction"])},
             "hierarchy": {"y": round(u.get("hierarchy", 0), 2), "n": n["hierarchy"], "confidence": conf(n["hierarchy"], W["hierarchy"])}}
    if not any(abs(x) > GATE for x in u.values()):
        return {"status": "not enough signal", "plane": plane, "top": [], "per_country": {}}
    ranked = sorted(ideas, key=lambda i: -cos(u, i["ratings"]))
    t = [(i["id"], round(cos(u, i["ratings"]), 3)) for i in ranked[:top]]
    per = {}
    for c in CC:
        f = "party_alignment" if c == "us" else "party_alignment_" + c
        pool = [i for i in ideas if i.get("modern_politics") and f in i]
        if pool:
            b = max(pool, key=lambda i: cos(u, i["ratings"])); per[c] = (b["id"], round(cos(u, b["ratings"]), 3))
    return {"status": "weak match" if t[0][1] < WEAK else "ok", "plane": plane, "top": t, "per_country": per}
def run_tests(ideas=None):
    out = {}
    for quiz in [q for q in ("politics", "philosophy", "combined") if q in B["quizzes"]]:
        ids = B["quizzes"][quiz]
        for lab, v in [("all-agree", 2), ("all-disagree", -2), ("all-neutral", 0)]:
            r = score({i: v for i in ids}, ideas); out[f"TEST {quiz} {lab}"] = r["status"]
            assert r["status"] in ("not enough signal", "weak match"), (quiz, lab, r["status"])
    return out
def profiles():
    """Made-up example answer sets: answer +2/-2 by the sign of each question's weight on the named axes."""
    sg = lambda x: (x > 0) - (x < 0)
    def by(*axes):
        return {k: (2 * sg(sum(q["weights"].get(a, 0) for a in axes)) if any(a in q["weights"] for a in axes) else 0) for k, q in QS.items()}
    return {
        "EXAMPLE C (made-up): liberal secularist": by("enlightenment_liberalism"),
        "EXAMPLE D (made-up): religious traditionalist": by("christianity", "hierarchy"),
        "EXAMPLE E (made-up): class-first socialist": by("marxism"),
        "EXAMPLE F (made-up): Daoist-Buddhist quietist": by("daoism", "buddhism"),
        "EXAMPLE G (made-up): abstract realist, favors hierarchy": by("abstraction", "hierarchy"),
        "EXAMPLE H (made-up): materialist egalitarian": {k: -v for k, v in by("abstraction", "hierarchy").items()},
    }
if __name__ == "__main__":
    a = sys.argv[1:]
    load(*(a[1:3]))
    if a and a[0] != "-":
        print(json.dumps(score(json.load(open(a[0]))), indent=1, ensure_ascii=False))
    else:
        res = {"tests": run_tests()}
        for n, ans in profiles().items(): res[n] = score(ans)
        print(json.dumps(res, indent=1, ensure_ascii=False))
