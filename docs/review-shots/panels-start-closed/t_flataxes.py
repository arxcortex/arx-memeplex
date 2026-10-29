import asyncio,subprocess
from playwright.async_api import async_playwright
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8774"],cwd="site-v3",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for name,vp,mob in [("flat-axes",dict(width=1440,height=900),False),("flatH-axes",dict(width=1440,height=900),False),("mobile-flat-axes",dict(width=390,height=844),True),("mobile-flatH-axes",dict(width=390,height=844),True)]:
      pg=await b.new_page(viewport=vp,is_mobile=mob,has_touch=mob)
      pg.on("pageerror",lambda e:errs.append(str(e)))
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      await pg.goto("http://localhost:8774/memeplex.html?intro=none"); await pg.wait_for_function("window.__views"); await pg.wait_for_timeout(1500)
      v="flatH" if "flatH" in name else "flat"
      await pg.evaluate("v => __views.set(v)", v); await pg.wait_for_function("!__views.busy",timeout=20000); await pg.wait_for_timeout(1500)
      vis=await pg.evaluate("[...document.querySelectorAll('.axl.chart')].filter(e=>e.style.display==='block').map(e=>e.textContent)")
      names=await pg.evaluate("[...document.querySelectorAll('.lbl')].filter(e=>e.style.display==='block').length")
      print(name,"chart labels",vis,"idea names shown",names,"grid visible",await pg.evaluate("__chart.g.visible"),"op",await pg.evaluate("__chart.mats.map(m=>+m.opacity.toFixed(2))"))
      await pg.screenshot(path=f"shots/views/{name}.png")
      await pg.evaluate("__views.set('tree')"); await pg.wait_for_function("!__views.busy",timeout=20000); await pg.wait_for_timeout(1500)
      print("  tree: chart labels",await pg.evaluate("[...document.querySelectorAll('.axl.chart')].filter(e=>e.style.display==='block').length"),"grid",await pg.evaluate("__chart.g.visible"))
      await pg.evaluate("__views.set('default')"); await pg.wait_for_function("!__views.busy",timeout=20000); await pg.wait_for_timeout(1500)
      print("  default: chart",await pg.evaluate("[...document.querySelectorAll('.axl.chart')].filter(e=>e.style.display==='block').length"),"axis labels",await pg.evaluate("[...document.querySelectorAll('.axl:not(.chart)')].filter(e=>e.style.display==='block').length"),"cur",await pg.evaluate("__views.cur"))
    print("check",await pg.evaluate("JSON.stringify(__views.check())"))
    print("errors",errs)
  srv.terminate()
asyncio.run(run())
