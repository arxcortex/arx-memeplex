# Share card stacking test (desktop + phone). Run from this folder: python3 t_sharecard.py   (set SHOTS=dir to save screenshots there)
# The share card preview (#sharecard, from assets/sharecard.js) must open on top of everything: the quiz overlay, the menu,
# the info panel and the toolbar. Checked with document.elementFromPoint at the card's centre, its corners and its buttons,
# for the quiz card, the idea card from the info panel, and the Snip & share card (#snipmod). No page or console errors.
import asyncio,subprocess,sys,socket,os,json
from playwright.async_api import async_playwright
R='../../../'; SHOTS=os.environ.get('SHOTS')
with socket.socket() as _s: _s.bind(('127.0.0.1',0)); PORT=_s.getsockname()[1]
# topmost check: every probe point lands inside the modal; also no visible positioned element outranks it in the body stack
TOP="""sel=>{const m=document.querySelector(sel); if(!m||getComputedStyle(m).display==='none') return {err:'not open'};
  const im=m.querySelector('img'), r=im.getBoundingClientRect(), pts=[[r.left+r.width/2,r.top+r.height/2],[r.left+6,r.top+6],[r.right-6,r.top+6],[r.left+6,r.bottom-6],[r.right-6,r.bottom-6]];
  m.querySelectorAll('button,a').forEach(b=>{const q=b.getBoundingClientRect(); if(q.width&&q.height) pts.push([q.left+q.width/2,q.top+q.height/2]);});
  const miss=pts.filter(([x,y])=>{const e=document.elementFromPoint(x,y); return !e||!m.contains(e);}).map(([x,y])=>{const e=document.elementFromPoint(x,y);return [Math.round(x),Math.round(y),e?(e.id||e.className||e.tagName):null]});
  const zi=e=>{const z=parseInt(getComputedStyle(e).zIndex);return isNaN(z)?0:z}, mz=zi(m);
  const over=[...document.body.children].filter(e=>e!==m&&getComputedStyle(e).position!=='static'&&getComputedStyle(e).display!=='none'&&getComputedStyle(e).visibility!=='hidden'&&zi(e)>=mz&&!(zi(e)===mz&&(m.compareDocumentPosition(e)&Node.DOCUMENT_POSITION_PRECEDING))).map(e=>(e.id||e.className)+':'+zi(e));
  return {miss,over,parent:m.parentElement===document.body,z:mz,centre:pts[0].map(Math.round)}}"""
