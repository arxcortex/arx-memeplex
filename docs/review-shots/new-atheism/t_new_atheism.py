# Loads the new ideas.json, checks tour edges and alias search, and shoots tour start, a middle stop and the lineage view. Run from this folder.
import asyncio,subprocess,sys,json
from playwright.async_api import async_playwright
R='../../../'; T='new-atheism-to-the-online-right'
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8931"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); errs=[]; fail=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    pg=await (await b.new_context(viewport=dict(width=1440,height=900))).new_page(); pg.on("pageerror",lambda e:errs.append(str(e)))
    for f in ['ideas.json','thinkers.json','axes.json','currents.json']:
      await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
    await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
    await pg.goto("http://localhost:8931/memeplex.html?intro=none"); await pg.wait_for_function("window.__memeplex && __memeplex.ideas.length && window.__tours",polling=500); await pg.wait_for_timeout(3000)
    n=await pg.evaluate("__memeplex.ideas.length"); bad=await pg.evaluate("__tours.validate()"); print('ideas',n,'tour validate',bad or 'OK')
    tl=await pg.evaluate(f"__tours.list.find(t=>t.id=='{T}')"); print('tour listed',tl and (tl['kind'],len(tl['steps']))); print(await pg.evaluate("__tours.list.map(t=>t.id)"), await pg.evaluate("__tours.data.map(t=>t.id)"))
    if not tl: fail.append('tour missing')
    else:
      st=tl['steps']
      for a,c in zip(st,st[1:]):
        ok=await pg.evaluate("([a,c])=>__tours.linked(a,c)",[a,c]); print('edge',a,'->',c,ok)
        if not ok: fail.append(a+'->'+c)
    for q in ['Atheism+','New Atheism','Gamergate','Alt-right','Alt-lite','Online right','CPUSA','Ásatrú']:
      await pg.evaluate("q=>{const e=document.getElementById('search');e.value=q;e.dispatchEvent(new Event('input',{bubbles:true}))}",q); await pg.wait_for_timeout(500)
      txt=await pg.evaluate("()=>{const e=document.querySelector('#results');return e?e.innerText.slice(0,200):''}")
      print('search',q,'->',txt.replace('\n',' | ')[:120])
    await pg.evaluate(f"__tours.start('{T}')"); await pg.wait_for_timeout(2500); await pg.screenshot(path='tour-start.png')
    for _ in range(3): await pg.keyboard.press('ArrowRight'); await pg.wait_for_timeout(1500)
    print('step after 3 next',await pg.evaluate("__tours.step")); await pg.screenshot(path='tour-middle-stop.png')
    await pg.evaluate("__tours.stop()"); await pg.wait_for_timeout(1000)
    await pg.evaluate("i=>__memeplex.focusIdea(i)",'gamergate'); await pg.wait_for_timeout(2000); await pg.screenshot(path='lineage-gamergate.png')
    await b.close()
  srv.terminate(); print('errors',errs,'fail',fail); sys.exit(1 if errs or bad or fail else 0)
asyncio.run(run())
