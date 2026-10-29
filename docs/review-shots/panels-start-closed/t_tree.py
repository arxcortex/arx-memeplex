import asyncio,subprocess
from playwright.async_api import async_playwright
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8772"],cwd="site-v3",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    pg=await b.new_page(viewport=dict(width=1440,height=900))
    pg.on("pageerror",lambda e:errs.append(str(e)))
    await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
    await pg.goto("http://localhost:8772/memeplex.html?intro=none"); await pg.wait_for_function("window.__views"); await pg.wait_for_timeout(2000)
    print("check",await pg.evaluate("JSON.stringify(__views.check())"))
    print("dup positions per view",await pg.evaluate("""Object.fromEntries(Object.keys(__views.pos).map(k=>{const s=new Set(Object.values(__views.pos[k]).map(v=>{const q=v[0]||v;return [q.x,q.y,q.z].map(n=>n.toFixed(2)).join()}));return [k,__memeplex.ideas.length-s.size]}))"""))
    await pg.evaluate("__views.set('tree')"); await pg.wait_for_function("!__views.busy",timeout=20000); await pg.wait_for_timeout(2500)
    vis=await pg.evaluate("""[...document.querySelectorAll('.lbl')].filter(e=>e.style.display==='block').map(e=>e.textContent)""")
    roots=await pg.evaluate("__memeplex.ideas.filter(d=>d.root).map(d=>d.name)")
    print("roots shown",sum(r in vis for r in roots),"/",len(roots),[r for r in roots if r not in vis])
    print("opacity",await pg.evaluate("getComputedStyle(document.querySelector('.lbl').parentElement).opacity"))
    await pg.screenshot(path="shots/views/tree-roots.png")
    await pg.evaluate("__views.set('helix')"); await pg.wait_for_function("!__views.busy",timeout=20000); await pg.wait_for_timeout(1500)
    vis=await pg.evaluate("""[...document.querySelectorAll('.lbl')].filter(e=>e.style.display==='block').map(e=>e.textContent)""")
    print("helix roots shown",sum(r in vis for r in roots))
    print("errors",errs)
  srv.terminate()
asyncio.run(run())
