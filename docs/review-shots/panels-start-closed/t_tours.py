import asyncio,subprocess
from playwright.async_api import async_playwright
R='/workspace/amrepo/'
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8776"],cwd="site-v3",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    async def mk(vp,mob,url):
      pg=await b.new_page(viewport=vp,is_mobile=mob,has_touch=mob)
      pg.on("pageerror",lambda e:errs.append(str(e)))
      for f in ['ideas.json','thinkers.json','axes.json']:
        await pg.route("**/arx-memeplex/"+f,(lambda f: (lambda r: r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      await pg.goto(url); await pg.wait_for_function("window.__views && window.__tours"); return pg
    for tag,vp,mob in [("desk",dict(width=1440,height=900),False),("mobile",dict(width=390,height=844),True)]:
      pg=await mk(vp,mob,"http://localhost:8776/memeplex.html?intro=none"); await pg.wait_for_timeout(4800)
      print(tag,"ideas",await pg.evaluate("__memeplex.ideas.length"),"check",await pg.evaluate("JSON.stringify(__views.check()).replace(/\\[\\]/g,'0')"))
      print(" tours",await pg.evaluate("__tours.list.map(t=>t.name+':'+t.steps.length)"))
      await pg.click("#tb button[data-k=tours]"); await pg.wait_for_timeout(400); await pg.screenshot(path=f"shots/views/tours-menu-{tag}.png")
      await pg.click("#tourmenu button[data-t=east-west]"); await pg.wait_for_timeout(2200)
      for _ in range(3): await pg.click("#tourbar [data-a=next]"); await pg.wait_for_timeout(700)
      await pg.wait_for_timeout(1500)
      print(" tour step",await pg.evaluate("__tours.step"),"caption",await pg.inner_text("#tourbar .tc"))
      await pg.screenshot(path=f"shots/views/tour-{tag}.png")
      await pg.click("#tourbar [data-a=exit]")
      await pg.evaluate("__memeplex.focusIdea('marxism')"); await pg.wait_for_timeout(1800)
      await pg.click("#panel [data-act=kin]"); await pg.wait_for_timeout(500)
      print(" kin",(await pg.inner_text("#panel .when")), "levels",await pg.evaluate("document.querySelectorAll('#panel .kinlv').length"))
      await pg.screenshot(path=f"shots/views/kin-{tag}.png")
      await pg.click("#panel .kinlv button"); await pg.wait_for_timeout(800); print(" kin click opened",await pg.inner_text("#panel h2"))
      await pg.evaluate("document.querySelector('#filt .dchip[data-dom=abrahamic]').click()"); await pg.wait_for_timeout(500)
      print(" abrahamic visible",await pg.evaluate("__filter.visible"))
      await pg.evaluate("__views.set('tree')"); await pg.wait_for_function("!__views.busy",timeout=20000); await pg.evaluate("__memeplex.focusIdea('sufism')"); await pg.wait_for_timeout(1000)
      url=await pg.evaluate("__copyLink(document.querySelector('#tb button[data-k=link]'))"); print(" link",url)
      pg2=await mk(vp,mob,url); await pg2.wait_for_timeout(8000)
      print(" restored view",await pg2.evaluate("__views.cur"),"filter",await pg2.evaluate("JSON.stringify(__filter)"),"panel",await pg2.inner_text("#panel h2"))
      await pg2.screenshot(path=f"shots/views/link-restore-{tag}.png")
      await pg2.click("#tb button[data-k=legend]"); await pg2.wait_for_timeout(300)
      await pg2.evaluate("document.querySelector('#legend .why-mp').open=true"); await pg2.wait_for_timeout(300)
      print(" why", (await pg2.inner_text("#legend .why-mp"))[:80])
      await pg2.screenshot(path=f"shots/views/why-memeplex-{tag}.png")
    print("errors",errs)
  srv.terminate()
asyncio.run(run())