async def run():
  srv=subprocess.Popen(["python3","-m","http.server",str(PORT)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); fail=[]; errs=[]
  async def shot(pg,n):
    if SHOTS: await pg.screenshot(path=os.path.join(SHOTS,n+'.png'))
  def check(tag,what,t):
    print(tag,what,json.dumps(t))
    if t.get('err') or t['miss'] or t['over'] or not t['parent']: fail.append((tag,what,t))
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for tag,mob in (('desk',False),('phone',True)):
      ctx=await b.new_context(viewport=dict(width=390,height=844) if mob else dict(width=1440,height=900),is_mobile=mob,has_touch=mob,device_scale_factor=2 if mob else 1); pg=await ctx.new_page()
      pg.on("pageerror",lambda e,tag=tag:errs.append(f"{tag}: {e}"))
      pg.on("console",lambda m,tag=tag:errs.append(f"{tag} console: {m.text}") if m.type=='error' and 'Failed to load resource' not in m.text else None)
      for f in ['ideas.json','thinkers.json','axes.json','currents.json','politics.json','national.json','impact.json','quiz/quiz-bank.json']:
        await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      await pg.goto(f"http://localhost:{PORT}/memeplex.html?intro=none{'&full=1' if mob else ''}"); await pg.wait_for_function("window.__quiz && window.__memeplex && __memeplex.ideas.length",polling=500,timeout=30000); await pg.wait_for_timeout(3000)
      await pg.evaluate("__memeplex.controls.autoRotate=false")
      # 1. quiz: Menu > Quizzes > Politics short, answer every question, Share card
      await pg.click('#menubtn'); await pg.wait_for_timeout(300); await pg.click('#menu [data-k=quiz]')
      mode='short' if len(json.load(open(R+'quiz/quiz-bank.json'))['quizzes']['politics'])>50 else 'full'
      await pg.wait_for_selector(f'#quiz [data-q=politics][data-m={mode}]',timeout=15000); await pg.click(f'#quiz [data-q=politics][data-m={mode}]')
      n=len(await pg.evaluate("__quiz.state.list"))
      for j in range(n): await pg.click(f'#quiz .qz-ans button[data-v="{[2,1,-1,-2,0][j%5]}"]'); await pg.wait_for_timeout(20)
      await pg.wait_for_selector('#quiz .qz-plane svg',timeout=10000)
      await pg.evaluate("document.querySelector('#quiz [data-a=card]').scrollIntoView()"); await pg.click('#quiz [data-a=card]')
      await pg.wait_for_function("document.getElementById('sharecard')&&getComputedStyle(document.getElementById('sharecard')).display!=='none'&&document.querySelector('#sharecard img').naturalWidth>0",timeout=15000); await pg.wait_for_timeout(300)
      check(tag,'quiz card over quiz overlay',await pg.evaluate(TOP,'#sharecard')); await shot(pg,f'sharecard-{tag}-quiz')
      await pg.keyboard.press('Escape'); await pg.wait_for_timeout(200)
      if not await pg.evaluate("__quiz.open"): fail.append((tag,'Escape on the card closed the quiz too'))
      # 2. a card with the menu, the info panel, the quiz overlay and the toolbar all open underneath
      await pg.keyboard.press('Escape'); await pg.wait_for_timeout(200)
      await pg.evaluate("__memeplex.focusIdea('stoic_logos')"); await pg.wait_for_timeout(1500)
      await pg.evaluate("__quiz.loadBank().then(()=>__quiz.menu())"); await pg.wait_for_selector('#quiz [data-q=politics]',timeout=15000)
      await pg.evaluate("document.getElementById('menu').classList.add('open')"); await pg.wait_for_timeout(200)
      under=await pg.evaluate("({menu:getComputedStyle(document.getElementById('menu')).display,quiz:__quiz.open,panel:getComputedStyle(document.getElementById('panel')).visibility,tb:getComputedStyle(document.getElementById('tb')).display})")
      print(tag,'open underneath',under)
      if under['menu']=='none' or not under['quiz']: fail.append((tag,'could not open the layers underneath',under))
      await pg.evaluate("(async()=>{const c=document.createElement('canvas');c.width=1080;c.height=1920;c.getContext('2d').fillRect(0,0,9,9);const bl=await new Promise(r=>c.toBlob(r));ArxShareCard.open(bl,'t.png')})()")
      await pg.wait_for_function("document.querySelector('#sharecard img').complete&&document.querySelector('#sharecard img').naturalWidth>0"); await pg.wait_for_timeout(300)
      check(tag,'card over menu+quiz+panel+toolbar',await pg.evaluate(TOP,'#sharecard')); await shot(pg,f'sharecard-{tag}-all-layers')
      await pg.click('#sharecard .sc-x'); await pg.wait_for_timeout(200)
      await pg.evaluate("document.getElementById('menu').classList.remove('open')")
      if await pg.evaluate("__quiz.open"): await pg.evaluate("__quiz.close()"); await pg.wait_for_timeout(200)
      # 3. idea card from the info panel
      await pg.evaluate("__memeplex.focusIdea('stoic_logos')"); await pg.wait_for_timeout(1500)
      await pg.evaluate("document.querySelector('#panel [data-act=card]').click()")
      await pg.wait_for_function("getComputedStyle(document.getElementById('sharecard')).display!=='none'&&document.querySelector('#sharecard img').naturalWidth>0",timeout=15000); await pg.wait_for_timeout(300)
      check(tag,'idea card over info panel',await pg.evaluate(TOP,'#sharecard')); await shot(pg,f'sharecard-{tag}-idea')
      await pg.click('#sharecard .sc-x'); await pg.wait_for_timeout(200)
      # 4. Snip & share card
      if mob: await pg.evaluate("document.querySelector('#panel .close') && document.querySelector('#panel .close').click()"); await pg.wait_for_timeout(300)
      await pg.evaluate("__memeplex.controls.autoRotate=false; document.querySelector('#tb button[data-k=snip]').click()"); await pg.wait_for_timeout(300)
      W,H=(390,844) if mob else (1440,900); x0,y0,x1,y1=int(W*.15),int(H*.2),int(W*.8),int(H*.6)
      await pg.mouse.move(x0,y0); await pg.mouse.down(); await pg.mouse.move((x0+x1)//2,(y0+y1)//2,steps=4); await pg.mouse.move(x1,y1,steps=4); await pg.mouse.up()
      await pg.wait_for_function("window.__snipLast",timeout=10000); await pg.wait_for_timeout(800)
      check(tag,'snip card',await pg.evaluate(TOP,'#snipmod')); await shot(pg,f'sharecard-{tag}-snip')
      await ctx.close()
    await b.close()
  srv.terminate(); print('errors',errs,'FAILS',fail); sys.exit(1 if fail or errs else 0)
asyncio.run(run())
