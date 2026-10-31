# Choose-your-axes view test (desktop + phone). Run from this folder: python3 t_axes.py
import asyncio,subprocess,sys,json
from playwright.async_api import async_playwright
R='../../../'
AX=[a['id'] for a in json.load(open(R+'axes.json'))]
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8787"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); fail=[]; errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for tag,vp,mob in [('desk',dict(width=1440,height=900),False),('phone',dict(width=390,height=844),True)]:
      ctx=await b.new_context(viewport=vp,is_mobile=mob,has_touch=mob,device_scale_factor=2 if mob else 1); pg=await ctx.new_page(); pg.on("pageerror",lambda e:errs.append(f"{tag}: {e}"))
      for f in ['ideas.json','thinkers.json','axes.json','currents.json','impact.json','national.json','politics.json']:
        await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      await pg.goto("http://localhost:8787/memeplex.html?intro=none#v=axes&x=platonism&y=darwinism")
      await pg.wait_for_function("window.__views && __views.cur==='axes' && !__views.busy",timeout=30000,polling=500); await pg.wait_for_timeout(2500)
      r=await pg.evaluate("""()=>{const A=__axesView,S=6.4;let worst=0;__memeplex.ideas.forEach(d=>{const sx=(d.ratings||{})[A.x]||0,sy=(d.ratings||{})[A.y]||0;worst=Math.max(worst,Math.abs(d.pos.x-sx*S),Math.abs(d.pos.y-sy*S),Math.abs(d.pos.z))});
        const ks=new Set(__memeplex.ideas.map(d=>d.pos.x.toFixed(2)+','+d.pos.y.toFixed(2)));
        return {x:A.x,y:A.y,worst,uniq:ks.size,n:__memeplex.ideas.length,presets:A.presets,titles:A.L4.filter(o=>/title|pole/.test(o.el.className)).map(o=>o.el.textContent),bar:getComputedStyle(document.getElementById('axpick')).display}}""")
      print(tag,{k:v for k,v in r.items() if k!='presets'}); print('presets',[q[2] for q in r['presets']])
      if (r['x'],r['y'])!=('platonism','darwinism'): fail.append((tag,'url restore',r['x'],r['y']))
      if r['worst']>6.4*0.31+1e-6: fail.append((tag,'positions off',r['worst']))
      if r['uniq']<r['n']*0.95: fail.append((tag,'stacked',r['uniq']))
      if r['bar']=='none': fail.append((tag,'picker hidden'))
      if not any('Platonism' in t for t in r['titles']) or not any('Darwinism' in t for t in r['titles']): fail.append((tag,'titles',r['titles']))
      for q in r['presets']:
        if q[0] not in AX or q[1] not in AX: fail.append((tag,'preset axis',q))
      await pg.screenshot(path=f"axes-{tag}-platonism-darwinism.png")
      # pick via dropdowns -> URL
      await pg.select_option('#axpick select[data-a=x]','christianity'); await pg.select_option('#axpick select[data-a=y]','marxism'); await pg.wait_for_timeout(2200)
      h=await pg.evaluate("location.hash")
      if 'x=christianity' not in h or 'y=marxism' not in h or 'v=axes' not in h: fail.append((tag,'hash',h))
      # preset
      (await pg.select_option('#axpick .psel','christianity,irony')) if mob else (await pg.locator('#axpick .pre button').nth(2).click()); await pg.wait_for_timeout(1800)
      await pg.screenshot(path=f"axes-{tag}-preset.png")
      # impact slider, lines, select, theme
      await pg.evaluate("const i=document.querySelector('#impslider input');i.value=50;i.dispatchEvent(new Event('input'))"); await pg.wait_for_timeout(600)
      vis=await pg.evaluate("__memeplex.ideas.filter(d=>d.star.grp.visible!==false).length")
      await pg.evaluate("__memeplex.focusIdea('marxism')"); await pg.wait_for_timeout(2200)
      still=await pg.evaluate("__views.cur")
      if still!='axes': fail.append((tag,'select left view',still))
      await pg.keyboard.press('l') if not mob else await pg.evaluate("document.getElementById('linesbtn').click()"); await pg.wait_for_timeout(500)
      await pg.evaluate("document.getElementById('themebtn').click()"); await pg.wait_for_timeout(1500)
      await pg.screenshot(path=f"axes-{tag}-light-selected.png")
      await pg.evaluate("document.getElementById('themebtn').click(); document.getElementById('linesbtn').click(); const i=document.querySelector('#impslider input');i.value=0;i.dispatchEvent(new Event('input'))"); await pg.wait_for_timeout(800)
      print(tag,'visible at impact 50:',vis,'hash',await pg.evaluate("location.hash"))
      # snip
      await pg.evaluate("document.querySelector('#tb button[data-k=snip]').click()"); await pg.wait_for_timeout(300)
      W,H=vp['width'],vp['height']; await pg.mouse.move(int(W*.1),int(H*.15)); await pg.mouse.down(); await pg.mouse.move(int(W*.6),int(H*.5),steps=4); await pg.mouse.move(int(W*.9),int(H*.75),steps=4); await pg.mouse.up()
      await pg.wait_for_function("window.__snipLast",timeout=15000); await pg.wait_for_timeout(800)
      link=await pg.evaluate("__snipLast.link"); print(tag,'snip link',link)
      if 'v=axes' not in link or 'x=' not in link: fail.append((tag,'snip link',link))
      await pg.screenshot(path=f"axes-{tag}-snip-card.png")
      await pg.keyboard.press('Escape'); await pg.evaluate("const x=document.querySelector('#snipmod .x'); x&&x.click()"); await pg.wait_for_timeout(400)
      # hide UI
      await pg.evaluate("const c=document.querySelector('#panel .close'); c&&c.click()"); await pg.wait_for_timeout(800)
      await pg.evaluate("document.getElementById('hideuibtn').click()"); await pg.wait_for_timeout(500)
      hid=await pg.evaluate("({tb:getComputedStyle(document.getElementById('tb')).display,show:getComputedStyle(document.getElementById('uishow')).display,h:location.hash})")
      await pg.wait_for_timeout(500); h2=await pg.evaluate("location.hash")
      if hid['tb']!='none' or hid['show']=='none' or 'ui=0' not in h2: fail.append((tag,'hide ui',hid,h2))
      await pg.screenshot(path=f"axes-{tag}-ui-hidden.png")
      await pg.evaluate("document.getElementById('uishow').click()"); await pg.wait_for_timeout(300)
      if await pg.evaluate("document.body.classList.contains('uihidden')"): fail.append((tag,'restore ui'))
      if not mob:
        await pg.keyboard.press('u'); await pg.wait_for_timeout(200)
        if not await pg.evaluate("document.body.classList.contains('uihidden')"): fail.append((tag,'U key'))
        await pg.evaluate("__views.set('default')"); await pg.wait_for_timeout(2600); await pg.screenshot(path=f"default-{tag}-ui-hidden.png"); await pg.keyboard.press('u')
      await ctx.close()
    await b.close()
  srv.terminate(); print('errors',errs,'FAILS',fail); sys.exit(1 if fail or errs else 0)
asyncio.run(run())
