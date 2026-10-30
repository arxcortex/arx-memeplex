import json,sys
import os
B=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","")
B=os.path.join(B,"")
axes=json.load(open(B+"axes.json")); ideas=json.load(open(B+"ideas.json")); E=[];W=[]
AX=[a["id"] for a in axes]; ids=[d["id"] for d in ideas]; by={d["id"]:d for d in ideas}
for a in axes:
  for k in("id","label","group","description","plain"):
    if not a.get(k): E.append(f"axis {a.get('id')}: missing {k}")
  if a.get("group") not in("tradition","register","stance"): E.append(f"axis {a['id']}: bad group")
if len(set(ids))!=len(ids): E.append("duplicate ids")
roots={}
for d in ideas:
  i=d["id"]
  if not i.replace("_","").isalnum() or i!=i.lower(): E.append(f"{i}: bad id")
  if len(d["name"])>90: E.append(f"{i}: name too long")
  for k in("plain","summary"):
    if not d.get(k) or len(d[k])>200: E.append(f"{i}: {k} missing or >200 ({len(d.get(k) or '')})")
  if not isinstance(d["year"],int): E.append(f"{i}: year not int")
  if not isinstance(d.get("year_approx"),bool): E.append(f"{i}: year_approx not bool")
  if not str(d.get("origin_src","")).startswith("https://"): E.append(f"{i}: no origin_src")
  if d["lat"] is not None and not(-90<=d["lat"]<=90 and -180<=d["lon"]<=180): E.append(f"{i}: bad coords")
  for p in d["parents"]:
    if p not in by: E.append(f"{i}: parent {p} missing")
    elif by[p]["year"]>d["year"]: E.append(f"{i}: parent {p} ({by[p]['year']}) later than child ({d['year']})")
  if set(d["ratings"])!=set(AX): E.append(f"{i}: ratings must cover all axes exactly")
  if set(d["rationale"])!=set(AX): E.append(f"{i}: rationale must cover all axes exactly")
  for a,v in d["ratings"].items():
    if v is not None and (not isinstance(v,int) or not -5<=v<=5): E.append(f"{i}: {a}={v} out of range")
    r=d["rationale"].get(a) or ""
    if not r or len(r)>160: E.append(f"{i}: rationale {a} missing or >160")
  if not d["sources"]: E.append(f"{i}: no sources")
  dm=d.get("domain")
  if not isinstance(dm,list) or not dm or len(dm)>3 or len(set(dm))!=len(dm) or any(x not in("politics","philosophy","religion","culture") for x in dm): E.append(f"{i}: domain must be 1-3 of politics/philosophy/religion/culture, primary first")
  for a in ("hierarchy","abstraction"):
    if a not in AX: E.append(f"stance axis {a} missing (map layout needs it)")
    elif not isinstance(d["ratings"].get(a),int): E.append(f"{i}: stance {a} must be scored (map layout)")
  if "wikipedia.org" in str(d.get("origin_src","")) or any("wikipedia.org" in u for u in d["sources"]): E.append(f"{i}: Wikipedia source; use Grokipedia")
  for u in [d.get("origin_src") or ""]+d["sources"]:
    if u and not u.startswith(("https://grokipedia.com/page/","https://plato.stanford.edu/","https://iep.utm.edu/")): W.append(f"{i}: non-Grokipedia source {u}")
  ti=d.get("thrives_in")
  if not isinstance(ti,dict) or not isinstance(ti.get("historical"),bool) or not isinstance(ti.get("places"),list): E.append(f"{i}: thrives_in needs historical (bool) and places (list)")
  else:
    pl=ti["places"]
    if len(pl)>4: E.append(f"{i}: thrives_in has more than 4 places")
    if not pl and ti.get("uncertain") is not True: E.append(f"{i}: thrives_in empty but not marked uncertain")
    if pl and ti.get("uncertain"): E.append(f"{i}: thrives_in marked uncertain but has places")
    if not pl: W.append(f"{i}: thrives_in uncertain (no sourced place)")
    for x in pl:
      if not isinstance(x.get("place"),str) or not x["place"].strip() or len(x["place"])>60: E.append(f"{i}: thrives_in place missing or >60")
      if "period" in x and (not isinstance(x["period"],str) or not x["period"].strip()): E.append(f"{i}: thrives_in period empty")
      if not str(x.get("src","")).startswith("https://grokipedia.com/page/") and not str(x.get("src","")).startswith(("https://plato.stanford.edu/","https://www.pewresearch.org/","https://www.wikidata.org/")): E.append(f"{i}: thrives_in src must be Grokipedia/SEP/Pew/Wikidata")
      if not x.get("note") or len(x["note"])>160: E.append(f"{i}: thrives_in note missing or >160")
    if len({x.get("place") for x in pl})!=len(pl): E.append(f"{i}: thrives_in duplicate place")
  if not isinstance(d.get("root"),bool): E.append(f"{i}: root not bool")
  if d["root"]:
    ax=d.get("root_axis")
    if ax not in AX or d["ratings"].get(ax)!=5: E.append(f"{i}: root needs root_axis scored +5")
    roots[ax]=roots.get(ax,0)+1
  elif d.get("root_axis"): E.append(f"{i}: root_axis set on non-root")
