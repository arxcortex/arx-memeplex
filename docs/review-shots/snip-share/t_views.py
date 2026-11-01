# Menu + Family tree + Fingerprint test (desktop + phone). Run from this folder: python3 t_views.py
import asyncio,subprocess,sys,json
from playwright.async_api import async_playwright
R='../../../'
BAR={'menu','search','color','filter','stretch','impact','lines','hidepol','theme','snip','reset','hideui'}
MOVED={'dice','tours','games','link','legend','help','sym'}
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8788"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); fail=[]; errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for tag,vp,mob in [('desk',dict(width=1440,height=900),False),('phone',dict(width=390,height=844),True)]:
      async def page(url):
        ctx=await b.new_context(viewport=vp,is_mobile=mob,has_touch=mob,device_scale_factor=2 if mob else 1); pg=await ctx.new_page(); pg.on("pageerror",lambda e:errs.append(f"{tag}: {e}"))
        for f in ['ideas.json','thinkers.json','axes.json','currents.json','impact.json','national.json','politics.json']:
          await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
        await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
        await pg.goto("http://localhost:8788/memeplex.html?intro=none"+url); await pg.wait_for_function("window.__viz && window.__views && !__views.busy",timeout=30000,polling=500); await pg.wait_for_timeout(2500)
        return ctx,pg
      ctx,pg=await page('')
      # toolbar: map controls stay, the rest moved into the menu
      r=await pg.evaluate("""()=>({bar:[...document.querySelectorAll('#tb [data-k]')].map(e=>e.dataset.k),menu:[...document.querySelectorAll('#menu [data-k]')].map(e=>e.dataset.k),
        shown:[...document.querySelectorAll('#tb [data-k]')].filter(e=>e.offsetParent!==null).map(e=>e.dataset.k),vz:getComputedStyle(document.getElementById('vz')).display,cur:__views.cur})""")
      print(tag,'bar',r['bar'],'menu',r['menu'])
      if set(r['bar'])!=BAR: fail.append((tag,'bar items',sorted(set(r['bar'])^BAR)))
      if not MOVED<=set(r['menu']): fail.append((tag,'menu items',MOVED-set(r['menu'])))
      if 'menu' not in r['shown']: fail.append((tag,'menu button hidden'))
      if r['vz']!='none' or r['cur']!='default': fail.append((tag,'default view on open',r))
      # menu: open, keyboard, close
      await pg.click('#menubtn'); await pg.wait_for_timeout(300)
      m=await pg.evaluate("({open:document.getElementById('menu').classList.contains('open'),exp:document.getElementById('menubtn').getAttribute('aria-expanded'),foc:document.getElementById('menu').contains(document.activeElement),shapes:[...document.querySelectorAll('#menu .vbtn')].map(b=>b.dataset.v)})")
      if not (m['open'] and m['exp']=='true' and m['foc']): fail.append((tag,'menu open',m))
      if 'axes' not in m['shapes'] or 'politics' not in m['shapes']: fail.append((tag,'shapes in menu',m['shapes']))
      await pg.screenshot(path=f"views-{tag}-menu.png")
      await pg.keyboard.press('ArrowDown'); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(200)
      m=await pg.evaluate("({open:document.getElementById('menu').classList.contains('open'),foc:document.activeElement.id})")
      if m['open'] or m['foc']!='menubtn': fail.append((tag,'menu escape',m))
      if not mob:
        await pg.keyboard.press('m'); await pg.wait_for_timeout(200)
        if not await pg.evaluate("document.getElementById('menu').classList.contains('open')"): fail.append((tag,'M key'))
        await pg.keyboard.press('Escape')
      # family tree from the menu
      await pg.click('#menubtn'); await pg.wait_for_timeout(200); await pg.click('#menu [data-vz=family]'); await pg.wait_for_timeout(600)
      await pg.select_option('#vz select[data-p=f]','christianity'); await pg.wait_for_timeout(700)
      r=await pg.evaluate("""()=>{const L=s=>{const seen=new Set(['christianity']);let f=['christianity'],n=0;while(f.length){const nx=[];f.forEach(k=>{const d=__memeplex.ideas.find(x=>x.id===k);(s?d.parents:__memeplex.ideas.filter(c=>(c.parents||[]).includes(k)).map(c=>c.id)).forEach(q=>{if(!seen.has(q)&&__memeplex.ideas.some(x=>x.id===q)){seen.add(q);nx.push(q)}})});n+=nx.length;f=nx}return n};
        return {nodes:document.querySelectorAll('#vz .nd').length,edges:document.querySelectorAll('#vz .e').length,want:1+L(1)+L(0),focus:document.querySelector('#vz .nd.focus').dataset.id,menu:closed=!document.getElementById('menu').classList.contains('open')}}""")
      print(tag,'family',r)
      if r['nodes']!=r['want'] or r['focus']!='christianity' or r['edges']<r['nodes']-1: fail.append((tag,'family nodes',r))
      await pg.wait_for_timeout(600); h=await pg.evaluate("location.hash")
      if 'v=family' not in h or 'f=christianity' not in h: fail.append((tag,'family hash',h))
      await pg.screenshot(path=f"views-{tag}-family.png")
      # click a node to recenter; keyboard Enter on a node
      await pg.evaluate("document.querySelector('#vz .nd[data-id=apostolic_christianity]').dispatchEvent(new MouseEvent('click',{bubbles:true}))"); await pg.wait_for_timeout(400)
      if await pg.evaluate("document.querySelector('#vz .nd.focus').dataset.id")!='apostolic_christianity': fail.append((tag,'family click'))
      await pg.focus('#vz .nd[data-id=christianity]'); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(400)
      if await pg.evaluate("document.querySelector('#vz .nd.focus').dataset.id")!='christianity': fail.append((tag,'family enter'))
      # light theme
      await pg.evaluate("document.getElementById('themebtn').click()"); await pg.wait_for_timeout(900)
      bg=await pg.evaluate("document.querySelector('#vz svg rect').getAttribute('fill')")
      if bg.lower() not in ('#f3ecdc',): fail.append((tag,'light bg',bg))
      await pg.screenshot(path=f"views-{tag}-family-light.png")
      await pg.evaluate("document.getElementById('themebtn').click()"); await pg.wait_for_timeout(600)
      # snip in the chart view
      await pg.evaluate("document.querySelector('#tb button[data-k=snip]').click()"); await pg.wait_for_timeout(300)
      W,H=vp['width'],vp['height']; await pg.mouse.move(int(W*.08),int(H*.3)); await pg.mouse.down(); await pg.mouse.move(int(W*.5),int(H*.5),steps=4); await pg.mouse.move(int(W*.92),int(H*.8),steps=4); await pg.mouse.up()
      await pg.wait_for_function("window.__snipLast",timeout=15000); await pg.wait_for_timeout(800)
      sn=await pg.evaluate("""async()=>{const im=document.querySelector('#snipmod img');await im.decode();const c=document.createElement('canvas');c.width=im.naturalWidth;c.height=im.naturalHeight;const x=c.getContext('2d');x.drawImage(im,0,0);
        const d=x.getImageData(0,0,c.width,Math.floor(c.height*.7)).data;let lit=0;for(let i=0;i<d.length;i+=16){if(d[i]+d[i+1]+d[i+2]>200)lit++}return {link:__snipLast.link,lit:lit/(d.length/16),title:__viz.title()}}""")
      print(tag,'snip',sn)
      if 'v=family' not in sn['link'] or sn['lit']<0.005 or 'Family tree' not in sn['title']: fail.append((tag,'snip family',sn))
      await pg.screenshot(path=f"views-{tag}-family-snip.png"); await pg.evaluate("document.querySelector('#snipmod .x').click()")
      # map shape from the menu leaves the chart view
      await pg.evaluate("document.querySelector('#menu .vbtn[data-v=helix]').click()"); await pg.wait_for_timeout(2600)
      r=await pg.evaluate("({viz:__viz.cur,v:__views.cur,vz:document.body.classList.contains('vzon')})")
      if r['viz'] or r['v']!='helix' or r['vz']: fail.append((tag,'shape leaves chart',r))
      await pg.evaluate("__views.set('default',{instant:true})")
      # from the idea panel
      await pg.evaluate("__memeplex.focusIdea('leninism')"); await pg.wait_for_timeout(2200)
      await pg.evaluate("document.querySelector('#panel [data-act=fprint]').click()"); await pg.wait_for_timeout(700)
      r=await pg.evaluate("({cur:__viz.cur,f:__viz.P.f,polys:document.querySelectorAll('#vz svg polygon[fill-opacity]').length,spokes:document.querySelectorAll('#vz [data-ax]').length})")
      print(tag,'fingerprint from panel',r)
      if r['cur']!='fingerprint' or r['f']!='leninism' or r['polys']!=1 or r['spokes']!=23: fail.append((tag,'fingerprint panel',r))
      await pg.select_option('#vz select[data-p=g]','christianity'); await pg.wait_for_timeout(600)
      r=await pg.evaluate("({polys:document.querySelectorAll('#vz svg polygon[fill-opacity]').length,spokes:document.querySelectorAll('#vz [data-ax]').length,h:location.hash})")
      if r['polys']!=2 or r['spokes']!=21: fail.append((tag,'fingerprint compare (root: tone hidden)',r))
      await pg.wait_for_timeout(500); h=await pg.evaluate("location.hash")
      if 'v=fingerprint' not in h or 'g=christianity' not in h: fail.append((tag,'fingerprint hash',h))
      await pg.screenshot(path=f"views-{tag}-fingerprint.png")
      # search retargets the view
      await pg.evaluate("__memeplex.focusIdea('stoic_logos')"); await pg.wait_for_timeout(400)
      if await pg.evaluate("__viz.P.g")!='stoic_logos': fail.append((tag,'search retarget'))
      await pg.evaluate("document.getElementById('panel').classList.contains('x')")
      await pg.evaluate("document.querySelector('#panel [data-act=ftree]') && 0"); 
      await pg.evaluate("document.querySelector('#vz [data-act=map]').click()"); await pg.wait_for_timeout(300)
      if await pg.evaluate("__viz.cur"): fail.append((tag,'close view'))
      await ctx.close()
      # share links restore: chart views, plus old National, axes and ui=0 links
      for url,check in [('#v=fingerprint&f=stoic_logos&g=epicureanism',"__viz.cur==='fingerprint'&&__viz.P.f==='stoic_logos'&&__viz.P.g==='epicureanism'"),
                        ('#v=family&f=marxism&ui=0',"__viz.cur==='family'&&__viz.P.f==='marxism'&&document.body.classList.contains('uihidden')"),
                        ('#v=national&ns=religion',"__views.cur==='politics'&&__pol.sub==='religion'&&!__viz.cur"),
                        ('#v=axes&x=platonism&y=darwinism',"__views.cur==='axes'&&__axesView.x==='platonism'&&!__viz.cur")]:
        ctx,pg=await page(url); await pg.wait_for_timeout(4800 if 'v=' in url else 0); await pg.wait_for_timeout(1200)
        ok=await pg.evaluate(check); print(tag,url,ok)
        if not ok: fail.append((tag,'restore',url))
        if 'fingerprint' in url: await pg.screenshot(path=f"views-{tag}-fingerprint-link.png")
        if 'ui=0' in url: await pg.screenshot(path=f"views-{tag}-family-ui-hidden.png")
        await ctx.close()
    await b.close()
  srv.terminate(); print('errors',errs,'FAILS',fail); sys.exit(1 if fail or errs else 0)
asyncio.run(run())
