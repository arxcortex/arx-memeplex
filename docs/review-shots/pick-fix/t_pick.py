"""Dense-cluster picking test. Serve the folder holding memeplex.html on :8765, then: python3 t_pick.py [page]
Desktop: hover each crowded idea's exact screen point, check the tooltip; click one, check the panel.
Phone (390x844, touch, ?full=1, explore on): tap each crowded idea, check the panel; the camera is reset
between taps with window.__pickCam so every tap sees the same view. Also: labels never take hits, Snip still works."""
import sys, json, time
from playwright.sync_api import sync_playwright
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'memeplex.html'
HEAD = "()=>document.body.classList.contains('panel-open')?(document.querySelector('#panel h2,#panel h1')||{}).textContent||'':''"
def run(p, name, vp, touch):
    b = p.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader'])
    c = b.new_context(viewport=vp, has_touch=touch, is_mobile=touch, device_scale_factor=2 if touch else 1)
    c.add_init_script("try{localStorage.setItem('memeplex-help-seen','1');sessionStorage.setItem('memeplex-explore','1')}catch(e){}")
    pg = c.new_page(); pg.goto(f'http://localhost:8765/{PAGE}?full=1', wait_until='networkidle'); time.sleep(9)
    pg.evaluate("()=>{ if(window.__phone) __phone.set(false); }")
    cam0 = pg.evaluate("()=>{const c=__pickCam.get();__pickCam.set(...c);return __pickCam.get()}"); time.sleep(.5)
    ids = pg.evaluate("()=>fetch('https://arxcortex.github.io/arx-memeplex/ideas.json').then(r=>r.json()).then(j=>(j.ideas||j).map(d=>[d.id,d.name]))")
    P = pg.evaluate("ids=>ids.map(i=>__proj(i))", [i for i, _ in ids])
    vis = [(i, n, q) for (i, n), q in zip(ids, P) if q['ok'] and 0 < q['x'] < vp['width'] and 80 < q['y'] < vp['height'] - 80]
    dense = []
    for i, n, q in vis:
        k = sum(1 for j, _, r in vis if j != i and ((r['x'] - q['x'])**2 + (r['y'] - q['y'])**2)**.5 < 14)
        if k: dense.append((i, n, k))
    dense.sort(key=lambda t: -t[2]); dense = dense[:40]
    ok = 0; fails = []; ties = 0
    for i, n, k in dense:
        pg.evaluate("c=>__pickCam.set(c[0],c[1])", cam0); time.sleep(.25 if not touch else .6)
        q = pg.evaluate("id=>__proj(id)", i)
        exp = pg.evaluate("a=>__pick(a[0],a[1],a[2])", [q['x'], q['y'], 'touch' if touch else 'mouse'])
        if exp != i: ties += 1   # a genuine <=3px tie resolved to the nearer idea
        if touch:
            pg.touchscreen.tap(q['x'], q['y']); time.sleep(.7); got = pg.evaluate(HEAD)
        else:
            pg.mouse.move(q['x'] + 40, q['y'] + 40); pg.mouse.move(q['x'], q['y']); time.sleep(.15)
            got = pg.evaluate("()=>getComputedStyle(tip).visibility==='hidden'?'':tip.textContent.split(' · ')[0]")
        if got.strip().lower() == n.lower(): ok += 1
        else: fails.append((n, got, 'tie' if exp != i else ''))
    clk = None
    if not touch and dense:
        pg.evaluate("c=>__pickCam.set(c[0],c[1])", cam0); time.sleep(.3)
        i, n, k = dense[0]; q = pg.evaluate("id=>__proj(id)", i); pg.mouse.click(q['x'], q['y']); time.sleep(.8)
        clk = [n, pg.evaluate(HEAD)]; pg.keyboard.press('Escape'); time.sleep(.5)
    lab = pg.evaluate("()=>{let bad=0,n=0;document.querySelectorAll('.lbl').forEach(e=>{if(getComputedStyle(e).display==='none')return;const r=e.getBoundingClientRect();if(!r.width)return;n++;const t=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);if(t===e)bad++});return [n,bad]}")
    snip = pg.evaluate("()=>!!(window.__snip&&window.__snip.start)")
    if not touch and snip:
        pg.keyboard.press('s'); time.sleep(.4); ovs = pg.evaluate("()=>getComputedStyle(document.getElementById('snipov')).display")
        pg.mouse.move(300, 300); pg.mouse.down(); pg.mouse.move(500, 450, steps=5); pg.mouse.up(); time.sleep(2.5)
        snip = [snip, ovs, pg.evaluate("()=>getComputedStyle(document.getElementById('snipmod')).display")]
    b.close()
    return dict(dense=len(dense), correct=ok, ties=ties, fails=fails[:8], click=clk, labels_visible_hit=lab, snip=snip)
with sync_playwright() as p:
    out = {'desktop': run(p, 'desktop', {'width': 1440, 'height': 900}, False), 'phone': run(p, 'phone', {'width': 390, 'height': 844}, True)}
print(json.dumps(out, indent=1))