for a in axes:
  if a["group"]=="tradition" and a.get("root_pending") is True and roots.get(a["id"],0)==0: W.append(f"tradition {a['id']}: root idea pending (no anchor idea on the map yet)"); continue
  if a["group"]=="tradition" and roots.get(a["id"])!=1: E.append(f"tradition {a['id']}: needs exactly one root idea, has {roots.get(a['id'],0)}")
# currents.json: trends in thought, same rating schema as ideas
cur=json.load(open(B+"currents.json")) if os.path.exists(B+"currents.json") else []
cids=[c["id"] for c in cur]
if len(set(cids))!=len(cids) or set(cids)&set(ids): E.append("currents: duplicate ids (or clash with idea ids)")
for c in cur:
  i="current "+c.get("id","?")
  for k in("id","name","place","origin_src","story_url"):
    if not c.get(k): E.append(f"{i}: missing {k}")
  for k in("plain","summary"):
    if not c.get(k) or len(c[k])>200: E.append(f"{i}: {k} missing or >200")
  if not isinstance(c.get("year"),int): E.append(f"{i}: year not int")
  if set(c.get("ratings",{}))!=set(AX) or set(c.get("rationale",{}))!=set(AX): E.append(f"{i}: ratings/rationale must cover all axes exactly")
  for a,v in c.get("ratings",{}).items():
    if v is not None and (not isinstance(v,int) or not -5<=v<=5): E.append(f"{i}: {a}={v} out of range")
    r=c.get("rationale",{}).get(a) or ""
    if not r or len(r)>160: E.append(f"{i}: rationale {a} missing or >160")
  for a in("hierarchy","abstraction"):
    if not isinstance(c.get("ratings",{}).get(a),int): E.append(f"{i}: stance {a} must be scored")
  if not c.get("related_ideas"): E.append(f"{i}: needs related_ideas")
  for r in c.get("related_ideas",[]):
    if r not in by: E.append(f"{i}: related idea {r} missing")
    elif c["id"] not in by[r].get("related_currents",[]): E.append(f"{i}: {r} lacks back-link in related_currents")
  if not c.get("sources"): E.append(f"{i}: no sources")
for d in ideas:
  for r in d.get("related_currents",[]):
    if r not in cids: E.append(f"{d['id']}: related_current {r} missing")
for _f in ("thinkers.json","politics.json","currents.json"):
  try: json.load(open(B+_f))
  except Exception as _e: E.append(f"{_f}: invalid JSON: {_e}")
# schema: top-level idea keys must be allowed by schema/idea.schema.json
_S=json.load(open(B+"schema/idea.schema.json"))["items"]; _P=set(_S["properties"]); _R=set(_S.get("required",[]))
for d in ideas:
  for k in set(d)-_P: E.append(f"{d['id']}: field {k} not allowed by schema")
  for k in _R-set(d): E.append(f"{d['id']}: required field {k} missing")
# national.json: National view Religion/Philosophy lists per country
if os.path.exists(B+"national.json"):
  nat=json.load(open(B+"national.json")); pcs=[c["id"] for c in json.load(open(B+"politics.json"))["countries"]] if os.path.exists(B+"politics.json") else None
  if not isinstance(nat.get("countries"),list): E.append("national: countries must be a list")
  for c in nat.get("countries",[]):
    ci="national "+str(c.get("id"))
    if pcs is not None and c.get("id") not in pcs: E.append(f"{ci}: country not in politics.json")
    for k in("religion","philosophy"):
      if not isinstance(c.get(k),list): E.append(f"{ci}: {k} must be a list"); continue
      seen=set()
      for e in c[k]:
        i=e.get("idea")
        if i in seen: E.append(f"{ci} {k}: duplicate {i}")
        seen.add(i)
        if not e.get("why"): E.append(f"{ci} {k} {i}: missing why")
        if not str(e.get("src","")).startswith("https://"): E.append(f"{ci} {k} {i}: src must be https")
        elif "wikipedia.org" in e["src"]: E.append(f"{ci} {k} {i}: Wikipedia source; use Grokipedia")
        if k=="philosophy" and e.get("call") not in("historical","living"): E.append(f"{ci} philosophy {i}: call must be historical or living")
        if i not in by: W.append(f"{ci} {k}: {i} not on the map yet ({e.get('status','unknown')}); skipped in view")
print("\n".join("WARN "+w for w in W)) if W else None
print("\n".join(E) or f"OK: {len(ideas)} ideas, {len(cur)} currents, {len(AX)} axes, {len(roots)} roots, all axes scored"); sys.exit(bool(E))
