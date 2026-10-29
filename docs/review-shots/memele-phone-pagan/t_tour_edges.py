# Fails (exit 1) if any guided-tour step is not a direct parent/child edge in ideas.json.
import asyncio,subprocess,sys,json
from playwright.async_api import async_playwright
R='/workspace/amrepo/'
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8779"],cwd="site-v3",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); errs=[]; bad=None
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    pg=await b.new_page(viewport=dict(width=1440,height=900)); pg.on("pageerror",lambda e:errs.append(str(e)))
    for f in ['ideas.json','thinkers.json','axes.json']:
      await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
    await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
    await pg.goto("http://localhost:8779/memeplex.html?intro=none"); await pg.wait_for_function("window.__tours"); await pg.wait_for_timeout(4500)
    bad=await pg.evaluate("__tours.validate()")
    neg=await pg.evaluate("__tours.validate([{id:'x',steps:[{id:'platonic_forms'},{id:'marxism'}]}])")
    print("tours",await pg.evaluate("__tours.list.map(t=>t.id+':'+t.steps.join('>'))"))
    print("bad edges",bad,"| negative control caught:",bool(neg))
    await pg.evaluate("__tours.start('abrahamic')"); await pg.wait_for_timeout(2000)
    for _ in range(3): await pg.click("#tourbar [data-a=next]"); await pg.wait_for_timeout(3200)
    lit=await pg.evaluate("""(()=>{const s=__tours.list.find(t=>t.id==='abrahamic').steps.slice(0,4);return s.slice(1).map((k,j)=>{const l=__memeplex.lines?null:null;return k})})()""")
    await pg.screenshot(path="shots/views/tour-path-glow.png"); print("step",await pg.evaluate("__tours.step"),"errors",errs)
  srv.terminate()
  if bad or not neg or errs: sys.exit(1)
asyncio.run(run())
