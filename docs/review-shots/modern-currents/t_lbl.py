import asyncio,subprocess
from playwright.async_api import async_playwright
OUT='/workspace/mc-wt/docs/review-shots/modern-currents/'
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8797"],cwd="/workspace/mc-serve",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); await asyncio.sleep(1); bad=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for which,R in [("before","/workspace/mc-serve/old/"),("after","/workspace/mc-wt/")]:
     for tag,vp,mob in [("desk",dict(width=1440,height=900),False),("mobile",dict(width=390,height=844),True)]:
      ctx=await b.new_context(viewport=vp,is_mobile=mob,has_touch=mob); pg=await ctx.new_page(); pg.on("pageerror",lambda e:bad.append(str(e)))
      async def h(route,request=None,R=R):
        f=route.request.url.split('/')[-1].split('?')[0]; await route.fulfill(status=200,content_type="application/json",body=open(R+f).read(),headers={"Access-Control-Allow-Origin":"*"})
      await pg.route("**/arx-memeplex/*.json",h); await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      await pg.goto(f"http://localhost:8797/{which}/memeplex.html?intro=none{'&full=1' if mob else ''}"); await pg.wait_for_function("window.__memeplex&&window.__views",polling=500,timeout=90000); await pg.wait_for_timeout(4000)
      await pg.evaluate("__memeplex.focusIdea('fascism')"); await pg.wait_for_timeout(3000)
      # labels shown that belong to non-lineage ideas
      r=await pg.evaluate("""(()=>{const I=__memeplex.ideas,B=Object.fromEntries(I.map(d=>[d.id,d]));const up=new Set(),dn=new Set(),go=(id,k,s)=>(k==='p'?(B[id].parents||[]):(B[id].children||[])).forEach(x=>{if(B[x]&&!s.has(x)){s.add(x);go(x,k,s)}});go('fascism','p',up);go('fascism','c',dn);
        const lin=new Set(['fascism',...up,...dn]);const shown=[...document.querySelectorAll('.lbl')].filter(e=>e.offsetParent&&getComputedStyle(e).display!=='none'&&getComputedStyle(e).visibility!=='hidden'&&+getComputedStyle(e).opacity>0.05);
        const names=new Map(I.map(d=>[d.name,d.id]));const ids=shown.map(e=>names.get(e.textContent)).filter(Boolean);return {lin:lin.size,shownIdea:ids.length,outside:ids.filter(i=>!lin.has(i))}})()""")
      print(which,tag,"lineage",r['lin'],"idea labels shown",r['shownIdea'],"outside lineage",len(r['outside']),r['outside'][:5])
      await pg.screenshot(path=f"{OUT}labels-{which}-select-{tag}.png")
      if which=="after":
        if r['outside']: bad.append(tag+" outside labels")
        await pg.keyboard.press("Escape"); await pg.wait_for_timeout(1500)
        n=await pg.evaluate("[...document.querySelectorAll('.lbl')].filter(e=>getComputedStyle(e).display!=='none'&&e.offsetParent).length")
        print(" after deselect labels visible:",n); 
        if n<=r['shownIdea']: bad.append(tag+" not restored")
        await pg.screenshot(path=f"{OUT}labels-after-deselect-{tag}.png")
        # endless games
        r=await pg.evaluate("""(()=>{localStorage.removeItem('arxgames-v1');const out={};
          __games.play('odd');let P=__games.puzzle('odd');__games.choose(P.rounds[0].odd);__games.choose(P.rounds[1].odd);out.s2=__games.stats('odd').streak;
          const w=P.rounds[2].opts.find(x=>x!==P.rounds[2].odd);__games.choose(w);out.s0=__games.stats('odd').streak;out.best=__games.stats('odd').best;
          __games.choose(P.rounds[3].odd);__games.choose(P.rounds[4].odd);out.again=!!document.querySelector('#games [data-a=again]');
          document.querySelector('#games [data-a=again]').click();const P2=__games.puzzle('odd');out.newRound=JSON.stringify(P2.rounds[0])!==JSON.stringify(P.rounds[0]);
          out.persist=JSON.parse(localStorage.getItem('arxgames-v1')).stats.odd.best;out.recent=JSON.parse(localStorage.getItem('arxgames-v1')).stats.odd.recent.length;
          out.sub=document.querySelector('#games .sub').textContent;return out})()""")
        print(" endless:",r); 
        if not (r['s2']==2 and r['s0']==0 and r['best']==2 and r['again'] and r['persist']==2 and r['recent']==5): bad.append(tag+' endless')
        await pg.screenshot(path=f"{OUT}games-endless-{tag}.png")
        await pg.evaluate("__games.menu()"); await pg.wait_for_timeout(300); await pg.screenshot(path=f"{OUT}games-menu-{tag}.png"); await pg.evaluate("__games.close()")
      await ctx.close()
    await b.close()
  srv.terminate(); print("FAILS",bad)
asyncio.run(run())
