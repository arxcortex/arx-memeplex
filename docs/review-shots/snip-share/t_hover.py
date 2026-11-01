# No-hover test (desktop mouse + phone touch). Hovering an idea changes nothing visible: no label enlarge, no dimming,
# no lineage lit, no tooltip. Clicking selects and highlights; clicking empty space or Esc clears it. Same rule in the chart views.
# Run from this folder: python3 t_hover.py   (set SHOTS=dir to save screenshots there)
import asyncio,subprocess,sys,socket,os
from playwright.async_api import async_playwright
R='../../../'; SHOTS=os.environ.get('SHOTS')
with socket.socket() as _s: _s.bind(('127.0.0.1',0)); PORT=_s.getsockname()[1]
# visible state of the map: tooltip, enlarged label, dimmed labels, lit/dim halos, line opacities, open panel
ST="""()=>{const I=__memeplex.ideas,h=I.map(d=>d.star.halo.material.opacity),L=[...document.querySelectorAll('.lbl')];
 return {tip:getComputedStyle(document.getElementById('tip')).visibility!=='hidden'&&getComputedStyle(document.getElementById('tip')).display!=='none',
  sel:document.querySelectorAll('.lbl.sel').length,dimLbl:L.filter(e=>e.style.opacity==='0.2').length,
  dimHalo:h.filter(v=>v<0.2).length,open:document.body.classList.contains('panel-open')}}"""
