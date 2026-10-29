import asyncio,subprocess,json,os
from playwright.async_api import async_playwright
V=["helix","beatific","tree","galaxy","sphere","brain"]
os.makedirs("shots/views",exist_ok=True)
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8768"],cwd="site-v3",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1)
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    errs=[]
    async def page(vp,mob=False,q="",reduced=False):
      pg=await b.new_page(viewport=vp,is_mobile=mob,has_touch=mob,reduced_motion="reduce" if reduced else "no-preference")
      pg.on("console",lambda m:errs.append(m.text) if m.type=="error" else None); pg.on("pageerror",lambda e:errs.append(str(e)))
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      await pg.goto("http://localhost:8768/memeplex.html"+q); return pg
    pg=await page(dict(width=1440,height=900),q="?intro=helix&fx=1")
    await pg.wait_for_function("window.__views"); 
    for i,ms in enumerate([300,1500,2400,3200,5500]):
      await pg.wait_for_timeout(ms-([0,300,1500,2400,3200][i])); await pg.screenshot(path=f"shots/views/intro-{i+1}-{ms}ms.png")
    print("intro",await pg.evaluate("__views.intro"),"fps",await pg.evaluate("__views.introFps"),"fx",await pg.evaluate("__views.fx()"),"cur",await pg.evaluate("__views.cur"))
    print("check",json.dumps(await pg.evaluate("__views.check()")))
    print("fams",await pg.evaluate("__views.fams"))
    await pg.evaluate("__memeplex.controls.autoRotate=false")
    await pg.click("#tb button[data-k=views]"); await pg.wait_for_timeout(300)
    await pg.screenshot(path="shots/views/panel.png")
    for v in V:
      await pg.click(f".vbtn[data-v={v}]"); 
      if v=="tree": await pg.wait_for_timeout(1000); await pg.screenshot(path="shots/views/mid-tween-to-tree.png"); await pg.wait_for_timeout(1700)
      else: await pg.wait_for_timeout(2700)
      await pg.screenshot(path=f"shots/views/{v}.png")
    # filter in alt view
    await pg.evaluate("__memeplex.filt.sel.add('br:christianity');__memeplex.applyFilter()"); await pg.wait_for_timeout(900)
    await pg.screenshot(path="shots/views/brain-filter-christianity.png")
    await pg.evaluate("__stretch.set('x',2)"); s=await pg.evaluate("__stretch.get()"); print("stretch in alt (should stay 1)",s)
    await pg.keyboard.press("r"); await pg.wait_for_timeout(2500); print("after reset",await pg.evaluate("__views.cur"))
    await pg.screenshot(path="shots/views/default-after-reset.png")
    m=await page(dict(width=390,height=844),True,"?intro=galaxy&fx=1")
    await m.wait_for_timeout(1000); await m.screenshot(path="shots/views/mobile-intro-galaxy.png")
    await m.wait_for_timeout(4000)
    await m.click("#tb button[data-k=views]"); await m.wait_for_timeout(300); await m.screenshot(path="shots/views/mobile-panel.png")
    for v in V:
      await m.click(f".vbtn[data-v={v}]"); await m.wait_for_timeout(2600); await m.screenshot(path=f"shots/views/mobile-{v}.png")
    print("mobile fps",await m.evaluate("__views.introFps"))
    r=await page(dict(width=1440,height=900),reduced=True); await r.wait_for_timeout(2500)
    print("reduced cur",await r.evaluate("__views.cur"), await r.evaluate("__views.intro||null"))
    await r.screenshot(path="shots/views/reduced-motion-start.png")
    print("names",await r.evaluate("Object.keys(__views.names)"));print("errors:",errs)
    await b.close()
  srv.kill()
asyncio.run(run())
