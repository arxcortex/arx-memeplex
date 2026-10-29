import asyncio,subprocess,json
from playwright.async_api import async_playwright
R='/workspace/amrepo/'
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8784"],cwd="site-v3",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); errs=[]; fails=[]
  def ok(c,m):
    print(("  PASS " if c else "  FAIL ")+m); c or fails.append(m)
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for tag,vp,mob in [("desk",dict(width=1440,height=900),False),("mobile",dict(width=390,height=844),True)]:
      print(tag)
      ctx=await b.new_context(viewport=vp,is_mobile=mob,has_touch=mob); pg=await ctx.new_page(); pg.on("pageerror",lambda e:errs.append(str(e)))
      for f in ['ideas.json','thinkers.json','axes.json']:
        await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      await pg.goto("http://localhost:8784/memeplex.html?intro=none"); await pg.wait_for_function("window.__memele"); await pg.wait_for_timeout(4000)
      ans=await pg.evaluate("__memele.answerFor(__memele.today())"); name=ans['name']
      await pg.click("#tb button[data-k=games]"); await pg.wait_for_timeout(200); await pg.click("#games .gm-pick[data-g=memele]"); await pg.wait_for_timeout(300)
      ok(await pg.is_visible("#memele [data-a=giveup]"),"give-up button visible at start")
      wrong="marxism" if ans['id']!="marxism" else "neoplatonism"
      await pg.evaluate("id=>__memele.guess(id)",wrong); await pg.click("#memele [data-a=hint]"); await pg.wait_for_timeout(150)
      ok(await pg.is_visible("#memele [data-a=giveup]"),"still visible mid-game")
      await pg.click("#memele [data-a=giveup]"); await pg.wait_for_timeout(150)
      ok("Reveal answer?" in await pg.inner_text("#memele .mm-gu") and not await pg.evaluate("__memele.day.done"),"first tap asks 'Reveal answer?' without ending")
      await pg.click("#memele [data-a=gucancel]"); await pg.wait_for_timeout(150)
      ok(not await pg.evaluate("__memele.day.done") and "I don't know" in await pg.inner_text("#memele .mm-gu"),"Keep playing cancels")
      await pg.click("#memele [data-a=giveup]"); await pg.wait_for_timeout(150)
      await pg.screenshot(path=f"shots/views/memele-giveup-confirm-{tag}.png")
      await pg.click("#memele [data-a=giveup]"); await pg.wait_for_timeout(300)
      d=await pg.evaluate("__memele.day")
      ok(d['done'] and d['gaveUp'] and not d['won'],"second tap ends game as gave-up")
      ok(not await pg.is_visible("#memele input") and not await pg.query_selector("#memele [data-a=giveup]"),"input and give-up hidden after")
      rev=await pg.inner_text("#memele .mm-rev"); print("   reveal:",rev.replace("\n"," | "))
      ok(name in rev and await pg.is_visible("#memele [data-a=panel]"),"answer, lineage and panel link shown")
      sh=await pg.evaluate("__memele.shareText()"); print("   share:",json.dumps(sh))
      ok("🏳️" in sh and "Gave up after 1 guess and 1 hint" in sh and name.lower() not in sh.lower(),"share text has 🏳️ marker, counts, no spoiler")
      st=json.loads(await pg.evaluate("localStorage.getItem('memele-v1')")); ok(st['days'][await pg.evaluate("__memele.today()")].get('gaveUp') and st.get('streak')==0,"saved in memele-v1 with streak reset")
      await pg.screenshot(path=f"shots/views/memele-giveup-{tag}.png")
      sz=await pg.evaluate("""(async()=>{let o=null;const r=ArxGameCard.result;ArxGameCard.result=async d=>{o=d;return r(d)};const sc=ArxShareCard.open;ArxShareCard.open=()=>{};document.querySelector('#memele [data-a=card]').click();await new Promise(z=>setTimeout(z,1500));ArxShareCard.open=sc;ArxGameCard.result=r;return o})()""")
      ok(sz and sz['gaveUp'] and sz['lines'][0].startswith("🏳️") and not any(name.lower() in l.lower() for l in sz['lines']),"share card gets gaveUp + 🏳️ line, no spoiler")
      await pg.reload(); await pg.wait_for_function("window.__memele"); await pg.wait_for_timeout(1500); await pg.evaluate("__memele.open()"); await pg.wait_for_timeout(200)
      ok(await pg.evaluate("__memele.day.gaveUp") and name in await pg.inner_text("#memele .mm-rev"),"reload shows revealed gave-up result")
      await pg.click("#memele [data-a=panel]"); await pg.wait_for_timeout(1500)
      ok(not await pg.evaluate("document.getElementById('memele').classList.contains('open')"),"panel link closes game and focuses idea")
      await ctx.close()
    print("errors",errs); print("FAILS",fails)
  srv.terminate()
asyncio.run(run())
