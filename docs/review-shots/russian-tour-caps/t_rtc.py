# Checks the Russian state ideas tour, the new lineage lines, the capped scores and the US philosophy list (desktop + phone).
# Serves ../snip-share and routes the repo data files. Run from this folder: python3 t_rtc.py
import asyncio,subprocess,sys,json
from playwright.async_api import async_playwright
R='../../../'
TOUR='russian-state-ideas'
EDGES=[('tsarist_autocracy','putinism'),('official_nationality','putinism'),('liberal_international_order','wolfowitz_doctrine'),('political_realism','wolfowitz_doctrine'),('official_nationality','slavophilia')]
CAPS={('xi_jinping_thought','enlightenment_liberalism'):-2,('reform_uk_populism','marxism'):-1,('reform_uk_populism','critical_theory'):-1,('rassemblement_national','critical_theory'):-1,
      ('alternative_for_germany','marxism'):-1,('alternative_for_germany','critical_theory'):-1,('putinism','critical_theory'):-1}
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8961"],cwd="../snip-share",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); fail=[]; errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for tag,vp,mob in [('desk',dict(width=1440,height=900),False),('phone',dict(width=390,height=844),True)]:
      ctx=await b.new_context(viewport=vp,is_mobile=mob,has_touch=mob); pg=await ctx.new_page()
      pg.on("pageerror",lambda e:errs.append(f"{tag}: {e}")); pg.on("console",lambda m:errs.append(f"{tag}: {m.text}") if m.type=="error" and 'ReadPixels' not in m.text else None)
      for f in ['ideas.json','thinkers.json','axes.json','currents.json','politics.json','national.json','impact.json']:
        await pg.route("**/"+f,(lambda f:(lambda r:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1');sessionStorage.setItem('memeplex-full','1')")
      await pg.goto("http://localhost:8961/memeplex.html?intro=none&full=1"); await pg.wait_for_function("window.__memeplex && __memeplex.ideas && __memeplex.ideas.length && window.__tours",polling=500); await pg.wait_for_timeout(3500)
      n=await pg.evaluate("__memeplex.ideas.length"); print(tag,'ideas',n)
      bad=await pg.evaluate("__tours.validate()"); neg=await pg.evaluate("__tours.validate([{id:'x',steps:[{id:'platonic_forms'},{id:'marxism'}]}])")
      print(tag,'tour bad edges',bad,'| negative control fires',bool(neg))
      if bad or not neg: fail.append((tag,'tour edges'))
      t=await pg.evaluate(f"__tours.list.find(t=>t.id=='{TOUR}')")
      if not t or len(t['steps'])!=8: fail.append((tag,'tour missing',t)); continue
      for a,c in EDGES:
        ok=await pg.evaluate(f"__tours.linked('{a}','{c}')")
        if not ok: fail.append((tag,'edge not linked',a,c))
      print(tag,'new edges linked',all([await pg.evaluate(f"__tours.linked('{a}','{c}')") for a,c in EDGES]))
      for (i,a),v in CAPS.items():
        got=await pg.evaluate(f"__memeplex.ideas.find(d=>d.id=='{i}').ratings['{a}']")
        if got!=v: fail.append((tag,'cap',i,a,got))
      # walk the tour with the Next button
      await pg.evaluate(f"__tours.start('{TOUR}')"); await pg.wait_for_timeout(900)
      names=await pg.evaluate("__tours.list.find(t=>t.id=='%s').steps.map(k=>__memeplex.ideas.find(d=>d.id==k).name)"%TOUR)
      for k,nm in enumerate(names):
        await pg.wait_for_timeout(2300 if not mob else 700)
        txt=await pg.inner_text('#tourbar'); vis=await pg.is_visible('#tourbar')
        okstep=vis and nm in txt and f"{k+1} / 8" in txt
        print(tag,'stop',k+1,nm,'ok' if okstep else 'FAIL')
        if not okstep: fail.append((tag,'stop',k+1,nm))
        if k in (0,3,7): await pg.screenshot(path=f"{tag}-tour-{k+1}.jpg",quality=70)
        await pg.evaluate("document.querySelector('#tourbar [data-a=next]').click()")
      await pg.wait_for_timeout(500)
      if await pg.is_visible('#tourbar'): fail.append((tag,'tour did not finish'))
      # menu lists the tour
      await pg.evaluate("__tours.menu()"); await pg.wait_for_timeout(400)
      inm=await pg.evaluate(f"!!document.querySelector('#tourmenu button[data-t=\"{TOUR}\"]')"); print(tag,'in tour menu',inm)
      if not inm: fail.append((tag,'tour not in menu'))
      await pg.evaluate("__tours.menu()")
      # panels for touched ideas
      for iid in ['putinism','wolfowitz_doctrine','slavophilia','informal_empire']:
        await pg.evaluate(f"__memeplex.focusIdea('{iid}')"); await pg.wait_for_timeout(1400)
        txt=await pg.inner_text('#panel'); nm=await pg.evaluate(f"__memeplex.ideas.find(d=>d.id=='{iid}').name")
        ok=nm in txt; extra=''
        if iid=='informal_empire': extra='open door shown' if 'Open Door' in txt else 'OPEN DOOR NOT SHOWN'; ok=ok and 'Open Door' in txt
        print(tag,iid,'panel ok' if ok else 'PANEL FAIL',extra)
        if not ok: fail.append((tag,'panel',iid))
        if tag=='desk' and iid=='putinism': await pg.screenshot(path=f"{tag}-putinism.jpg",quality=70)
      await ctx.close()
    # National view: US philosophy list includes Transcendentalism
    for tag,vp,mob in [('desk',dict(width=1440,height=900),False),('phone',dict(width=390,height=844),True)]:
      ctx=await b.new_context(viewport=vp,is_mobile=mob,has_touch=mob); pg=await ctx.new_page(); pg.on("pageerror",lambda e:errs.append(f"{tag}: {e}"))
      for f in ['ideas.json','thinkers.json','axes.json','currents.json','politics.json','national.json','impact.json']:
        await pg.route("**/"+f,(lambda f:(lambda r:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      await pg.goto("http://localhost:8961/memeplex.html?intro=none#v=national&ns=philosophy"); await pg.wait_for_function("window.__pol && window.__views && !__views.busy",timeout=30000,polling=500); await pg.wait_for_timeout(2500)
      await pg.evaluate("__pol.setCountry('us')"); await pg.wait_for_timeout(1200)
      r=await pg.evaluate("({sub:__pol.sub,country:__pol.country,fac:[...(__pol.fac||[])]})")
      print(tag,'national',r['country'],r['sub'],r['fac'])
      if r['sub']!='philosophy' or 'transcendentalism' not in r['fac']: fail.append((tag,'national us philosophy',r))
      await pg.screenshot(path=f"{tag}-national-us-philosophy.jpg",quality=70)
      await ctx.close()
    await b.close()
  srv.terminate(); print('errors',errs[:10],'FAILS',fail); sys.exit(1 if fail or errs else 0)
asyncio.run(run())
