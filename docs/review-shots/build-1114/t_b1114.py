# Checks the 2026-11-14 build: the end-of-empires-1918 guided tour and the leninism -> self_determination line (desktop + phone), views and tour edges.
import asyncio, subprocess, sys, json
from playwright.async_api import async_playwright

R = '../../../'
PORT = 9101
TOUR = 'end-of-empires-1918'
STEPS = ['hobson_imperialism', 'leninist_theory_of_imperialism', 'leninism', 'self_determination', 'wilsonianism', 'liberal_international_order']
EDGES = [('hobson_imperialism', 'leninist_theory_of_imperialism'), ('leninism', 'leninist_theory_of_imperialism'), ('leninism', 'self_determination'), ('wilsonianism', 'self_determination'), ('wilsonianism', 'liberal_international_order')]
EXPECT = 348

async def run():
    srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT)], cwd='../snip-share', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(1)
    fail, errs = [], []
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
            for tag, vp, mob in [('desk', dict(width=1440, height=900), False), ('phone', dict(width=390, height=844), True)]:
                ctx = await b.new_context(viewport=vp, is_mobile=mob, has_touch=mob)
                pg = await ctx.new_page()
                pg.on('pageerror', lambda e, tag=tag: errs.append(f'{tag}: {e}'))
                pg.on('console', lambda m, tag=tag: errs.append(f'{tag}: {m.text}') if m.type == 'error' and 'ReadPixels' not in m.text else None)
                for f in ['ideas.json', 'thinkers.json', 'axes.json', 'currents.json', 'politics.json', 'national.json', 'impact.json']:
                    await pg.route('**/' + f, (lambda f: (lambda r: r.fulfill(status=200, content_type='application/json', body=open(R + f).read())))(f))
                await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1');sessionStorage.setItem('memeplex-full','1')")
                await pg.goto(f'http://localhost:{PORT}/memeplex.html?intro=none&full=1')
                await pg.wait_for_function('window.__memeplex && __memeplex.ideas && __memeplex.ideas.length && window.__tours', polling=500)
                await pg.wait_for_timeout(3500)
                n = await pg.evaluate('__memeplex.ideas.length')
                print(tag, 'ideas', n)
                if n != EXPECT:
                    fail.append(('count', n))
                chk = await pg.evaluate('window.__views&&__views.check?__views.check():null')
                print(tag, 'views.check', json.dumps(chk))
                if chk is None or any((v if isinstance(v, (int, float)) else len(v) if isinstance(v, list) else 0) for v in chk.values()):
                    fail.append((tag, 'views', chk))
                bad = await pg.evaluate('__tours.validate()')
                neg = await pg.evaluate("__tours.validate([{id:'x',steps:[{id:'platonic_forms'},{id:'marxism'}]}])")
                print(tag, 'tour bad edges', bad, '| negative control fires', bool(neg))
                if bad or not neg:
                    fail.append((tag, 'tour edges'))
                for a, c in EDGES:
                    if not await pg.evaluate(f"__tours.linked('{a}','{c}')"):
                        fail.append((tag, 'edge', a, c))
                t = await pg.evaluate(f"__tours.list.find(t=>t.id=='{TOUR}')")
                if not t or t['steps'] != STEPS:
                    fail.append((tag, 'tour missing or wrong steps', t)); await ctx.close(); continue
                await pg.evaluate("__tours.menu()"); await pg.wait_for_timeout(500)
                inm = await pg.evaluate(f"!!document.querySelector('#tourmenu button[data-t=\"{TOUR}\"]')")
                print(tag, 'in tour menu', inm)
                if not inm:
                    fail.append((tag, 'tour not in menu'))
                await pg.screenshot(path=f'{tag}-menu.jpg', quality=70)
                await pg.evaluate("__tours.menu()")
                await pg.evaluate(f"__tours.start('{TOUR}')"); await pg.wait_for_timeout(1200)
                names = await pg.evaluate("__tours.list.find(t=>t.id=='%s').steps.map(k=>__memeplex.ideas.find(d=>d.id==k).name)" % TOUR)
                for k in range(len(STEPS)):
                    await pg.wait_for_timeout(2600)
                    st = await pg.evaluate('__tours.step')
                    txt = await pg.inner_text('#tourbar'); vis = await pg.is_visible('#tourbar')
                    ok = vis and st == [TOUR, k] and names[k] in txt and f'{k + 1} / {len(STEPS)}' in txt
                    print(tag, k + 1, STEPS[k], 'ok' if ok else 'BAD', '|', txt.split('\n')[0][:110])
                    if not ok:
                        fail.append((tag, 'step', k, st))
                    await pg.screenshot(path=f'{tag}-tour-{k + 1:02d}.jpg', quality=70)
                    await pg.evaluate("document.querySelector('#tourbar [data-a=next]').click()")
                await pg.wait_for_timeout(800)
                done = not await pg.is_visible('#tourbar') and await pg.evaluate('__tours.step') is None
                print(tag, 'tour finished', done)
                if not done:
                    fail.append((tag, 'tour did not finish'))
                await ctx.close()
            await b.close()
    finally:
        srv.terminate()
    print('errors', errs[:10], 'FAILS', fail)
    sys.exit(1 if fail or errs else 0)

asyncio.run(run())
