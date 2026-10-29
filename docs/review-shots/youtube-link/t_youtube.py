# Checks the 'Search on YouTube' link in the idea panel (desktop + phone). Run from this folder.
import asyncio,subprocess,sys,urllib.parse
from playwright.async_api import async_playwright
R='../../../'
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8784"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); fail=[]; errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for tag,vp,mob in [('desk',dict(width=1440,height=900),False),('mobile',dict(width=390,height=844),True)]:
      ctx=await b.new_context(viewport=vp,is_mobile=mob,has_touch=mob,device_scale_factor=2 if mob else 1); pg=await ctx.new_page(); pg.on("pageerror",lambda e:errs.append(str(e)))
      for f in ['ideas.json','thinkers.json','axes.json','currents.json']:
        await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      await pg.goto("http://localhost:8784/memeplex.html?intro=none"); await pg.wait_for_function("window.__memeplex && __memeplex.ideas && __memeplex.ideas.length",polling=500); await pg.wait_for_timeout(3000)
      for iid in ['existentialism','social_justice_movement']:
        await pg.evaluate(f"__memeplex.focusIdea('{iid}')"); await pg.wait_for_timeout(1500)
        a=pg.locator('#panel a',has_text='Search on YouTube')
        if await a.count()!=1: fail.append((tag,iid,'count')); continue
        h=await a.get_attribute('href'); t=await a.get_attribute('target'); rel=await a.get_attribute('rel')
        name=await pg.evaluate(f"__memeplex.ideas.find(d=>d.id=='{iid}').name")
        q=urllib.parse.parse_qs(urllib.parse.urlparse(h).query).get('search_query',[''])[0]
        ok=h.startswith('https://www.youtube.com/results?search_query=') and t=='_blank' and 'noopener' in rel and q==name
        print(tag,iid,ok,h)
        if not ok: fail.append((tag,iid,h))
        await a.scroll_into_view_if_needed(); await pg.wait_for_timeout(400)
        await pg.screenshot(path=f"yt-{tag}-{iid}.png")
      await ctx.close()
    await b.close()
  srv.terminate(); print('errors',errs,'FAILS',fail); sys.exit(1 if fail or errs else 0)
asyncio.run(run())
