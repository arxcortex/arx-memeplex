# Drag-over-labels test (desktop mouse, left and right button, default + National views; phone touch).
# Passing over ideas (button held or not) must not enlarge labels, dim the map or show the tooltip; there is no hover effect,
# only a pointer cursor. A drag is never a click; a left click that moves less than 6 px selects.
# Run from this folder: python3 t_drag.py
import asyncio,subprocess,sys,socket
from playwright.async_api import async_playwright
R='../../../'
with socket.socket() as _s: _s.bind(('127.0.0.1',0)); PORT=_s.getsockname()[1]  # a free port, so a stale server can't serve an old page
ST="""()=>({tip:getComputedStyle(document.getElementById('tip')).visibility!=='hidden',sel:document.querySelectorAll('.lbl.sel').length,open:document.body.classList.contains('panel-open')})"""
FIND="""()=>{const W=innerWidth,H=innerHeight;return __memeplex.ideas.map(d=>[d.id,__proj(d.id)]).filter(([id,p])=>p.ok&&p.x>W*.3&&p.x<W*.7&&p.y>H*.3&&p.y<H*.7&&__pick(p.x,p.y)===id&&document.elementFromPoint(p.x,p.y)===document.querySelector('#stage canvas')).map(([id,p])=>({id,x:p.x,y:p.y}))}"""
async def run():
  srv=subprocess.Popen(["python3","-m","http.server",str(PORT)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); fail=[]; errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    async def page(hash='',mob=False,qs=''):
      ctx=await b.new_context(viewport=dict(width=390,height=844) if mob else dict(width=1440,height=900),is_mobile=mob,has_touch=mob); pg=await ctx.new_page(); pg.on("pageerror",lambda e:errs.append(str(e)))
      for f in ['ideas.json','thinkers.json','axes.json','currents.json','politics.json','national.json','impact.json']:
        await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      await pg.goto(f"http://localhost:{PORT}/memeplex.html?intro=none{qs}{hash}"); await pg.wait_for_function("window.__memeplex && __memeplex.ideas && __memeplex.ideas.length",polling=500); await pg.wait_for_timeout(3500)
      await pg.evaluate("__memeplex.controls.autoRotate=false"); await pg.wait_for_timeout(500); return ctx,pg
    async def empty(pg):  # a spot with no idea under it
      return await pg.evaluate("()=>{for(let y=120;y<innerHeight-80;y+=17)for(let x=80;x<innerWidth-300;x+=23)if(!__pick(x,y)&&document.elementFromPoint(x,y)===document.querySelector('#stage canvas'))return [x,y];return null}")
    hits=0
    for view,hash in [('default',''),('national-politics','#v=national'),('national-religion','#v=national&ns=religion')]:
      for btn in ['left','right']:
        tag=f'{view}/{btn}'; ctx,pg=await page(hash)
        c=await pg.evaluate(FIND)
        if not c: fail.append((tag,'no idea in view')); await ctx.close(); continue
        t=c[0]
        # plain hover: pointer cursor, nothing else
        await pg.mouse.move(t['x'],t['y']); await pg.wait_for_timeout(250); s=await pg.evaluate(ST)
        if s['tip'] or s['sel'] or s['open']: fail.append((tag,'plain hover lit the idea',s))
        cur=await pg.evaluate("document.querySelector('#stage canvas').style.cursor")
        if cur!='pointer': fail.append((tag,'cursor over an idea',cur))
        e=await empty(pg); await pg.mouse.move(*e); await pg.wait_for_timeout(150)
        await pg.mouse.down(button=btn); over=0; bad=[]
        # sweep across every candidate idea while held
        for k in c[:8]:
          for i in range(1,9):
            q=await pg.evaluate(f"__proj('{k['id']}')"); x=e[0]+(q['x']-e[0])*i/8; y=e[1]+(q['y']-e[1])*i/8
            await pg.mouse.move(x,y)
            if await pg.evaluate(f"__pick({x},{y})"): over+=1
            s=await pg.evaluate(ST)
            if s['tip'] or s['sel'] or s['open']: bad.append((round(x),round(y),s))
          e=[x,y]
        if not over: fail.append((tag,'drag never passed over an idea'))
        if bad: fail.append((tag,'hover effects during drag',bad[:3]))
        # release on top of an idea: no click, no hover effect, the pointer cursor comes back
        await pg.evaluate("__memeplex.controls.enableDamping=false; __memeplex.controls.enabled=false"); await pg.wait_for_timeout(100)  # freeze the map (button still held) so the release can land on a known idea
        q=await pg.evaluate(FIND)
        if q: await pg.mouse.move(q[0]['x'],q[0]['y'],steps=3)
        s=await pg.evaluate(ST)
        if q and (s['tip'] or s['sel']): fail.append((tag,'hover while held on an idea',s))
        mx,my=(q[0]['x'],q[0]['y']) if q else e
        await pg.mouse.up(button=btn); await pg.wait_for_timeout(300); s=await pg.evaluate(ST)
        if s['open']: fail.append((tag,'drag opened an idea'))
        under=await pg.evaluate(f"__pick({mx},{my})")  # the cursor is re-checked on release
        cur=await pg.evaluate("document.querySelector('#stage canvas').style.cursor")
        if s['tip'] or s['sel']: fail.append((tag,'hover effect after release',under,s))
        if (cur=='pointer')!=bool(under): fail.append((tag,'cursor not re-checked after release',under,cur))
        if under: hits+=1
        await pg.evaluate("__memeplex.controls.enabled=true")
        # drag that comes back to where it started is still a drag
        q=await pg.evaluate(FIND)
        if q:
          x,y=q[0]['x'],q[0]['y']; await pg.mouse.move(x,y); await pg.mouse.down(button=btn); await pg.mouse.move(x+80,y+40,steps=4); await pg.mouse.move(x,y,steps=4); await pg.mouse.up(button=btn); await pg.wait_for_timeout(300)
          if (await pg.evaluate(ST))['open']: fail.append((tag,'out-and-back drag opened an idea'))
        # a plain click: left opens, right does not
        q=await pg.evaluate(FIND)
        if q:
          await pg.mouse.click(q[0]['x'],q[0]['y'],button=btn); await pg.wait_for_timeout(400); o=(await pg.evaluate(ST))['open']
          if o!=(btn=='left'): fail.append((tag,'click open =',o))
        print(tag,'passes over ideas',over,'bad',len(bad))
        await ctx.close()
    if not hits: fail.append(('mouse','no release ever landed on an idea, so the cursor re-check went untested'))
    # touch: a finger drag over ideas never opens one; a tap does
    ctx,pg=await page('',True,'&full=1'); cdp=await ctx.new_cdp_session(pg)  # full=1: the explorable map on a touch phone
    q=await pg.evaluate(FIND)
    if q:
      x,y=q[0]['x'],q[0]['y']; tp=lambda t,x,y:cdp.send('Input.dispatchTouchEvent',{'type':t,'touchPoints':[] if t=='touchEnd' else [{'x':x,'y':y}]})
      await tp('touchStart',x,y)
      for i in range(1,7): await tp('touchMove',x+i*15,y+i*10); await pg.wait_for_timeout(16)
      for i in range(5,-1,-1): await tp('touchMove',x+i*15,y+i*10); await pg.wait_for_timeout(16)
      await tp('touchEnd',x,y); await pg.wait_for_timeout(400); s=await pg.evaluate(ST)
      if s['open'] or s['tip']: fail.append(('touch','drag opened/hovered',s))
      q=await pg.evaluate(FIND)
      if q: await pg.touchscreen.tap(q[0]['x'],q[0]['y']); await pg.wait_for_timeout(600)
      if q and not (await pg.evaluate(ST))['open']: fail.append(('touch','tap did not open'))
      print('touch ok' if not [f for f in fail if f[0]=='touch'] else 'touch FAIL')
    else: fail.append(('touch','no idea in view'))
    await ctx.close(); await b.close()
  srv.terminate(); print('errors',errs,'FAILS',fail); sys.exit(1 if fail or errs else 0)
asyncio.run(run())
