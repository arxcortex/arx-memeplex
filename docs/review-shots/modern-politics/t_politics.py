# Modern politics view test (desktop + phone). Run from this folder: python3 t_politics.py
import asyncio,subprocess,sys,json
from playwright.async_api import async_playwright
R='../../../'; PAGE='../snip-share/'
def rgb(h): h=h.lstrip('#'); return [int(h[i:i+2],16)/255 for i in (0,2,4)]
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8813"],cwd=PAGE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); fail=[]; errs=[]; res={}
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for tag,vp,mob in [('desk',dict(width=1440,height=900),False),('phone',dict(width=390,height=844),True)]:
      ctx=await b.new_context(viewport=vp,is_mobile=mob,has_touch=mob,device_scale_factor=2 if mob else 1); pg=await ctx.new_page()
      pg.on("pageerror",lambda e,t=tag:errs.append(f"{t}: {e}")); pg.on("console",lambda m,t=tag:m.type=='error' and errs.append(f"{t} console: {m.text}"))
      for f in ['ideas.json','thinkers.json','axes.json','currents.json','politics.json']:
        await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      await pg.goto("http://localhost:8813/memeplex.html?intro=none#v=politics"); await pg.wait_for_function("window.__pol && __pol.on",timeout=60000); await pg.wait_for_timeout(3000)
      r=await pg.evaluate("""()=>{const m=__pol.mix,c=id=>'#'+__memeplex.ideas.find(d=>d.id===id).star.core.material.color.getHexString();
        const anc=Object.entries(m).filter(([k,v])=>v.kind==='ancestor'&&v.t>0.25&&v.t<0.75).sort((a,b)=>(b[1].a+b[1].b)-(a[1].a+a[1].b)).map(([k,v])=>({id:k,t:v.t}));
        const key=document.getElementById('polkey');
        return {maga:m.maga, nd:m.new_democrats, neo:m.neoconservatism, cols:{maga:c('maga'),new_democrats:c('new_democrats'),neoconservatism:c('neoconservatism')},
          anc:anc.slice(0,5), ancCol:anc[0]&&c(anc[0].id), keyShown:getComputedStyle(key).display!=='none'&&key.getBoundingClientRect().height>40,
          keyRows:[...key.querySelectorAll('.row[data-party]')].map(e=>e.dataset.party), facs:key.querySelectorAll('.fl button').length,
          country:[...key.querySelectorAll('select option')].map(o=>o.textContent), hash:location.hash, none:Object.values(m).filter(v=>v.kind==='none').length}}""")
      res[tag]=r; print(tag,json.dumps(r,default=str)[:900])
      def near(h,ref,tol=.12): return max(abs(a-b) for a,b in zip(rgb(h),rgb(ref)))<=tol
      if r['maga']['party']!='R' or not near(r['cols']['maga'],'#d62828'): fail.append((tag,'maga not red',r['cols']['maga']))
      if r['nd']['party']!='D' or not near(r['cols']['new_democrats'],'#1d4ed8'): fail.append((tag,'new_democrats not blue',r['cols']['new_democrats']))
      if r['neo']['party']!='mixed' or not near(r['cols']['neoconservatism'],'#7b3fb0',.15): fail.append((tag,'neocon not purple',r['cols']['neoconservatism']))
      if not r['anc']: fail.append((tag,'no blended shared ancestor'))
      else:
        R_,G_,B_=rgb(r['ancCol'])
        if not (R_>0.15 and B_>0.15): fail.append((tag,'ancestor colour not a blend',r['ancCol']))
      if not r['keyShown'] or set(r['keyRows'])!={'R','D','mixed'} or r['facs']<10 or r['country'][0]!='United States': fail.append((tag,'key',r))
      if 'v=politics' not in r['hash']: fail.append((tag,'url state',r['hash']))
      if r['none']<50: fail.append((tag,'unrelated not dimmed'))
      await pg.screenshot(path=f"politics-{tag}-view.png")
      # panel note + source
      await pg.evaluate("__memeplex.controls.autoRotate=false; __memeplex.focusIdea('neoconservatism')"); await pg.wait_for_timeout(2500)
      pb=await pg.evaluate("(()=>{const b=document.querySelector('#panel .polbox');return b?{t:b.textContent,a:(b.querySelector('a')||{}).href}:null})()")
      if not pb or 'Split' not in pb['t'] or 'grokipedia.com/page/Neoconservatism' not in (pb['a'] or ''): fail.append((tag,'panel',pb))
      await pg.screenshot(path=f"politics-{tag}-panel.png")
      # other views and snip still work; leaving the view restores normal colours
      await pg.evaluate("__views.set('helix',{instant:true})"); await pg.wait_for_timeout(1200)
      off=await pg.evaluate("({on:__pol.on,key:getComputedStyle(document.getElementById('polkey')).display,maga:'#'+__memeplex.ideas.find(d=>d.id==='maga').star.core.material.color.getHexString()})")
      if off['on'] or off['key']!='none' or near(off['maga'],'#d62828'): fail.append((tag,'leave view',off))
      await pg.evaluate("__views.set('politics',{instant:true})"); await pg.wait_for_timeout(1200)
      if not mob:
        await pg.evaluate("document.querySelector('#panel .close') && document.querySelector('#panel .close').click()"); await pg.wait_for_timeout(600)
        await pg.keyboard.press('s'); await pg.wait_for_timeout(300)
        await pg.mouse.move(300,200); await pg.mouse.down(); await pg.mouse.move(900,600,steps=6); await pg.mouse.up()
        await pg.wait_for_function("window.__snipLast",timeout=10000); link=await pg.evaluate("__snipLast.link")
        print(tag,'snip link',link)
        if 'v=politics' not in link: fail.append((tag,'snip link',link))
        await pg.screenshot(path=f"politics-{tag}-snip.png")
      await ctx.close()
    await b.close()
  srv.terminate(); json.dump({'results':res,'errors':errs,'fails':[str(x) for x in fail]},open('results.json','w'),indent=1,default=str)
  print('errors',errs,'FAILS',fail); sys.exit(1 if fail or errs else 0)
asyncio.run(run())
