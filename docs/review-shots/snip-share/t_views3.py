# Similarity map + Thinker network + Chronosphere link test (desktop + phone). Run from this folder: python3 t_views3.py
import asyncio,subprocess,sys,json,re,itertools
from playwright.async_api import async_playwright
R='../../../'
I=json.load(open(R+'ideas.json')); B={d['id']:d for d in I}
BR=[{"idea_id":"protestantism","lens":"religion","era_year":1517,"event_year":1517,"lat":51.8678,"lon":12.6465,"event_slug":"religion-95-theses-1517","relation":"opens","note":"Luther posts the 95 Theses."},
    {"idea_id":"protestantism","lens":"geo","era_year":1517,"event_year":1517,"lat":51.866,"lon":12.648,"event_slug":"geo-luther-s-ninety-five-theses-1517","relation":"opens","note":"Geo-lens view."},
    {"idea_id":"protestantism","lens":"religion","era_year":1517,"event_year":1521,"lat":49.63,"lon":8.36,"event_slug":"religion-diet-of-worms-1521","relation":"peaks","note":"Worms."},
    {"idea_id":"roman_catholicism","lens":"religion","era_year":1054,"event_year":1054,"lat":41.0,"lon":28.9,"event_slug":"religion-the-great-schism-1054","relation":"opens","note":"Schism."},
    {"idea_id":"not_an_idea","lens":"geo","era_year":1,"event_year":1,"event_slug":"geo-x-1","relation":"context"}]
