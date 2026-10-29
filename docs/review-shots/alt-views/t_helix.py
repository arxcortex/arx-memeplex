import asyncio,subprocess,json
from playwright.async_api import async_playwright
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8770"],cwd="site-v3",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); await asyncio.sleep(1)
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"]); errs=[]
    for name,vp,mob in [("helix",dict(width=1440,height=900),False),("mobile-helix",dict(width=390,height=844),True)]:
      pg=await b.new_page(viewport=vp,is_mobile=mob,has_touch=mob); pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m:errs.append(m.text) if m.type=="error" else None)
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      await pg.goto("http://localhost:8770/memeplex.html?intro=sphere&fx=1"); await pg.wait_for_timeout(5500)
      await pg.evaluate("__memeplex.controls.autoRotate=false; __views.set('helix')"); await pg.wait_for_timeout(1000)
      if not mob: await pg.screenshot(path="shots/views/mid-tween-to-helix.png")
      await pg.wait_for_timeout(1800); await pg.screenshot(path=f"shots/views/{name}.png")
      if not mob: print("check",json.dumps(await pg.evaluate("__views.check()")))
    print("errors",errs); await b.close()
  srv.kill()
asyncio.run(run())
