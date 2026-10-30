# Checks the later-era batch 1 data on the current page (served from ../thrives-in): views order check, tour edges, panels for new ideas, overlaps, no errors. Run from this folder.
import asyncio,subprocess,sys,json
from playwright.async_api import async_playwright
R='../../../'
NEW=['neo_thomism','neostoicism','modern_synthesis','western_marxism','new_confucianism','epicureanism','islam']
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8843"],cwd="../thrives-in",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); fail=[]; errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for tag,vp,mob in [('desk',dict(width=1440,height=900),False),('mobile',dict(width=390,height=844),True)]:
      ctx=await b.new_context(viewport=vp,is_mobile=mob,has_touch=mob); pg=await ctx.new_page()
      pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m:errs.append(m.text) if m.type=="error" and 'ReadPixels' not in m.text else None)
      for f in ['ideas.json','thinkers.json','axes.json','currents.json']:
        await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1');sessionStorage.setItem('memeplex-full','1')")
      await pg.goto("http://localhost:8843/memeplex.html?intro=none&full=1"); await pg.wait_for_function("window.__memeplex && __memeplex.ideas && __memeplex.ideas.length",polling=500); await pg.wait_for_timeout(3500)
      n=await pg.evaluate("__memeplex.ideas.length"); print(tag,'ideas',n)
      if tag=='desk':
        chk=await pg.evaluate("window.__views&&__views.check?__views.check():null"); print('views.check',json.dumps(chk))
        bad=await pg.evaluate("__tours.validate()"); neg=await pg.evaluate("__tours.validate([{id:'x',steps:[{id:'platonic_forms'},{id:'marxism'}]}])")
        print('tour bad edges',bad,'neg control',bool(neg))
        if bad or not neg: fail.append('tours')
        if chk and any((v if isinstance(v,(int,float)) else len(v) if isinstance(v,list) else 0) for v in (chk.values() if isinstance(chk,dict) else [])): fail.append(('views',chk))
        lod=await pg.evaluate("window.__lod&&__lod.overlaps?__lod.overlaps():null"); print('label overlaps',lod)
        await pg.screenshot(path="1-default.jpg",quality=70)
      for iid in NEW:
        await pg.evaluate(f"__memeplex.focusIdea('{iid}')"); await pg.wait_for_timeout(1600)
        txt=await pg.inner_text('#panel')
        name=await pg.evaluate(f"__memeplex.ideas.find(d=>d.id=='{iid}').name")
        ok=name in txt
        print(tag,iid,'panel ok' if ok else 'PANEL MISSING', '| thrives shown' if 'thrives' in txt.lower() else '')
        if not ok: fail.append((tag,iid))
        if tag=='desk' or iid in ('neostoicism','new_confucianism'): await pg.screenshot(path=f"{tag}-{iid}.jpg",quality=70)
      await ctx.close()
    await b.close()
  srv.terminate(); print('errors',errs[:10],'FAILS',fail); sys.exit(1 if fail or errs else 0)
asyncio.run(run())
