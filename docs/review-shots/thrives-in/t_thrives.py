# Checks thrives_in on the page: tour validator, alias search, panel row, Memele clue, Thinker Match place rounds; takes screenshots. Run from this folder.
import asyncio,subprocess,sys
from playwright.async_api import async_playwright
R='../../../'
CASES={'CPUSA':'american_communism','woke':'social_justice_movement','e/acc':'effective_accelerationism','Nazism':'nazism','Ásatrú':'heathenry'}
async def page(b,vp,port):
  pg=await (await b.new_context(viewport=vp,device_scale_factor=2 if vp['width']<500 else 1,is_mobile=vp['width']<500,has_touch=vp['width']<500)).new_page()
  for f in ['ideas.json','thinkers.json','axes.json','currents.json']:
    await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
  pg.on("pageerror",lambda e:print("PAGEERR",e)); pg.on("console",lambda m:m.type=="error" and print("CONSOLE",m.text)); pg.on("response",lambda r:r.status>=400 and print("BAD",r.status,r.url))
  await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
  await pg.goto(f"http://localhost:{port}/memeplex.html?intro=none"); await pg.wait_for_function("window.__memele && window.__tours && __memeplex.ideas.length",polling=500); await pg.wait_for_timeout(2500)
  return pg
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8853"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); errs=[]; fail=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    pg=await page(b,dict(width=1440,height=900),8853); pg.on("pageerror",lambda e:errs.append(str(e)))
    print('ideas',await pg.evaluate("__memeplex.ideas.length"))
    bad=await pg.evaluate("__tours.validate()"); print('tour validate',bad); bad and fail.append('tours')
    for q,w in CASES.items():
      r=await pg.evaluate("q=>__memele.search(q,[]).slice(0,3)",q); print(q,r); (not r or r[0]!=w) and fail.append(q)
    await pg.evaluate("__memeplex.focusIdea('pentecostalism')"); await pg.wait_for_timeout(1500)
    txt=await pg.inner_text('#panel'); print('panel has Thrives in:', 'THRIVES IN' in txt.upper()); 'THRIVES IN' not in txt.upper() and fail.append('panel')
    await pg.screenshot(path='thrives-desktop-pentecostalism.png')
    await pg.evaluate("__memeplex.focusIdea('neo_confucianism')"); await pg.wait_for_timeout(1500); await pg.screenshot(path='thrives-desktop-neo_confucianism.png')
    # Memele: reveal hints until the thrives clue shows
    await pg.evaluate("__memele.open()"); await pg.wait_for_timeout(800)
    ct=await pg.evaluate("__memele.clueTypes()"); print('memele clue order',ct)
    if 'thrives' in ct:
      for _ in range(ct.index('thrives')): await pg.evaluate("__memele.hint()")
      await pg.wait_for_timeout(600); t=await pg.inner_text('#memele'); print('memele thrives clue shown:', 'thrive' in t.lower() or 'flourished' in t.lower())
      await pg.screenshot(path='thrives-memele-clue.png')
      st=await pg.evaluate("__memele.shareText ? 1 : 0")
    await pg.evaluate("__memele.close()")
    # Thinker Match: check place rounds are unambiguous over many seeds
    amb=await pg.evaluate("""()=>{let n=0,bad=0;for(let k=0;k<300;k++){const P=__games.puzzle('thinker','s'+k);for(const q of P.rounds){if(q.kind!=='place')continue;n++;
      const has=id=>((__memeplex.ideas.find(x=>x.id===id).thrives_in||{}).places||[]).some(p=>p.place===q.th);if(q.opts.filter(has).length!==1)bad++;}}return [n,bad]}""")
    print('place rounds, ambiguous',amb); amb[1] and fail.append('ambiguous')
    await b.close(); b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    ph=await page(b,dict(width=390,height=844),8853); ph.on("pageerror",lambda e:errs.append(str(e)))
    await ph.evaluate("__memeplex.focusIdea('islam')"); await ph.wait_for_timeout(1500)
    await ph.evaluate("()=>{const p=document.getElementById('panel');const k=[...p.querySelectorAll('.k')].find(e=>/thinkers/i.test(e.textContent));k&&k.scrollIntoView({block:'center'})}"); await ph.wait_for_timeout(500)
    await ph.screenshot(path='thrives-phone-islam.png')
    await ph.evaluate("__games.play('thinker','s3')"); await ph.wait_for_timeout(600)
    P=await ph.evaluate("__games.puzzle('thinker','s3')"); await ph.evaluate("a=>__games.choose(a)",P['rounds'][0]['ans']); await ph.wait_for_timeout(600)
    await ph.screenshot(path='thrives-phone-thinkermatch-place.png')
    await b.close()
  srv.terminate(); print('errors',errs,'FAILS',fail); sys.exit(1 if fail or errs else 0)
asyncio.run(run())
