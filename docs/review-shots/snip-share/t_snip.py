# Snip & share test (desktop + phone). Run from this folder: python3 t_snip.py
import asyncio,subprocess,sys,base64,io
from playwright.async_api import async_playwright
R='../../../'
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8786"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); fail=[]; errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for tag,vp,mob in [('desk',dict(width=1440,height=900),False),('phone',dict(width=390,height=844),True)]:
      async def page():
        ctx=await b.new_context(viewport=vp,is_mobile=mob,has_touch=mob,device_scale_factor=2 if mob else 1); pg=await ctx.new_page(); pg.on("pageerror",lambda e:errs.append(f"{tag}: {e}"))
        for f in ['ideas.json','thinkers.json','axes.json','currents.json']:
          await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
        await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')"); return ctx,pg
      ctx,pg=await page()
      await pg.goto("http://localhost:8786/memeplex.html?intro=none"); await pg.wait_for_function("window.__memeplex && __memeplex.ideas && __memeplex.ideas.length",polling=500); await pg.wait_for_timeout(3000)
      await pg.evaluate("__memeplex.focusIdea('stoic_logos'); __memeplex.controls.autoRotate=false"); await pg.wait_for_timeout(2500)
      if mob: await pg.evaluate("document.querySelector('#panel .close') && document.querySelector('#panel .close').click(); __memeplex.controls.autoRotate=false; window.__memeplex.focusIdea('stoic_logos')"); await pg.wait_for_timeout(2000)
      btn=pg.locator('#tb button[data-k=snip]')
      if not await btn.is_visible(): fail.append((tag,'snip button hidden'))
      if mob: await btn.evaluate('b=>b.click()')
      else: await pg.keyboard.press('s')
      await pg.wait_for_timeout(300)
      W,H=vp['width'],vp['height']; x0,y0,x1,y1=int(W*.15),int(H*.2),int(W*.8),int(H*.6)
      await pg.mouse.move(x0,y0); await pg.mouse.down(); await pg.mouse.move((x0+x1)//2,(y0+y1)//2,steps=4); await pg.mouse.move(x1,y1,steps=4)
      await pg.screenshot(path=f"snip-{tag}-overlay.png")
      await pg.mouse.up(); await pg.wait_for_timeout(1500); await pg.wait_for_function("window.__snipLast",timeout=10000); await pg.wait_for_timeout(800)
      await pg.screenshot(path=f"snip-{tag}-card.png")
      info=await pg.evaluate("""async()=>{const im=document.querySelector('#snipmod img');await im.decode();const c=document.createElement('canvas');c.width=im.naturalWidth;c.height=im.naturalHeight;const x=c.getContext('2d');x.drawImage(im,0,0);
        const d=x.getImageData(0,0,c.width,Math.round(c.height*.8)).data;let lit=0,n=0;for(let i=0;i<d.length;i+=40){n++;if(d[i]+d[i+1]+d[i+2]>90)lit++}
        return {w:c.width,h:c.height,lit:lit/n,last:__snipLast,cam:[...__cam.position.toArray(),...__memeplex.controls.target.toArray()],cur:new URLSearchParams(location.hash.slice(1)).get('i')}}""")
      SN=await pg.evaluate("__memeplex.ideas.find(d=>d.id=='stoic_logos').name"); m=info['last']['meta']; link=info['last']['link']; r=info['last']['rect']
      ratio=(info['h']-(info['h']-info['w']*r['h']/r['w']))  # image part height
      print(tag,'card',info['w'],'x',info['h'],'lit',round(info['lit'],3),'link',link,'lines',m['lines'],'brand',m['brand'],'title',m['title'])
      if info['lit']<0.01: fail.append((tag,'blank card'))
      if not m['brand']: fail.append((tag,'no brand mark'))
      if not ''.join(m['lines']).startswith('arxcortex.io/memeplex.html#'): fail.append((tag,'no link text'))
      if m['title']!=SN: fail.append((tag,'title',m['title']))
      if 'i=stoic_logos' not in link or 'cam=' not in link: fail.append((tag,'link',link))
      if info['w']<r['w']*1.9 or info['h']<=info['w']*r['h']/r['w']: fail.append((tag,'size not as snipped'))
      await ctx.close()
      # restore from link
      ctx,pg=await page(); u=link.replace('https://arxcortex.io/memeplex.html','http://localhost:8786/memeplex.html?intro=none')
      await pg.goto(u); await pg.wait_for_function("window.__camRestored",timeout=20000); await pg.wait_for_timeout(1500)
      got=await pg.evaluate("({cam:[...__cam.position.toArray(),...__memeplex.controls.target.toArray()],i:new URLSearchParams(location.hash.slice(1)).get('i'),open:document.body.classList.contains('panel-open')})")
      want=[float(v) for v in dict(kv.split('=') for kv in link.split('#')[1].split('&'))['cam'].split(',')]
      dev=max(abs(a-b) for a,b in zip(got['cam'],want)); print(tag,'restore i',got['i'],'panel',got['open'],'cam dev',round(dev,3))
      if got['i']!='stoic_logos' or dev>0.5: fail.append((tag,'restore',got,want))
      if mob: await pg.screenshot(path="snip-phone-restored.png")
      await ctx.close()
    await b.close()
  srv.terminate(); print('errors',errs,'FAILS',fail); sys.exit(1 if fail or errs else 0)
asyncio.run(run())
