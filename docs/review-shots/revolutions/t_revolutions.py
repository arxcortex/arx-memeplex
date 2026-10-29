# Loads the revolution-ideas ideas.json, runs the tour validator and alias search, and shots the new ideas. Run from this folder.
import asyncio,subprocess,sys
from playwright.async_api import async_playwright
R='../../../'
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8788"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); errs=[]; miss=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    pg=await (await b.new_context(viewport=dict(width=1440,height=900))).new_page(); pg.on("pageerror",lambda e:errs.append(str(e)))
    for f in ['ideas.json','thinkers.json','axes.json','currents.json']:
      await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
    await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
    await pg.goto("http://localhost:8788/memeplex.html?intro=none"); await pg.wait_for_function("window.__memeplex && __memeplex.ideas.length && window.__tours",polling=500); await pg.wait_for_timeout(3000)
    n=await pg.evaluate("__memeplex.ideas.length"); bad=await pg.evaluate("__tours.validate()"); print('ideas',n,'tour validate',bad)
    for q,want in [('natural rights','american_republicanism'),('Jacobins','jacobinism'),('Declaration of the Rights of Man','rights_of_man')]:
      r=await pg.evaluate("q=>__memele.search(q,[]).slice(0,3).map(x=>x.id||x)",q); print(q,r)
      if not r or r[0]!=want: miss.append(q)
    for i in ['classical_republicanism','american_republicanism','rights_of_man','jacobinism']:
      await pg.evaluate("i=>__memeplex.focusIdea(i)",i); await pg.wait_for_timeout(1500); await pg.screenshot(path=f'rev-{i}.png')
    await pg.evaluate("__memeplex.focusIdea('rights_of_man'); {const I=__memeplex.ideas,P=Object.fromEntries(I.map(d=>[d.id,d.parents||[]])),S=new Set(['rights_of_man']);let ch=1;const up=i=>(P[i]||[]).forEach(p=>{if(!S.has(p)){S.add(p);up(p)}});up('rights_of_man');const dn=i=>I.forEach(d=>{if((d.parents||[]).includes(i)&&!S.has(d.id)){S.add(d.id);dn(d.id)}});dn('rights_of_man');__memeplex.frameBranch(S)}"); await pg.wait_for_timeout(2500); await pg.screenshot(path='rev-rights_of_man-lineage.png')
    await b.close()
  srv.terminate(); print('errors',errs,'alias misses',miss); sys.exit(1 if errs or bad or miss else 0)
asyncio.run(run())
