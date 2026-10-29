import asyncio,subprocess,json
from playwright.async_api import async_playwright
R='/workspace/amrepo/'
FUZZ={"marxsim":"marxism","Marx":"marxism","stoics":"stoic_logos","stoicsm":"stoic_logos","neoplatonsim":"neoplatonism","chrstianity":"christianity","Neo-Platonism":"neoplatonism","Asatru":"heathenry","ásatrú":"heathenry","the dao":"daoist_way","RODNOVRY":"rodnovery","vajrayanna":"vajrayana","e/acc":"effective_accelerationism","pure land":"pure_land","4chan":"chan_culture"}
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8783"],cwd="site-v3",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); errs=[]; bad=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for tag,vp,mob in [("desk",dict(width=1440,height=900),False),("mobile",dict(width=390,height=844),True)]:
      ctx=await b.new_context(viewport=vp,is_mobile=mob,has_touch=mob); pg=await ctx.new_page(); pg.on("pageerror",lambda e:errs.append(str(e)))
      for f in ['ideas.json','thinkers.json','axes.json']:
        await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      await pg.goto("http://localhost:8783/memeplex.html?intro=none"); await pg.wait_for_function("window.__memele && window.__views"); await pg.wait_for_timeout(4500)
      print(tag,"phone",await pg.evaluate("__phone.on"),"check",await pg.evaluate("JSON.stringify(__views.check()).replace(/\\[\\]/g,'0')"))
      for q,want in FUZZ.items():
        r=await pg.evaluate("q=>__memele.resolve(q)",q)
        if r.get('id')!=want: bad.append((q,want,r))
      print(" ambiguous 'christ':",await pg.evaluate("__memele.resolve('christ')"),"| nonsense:",await pg.evaluate("__memele.resolve('zzqxv')"))
      ans=await pg.evaluate("__memele.answerFor(__memele.today()).id")
      await pg.click("#tb button[data-k=games]"); await pg.wait_for_timeout(200); await pg.click("#games .gm-pick[data-g=memele]"); await pg.wait_for_timeout(300)
      print(" clue order",await pg.evaluate("__memele.clueTypes()"))
      print(" opening",await pg.evaluate("[...document.querySelectorAll('#memele .arx-game-clue')].map(c=>c.innerText)"),"left",await pg.evaluate("document.querySelector('#memele .mm-left').textContent"))
      for i in range(3): await pg.click("#memele [data-a=hint]"); await pg.wait_for_timeout(150)
      print(" clues after 3 hints",await pg.evaluate("[...document.querySelectorAll('#memele .arx-game-clue')].map(c=>c.innerText)"))
      await pg.fill("#memele input","zzqxv"); await pg.keyboard.press("Enter"); await pg.wait_for_timeout(150)
      print(" unrecognized:",await pg.inner_text("#memele .mm-msg"),"guesses",await pg.evaluate("__memele.day.guesses.length"))
      await pg.fill("#memele input","christ"); await pg.keyboard.press("Enter"); await pg.wait_for_timeout(150)
      print(" didyoumean:",await pg.inner_text("#memele .mm-msg"),await pg.evaluate("[...document.querySelectorAll('#memele .ac button')].map(b=>b.textContent)"),"guesses",await pg.evaluate("__memele.day.guesses.length"))
      wrong="marxism" if ans!="marxism" else "neoplatonism"
      await pg.fill("#memele input","marxsim" if wrong=="marxism" else "neo-platonism"); await pg.keyboard.press("Enter"); await pg.wait_for_timeout(200)
      print(" typo guess counted as",await pg.evaluate("__memele.day.guesses"),"clues",await pg.evaluate("document.querySelectorAll('#memele .arx-game-clue').length"))
      await pg.screenshot(path=f"shots/views/memele-hints-{tag}.png")
      while await pg.evaluate("document.querySelectorAll('#memele .arx-game-clue').length")<7: await pg.click("#memele [data-a=hint]"); await pg.wait_for_timeout(300)
      await pg.wait_for_timeout(1500); print(" flash blur",await pg.evaluate("document.getElementById('stage').style.filter"),"modal hidden",await pg.evaluate("document.getElementById('memele').classList.contains('flashing')"))
      await pg.screenshot(path=f"shots/views/memele-flash-{tag}.png"); await pg.wait_for_timeout(2500)
      print(" after flash blur",repr(await pg.evaluate("document.getElementById('stage').style.filter")))
      await pg.evaluate("id=>__memele.guess(id)",ans); await pg.wait_for_timeout(300)
      print(" share",json.dumps(await pg.evaluate("__memele.shareText()")))
      print(" stored",await pg.evaluate("JSON.stringify(JSON.parse(localStorage.getItem('memele-v1')).days)"))
      await pg.screenshot(path=f"shots/views/memele-hints-done-{tag}.png")
      await pg.reload(); await pg.wait_for_function("window.__memele"); await pg.wait_for_timeout(1500); await pg.evaluate("__memele.open()")
      print(" persisted hints",await pg.evaluate("__memele.day.hints"))
    print("fuzzy failures",bad); print("errors",errs)
  srv.terminate()
asyncio.run(run())
