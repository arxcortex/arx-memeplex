import asyncio,subprocess,json,sys
from playwright.async_api import async_playwright
OLD='/workspace/mc-serve/old/'; NEW='/workspace/mc-wt/'; OUT='/workspace/memeplex-build/shots/views/'
MOD=["social_justice_movement","intersectionality","maga","america_first","postliberalism","national_conservatism","effective_altruism","neoreaction"]
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8796"],cwd="/workspace/mc-serve",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for which,R in [("before",OLD),("after",NEW)]:
     for tag,vp,mob in [("desk",dict(width=1440,height=900),False),("mobile",dict(width=390,height=844),True)]:
      ctx=await b.new_context(viewport=vp,is_mobile=mob,has_touch=mob); pg=await ctx.new_page(); pg.on("pageerror",lambda e:print("PAGEERR",which,tag,e))
      async def h(route,request=None,R=R):
        f=route.request.url.split('/')[-1].split('?')[0]
        await route.fulfill(status=200,content_type="application/json",body=open(R+f).read(),headers={"Access-Control-Allow-Origin":"*"})
      await pg.route("**/arx-memeplex/*.json",h)
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      q="?intro=none"+("&full=1" if mob else "")
      await pg.goto(f"http://localhost:8796/{which}/memeplex.html{q}"); await pg.wait_for_function("window.__memeplex && window.__views && window.__tours",polling=500,timeout=90000); await pg.wait_for_timeout(3000)
      print(which,tag,"n",await pg.evaluate("__memeplex.ideas.length"),"check",await pg.evaluate("JSON.stringify(__views.check()).replace(/\\[\\]/g,'0')"))
      # zoom default view onto modern cluster (ideas >= 1900)
      await pg.evaluate("""()=>{const I=__memeplex.ideas,C=__memeplex.controls,m=I.filter(d=>d.year>=1900);let x=0,y=0,z=0;m.forEach(d=>{x+=d.pos.x;y+=d.pos.y;z+=d.pos.z});x/=m.length;y/=m.length;z/=m.length;
        C.autoRotate=false;C.target.set(x,y,z);__cam.position.set(x+10,y+8,z+(innerWidth<800?150:95));C.update();}""")
      await pg.wait_for_timeout(1200); await pg.screenshot(path=f"{OUT}modern-{which}-default-{tag}.png")
      if which=="after":
        await pg.evaluate("__views.set('timeline',{instant:true})"); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f"{OUT}modern-after-timeline-{tag}.png")
        print(" timeline x order ok:",await pg.evaluate("(()=>{const s=[...__memeplex.ideas].sort((a,b)=>a.year-b.year);for(let i=1;i<s.length;i++) if(__timeline.x(s[i].year)<__timeline.x(s[i-1].year)) return false; return true})()"))
        print(" ticks:",await pg.evaluate("__timeline.ticks"), "visible tick labels:",await pg.evaluate("[...document.querySelectorAll('.axl.chart.tick.yr')].filter(e=>getComputedStyle(e).display!='none'&&e.style.opacity!=='0').length"))
        # zoom into modern part
        await pg.evaluate("""()=>{const x=__timeline.x(1960);const C=__memeplex.controls;C.autoRotate=false;C.target.set(x,0,0);__cam.position.set(x+6,14,innerWidth<800?120:70);C.update();}""")
        await pg.wait_for_timeout(1200); await pg.screenshot(path=f"{OUT}modern-after-timeline-zoom-{tag}.png")
        await pg.evaluate("__views.set('default',{instant:true})"); await pg.wait_for_timeout(500)
        print(" tours validate:",(await pg.evaluate("JSON.stringify(__tours.validate())"))[:300])
        print(" memele woke:",await pg.evaluate("window.__memele?JSON.stringify(__memele.resolve('woke')):'n/a'"),await pg.evaluate("window.__memele?JSON.stringify(__memele.resolve('maga')):'n/a'"),await pg.evaluate("window.__memele?JSON.stringify(__memele.resolve('america first')):'n/a'"))
        # hash link
        await pg.goto(f"http://localhost:8796/after/memeplex.html?intro=none&h=1{'&full=1' if mob else ''}#v=timeline&i=maga"); await pg.wait_for_function("window.__memeplex && window.__views && window.__tours",polling=500,timeout=90000); await pg.wait_for_timeout(8000)
        print(" hash restore view:",await pg.evaluate("__views.cur"),"panel:",await pg.evaluate("document.getElementById('panel').style.visibility||getComputedStyle(document.getElementById('panel')).visibility"))
        await pg.screenshot(path=f"{OUT}modern-after-hash-{tag}.png")
        # compare picker
        await pg.evaluate("__memeplex.focusIdea('maga')"); await pg.wait_for_timeout(2500)
        await pg.click("#panel [data-act=compare]"); await pg.wait_for_timeout(500)
        print(" picker open:",await pg.evaluate("__cmpPick.el.classList.contains('open')"))
        await pg.fill("#cmppick input","woke"); await pg.wait_for_timeout(300)
        print(" picker results for 'woke':",await pg.evaluate("[...document.querySelectorAll('#cmppick .res button')].map(b=>b.dataset.id)"))
        await pg.screenshot(path=f"{OUT}compare-search-{tag}.png")
        await pg.click("#cmppick .res button"); await pg.wait_for_timeout(1200)
        print(" compare rendered:",await pg.evaluate("document.querySelector('#panel h2').innerText.replace(/\\n/g,' ')"),"picker closed:",not await pg.evaluate("__cmpPick.el.classList.contains('open')"))
        await pg.screenshot(path=f"{OUT}compare-result-{tag}.png")
        # reset
        await pg.evaluate("localStorage.setItem('memele-v1',JSON.stringify({days:{[__memele.today()]:{guesses:['marxism'],hints:['x'],done:true,gaveUp:true},'2026-10-27':{done:true,won:true}},streak:3,best:5,lastWin:'2026-10-27'}));localStorage.setItem('arxgames-v1',JSON.stringify({ladder:{[__memele.today()]:{tries:[[1]],done:true},'2026-10-27':{done:true}}}))")
        await pg.evaluate("__memeplex.closePanel&&__memeplex.closePanel()"); await pg.evaluate("__games.menu()"); await pg.wait_for_timeout(300)
        await pg.click("#games [data-r=today]"); await pg.wait_for_timeout(200); await pg.screenshot(path=f"{OUT}games-reset-confirm-{tag}.png")
        await pg.click("#games [data-r=yes-today]"); await pg.wait_for_timeout(200)
        m=await pg.evaluate("JSON.parse(localStorage.getItem('memele-v1'))"); g=await pg.evaluate("JSON.parse(localStorage.getItem('arxgames-v1'))"); T=await pg.evaluate("__memele.today()")
        print(" reset today ok:", T not in m['days'] and '2026-10-27' in m['days'] and m['streak']==3 and m['best']==5 and g is not None)
        await pg.click("#games [data-r=all]"); await pg.click("#games [data-r=yes-all]"); await pg.wait_for_timeout(200)
        print(" reset all ok:", await pg.evaluate("localStorage.getItem('memele-v1')===null&&localStorage.getItem('arxgames-v1')===null"))
        await pg.evaluate("__games.close()"); await pg.evaluate("__memele.open()"); await pg.wait_for_timeout(300)
        print(" memele replayable:", await pg.evaluate("__memele.day.guesses.length===0&&!__memele.day.done"))
      await ctx.close()
    await b.close()
  srv.terminate(); print("ERRORS",errs)
asyncio.run(run())
