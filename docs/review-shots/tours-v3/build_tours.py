# Replaces TOUR_DATA in memeplex.html with tours-v3 and adds tour kind badges. Run: python3 build_tours.py tours-v3.json
import json,re,sys
T=json.load(open(sys.argv[1]))['tours']
ideas={i['id']:i for i in json.load(open('../../../ideas.json'))['ideas']} if isinstance(json.load(open('../../../ideas.json')),dict) else {i['id']:i for i in json.load(open('../../../ideas.json'))}
bad=[]
for t in T:
  s=[x['id'] for x in t['stops']]
  for a,b in zip(s,s[1:]):
    if not(b in ideas and a in ideas and (a in ideas[b]['parents'] or b in ideas[a]['parents'])): bad.append((t['id'],a,b))
  assert t['kind'] in ('genealogy','transmission','narrative')
if bad: sys.exit('bad edges %s'%bad)
data=[{'id':t['id'],'name':t['title'],'kind':t['kind'],'summary':t['summary'],
       'steps':[{'id':x['id'],'cap':x['caption'],'src':x.get('source','')} for x in t['stops']]} for t in T]
h=open('memeplex.html').read()
a=h.index('  const TOUR_DATA = ['); b=h.index('\n',h.index('} ];',a))
h=h[:a]+'  const TOUR_DATA = '+json.dumps(data,ensure_ascii=False)+';'+h[b:]
h=h.replace("""     Placeholder tours below use real edges; their captions fall back to each idea's sourced origin note until researched captions land. */""",
"""     kind = what sort of tour it is (see TOUR_KINDS). */""")
h=h.replace("  const linked = (a, b) =>","""  const TOUR_KINDS = { genealogy: "One idea's documented descent", transmission: 'An idea traveling across places or cultures', narrative: 'A chain of linked events with stakes' };
  const kindBadge = k => TOUR_KINDS[k] ? `<span class="tk tk-${k}" title="${TOUR_KINDS[k]}">${k}</span>` : '';
  const linked = (a, b) =>""",1)
h=h.replace("""'<div class="ph">Guided tours</div>' + TOURS.map(t => `<button type="button" role="menuitem" data-t="${t.id}">${esc(t.name)}<small>""",
"""'<div class="ph">Guided tours</div><div class="tkl">' + Object.entries(TOUR_KINDS).filter(([k]) => TOURS.some(t => t.kind === k)).map(([k, v]) => kindBadge(k) + ' ' + esc(v)).join('<br>') + '</div>' + TOURS.map(t => `<button type="button" role="menuitem" data-t="${t.id}">${kindBadge(t.kind)} ${esc(t.name)}<small>""")
h=h.replace("""bar.innerHTML = `<div class="tn">${esc(T.name)} ·""","""bar.innerHTML = `${i ? '' : `<div class="tkh">${kindBadge(T.kind)} <span>${esc(TOUR_KINDS[T.kind] || '')}</span></div>`}<div class="tn">${kindBadge(T.kind)} ${esc(T.name)} ·""")
h=h.replace("list: TOURS.map(t => ({ id: t.id, name: t.name,","list: TOURS.map(t => ({ id: t.id, name: t.name, kind: t.kind,")
h=h.replace("#tourmenu{position:fixed;","""#tourmenu .tk,#tourbar .tk{display:inline-block;font-family:var(--mono);font-size:9px;letter-spacing:.14em;text-transform:uppercase;padding:2px 6px;border-radius:5px;border:1px solid var(--amber);color:var(--amber-bright);vertical-align:middle}
#tourmenu .tk-transmission,#tourbar .tk-transmission{border-color:#6fa8c8;color:#9fd0ea}#tourmenu .tk-narrative,#tourbar .tk-narrative{border-color:#b88ad0;color:#d8b4ea}
#tourmenu .tkl{font-family:var(--serif);font-size:13px;line-height:1.7;color:var(--ink-dim);margin:0 4px 8px}#tourbar .tkh{font-family:var(--serif);font-size:13px;color:var(--ink-dim);margin-bottom:6px}
#tourmenu{max-height:80vh;overflow:auto}
#tourmenu{position:fixed;""",1)
for k in ['TOUR_KINDS','kindBadge(t.kind)','kind: t.kind','class="tkh"','#tourmenu .tk,']: assert k in h,k
open('memeplex.html','w').write(h); print('ok',len(data))
