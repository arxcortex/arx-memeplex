# Spread over time + Tradition flows test (desktop + phone). Run from this folder: python3 t_views2.py
import asyncio,subprocess,sys,json
from playwright.async_api import async_playwright
R='../../../'
I=json.load(open(R+'ideas.json')); B={d['id']:d for d in I}
def fam(r):
  s={r}; ch=True
  while ch:
    ch=False
    for d in I:
      if d['id'] not in s and any(p in s for p in d.get('parents',[])): s.add(d['id']); ch=True
  return s
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8789"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); fail=[]; errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for tag,vp,mob in [('desk',dict(width=1440,height=900),False),('phone',dict(width=390,height=844),True)]:
      async def page(url):
        ctx=await b.new_context(viewport=vp,is_mobile=mob,has_touch=mob,device_scale_factor=2 if mob else 1); pg=await ctx.new_page(); pg.on("pageerror",lambda e:errs.append(f"{tag}: {e}"))
        for f in ['ideas.json','thinkers.json','axes.json','currents.json','impact.json','national.json','politics.json']:
          await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
        await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
        await pg.goto("http://localhost:8789/memeplex.html?intro=none"+url); await pg.wait_for_function("window.__viz && window.__views && !__views.busy",timeout=30000,polling=500); await pg.wait_for_timeout(2500)
        return ctx,pg
      ctx,pg=await page('')
      # spread over time from the menu
      await pg.click('#menubtn'); await pg.wait_for_timeout(200); await pg.click('#menu [data-vz=spread]'); await pg.wait_for_timeout(700)
      r=await pg.evaluate("""()=>({streams:[...document.querySelectorAll('#vz path[data-k]')].map(e=>[e.dataset.k,e.dataset.tip]),note:document.querySelector('#vz .vn').textContent,foot:document.querySelector('#vz .vf').textContent})""")
      roots=[d for d in I if d.get('root')]
      if len(r['streams'])!=len(roots): fail.append((tag,'stream count',len(r['streams'])))
      tips=dict(r['streams'])
      for rt in roots:
        want=len(fam(rt['id'])); t=tips.get(rt['id'],'')
        if not t.endswith(f' {want} today'): fail.append((tag,'spread count',rt['id'],want,t))
        w1500=sum(1 for k in fam(rt['id']) if B[k]['year']<=1500)
        if f'{w1500} by 1500' not in t: fail.append((tag,'spread 1500',rt['id'],w1500,t))
      if 'descend' not in r['note'] or 'How it is measured' not in r['foot']: fail.append((tag,'spread note'))
      await pg.screenshot(path=f"views-{tag}-spread.png")
      # alignment measure + pin a stream -> link
      await pg.click('#vz [data-set="m=score"]'); await pg.wait_for_timeout(500)
      t=await pg.evaluate("document.querySelector('#vz path[data-k=platonic_forms]').dataset.tip")
      want=sum(1 for d in I if d['ratings'].get('platonism',0)>=3)
      if not t.endswith(f' {want} today'): fail.append((tag,'score measure',want,t))
      await pg.evaluate("document.querySelector('#vz g[data-k=christianity]').dispatchEvent(new MouseEvent('click',{bubbles:true}))"); await pg.wait_for_timeout(900)
      h=await pg.evaluate("location.hash")
      if 'v=spread' not in h or 'm=score' not in h or 'f=christianity' not in h: fail.append((tag,'spread hash',h))
      await pg.screenshot(path=f"views-{tag}-spread-score.png")
      await pg.evaluate("document.getElementById('themebtn').click()"); await pg.wait_for_timeout(900); await pg.screenshot(path=f"views-{tag}-spread-light.png"); await pg.evaluate("document.getElementById('themebtn').click()"); await pg.wait_for_timeout(500)
      # flows by era: totals add up to the number of ideas, each idea split across its roots
      await pg.click('#menubtn'); await pg.wait_for_timeout(200); await pg.click('#menu [data-vz=flows]'); await pg.wait_for_timeout(700)
      r=await pg.evaluate("""()=>{const t=[...document.querySelectorAll('#vz path[data-s]')].map(e=>+e.dataset.tip.match(/: ([\\d.]+) idea/)[1]);return {n:t.length,sum:t.reduce((a,b)=>a+b,0),targets:[...document.querySelectorAll('#vz g[data-t]')].map(g=>g.getAttribute('aria-label'))}}""")
      print(tag,'flows era',r['n'],round(r['sum'],1),r['targets'])
      if abs(r['sum']-len(I))>0.5*r['n']*0.05+0.6: fail.append((tag,'flows total',r['sum'],len(I)))
      if len(r['targets'])!=7: fail.append((tag,'era targets',r['targets']))
      await pg.screenshot(path=f"views-{tag}-flows-era.png")
      await pg.click('#vz [data-set="by=country"]'); await pg.wait_for_timeout(600)
      r=await pg.evaluate("({t:[...document.querySelectorAll('#vz g[data-t]')].map(g=>g.getAttribute('aria-label')),h:location.hash})")
      print(tag,'flows country',r['t'])
      if len(r['t'])<5: fail.append((tag,'countries',r['t']))
      await pg.wait_for_timeout(500); h=await pg.evaluate("location.hash")
      if 'v=flows' not in h or 'by=country' not in h: fail.append((tag,'flows hash',h))
      await pg.screenshot(path=f"views-{tag}-flows-country.png")
      # hover a tradition highlights its ribbons; click opens its family tree
      if not mob:
        await pg.hover('#vz g[data-k="n:platonic_forms"] rect'); await pg.wait_for_timeout(300)
        on=await pg.evaluate("document.querySelectorAll('#vz path.on[data-s=platonic_forms]').length")
        if not on: fail.append((tag,'flows hover'))
      await pg.evaluate("document.querySelector('#vz g[data-k=\"n:platonic_forms\"]').dispatchEvent(new MouseEvent('click',{bubbles:true}))"); await pg.wait_for_timeout(500)
      if await pg.evaluate("__viz.cur+'/'+__viz.P.f")!='family/platonic_forms': fail.append((tag,'flows click'))
      # snip in flows
      await pg.evaluate("__viz.open('flows',{by:'era'})"); await pg.wait_for_timeout(500)
      await pg.evaluate("document.querySelector('#tb button[data-k=snip]').click()"); await pg.wait_for_timeout(300)
      W,H=vp['width'],vp['height']; await pg.mouse.move(int(W*.05),int(H*.25)); await pg.mouse.down(); await pg.mouse.move(int(W*.5),int(H*.5),steps=4); await pg.mouse.move(int(W*.95),int(H*.8),steps=4); await pg.mouse.up()
      await pg.wait_for_function("window.__snipLast",timeout=15000); await pg.wait_for_timeout(800)
      link=await pg.evaluate("__snipLast.link")
      if 'v=flows' not in link: fail.append((tag,'snip link',link))
      await pg.screenshot(path=f"views-{tag}-flows-snip.png")
      await ctx.close()
      ctx,pg=await page('#v=spread&m=score&f=marxism'); await pg.wait_for_timeout(5500)
      ok=await pg.evaluate("__viz.cur==='spread'&&__viz.P.m==='score'&&__viz.P.f==='marxism'")
      if not ok: fail.append((tag,'spread link restore'))
      await ctx.close()
    await b.close()
  srv.terminate(); print('errors',errs,'FAILS',fail); sys.exit(1 if fail or errs else 0)
asyncio.run(run())
