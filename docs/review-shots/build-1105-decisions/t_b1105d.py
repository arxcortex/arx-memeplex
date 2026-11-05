# Checks the 2026-11-05 decisions on PR #67: two Pan-Slavism influence lines,
# unchanged dates, no Containment/Bush Doctrine additions, all five idea panels,
# and Russia's National philosophy list on desktop and phone. Run from this folder.
import asyncio, subprocess, sys, json
from playwright.async_api import async_playwright

R = '../../../'
PORT = 8971
NEW = ['westernizers', 'pan_slavism', 'bush_doctrine', 'containment', 'russian_cosmism']
EDGES = [('slavophilia', 'pan_slavism'), ('official_nationality', 'pan_slavism')]
YEARS = {'westernizers': (1840, True), 'pan_slavism': (1848, False), 'russian_cosmism': (1880, True)}
RU = ['slavophilia', 'westernizers', 'russian_cosmism']

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
                await pg.wait_for_function('window.__memeplex && __memeplex.ideas && __memeplex.ideas.length && window.__pol', polling=500)
                await pg.wait_for_timeout(3500)
                n = await pg.evaluate('__memeplex.ideas.length')
                print(tag, 'ideas', n)
                if n != 298:
                    fail.append((tag, 'idea count', n))
                for a, c in EDGES:
                    linked = await pg.evaluate(f"__tours.linked('{a}','{c}')")
                    print(tag, 'edge', a, '->', c, linked)
                    if not linked:
                        fail.append((tag, 'missing edge', a, c))
                forbidden = await pg.evaluate("""({containment:__memeplex.ideas.find(d=>d.id=='containment').parents,
                  bush:__memeplex.ideas.find(d=>d.id=='bush_doctrine').parents})""")
                if 'cold_war_liberalism' in forbidden['containment'] or 'containment' in forbidden['bush'] or 'bush_doctrine' in forbidden['containment']:
                    fail.append((tag, 'forbidden lineage', forbidden))
                for iid, (year, approx) in YEARS.items():
                    got = await pg.evaluate(f"(()=>{{const d=__memeplex.ideas.find(d=>d.id=='{iid}');return [d.year,d.year_approx]}})()")
                    if got != [year, approx]:
                        fail.append((tag, 'year', iid, got))
                for iid in NEW:
                    await pg.evaluate(f"__memeplex.focusIdea('{iid}')")
                    await pg.wait_for_timeout(1600)
                    txt = await pg.inner_text('#panel')
                    name = await pg.evaluate(f"__memeplex.ideas.find(d=>d.id=='{iid}').name")
                    ok = name in txt
                    if iid == 'pan_slavism':
                        ok = ok and 'Slavophilia' in txt and 'Official Nationality' in txt
                    print(tag, iid, 'panel ok' if ok else 'PANEL FAIL')
                    if not ok:
                        fail.append((tag, 'panel', iid))
                    if tag == 'desk' or iid in ('pan_slavism', 'westernizers', 'russian_cosmism'):
                        await pg.screenshot(path=f'{tag}-{iid}.jpg', quality=70)
                await ctx.close()

                # A separate National-view load exercises the shared-link route and its Russia list.
                ctx = await b.new_context(viewport=vp, is_mobile=mob, has_touch=mob)
                pg = await ctx.new_page()
                pg.on('pageerror', lambda e, tag=tag: errs.append(f'{tag}: {e}'))
                pg.on('console', lambda m, tag=tag: errs.append(f'{tag}: {m.text}') if m.type == 'error' and 'ReadPixels' not in m.text else None)
                for f in ['ideas.json', 'thinkers.json', 'axes.json', 'currents.json', 'politics.json', 'national.json', 'impact.json']:
                    await pg.route('**/' + f, (lambda f: (lambda r: r.fulfill(status=200, content_type='application/json', body=open(R + f).read())))(f))
                await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
                await pg.goto(f'http://localhost:{PORT}/memeplex.html?intro=none#v=national&ns=philosophy')
                await pg.wait_for_function('window.__pol && window.__views && !__views.busy', timeout=30000, polling=500)
                await pg.wait_for_timeout(2500)
                await pg.evaluate("__pol.setSub('philosophy');__pol.setCountry('ru')")
                await pg.wait_for_timeout(1200)
                state = await pg.evaluate("({sub:__pol.sub,country:__pol.country,fac:[...(__pol.fac||[])]})")
                buttons = await pg.locator('#polkey [data-go]').evaluate_all('(els)=>els.map(e=>e.dataset.go)')
                if not buttons:
                    await pg.locator('#polkey [data-sub="philosophy"]').click()
                    await pg.wait_for_timeout(600)
                    await pg.evaluate("__pol.setCountry('ru')")
                    await pg.wait_for_timeout(600)
                    buttons = await pg.locator('#polkey [data-go]').evaluate_all('(els)=>els.map(e=>e.dataset.go)')
                text = await pg.inner_text('#polkey')
                ok = state['sub'] == 'philosophy' and state['country'] == 'ru' and all(i in buttons for i in RU) and 'slavophilism' not in buttons
                print(tag, 'national ru philosophy buttons', buttons, 'list ok' if ok else 'LIST FAIL')
                if not ok:
                    fail.append((tag, 'national ru philosophy', state, buttons, text))
                # The formerly missing cosmism entry must open a real panel from the National list.
                await pg.locator('#polkey details').evaluate('(el)=>el.open=true')
                await pg.locator('#polkey [data-go="russian_cosmism"]').click()
                await pg.wait_for_timeout(1500)
                panel = await pg.inner_text('#panel')
                if 'Russian cosmism' not in panel or 'NATIONAL PHILOSOPHY' not in panel.upper() or 'RUSSIA' not in panel.upper():
                    fail.append((tag, 'national cosmism panel', panel))
                await pg.screenshot(path=f'{tag}-national-ru-philosophy.jpg', quality=70)
                await ctx.close()
            await b.close()
    finally:
        srv.terminate()
    print('errors', errs[:10], 'FAILS', fail)
    sys.exit(1 if fail or errs else 0)

asyncio.run(run())
