import asyncio,subprocess,json,sys,os
MODE=os.environ.get('MODE','http')
URL='http://127.0.0.1:8765/memeplex.html?intro=none' if MODE=='http' else 'file://'+os.path.abspath('../snip-share/memeplex.html')+'?intro=none'
P='' if MODE=='http' else 'file-'
from playwright.async_api import async_playwright
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8765","--bind","127.0.0.1"],cwd='../snip-share',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); errs=[]; out={}
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for tag,vp,mob in [('desk',dict(width=1440,height=900),False),('phone',dict(width=390,height=844),True)]:
      ctx=await b.new_context(viewport=vp,is_mobile=mob,has_touch=mob,device_scale_factor=2 if mob else 1,permissions=['clipboard-read','clipboard-write'])
      pg=await ctx.new_page(); r={}
      pg.on("pageerror",lambda e,t=tag:errs.append(f"{t}: {e}")); pg.on("console",lambda m,t=tag:m.type=='error' and errs.append(f"{t}: {m.text}"))
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      if MODE!='http': await pg.route("**/arx-memeplex/politics.json",lambda rt: rt.abort())
      await pg.goto(URL); await pg.wait_for_function("window.__views && __memeplex.ideas.length>100",timeout=60000); await pg.wait_for_timeout(3000)
      r['polbtn']=await pg.evaluate("(()=>{const b=document.getElementById('polbtn');return b&&b.getBoundingClientRect().width>0})()")
      await pg.evaluate("document.getElementById('polbtn').click()"); await pg.wait_for_timeout(3500)
      r['pol']=await pg.evaluate("({on:__pol.on,key:getComputedStyle(document.getElementById('polkey')).display,maga:'#'+__memeplex.ideas.find(d=>d.id==='maga').star.core.material.color.getHexString(),nd:'#'+__memeplex.ideas.find(d=>d.id==='new_democrats').star.core.material.color.getHexString()})")
      await pg.screenshot(path=P+f'fix-{tag}-politics.png')
      await pg.evaluate("document.getElementById('polbtn').click()"); await pg.wait_for_timeout(2500)
      # select idea in dense area
      await pg.evaluate("__memeplex.controls.autoRotate=false"); await pg.wait_for_timeout(500)
      xy=await pg.evaluate("(()=>{const l=[...document.querySelectorAll('.lbl')].find(e=>e.textContent==='Neoplatonism'&&getComputedStyle(e).display!=='none');if(!l)return null;const b=l.getBoundingClientRect();return [b.left-2,b.top+b.height/2]})()")
      r['clickxy']=xy
      if xy and not mob: await pg.mouse.click(xy[0]-1,xy[1]+0)
      else: await pg.evaluate("__memeplex.focusIdea('neoplatonism')")
      await pg.wait_for_timeout(2600); r['cur']=await pg.evaluate("document.querySelector('#panel h1,#panel h2') && document.querySelector('#panel h1,#panel h2').textContent")
      if mob: await pg.evaluate("document.querySelector('#panel .close') && 0")
      r['sel']=await pg.evaluate("(()=>{const l=[...document.querySelectorAll('.lbl.sel')];const g=document.getElementById('selring');return {n:l.length,txt:l[0]&&l[0].textContent,shown:l[0]&&getComputedStyle(l[0]).display,ring:getComputedStyle(g).display}})()")
      await pg.screenshot(path=P+f'fix-{tag}-selected.png')
      # snip
      await pg.evaluate("document.querySelector('#panel .close') && document.querySelector('#panel .close').click()"); await pg.wait_for_timeout(600)
      await pg.evaluate("(()=>{const e=[...document.querySelectorAll('button')].find(e=>/snip/i.test(e.title));e.click()})()"); await pg.wait_for_timeout(500)
      W,H=vp['width'],vp['height']
      if mob:
        await pg.mouse.move(40,250); await pg.mouse.down(); await pg.mouse.move(350,600,steps=10); await pg.mouse.up()
      else:
        await pg.mouse.move(400,250); await pg.mouse.down(); await pg.mouse.move(1000,650,steps=10); await pg.mouse.up()
      await pg.wait_for_timeout(3000)
      r['card']=await pg.evaluate("(()=>{const i=document.querySelector('#snipmod img');const d=document.querySelector('#snipmod .dl');return {w:i.naturalWidth,h:i.naturalHeight,dl:d&&d.href.slice(0,5),dln:d&&d.download}})()")
      await pg.screenshot(path=P+f'fix-{tag}-snipcard.png')
      if not mob:
        try:
          async with pg.expect_download(timeout=5000) as dl: await pg.click('#snipmod .dl')
          d=await dl.value; await d.save_as(P+'fix-download.png'); r['download']=d.suggested_filename
        except Exception as e: r['download']='ERR '+str(e)[:80]
        cb=await pg.evaluate("(()=>{const b=[...document.querySelectorAll('#snipmod button')].find(b=>/copy image/i.test(b.textContent));return !!b})()")
        await pg.evaluate("[...document.querySelectorAll('#snipmod button')].find(b=>/copy image/i.test(b.textContent)).click()"); await pg.wait_for_timeout(1500)
        r['copy']=await pg.evaluate("navigator.clipboard.read().then(it=>it.map(x=>x.types.join(','))).catch(e=>'ERR '+e)")
      out[tag]=r
    await b.close()
  srv.terminate(); json.dump(out,open(P+'fix.json','w'),indent=1); print(json.dumps(out)); print('ERRS',[e[:200] for e in errs if 'GL Driver' not in e])
asyncio.run(run())
