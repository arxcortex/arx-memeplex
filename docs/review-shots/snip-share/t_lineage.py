# Lineage test (desktop): clicking an idea lights every ancestor, past root ideas, back to the oldest one, and names them.
# Judaism (Rabbinic Judaism, a root) must light and name the chain back to Canaanite religion; its root symbol is the Star of David.
# Run from this folder: python3 t_lineage.py   (set SHOTS=dir to save screenshots there)
import asyncio,subprocess,sys,socket,os,json
from playwright.async_api import async_playwright
R='../../../'; SHOTS=os.environ.get('SHOTS')
with socket.socket() as _s: _s.bind(('127.0.0.1',0)); PORT=_s.getsockname()[1]
I={d['id']:d for d in json.load(open(R+'ideas.json'))}
CHAIN=['rabbinic_judaism','second_temple_judaism','ancient_israelite_religion','canaanite_religion']
async def run():
  srv=subprocess.Popen(["python3","-m","http.server",str(PORT)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); fail=[]; errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    pg=await (await b.new_context(viewport=dict(width=1440,height=900))).new_page(); pg.on("pageerror",lambda e:errs.append(str(e)))
    for f in ['ideas.json','thinkers.json','axes.json','currents.json','politics.json','national.json','impact.json']:
      await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
    await pg.route("**/arx-memeplex/quiz/quiz-bank.json",lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+'quiz/quiz-bank.json').read()))
    await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
    await pg.goto(f"http://localhost:{PORT}/memeplex.html?intro=none"); await pg.wait_for_function("window.__viz && window.__views && !__views.busy",timeout=30000); await pg.wait_for_timeout(2500)
    await pg.evaluate("__memeplex.controls.autoRotate=false")
    if not I['rabbinic_judaism'].get('root'): fail.append(('data','Rabbinic Judaism should stay a root'))
    sym=dict(await pg.evaluate("window.__symbols"))
    if sym.get('rabbinic_judaism')!='svg:starofdavid': fail.append(('symbol','Judaism should carry the Star of David',sym.get('rabbinic_judaism')))
    await pg.evaluate("__memeplex.focusIdea('rabbinic_judaism')"); await pg.wait_for_timeout(2500)
    if SHOTS: await pg.screenshot(path=os.path.join(SHOTS,'judaism-star-after.png'))
    lit=set(await pg.evaluate("__memeplex.ideas.filter(d=>d.star.halo.material.opacity>0.4).map(d=>d.id)"))
    miss=[k for k in CHAIN if k not in lit]
    if miss: fail.append(('lit','ancestors not lit',miss))
    # every mapped ancestor is lit, not only the chain
    up=set(); st=['rabbinic_judaism']
    while st:
      for q in I[st.pop()].get('parents',[]):
        if q in I and q not in up: up.add(q); st.append(q)
    if up-lit: fail.append(('lit','mapped ancestors not lit',sorted(up-lit)))
    await pg.click('#panel [data-act=lineage]'); await pg.wait_for_timeout(3500)
    names=await pg.evaluate("""(C)=>{return C.map(k=>{const d=__memeplex.ideas.find(x=>x.id===k);const el=[...document.querySelectorAll('div')].find(e=>e.textContent===d.name&&e.style.display==='block');return [k,!!el]})}""",CHAIN)
    hid=[k for k,v in names if not v]
    if hid: fail.append(('labels','lineage names hidden after Trace lineage',hid))
    if SHOTS: await pg.screenshot(path=os.path.join(SHOTS,'judaism-lineage-after.png'))
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(600)
    await pg.evaluate("document.getElementById('symbtn').click()"); await pg.wait_for_timeout(1200)
    about=await pg.evaluate("document.querySelector('#symabout .grid').textContent")
    if 'Star of David' not in about or 'Star_of_David.svg' not in about: fail.append(('about','Star of David missing from About the symbols'))
    await b.close()
  srv.terminate()
  if errs: fail.append(('pageerror',errs[:3]))
  print('lit chain:',' <- '.join(CHAIN)); print('FAIL' if fail else 'PASS', fail); sys.exit(1 if fail else 0)
asyncio.run(run())