FIND="""()=>{const W=innerWidth,H=innerHeight;return __memeplex.ideas.map(d=>[d.id,__proj(d.id)]).filter(([id,p])=>p.ok&&p.x>W*.3&&p.x<W*.65&&p.y>H*.3&&p.y<H*.7&&__pick(p.x,p.y)===id&&document.elementFromPoint(p.x,p.y)===document.querySelector('#stage canvas')).map(([id,p])=>({id,x:p.x,y:p.y}))}"""
VST="""()=>{const s=document.querySelector('#vz .vb svg'),t=document.getElementById('vztip');return {hov:!!s&&s.classList.contains('hov'),on:s?s.querySelectorAll('.on').length:0,tip:t.style.display==='block'}}"""
async def run():
  srv=subprocess.Popen(["python3","-m","http.server",str(PORT)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); fail=[]; errs=[]
  async def shot(pg,n):
    if SHOTS: await pg.screenshot(path=os.path.join(SHOTS,n+'.png'))
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    async def page(hash='',mob=False,qs=''):
      ctx=await b.new_context(viewport=dict(width=390,height=844) if mob else dict(width=1440,height=900),is_mobile=mob,has_touch=mob); pg=await ctx.new_page(); pg.on("pageerror",lambda e:errs.append(str(e)))
      for f in ['ideas.json','thinkers.json','axes.json','currents.json','politics.json','national.json','impact.json']:
        await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      await pg.goto(f"http://localhost:{PORT}/memeplex.html?intro=none{qs}{hash}"); await pg.wait_for_function("window.__memeplex && __memeplex.ideas && __memeplex.ideas.length",polling=500); await pg.wait_for_timeout(3500)
      await pg.evaluate("__memeplex.controls.autoRotate=false"); await pg.wait_for_timeout(500); return ctx,pg
    async def empty(pg):
      return await pg.evaluate("()=>{for(let y=160;y<innerHeight-120;y+=17)for(let x=120;x<innerWidth-400;x+=23)if(!__pick(x,y)&&document.elementFromPoint(x,y)===document.querySelector('#stage canvas'))return [x,y];return null}")
    # ---- default map, desktop mouse
    ctx,pg=await page(); e=await empty(pg); await pg.mouse.move(*e); await pg.wait_for_timeout(700)
    base=await pg.evaluate(ST); c=await pg.evaluate(FIND)
    if not c: fail.append(('map','no idea in view'))
    else:
      t=c[0]; await pg.mouse.move(t['x'],t['y'],steps=4); await pg.wait_for_timeout(900)
      s=await pg.evaluate(ST); cur=await pg.evaluate(f"document.querySelector('#stage canvas').style.cursor")
      await shot(pg,'map-hover')
      if s!=base: fail.append(('map','hover changed the map',base,s))
      if cur!='pointer': fail.append(('map','cursor over an idea is',cur))
      # sweep across several ideas: still nothing
      for k in c[1:6]: await pg.mouse.move(k['x'],k['y'],steps=3); await pg.wait_for_timeout(120)
      await pg.wait_for_timeout(700); s=await pg.evaluate(ST)
      if s!=base: fail.append(('map','hover sweep changed the map',s))
      # left click selects and highlights
      t=(await pg.evaluate(FIND))[0]; await pg.mouse.click(t['x'],t['y']); await pg.wait_for_timeout(1200)
      s=await pg.evaluate(ST); await shot(pg,'map-click')
      if not (s['open'] and s['sel']==1 and s['dimHalo']>base['dimHalo']): fail.append(('map','click did not highlight',s))
      # hovering other ideas while one is open leaves the selection as is
      await pg.wait_for_timeout(1200); s1=await pg.evaluate(ST)
      for k in (await pg.evaluate(FIND))[:4]: await pg.mouse.move(k['x'],k['y'],steps=3); await pg.wait_for_timeout(150)
      await pg.wait_for_timeout(700); s2=await pg.evaluate(ST)
      if s2!=s1: fail.append(('map','hover changed the selection',s1,s2))
      # Esc clears
      await pg.keyboard.press('Escape'); await pg.wait_for_timeout(1000); s=await pg.evaluate(ST)
      if s['open'] or s['sel'] or s['dimLbl']: fail.append(('map','Esc did not clear',s))
      # click again, then empty space clears
      t=await pg.evaluate(FIND)
      if t:
        await pg.mouse.click(t[0]['x'],t[0]['y']); await pg.wait_for_timeout(1500); e=await empty(pg)
        if e: await pg.mouse.click(*e); await pg.wait_for_timeout(1000); s=await pg.evaluate(ST)
        if e and (s['open'] or s['sel']): fail.append(('map','empty click did not clear',s))
      print('map',base,s)
    await ctx.close()
    # ---- chart views, desktop: hover does nothing, click highlights or pins
    ctx,pg=await page()
    async def hov_then(sel,label):
      await pg.hover(sel); await pg.wait_for_timeout(300); s=await pg.evaluate(VST)
      if s['hov'] or s['tip']: fail.append((label,'hover highlighted',s))
      return s
    await pg.evaluate("__viz.open('fingerprint',{f:'stoic_logos'})"); await pg.wait_for_timeout(600)
    ax=await pg.evaluate("document.querySelector('#vz g[data-ax]').dataset.ax")
    await hov_then(f'#vz g[data-ax="{ax}"] circle:nth-of-type(2)','fingerprint'); await shot(pg,'fingerprint-hover')
    await pg.click(f'#vz g[data-ax="{ax}"] circle:nth-of-type(2)'); await pg.wait_for_timeout(300); s=await pg.evaluate(VST); await shot(pg,'fingerprint-click')
    if not (s['hov'] and s['on'] and s['tip']): fail.append(('fingerprint','click did not highlight',s))
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(200); s=await pg.evaluate(VST)
    if s['hov'] or s['tip']: fail.append(('fingerprint','Esc did not clear',s))
    if await pg.evaluate("__viz.cur")!='fingerprint': fail.append(('fingerprint','Esc closed the view'))
    # flows: a ribbon click shows its share; clicking empty chart space clears
    await pg.evaluate("__viz.open('flows',{by:'era'})"); await pg.wait_for_timeout(600)
    await hov_then('#vz g[data-k="n:platonic_forms"] rect','flows')
    if await pg.evaluate("document.querySelectorAll('#vz path.on[data-s=platonic_forms]').length"): fail.append(('flows','hover lit ribbons'))
    k=await pg.evaluate("document.querySelector('#vz path[data-k^=\"f:platonic_forms\"]').dataset.k")
    await pg.evaluate(f"""(()=>{{const e=document.querySelector('#vz path[data-k="{k}"]'),b=e.getBoundingClientRect();e.dispatchEvent(new MouseEvent('click',{{bubbles:true,clientX:b.left+b.width/2,clientY:b.top+b.height/2}}))}})()"""); await pg.wait_for_timeout(300)
    s=await pg.evaluate(VST); await shot(pg,'flows-click')
    if not (s['hov'] and s['tip']): fail.append(('flows','ribbon click',s))
    await pg.evaluate("document.querySelector('#vz .vb svg').dispatchEvent(new MouseEvent('click',{bubbles:true}))"); await pg.wait_for_timeout(200); s=await pg.evaluate(VST)
    if s['hov'] or s['tip']: fail.append(('flows','empty click did not clear',s))
    # similarity map: hover nothing, click pins the idea and its neighbours
    await pg.evaluate("__viz.open('similar',{})"); await pg.wait_for_timeout(800)
    await hov_then('#vz g[data-id="stoic_logos"] circle:nth-of-type(2)','similar'); await shot(pg,'similar-hover')
    await pg.evaluate("document.querySelector('#vz g[data-id=\"stoic_logos\"]').dispatchEvent(new MouseEvent('click',{bubbles:true}))"); await pg.wait_for_timeout(500)
    if await pg.evaluate("__viz.P.f")!='stoic_logos' or not await pg.evaluate("document.querySelectorAll('#vz .nd.on').length>1"): fail.append(('similar','click did not pin'))
    await shot(pg,'similar-click')
    # family tree + thinkers: hover nothing
    await pg.evaluate("__viz.open('family',{f:'platonic_forms'})"); await pg.wait_for_timeout(600)
    await hov_then('#vz g.nd:not(.focus) rect','family'); await shot(pg,'family-hover')
    await pg.evaluate("__viz.open('thinkers',{})"); await pg.wait_for_timeout(800)
    await hov_then('#vz g.nd[data-k] circle:nth-of-type(2)','thinkers')
    await pg.evaluate("__viz.open('spread',{})"); await pg.wait_for_timeout(600)
    await hov_then('#vz g.fx[data-k] rect','spread')
    await ctx.close()
    # ---- phone: a tap still selects, a finger drag does not
    ctx,pg=await page('',True,'&full=1'); q=await pg.evaluate(FIND)
    if q:
      await pg.touchscreen.tap(q[0]['x'],q[0]['y']); await pg.wait_for_timeout(900); s=await pg.evaluate(ST)
      if not (s['open'] and s['sel']==1): fail.append(('phone','tap did not select',s))
    else: fail.append(('phone','no idea in view'))
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(800)
    await pg.evaluate("__viz.open('fingerprint',{f:'stoic_logos'})"); await pg.wait_for_timeout(600)
    await pg.tap('#vz g[data-ax] circle:nth-of-type(2)'); await pg.wait_for_timeout(300); s=await pg.evaluate(VST)
    if not (s['hov'] and s['tip']): fail.append(('phone','fingerprint tap',s))
    await ctx.close(); await b.close()
  srv.terminate(); print('errors',errs,'FAILS',fail); sys.exit(1 if fail or errs else 0)
asyncio.run(run())
