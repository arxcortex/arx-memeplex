# Checks the score-scale wording loads cleanly and screenshots an idea card's score area. Run from this folder.
import asyncio,subprocess,sys
from playwright.async_api import async_playwright
R='../../../'
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8785"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); errs=[]; fail=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    ctx=await b.new_context(viewport=dict(width=1440,height=900)); pg=await ctx.new_page()
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m:m.type=='error' and errs.append(m.text))
    for f in ['ideas.json','thinkers.json','axes.json','currents.json']:
      await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
    await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
    await pg.goto("http://localhost:8785/memeplex.html?intro=none"); await pg.wait_for_function("window.__memeplex && __memeplex.ideas && __memeplex.ideas.length",polling=500); await pg.wait_for_timeout(3000)
    await pg.evaluate("__memeplex.focusIdea('existentialism')"); await pg.wait_for_timeout(1500)
    sc=pg.locator('#panel p.scale').first
    if await sc.count()==0: fail.append('no scale')
    else:
      t=await sc.inner_text(); print(t)
      if 'strongly aligned' not in t or 'grows' in t: fail.append('wording')
      await sc.scroll_into_view_if_needed(); await pg.wait_for_timeout(400)
      await pg.locator('#panel').screenshot(path="score-card-existentialism.png")
    html=await pg.content()
    for bad in ['grows from it','grows out of each','GROWS FROM']:
      if bad in html: fail.append(bad)
    await b.close()
  srv.terminate(); print('errors',errs,'FAILS',fail); sys.exit(1 if fail or errs else 0)
asyncio.run(run())