NEW={"name":"Bridges","version":0,"status":"draft","bridges":BR,"deep_links":{"memeplex":"memeplex.html#i={idea_id}","chronosphere":"chronosphere.html#{hash_head}/{year}/{region}/{event_slug}"},"hash_heads":{"geo":"history","religion":"religion"}}
OLD={"name":"Bridges","version":0,"status":"draft","bridges":BR,"deep_links":{"memeplex":"memeplex.html#i={idea_id}","chronosphere":"chronosphere.html#{lens}/{year}/{region}/{event_slug}"}}
WANT={'religion-95-theses-1517':'chronosphere.html#religion/1517/globe/religion-95-theses-1517','geo-luther-s-ninety-five-theses-1517':'chronosphere.html#history/1517/globe/geo-luther-s-ninety-five-theses-1517',
      'religion-diet-of-worms-1521':'chronosphere.html#religion/1521/globe/religion-diet-of-worms-1521'}
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8793"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); fail=[]; errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for tag,vp,mob in [('desk',dict(width=1440,height=900),False),('phone',dict(width=390,height=844),True)]:
      async def page(url,br=NEW):
        ctx=await b.new_context(viewport=vp,is_mobile=mob,has_touch=mob,device_scale_factor=2 if mob else 1); pg=await ctx.new_page(); pg.on("pageerror",lambda e:errs.append(f"{tag}: {e}"))
        for f in ['ideas.json','thinkers.json','axes.json','currents.json','impact.json','national.json','politics.json']:
          await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
        await pg.route("**/chronosphere-data/lenses/bridges.json",lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=json.dumps(br)))
        await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
        await pg.goto("http://localhost:8793/memeplex.html?intro=none"+url); await pg.wait_for_function("window.__viz && window.__views && !__views.busy",timeout=30000,polling=500); await pg.wait_for_timeout(2500)
        return ctx,pg
      ctx,pg=await page('')
      # similarity: PCA is deterministic and uses scores only; neighbours match a 24-d distance computed here
      await pg.click('#menubtn'); await pg.wait_for_timeout(200); await pg.click('#menu [data-vz=similar]'); await pg.wait_for_timeout(800)
      r=await pg.evaluate("({n:document.querySelectorAll('#vz .nd[data-id]').length,c:__simPCA.comps.map(q=>q[1]),p:__simPCA.pos['stoic_logos']})")
      AX=[a['id'] for a in json.load(open(R+'axes.json'))]
      def dist(a,b2): return sum((B[a]['ratings'].get(k,0)-B[b2]['ratings'].get(k,0))**2 for k in AX)**.5
      if r['n']!=len(I): fail.append((tag,'sim nodes',r['n']))
      if not (r['c'][0]>=r['c'][1]>0): fail.append((tag,'pca variance',r['c']))
      await pg.select_option('#vz select[data-p=f]','stoicism' if 'stoicism' in B else 'stoic_logos'); await pg.wait_for_timeout(600)
      sel=await pg.evaluate("__viz.P.f"); nb=await pg.evaluate("__simPCA.near(__viz.P.f).map(q=>q[0])")
      want=[k for k,_ in sorted(((d['id'],dist(sel,d['id'])) for d in I if d['id']!=sel),key=lambda q:(round(q[1],9),q[0]))[:6]]
      if [round(dist(sel,k),6) for k in nb]!=[round(dist(sel,k),6) for k in want]: fail.append((tag,'neighbours',nb,want))
      lines=await pg.evaluate("document.querySelectorAll('#vz line.e').length")
      if lines!=6: fail.append((tag,'neighbour lines',lines))
      ctx2_pos=r['p']
      await pg.screenshot(path=f"views-{tag}-similar.png")
      await pg.wait_for_timeout(500); h=await pg.evaluate("location.hash")
      if 'v=similar' not in h or 'f='+sel not in h: fail.append((tag,'sim hash',h))
      await pg.evaluate("document.getElementById('themebtn').click()"); await pg.wait_for_timeout(900); await pg.screenshot(path=f"views-{tag}-similar-light.png"); await pg.evaluate("document.getElementById('themebtn').click()"); await pg.wait_for_timeout(400)
      # thinker network: edges = pairs of thinkers named on the same idea
      E=set(); T={}
      for d in I:
        L=sorted(set(d.get('thinkers',[])))
        for t in L: T.setdefault(t,set()).add(d['id'])
        for a,c in itertools.combinations(L,2): E.add((a,c))
      await pg.evaluate("__viz.open('thinkers',{m:'all'})"); await pg.wait_for_timeout(1500)
      r=await pg.evaluate("({n:document.querySelectorAll('#vz .nd').length,e:document.querySelectorAll('#vz line.e').length,tE:__thinkers.edges.length})")
      print(tag,'thinkers all',r,len(T),len(E))
      if r['n']!=len(T) or r['e']!=len(E) or r['tE']!=len(E): fail.append((tag,'thinker graph',r,len(T),len(E)))
      await pg.screenshot(path=f"views-{tag}-thinkers-all.png")
      await pg.click('#vz [data-set="m=linked"]'); await pg.wait_for_timeout(1500)
      multi=sorted(T,key=lambda t:-len(T[t]))[0]
      await pg.select_option('#vz select[data-p=f]',multi); await pg.wait_for_timeout(600)
      r=await pg.evaluate("({on:document.querySelectorAll('#vz line.e.on').length,foot:document.querySelector('#vz .vf').textContent,n:document.querySelectorAll('#vz .nd').length})")
      wantn=len({b2 for a,b2 in E if a==multi}|{a for a,b2 in E if b2==multi})
      print(tag,'thinker',multi,r['on'],wantn,r['n'])
      if r['on']!=wantn: fail.append((tag,'thinker links',multi,r['on'],wantn))
      await pg.screenshot(path=f"views-{tag}-thinkers.png")
      await pg.wait_for_timeout(500); h=await pg.evaluate("location.hash")
      if 'v=thinkers' not in h or 'f=' not in h: fail.append((tag,'thinker hash',h))
      # chronosphere link: bridges read at runtime, links from the template with hash_heads
      await pg.evaluate("__viz.open('chrono',{f:'protestantism'})"); await pg.wait_for_function("window.__chrono && __chrono.data",timeout=10000); await pg.wait_for_timeout(600)
      r=await pg.evaluate("({links:[...document.querySelectorAll('#vz a[href*=chronosphere]')].map(a=>a.getAttribute('href')),rows:[...document.querySelectorAll('#vz .nd[data-id]')].map(g=>g.dataset.id),f:__viz.P.f})")
      print(tag,'chrono',r)
      for slug,u in WANT.items():
        if 'https://arxcortex.io/'+u not in r['links']: fail.append((tag,'chrono link',slug,u))
      if any(re.search(r'\{[^}]*\}',u) for u in r['links']): fail.append((tag,'placeholder left'))
      if sorted(r['rows'])!=['protestantism','roman_catholicism'] or r['f']!='protestantism': fail.append((tag,'chrono rows',r['rows']))
      await pg.screenshot(path=f"views-{tag}-chrono.png")
      # snip in the chrono view
      await pg.evaluate("document.querySelector('#tb button[data-k=snip]').click()"); await pg.wait_for_timeout(300)
      W,H=vp['width'],vp['height']; await pg.mouse.move(int(W*.04),int(H*.2)); await pg.mouse.down(); await pg.mouse.move(int(W*.5),int(H*.5),steps=4); await pg.mouse.move(int(W*.96),int(H*.75),steps=4); await pg.mouse.up()
      await pg.wait_for_function("window.__snipLast",timeout=15000); await pg.wait_for_timeout(800)
      link=await pg.evaluate("__snipLast.link")
      if 'v=chrono' not in link or 'f=protestantism' not in link: fail.append((tag,'chrono snip',link))
      await pg.screenshot(path=f"views-{tag}-chrono-snip.png"); await pg.evaluate("document.querySelector('#snipmod .x').click()")
      # search: an idea without bridges falls back to its page; one with bridges retargets
      await pg.evaluate("__memeplex.focusIdea('roman_catholicism')"); await pg.wait_for_timeout(400)
      if await pg.evaluate("__viz.P.f")!='roman_catholicism': fail.append((tag,'chrono retarget'))
      await ctx.close()
      # old data: no hash_heads, {lens} template -> geo still becomes history; template substitution for both lenses
      ctx,pg=await page('#v=chrono&f=protestantism',OLD); await pg.wait_for_timeout(5200)
      r=await pg.evaluate("({links:[...document.querySelectorAll('#vz a[href*=chronosphere]')].map(a=>a.getAttribute('href')),cur:__viz.cur})")
      print(tag,'old data',r)
      for slug,u in WANT.items():
        if 'https://arxcortex.io/'+u not in r['links']: fail.append((tag,'old-data link',slug,u))
      if any('#geo/' in u or re.search(r'\{[^}]*\}',u) for u in r['links']): fail.append((tag,'old-data geo/placeholder',r['links']))
      u=await pg.evaluate("""()=>[__chrono.link({lens:'geo',event_year:1066,event_slug:'geo-hastings-1066'},{deep_links:{chronosphere:'chronosphere.html#{hash_head}/{year}/{region}/{event_slug}'},hash_heads:{geo:'history'}}),
        __chrono.link({lens:'religion',event_year:325,event_slug:'religion-nicaea-325'},{deep_links:{chronosphere:'chronosphere.html#{hash_head}/{year}/{region}/{event_slug}'},hash_heads:{geo:'history',religion:'religion'}}),
        __chrono.link({lens:'geo',event_year:1066,event_slug:'geo-hastings-1066'},{deep_links:{chronosphere:'chronosphere.html#{lens}/{year}/{region}/{event_slug}'}}),
        __chrono.link({lens:'religion',event_year:325,event_slug:'religion-nicaea-325'},{deep_links:{chronosphere:'chronosphere.html#{hash_head}/{year}/{unknown}/{event_slug}'}}),
        __chrono.link({lens:'geo',era_year:1000,event_slug:'geo-x-1000'},null)]""")
      exp=['chronosphere.html#history/1066/globe/geo-hastings-1066','chronosphere.html#religion/325/globe/religion-nicaea-325','chronosphere.html#history/1066/globe/geo-hastings-1066','chronosphere.html#religion/325/globe/religion-nicaea-325','chronosphere.html#history/1000/globe/geo-x-1000']
      if u!=exp: fail.append((tag,'template substitution',u))
      await ctx.close()
      ctx,pg=await page('#v=thinkers&m=linked',NEW); await pg.wait_for_timeout(5200)
      if not await pg.evaluate("__viz.cur==='thinkers'&&__viz.P.m==='linked'"): fail.append((tag,'thinker link restore'))
      await ctx.close()
    await b.close()
  srv.terminate(); print('errors',errs,'FAILS',fail); sys.exit(1 if fail or errs else 0)
asyncio.run(run())
