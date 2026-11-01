#!/usr/bin/env python3
"""Zero-score report for the Memeplex data (standard library only). Usage: python3 scripts/zero_report.py [repo_dir]. See docs/METHODOLOGY.md."""
import json,re,collections as C,sys
B=sys.argv[1] if len(sys.argv)>1 else '.'
I=json.load(open(B+'/ideas.json'));A=json.load(open(B+'/axes.json'))
grp={a['id']:a['group'] for a in A}; trad=[a for a in grp if grp[a]=='tradition']
tot=z=0; ax=C.Counter(); axn=C.Counter()
for d in I:
  for a,v in d['ratings'].items():
    tot+=1; axn[a]+=1
    if v==0: z+=1; ax[a]+=1
print(f"ideas {len(I)} scores {tot} zeros {z} ({100*z/tot:.1f}%) nulls {sum(v is None for d in I for v in d['ratings'].values())}")
tz=sum(1 for d in I for a in trad if d['ratings'][a]==0); print(f"tradition-axis zeros {tz}/{len(I)*len(trad)} ({100*tz/(len(I)*len(trad)):.1f}%)")
nr=[d for d in I if not d['root']]; tzn=sum(1 for d in nr for a in trad if d['ratings'][a]==0); print(f"non-root tradition zeros {tzn}/{len(nr)*len(trad)} ({100*tzn/(len(nr)*len(trad)):.1f}%)")
print("per axis:"); [print(f"  {a:26s}{grp[a]:10s}{ax[a]:4d} {100*ax[a]/axn[a]:5.1f}%") for a,_ in sorted(ax.items(),key=lambda x:-x[1])]
pz=sorted(((sum(1 for a in trad if d['ratings'][a]==0),d['id'],d['year'],d['domain'][0],d['root']) for d in I),reverse=True)
h=C.Counter(p[0] for p in pz); print(f"ideas by # tradition zeros (of {len(trad)}):",sorted(h.items()))
print("worst 30:",[(p[1],p[0],p[2],p[3]) for p in pz if not p[4]][:30])
def era(y): return 'ancient <500' if y<500 else 'medieval 500-1499' if y<1500 else 'early modern 1500-1799' if y<1800 else '19th c' if y<1900 else '1900-1949' if y<1950 else '1950+'
for name,key in (('era',lambda d:era(d['year'])),('domain',lambda d:d['domain'][0])):
  g=C.defaultdict(list)
  for d in nr: g[key(d)].append(sum(1 for a in trad if d['ratings'][a]==0))
  print('by',name); [print(f"  {k:24s} n={len(v):3d} avg trad zeros {sum(v)/len(v):5.2f}/{len(trad)} ({100*sum(v)/(len(trad)*len(v)):.0f}%)") for k,v in sorted(g.items())]
R=C.Counter()
for d in I:
  for a,v in d['ratings'].items():
    if v!=0: continue
    r=d['rationale'][a].lower()
    k='comes before' if re.search(r'comes before|predates|before .* existed|cannot descend',r) else 'no real link' if re.search(r'no real link|no (clear )?(link|relation|connection|debt|tie)|unrelated|n/a|not related|no bearing',r) else 'neutral/silent/mixed' if re.search(r'neutral|silent|mixed|split|both|neither',r) else 'other'
    R[k]+=1
print("zero rationale types:",R.most_common())
