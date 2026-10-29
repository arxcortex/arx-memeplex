# Fails if any tour stop pair isn't an edge, a kind is missing, or badges don't render. Run from this folder.
import asyncio,subprocess,sys,json
from playwright.async_api import async_playwright
R='../../../'; OUT=sys.argv[1] if len(sys.argv)>1 else '.'
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8783"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); errs=[]; fail=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    pg=await b.new_page(viewport=dict(width=1440,height=900)); pg.on("pageerror",lambda e:errs.append(str(e)))
    for f in ['ideas.json','thinkers.json','axes.json','currents.json']:
      await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
    await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
    await pg.goto("http://localhost:8783/memeplex.html?intro=none"); await pg.wait_for_function("window.__tours"); await pg.wait_for_timeout(4500)
    bad=await pg.evaluate("__tours.validate()"); neg=await pg.evaluate("__tours.validate([{id:'x',steps:[{id:'platonic_forms'},{id:'marxism'}]}])")
    L=await pg.evaluate("__tours.list"); print("tours",[(t['id'],t['kind'],len(t['steps'])) for t in L])
    if bad or not neg: fail.append(('edges',bad))
    if len(L)!=5 or any(t['kind'] not in ('genealogy','transmission','narrative') for t in L): fail.append('kinds')
    await pg.evaluate("__tours.menu()"); await pg.wait_for_timeout(600)
    nb=await pg.evaluate("document.querySelectorAll('#tourmenu button[data-t] .tk').length"); print("menu badges",nb)
    if nb!=5: fail.append('menu badges')
    await pg.screenshot(path=OUT+"/tour-picker-kinds.png")
    await pg.click("#tourmenu button[data-t=academy-to-the-ming-court]"); await pg.wait_for_timeout(2500)
    h=await pg.evaluate("document.querySelector('#tourbar .tkh').textContent"); print("header",h)
    if 'transmission' not in h.lower(): fail.append('header')
    await pg.screenshot(path=OUT+"/tour-start-header.png")
    for _ in range(3): await pg.click("#tourbar [data-a=next]"); await pg.wait_for_timeout(3200)
    print("step",await pg.evaluate("__tours.step")); await pg.screenshot(path=OUT+"/tour-in-progress.png")
    await pg.set_viewport_size(dict(width=390,height=844)); await pg.wait_for_timeout(800); await pg.screenshot(path=OUT+"/tour-in-progress-narrow.png")
  srv.terminate(); print("errors",errs,"fail",fail)
  if fail or errs: sys.exit(1)
asyncio.run(run())
