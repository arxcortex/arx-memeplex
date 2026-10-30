# World politics test: every country view + key, hide-politics toggle, selection, snip card. Desktop + phone, http + file://.
# Run from this folder: python3 t_world.py
import asyncio,subprocess,json,os
from playwright.async_api import async_playwright
R='../../../'; PAGE_DIR=os.path.abspath('../snip-share')
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8793"],cwd=PAGE_DIR,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); fail=[]; res={}
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist","--allow-file-access-from-files"])
    for proto in ['http','file']:
     for tag,vp,mob in [('desk',dict(width=1440,height=900),False),('phone',dict(width=390,height=844),True)]:
      T=f"{proto}-{tag}"; errs=[]
      ctx=await b.new_context(viewport=vp,is_mobile=mob,has_touch=mob,device_scale_factor=2 if mob else 1); pg=await ctx.new_page()
      pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m:errs.append(m.text) if m.type=='error' else None)
      for f in ['ideas.json','thinkers.json','axes.json','currents.json','politics.json']:
        await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      url=("http://localhost:8793/memeplex.html" if proto=='http' else "file://"+PAGE_DIR+"/memeplex.html")+"?intro=none"
      await pg.goto(url); await pg.wait_for_function("window.__memeplex && __memeplex.ideas && __memeplex.ideas.length && window.__pol",polling=500); await pg.wait_for_timeout(2500)
      r={'ideas':await pg.evaluate("__memeplex.ideas.length")}
      for k in ['politics','hidepol','snip']:
        if not await pg.locator(f'#tb button[data-k={k}]').is_visible(): fail.append((T,k+' button hidden'))
      await pg.locator('#tb button[data-k=politics]').evaluate('b=>b.click()'); await pg.wait_for_timeout(1500)
      ctry=await pg.evaluate("__pol && politicsCfg ? 0 : 0") if False else None
      ids=await pg.evaluate("[...document.querySelectorAll('#polkey select option')].map(o=>o.value)"); r['countries']=ids
      if ids!=['us','gb','fr','de','ru','cn','jp']: fail.append((T,'countries',ids))
      for c in ids:
        await pg.select_option('#polkey select',c); await pg.wait_for_timeout(1300)
        k=await pg.evaluate("""()=>{const k=document.getElementById('polkey');return {vis:getComputedStyle(k).display!=='none',head:k.querySelector('.h').textContent,rows:k.querySelectorAll('.row[data-party]').length,
          fac:k.querySelectorAll('[data-go]').length,judg:[...k.querySelectorAll('.row[data-judgment] .jn')].map(e=>e.textContent),
          cdu:(k.querySelector('.row[data-party=CDU] .sw')||{}).getAttribute?k.querySelector('.row[data-party=CDU] .sw').getAttribute('style'):null}}""")
        r[c]=k
        if not k['vis'] or k['rows']<3 or k['fac']<1: fail.append((T,c,'key',k))
        if c in('ru','cn') and 'bloc' not in k['head']: fail.append((T,c,'not bloc'))
        if c=='cn' and (len(k['judg'])!=3 or any(j!='Proposed shade, no party color' for j in k['judg'])): fail.append((T,'cn judgment',k['judg']))
        if c=='de':
          col=await pg.evaluate("'#'+__memeplex.ideas.find(d=>d.id==='christian_democracy').star.core.material.color.getHexString()")
          k['cdu_star']=col
          if not k['cdu'] or '#5c5c5c' not in k['cdu'] or 'box-shadow' not in k['cdu']: fail.append((T,'cdu key',k['cdu']))
        if c=='fr':
          sd=await pg.evaluate("'#'+__memeplex.ideas.find(d=>d.id==='social_democracy').star.core.material.color.getHexString()"); k['sd_blend']=sd
        if tag=='desk' or c in('de','cn','ru'): await pg.screenshot(path=f"world-{T}-{c}.png")
      # selection highlight
      await pg.evaluate("__memeplex.focusIdea('gaullism'); __memeplex.controls.autoRotate=false"); await pg.wait_for_timeout(2200)
      r['panel']=await pg.evaluate("document.body.classList.contains('panel-open')")
      if not r['panel']: fail.append((T,'panel not open'))
      if mob: await pg.evaluate("document.querySelector('#panel .close') && document.querySelector('#panel .close').click()"); await pg.wait_for_timeout(800)
      await pg.screenshot(path=f"world-{T}-selected.png")
      # hide toggle
      before=await pg.evaluate("[__memeplex.ideas.filter(d=>d.star.grp.visible).length]")
      await pg.locator('#tb button[data-k=hidepol]').evaluate('b=>b.click()'); await pg.wait_for_timeout(1200)
      h=await pg.evaluate("""()=>{const I=__memeplex.ideas,pol=I.filter(d=>d.modern_politics);return {pol:pol.length,polVis:pol.filter(d=>d.star.grp.visible).length,vis:I.filter(d=>d.star.grp.visible).length,
        edgesHidden:__filter.edgesHidden,pressed:document.getElementById('hidepolbtn').getAttribute('aria-pressed'),f:__filter}}""")
      r['hide']=h
      if h['pol']!=41 or h['polVis']!=0 or h['pressed']!='true' or h['vis']!=r['ideas']-41 or h['edgesHidden']<41: fail.append((T,'hide',h))
      await pg.screenshot(path=f"world-{T}-hidden.png")
      await pg.locator('#tb button[data-k=hidepol]').evaluate('b=>b.click()'); await pg.wait_for_timeout(800)
      back=await pg.evaluate("__memeplex.ideas.filter(d=>d.star.grp.visible).length")
      if back!=r['ideas']: fail.append((T,'unhide',back))
      # snip
      await pg.locator('#tb button[data-k=politics]').evaluate('b=>b.click()'); await pg.wait_for_timeout(1000)
      await pg.locator('#tb button[data-k=snip]').evaluate('b=>b.click()'); await pg.wait_for_timeout(300)
      W,H=vp['width'],vp['height']; x0,y0,x1,y1=int(W*.15),int(H*.2),int(W*.8),int(H*.6)
      await pg.mouse.move(x0,y0); await pg.mouse.down(); await pg.mouse.move(x1,y1,steps=6); await pg.mouse.up()
      try:
        await pg.wait_for_function("window.__snipLast",timeout=12000); await pg.wait_for_timeout(800)
        info=await pg.evaluate("""async()=>{const im=document.querySelector('#snipmod img');await im.decode();const c=document.createElement('canvas');c.width=im.naturalWidth;c.height=im.naturalHeight;const x=c.getContext('2d');x.drawImage(im,0,0);
          const d=x.getImageData(0,0,c.width,Math.round(c.height*.8)).data;let lit=0,n=0;for(let i=0;i<d.length;i+=40){n++;if(d[i]+d[i+1]+d[i+2]>90)lit++}return {w:c.width,h:c.height,lit:lit/n,brand:__snipLast.meta.brand}}""")
        r['snip']=info
        if info['lit']<0.01 or not info['brand']: fail.append((T,'snip card',info))
      except Exception as e: fail.append((T,'snip',str(e)[:200]))
      await pg.screenshot(path=f"world-{T}-snip.png")
      r['errors']=errs
      if errs: fail.append((T,'console',errs[:5]))
      res[T]=r; print(T,json.dumps({k:v for k,v in r.items() if k in('ideas','hide','snip','errors')}))
      await ctx.close()
    await b.close()
  srv.terminate(); json.dump({'results':res,'fail':[list(map(str,f)) for f in fail]},open('results.json','w'),indent=1)
  print('FAIL' if fail else 'PASS',fail)
asyncio.run(run())
