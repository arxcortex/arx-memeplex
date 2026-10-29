import asyncio,subprocess,json
from playwright.async_api import async_playwright
TJ=open('/workspace/amrepo/thinkers.json').read()
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8771"],cwd="site-v3",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1)
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for mode in ["ok","404"]:
      errs=[];pg=await b.new_page(viewport=dict(width=1440,height=900),reduced_motion="reduce")
      pg.on("pageerror",lambda e:errs.append(str(e)))
      pg.on("console",lambda m:m.type=="error" and errs.append("console:"+m.text))
      async def h(route):
        if mode=="ok": await route.fulfill(status=200,content_type="application/json",body=TJ)
        else: await route.fulfill(status=404,body="nf")
      await pg.route("**/thinkers.json",h)
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      await pg.goto("http://localhost:8771/memeplex.html?intro=none"); await pg.wait_for_function("window.__views"); await pg.wait_for_timeout(2500)
      await pg.evaluate("__memeplex.focusIdea('valentinianism')")
      await pg.wait_for_timeout(2500)
      links=await pg.eval_on_selector_all("#panel .chips a.tlink","els=>els.map(e=>[e.textContent,e.href,e.target,e.rel])")
      spans=await pg.eval_on_selector_all("#panel .chips span","els=>els.map(e=>e.textContent)")
      print(mode,"links",links,"spans",spans,"errors",errs)
      if mode=="ok":
        await pg.focus("#panel a.tlink"); await pg.screenshot(path="shots/views/thinker-links.png")
    srv.terminate()
asyncio.run(run())
