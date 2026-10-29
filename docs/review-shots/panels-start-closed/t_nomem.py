import asyncio,subprocess
from playwright.async_api import async_playwright
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8771"],cwd="site-v3",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); errs=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    pg=await b.new_page(viewport=dict(width=1440,height=900),reduced_motion="reduce")
    pg.on("pageerror",lambda e:errs.append(str(e)))
    await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1'); if(!sessionStorage.getItem('x')){localStorage.setItem('memeplex-ui',JSON.stringify({filter:true,search:true,legend:true}));sessionStorage.setItem('x','1')}")
    await pg.goto("http://localhost:8771/memeplex.html"); await pg.wait_for_function("window.__ui"); await pg.wait_for_timeout(1500)
    js="({filt:getComputedStyle(document.getElementById('filt')).display, search:document.getElementById('pSearch').classList.contains('open'), legendHidden:document.getElementById('legend').classList.contains('hid'), stored:localStorage.getItem('memeplex-ui')})"
    print("load1",await pg.evaluate(js))
    await pg.click("#tb [data-k=filter]"); await pg.wait_for_timeout(500)
    print("after open",await pg.evaluate(js))
    await pg.reload(); await pg.wait_for_function("window.__ui"); await pg.wait_for_timeout(1500)
    print("reload",await pg.evaluate(js))
    await pg.screenshot(path="shots/views/nomem-reload.png")
    print("errors",errs)
  srv.terminate()
asyncio.run(run())
