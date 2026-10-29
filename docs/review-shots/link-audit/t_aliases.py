# Checks search/Memele alias matching against the audited ideas.json. Run from this folder.
import asyncio,subprocess,sys
from playwright.async_api import async_playwright
R='../../../'
CASES={'CPUSA':'american_communism','woke':'social_justice_movement','e/acc':'effective_accelerationism','Nazism':'nazism','Ásatrú':'heathenry','Asatru':'heathenry','Apostolic Christianity':None}
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8785"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); fail=[]; errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    pg=await (await b.new_context(viewport=dict(width=1440,height=900))).new_page(); pg.on("pageerror",lambda e:errs.append(str(e)))
    for f in ['ideas.json','thinkers.json','axes.json','currents.json']:
      await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
    await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
    await pg.goto("http://localhost:8785/memeplex.html?intro=none"); await pg.wait_for_function("window.__memele && window.__memeplex && __memeplex.ideas.length",polling=500); await pg.wait_for_timeout(2000)
    print('ideas',await pg.evaluate("__memeplex.ideas.length"))
    for q,want in CASES.items():
      r=await pg.evaluate("q=>__memele.search(q,[]).slice(0,3)",q); print(q,r)
      if want and (not r or r[0]!=want): fail.append(q)
    await pg.evaluate("__memeplex.focusIdea('heathenry')"); await pg.wait_for_timeout(1500); await pg.screenshot(path='link-audit-heathenry.png')
    await b.close()
  srv.terminate(); print('errors',errs,'FAILS',fail); sys.exit(1 if fail or errs else 0)
asyncio.run(run())
