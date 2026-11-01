# Map state test (desktop): no stray text selection after using the menu, views, filters, games and the quiz;
# no hidden overlay left over the map; a filtered map keeps the kept ideas' ancestors up to their root, faded.
# Run from this folder: python3 t_mapstate.py   (set SHOTS=dir to save screenshots there)
import asyncio,subprocess,sys,socket,os,json
from playwright.async_api import async_playwright
R='../../../'; SHOTS=os.environ.get('SHOTS')
with socket.socket() as _s: _s.bind(('127.0.0.1',0)); PORT=_s.getsockname()[1]
I={d['id']:d for d in json.load(open(R+'ideas.json'))}
async def run():
  srv=subprocess.Popen(["python3","-m","http.server",str(PORT)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); fail=[]; errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    ctx=await b.new_context(viewport=dict(width=1440,height=900)); pg=await ctx.new_page(); pg.on("pageerror",lambda e:errs.append(str(e)))
    for f in ['ideas.json','thinkers.json','axes.json','currents.json','politics.json','national.json','impact.json']:
      await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
    await pg.route("**/arx-memeplex/quiz/quiz-bank.json",lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+'quiz/quiz-bank.json').read()))
    await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
    await pg.goto(f"http://localhost:{PORT}/memeplex.html?intro=none"); await pg.wait_for_function("window.__viz && window.__views && !__views.busy && window.__quiz",timeout=30000); await pg.wait_for_timeout(3000)
    await pg.evaluate("__memeplex.controls.autoRotate=false")
    SEL="()=>String(getSelection())"
    async def gestures(tag,pts):
      for x,y in pts:
        await pg.mouse.dblclick(x,y); await pg.wait_for_timeout(120); s=await pg.evaluate(SEL)
        if s: fail.append((tag,'double-click selected',x,y,s[:60]))
        await pg.mouse.click(x,y,click_count=3); await pg.wait_for_timeout(120); s=await pg.evaluate(SEL)
        if s: fail.append((tag,'triple-click selected',x,y,s[:60]))
        await pg.mouse.move(x,y); await pg.mouse.down(); await pg.mouse.move(x+260,y+140,steps=8); await pg.mouse.move(x-200,y-300,steps=8); await pg.mouse.up(); await pg.wait_for_timeout(120); s=await pg.evaluate(SEL)
        if s: fail.append((tag,'drag selected',x,y,s[:60]))
        await pg.evaluate("getSelection().removeAllRanges()"); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
    PTS=[(700,450),(400,640),(1000,300),(250,140)]
    # the reported session: menu, a chart view, filters, a game, the quiz, then back on the map
    await pg.click('#menubtn'); await pg.wait_for_timeout(250); await pg.click('#menu [data-vz=family]'); await pg.wait_for_timeout(1500)
    await gestures('chart view',[(700,300),(500,500),(900,420)])
    await pg.click('#menubtn'); await pg.wait_for_timeout(250); await pg.click('#menu [data-vz=""]'); await pg.wait_for_timeout(1500)
    await pg.click('#tb [data-k=filter]'); await pg.wait_for_timeout(400); await pg.click('#filt .chip[data-root="br:catholic"]'); await pg.wait_for_timeout(500); await pg.click('#filt .chip[data-root="br:catholic"]'); await pg.wait_for_timeout(400); await pg.click('#tb [data-k=filter]'); await pg.wait_for_timeout(400)
    await pg.click('#menubtn'); await pg.wait_for_timeout(250); await pg.click('#menu [data-k=games]'); await pg.wait_for_timeout(600); await pg.click('#games .x'); await pg.wait_for_timeout(300)
    await pg.click('#menubtn'); await pg.wait_for_timeout(250); await pg.click('#menu [data-k=quiz]'); await pg.wait_for_selector('#quiz [data-q]'); await pg.click('#quiz [data-q=politics][data-m=short]')
    await pg.evaluate("(()=>{const r=document.createRange();r.selectNodeContents(document.querySelector('#quiz .qz-st'));getSelection().addRange(r)})()")
    if not await pg.evaluate(SEL): fail.append(('quiz','question text should stay selectable'))
    await pg.click('#quiz .x'); await pg.wait_for_timeout(300)
    if await pg.evaluate(SEL): fail.append(('quiz','selection left after closing the quiz'))
    await pg.click('#menubtn'); await pg.wait_for_timeout(250); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
    # nothing invisible left over the map
    cover=await pg.evaluate("""()=>{const out=[];for(let y=200;y<innerHeight-120;y+=70)for(let x=100;x<innerWidth-120;x+=90){const e=document.elementFromPoint(x,y);
      if(e&&e!==document.querySelector('#stage canvas')){const c=getComputedStyle(e);out.push([x,y,e.id||e.className||e.tagName,c.opacity,c.visibility])}}return out}""")
    hidden=[c for c in cover if c[3]=='0' or c[4]=='hidden']
    if hidden: fail.append(('cover','invisible element over the map',hidden[:5]))
    print('non-canvas points over the map:',len(cover),cover[:4])
    await gestures('map',PTS)
    # an idea panel stays selectable text
    await pg.evaluate("__memeplex.focusIdea('platonic_forms')"); await pg.wait_for_timeout(2000)
    q=await pg.evaluate("(()=>{const f=document.querySelector('#panel .pq');if(!f)return null;const r=document.createRange();r.selectNodeContents(f.querySelector('blockquote'));getSelection().removeAllRanges();getSelection().addRange(r);return [String(getSelection()),f.textContent]})()")
    if not q or 'footnotes to Plato' not in q[0] or 'Whitehead' not in q[1]: fail.append(('panel','quote not shown or not selectable',q))
    if SHOTS: await pg.screenshot(path=os.path.join(SHOTS,'panel-quote-platonic-forms.png'))
    await pg.evaluate("getSelection().removeAllRanges()"); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(800)
    # filter context: Catholic line keeps Christianity (its root), faded; one other filter
    for key,expect in [('br:catholic',{'christianity','apostolic_christianity'}),('br:protestant',None),('br:socialism',None)]:
      await pg.evaluate(f"__memeplex.clearFilter(); __memeplex.filt.sel.add('{key}'); __memeplex.applyFilter()"); await pg.wait_for_timeout(900)
      r=await pg.evaluate("""()=>{const F=__filter,I=__memeplex.ideas,keep=I.filter(d=>d.star.core.material.opacity>0.9).map(d=>d.id),ctx=F.context;
        const op=Object.fromEntries(I.map(d=>[d.id,+d.star.core.material.opacity.toFixed(2)]));return {keep,ctx,op,count:document.querySelector('#filt .cnt, #filtcount')?.textContent||''}}""")
      if r['ctx'] and not any(I[k].get('root') for k in r['ctx']): fail.append((key,'no root in the context'))
      if len(r['ctx'])>12: fail.append((key,'context too large',len(r['ctx'])))
      if expect and not expect<=set(r['ctx']): fail.append((key,'expected context',expect-set(r['ctx'])))
      bad=[k for k in r['ctx'] if not (0.3<r['op'][k]<0.9)]
      if bad: fail.append((key,'context ideas not drawn faded',bad[:5]))
      if any(I[k].get('root') is not True and not any(p in r['ctx'] or p in r['keep'] for p in [c for c in I if k in I[c].get('parents',[])]) for k in r['ctx']): fail.append((key,'context idea not on a path from a kept idea'))
      print(key,'kept',len(r['keep']),'context',sorted(r['ctx']))
      if key=='br:catholic':
        if r['op'].get('christianity',0)<0.3: fail.append((key,'christianity not visible'))
        if SHOTS: await pg.evaluate("__memeplex.frameBranch(new Set(__filter.context.concat(__memeplex.ideas.filter(d=>d.star.core.material.opacity>0.9).map(d=>d.id))))"); await pg.wait_for_timeout(1800); await pg.screenshot(path=os.path.join(SHOTS,'filter-catholic-with-root.png'))
    await pg.evaluate("__memeplex.clearFilter()"); await pg.wait_for_timeout(500)
    if await pg.evaluate("__filter.context.length"): fail.append(('filter','context left after clearing'))
    await b.close()
  srv.terminate(); print('errors',errs,'FAILS',fail); sys.exit(1 if fail or errs else 0)
asyncio.run(run())
