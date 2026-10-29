import asyncio,subprocess
from playwright.async_api import async_playwright
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8775"],cwd="site-v3",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for vpn,vp,mob in [("desk",dict(width=1440,height=900),False),("mobile",dict(width=390,height=844),True)]:
      pg=await b.new_page(viewport=vp,is_mobile=mob,has_touch=mob)
      pg.on("pageerror",lambda e:errs.append(str(e)))
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      await pg.goto("http://localhost:8775/memeplex.html?intro=none"); await pg.wait_for_function("window.__views"); await pg.wait_for_timeout(1500)
      btn=pg.locator("#tb button[data-k=dice]"); print(vpn,"dice visible",await btn.is_visible(),"title",await btn.get_attribute("title"))
      for v in ["default","tree","flat","flatH","helix"]:
        if v!="default": await pg.evaluate("v=>__views.set(v)",v); await pg.wait_for_function("!__views.busy",timeout=20000); await pg.wait_for_timeout(800)
        picks=[]
        for i in range(6):
          await btn.click(); await pg.wait_for_timeout(300); picks.append(await pg.evaluate("document.querySelector('#panel h2, #panel h1')?.textContent"))
        print(" ",v,"picks",picks,"unique",len(set(picks)))
      await pg.evaluate("__views.set('default',{instant:true})")
      await pg.click("#tb button[data-k=filter]"); await pg.wait_for_timeout(500)
      await pg.evaluate("document.querySelector(\"#filt .dchip[data-dom=abrahamic]\").click()"); await pg.wait_for_timeout(1500)
      print("  abrahamic visible",await pg.evaluate("__filter.visible"))
      ok=True
      for i in range(10):
        idd=await pg.evaluate("__randomIdea()"); ok=ok and await pg.evaluate("id=>Math.max(__memeplex.ideas.find(d=>d.id==id).ratings.christianity||0,__memeplex.ideas.find(d=>d.id==id).ratings.islamic_philosophy||0)>=4",idd)
      print("  random within abrahamic filter",ok)
      await pg.wait_for_timeout(2000); await pg.screenshot(path=f"shots/views/abrahamic-{vpn}.png")
      await pg.click("#tb button[data-k=filter]"); await pg.wait_for_timeout(600)
      await pg.screenshot(path=f"shots/views/random-{vpn}.png")
    print("check",await pg.evaluate("JSON.stringify(__views.check())")); print("errors",errs)
  srv.terminate()
asyncio.run(run())
