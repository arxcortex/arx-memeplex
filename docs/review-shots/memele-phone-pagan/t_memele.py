import asyncio,subprocess,json
from playwright.async_api import async_playwright
R='/workspace/amrepo/'
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8778"],cwd="site-v3",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    async def mk(vp,mob,url="http://localhost:8778/memeplex.html?intro=none"):
      ctx=await b.new_context(viewport=vp,is_mobile=mob,has_touch=mob); pg=await ctx.new_page()
      pg.on("pageerror",lambda e:errs.append(str(e)))
      for f in ['ideas.json','thinkers.json','axes.json']:
        await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      await pg.goto(url); await pg.wait_for_function("window.__memele && window.__views"); await pg.wait_for_timeout(4500); return pg
    for tag,vp,mob in [("desk",dict(width=1440,height=900),False),("mobile",dict(width=390,height=844),True)]:
      pg=await mk(vp,mob)
      print(tag,"ideas",await pg.evaluate("__memeplex.ideas.length"),"check",await pg.evaluate("JSON.stringify(__views.check()).replace(/\\[\\]/g,'0')"),"phone",await pg.evaluate("__phone.on"))
      print(" visible toolbar",await pg.evaluate("[...document.querySelectorAll('#tb button')].filter(b=>b.offsetParent).map(b=>b.dataset.k)"))
      if mob:
        await pg.screenshot(path="shots/views/phone-home.png")
        print(" controls enabled",await pg.evaluate("__memeplex.controls.enabled"),"autorotate",await pg.evaluate("__memeplex.controls.autoRotate"))
      ans=await pg.evaluate("__memele.answerFor(__memele.today()).id"); print(" answer stable",ans==await pg.evaluate("__memele.answerFor(__memele.today()).id"))
      await pg.click("#tb button[data-k=memele]"); await pg.wait_for_timeout(300)
      wrong=await pg.evaluate("a=>__memeplex.ideas.filter(d=>d.id!==a).map(d=>d.id).sort((x,y)=>Math.abs(__memeplex.ideas.find(d=>d.id==x).year-2000)-0).slice(0,40)",ans)
      # type into autocomplete for first guess
      n1=await pg.evaluate("id=>__memeplex.ideas.find(d=>d.id==id).name",wrong[3])
      await pg.fill("#memele input",n1[:6]); await pg.wait_for_timeout(200); print(" autocomplete",await pg.evaluate("[...document.querySelectorAll('#memele .ac button')].map(b=>b.textContent).slice(0,3)"))
      await pg.evaluate("id=>__memele.guess(id)",wrong[3]); await pg.evaluate("id=>__memele.guess(id)",wrong[10]); await pg.evaluate("id=>__memele.guess(id)",wrong[20])
      print(" rows",await pg.evaluate("[...document.querySelectorAll('#memele .arx-game-row')].map(r=>r.innerText.replace(/\\n/g,' | '))"),"clues",await pg.evaluate("document.querySelectorAll('#memele .arx-game-clue').length"))
      await pg.screenshot(path=f"shots/views/memele-progress-{tag}.png")
      await pg.evaluate("id=>__memele.guess(id)",ans); await pg.wait_for_timeout(300)
      print(" share text",json.dumps(await pg.evaluate("__memele.shareText()")))
      print(" stored",(await pg.evaluate("localStorage.getItem('memele-v1')"))[:160])
      await pg.screenshot(path=f"shots/views/memele-done-{tag}.png")
      await pg.click("#memele [data-a=card]"); await pg.wait_for_timeout(2500)
      await pg.screenshot(path=f"shots/views/memele-card-{tag}.png")
      await pg.keyboard.press("Escape"); await pg.wait_for_timeout(300)
      if mob:
        await pg.goto("http://localhost:8778/memeplex.html?intro=none"); await pg.wait_for_timeout(4000)
        await pg.evaluate("window.__memele.close()")
        await pg.evaluate("__tours.start('east-west')"); await pg.wait_for_timeout(800); await pg.screenshot(path="shots/views/phone-tour.png")
        print(" phone tour panel open?",await pg.evaluate("document.body.classList.contains('panel-open')"))
        await pg.evaluate("__tours.stop()")
        await pg.click("#tb button[data-k=search]"); await pg.fill("#search","Romuva"); await pg.wait_for_timeout(300); await pg.click("#results button"); await pg.wait_for_timeout(1500)
        await pg.screenshot(path="shots/views/phone-sheet.png"); print(" sheet",await pg.inner_text("#panel h2"))
        await pg.click("#panel .close"); await pg.wait_for_timeout(500)
        await pg.click("#phonenote a"); await pg.wait_for_timeout(500); print(" explore anyway -> phone",await pg.evaluate("__phone.on"),"controls",await pg.evaluate("__memeplex.controls.enabled"))
    print("errors",errs)
  srv.terminate()
asyncio.run(run())
