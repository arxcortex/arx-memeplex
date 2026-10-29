# Loads the batch-1 ideas.json, runs the in-page tour validator, and shots the new ideas. Run from this folder.
import asyncio,subprocess,sys
from playwright.async_api import async_playwright
R='../../../'
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8787"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    pg=await (await b.new_context(viewport=dict(width=1440,height=900))).new_page(); pg.on("pageerror",lambda e:errs.append(str(e)))
    for f in ['ideas.json','thinkers.json','axes.json','currents.json']:
      await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
    await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
    await pg.goto("http://localhost:8787/memeplex.html?intro=none"); await pg.wait_for_function("window.__memeplex && __memeplex.ideas.length && window.__tours",polling=500); await pg.wait_for_timeout(3000)
    n=await pg.evaluate("__memeplex.ideas.length"); bad=await pg.evaluate("__tours.validate()"); print('ideas',n,'tour validate',bad)
    for i in ['bohmean_theosophy','racial_classification','manichaeism','protestantism']:
      await pg.evaluate("i=>__memeplex.focusIdea(i)",i); await pg.wait_for_timeout(1500); await pg.screenshot(path=f'loose-{i}.png')
    await b.close()
  srv.terminate(); print('errors',errs); sys.exit(1 if errs or bad else 0)
asyncio.run(run())
