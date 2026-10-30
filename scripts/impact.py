#!/usr/bin/env python3
"""Impact score for each idea, from the lineage graph in ideas.json only (no hand-set numbers).
Writes impact.json for review. memeplex.html computes the same scores in the browser (impactScores()).

Age-corrected: an old idea has had more later ideas that *could* descend from it, so every measure is
divided by its opportunity, the number of ideas dated after it (+ SMOOTH so the newest ideas don't spike).
  reach    = descendants, each counted 0.7^(generations-1), / (later + SMOOTH)
  direct   = direct children / (later + SMOOTH)
  central  = PageRank (credit flows child -> parent, damping 0.85) * N / (later + SMOOTH)
Each measure becomes a percentile rank (0..1, ties averaged); score = 0.45 reach + 0.30 central + 0.25 direct,
rescaled so the top idea is 100. Ideas with no descendants score 0.
"""
import json, os, sys
SMOOTH, DECAY, DAMP, W = 10, 0.7, 0.85, (0.45, 0.30, 0.25)

def scores(ideas):
    ids = [d['id'] for d in ideas]; by = {d['id']: d for d in ideas}; N = len(ids)
    par = {i: [p for p in (by[i].get('parents') or []) if p in by] for i in ids}
    kids = {i: [] for i in ids}
    for i in ids:
        for p in par[i]: kids[p].append(i)
    def reach(i):
        seen, out, fr, g = {i}, 0.0, [i], 1
        while fr:
            nx = []
            for k in fr:
                for c in kids[k]:
                    if c not in seen: seen.add(c); nx.append(c); out += DECAY ** (g - 1)
            fr, g = nx, g + 1
        return out
    pr = {i: 1 / N for i in ids}
    for _ in range(100):
        nx = {i: (1 - DAMP) / N for i in ids}
        for i in ids:
            if par[i]:
                for p in par[i]: nx[p] += DAMP * pr[i] / len(par[i])
            else:
                for j in ids: nx[j] += DAMP * pr[i] / N
        pr = nx
    later = {i: sum(1 for j in ids if by[j]['year'] > by[i]['year']) for i in ids}
    m = {i: (reach(i) / (later[i] + SMOOTH), pr[i] * N / (later[i] + SMOOTH), len(kids[i]) / (later[i] + SMOOTH)) for i in ids}
    def pct(k):
        vals = sorted(m[i][k] for i in ids); out = {}
        for i in ids:
            v = m[i][k]; lo = sum(1 for x in vals if x < v); eq = sum(1 for x in vals if x == v)
            out[i] = (lo + (eq - 1) / 2) / (N - 1)
        return out
    P = [pct(k) for k in range(3)]
    raw = {i: 0.0 if not kids[i] else sum(W[k] * P[k][i] for k in range(3)) for i in ids}
    mx = max(raw.values()) or 1
    return {i: round(100 * raw[i] / mx, 1) for i in ids}

if __name__ == '__main__':
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    ideas = json.load(open(os.path.join(root, 'ideas.json')))
    s = scores(ideas)
    json.dump(dict(sorted(s.items(), key=lambda kv: -kv[1])), open(os.path.join(root, 'impact.json'), 'w'), indent=1)
    if '-v' in sys.argv:
        by = {d['id']: d for d in ideas}; top = sorted(s, key=lambda i: -s[i])
        print('TOP 15'); [print(f"{s[i]:5} {by[i]['name']} ({by[i]['year']})") for i in top[:15]]
        for nm, a, b in [('Ancient', -9999, 500), ('Medieval', 500, 1500), ('Early modern', 1500, 1800), ('Modern', 1800, 1945), ('Contemporary', 1945, 9999)]:
            print(nm); [print(f"  {s[i]:5} {by[i]['name']} ({by[i]['year']})") for i in [i for i in top if a <= by[i]['year'] < b][:5]]
