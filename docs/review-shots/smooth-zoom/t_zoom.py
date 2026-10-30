"""Zoom smoothness test. Serve docs/review-shots/snip-share/ on :8766, then: python3 t_zoom.py [page]"""
import sys, json, time
from playwright.sync_api import sync_playwright
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'memeplex.html'
REC = """ms=>{const out=window.__rec=[];window.__recDone=false;const t0=performance.now();const f=()=>{out.push([performance.now()-t0,__zoom.dist()]);if(performance.now()-t0<ms)requestAnimationFrame(f);else window.__recDone=true};requestAnimationFrame(f)}"""
def rec_wait(pg):
    while not pg.evaluate("()=>window.__recDone"): time.sleep(.1)
    return pg.evaluate("()=>window.__rec")
def page(p, vp, touch=False, reduced=False):
    b = p.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader'])
    c = b.new_context(viewport=vp, has_touch=touch, is_mobile=touch, reduced_motion='reduce' if reduced else 'no-preference')
    c.add_init_script("try{localStorage.setItem('memeplex-help-seen','1');sessionStorage.setItem('memeplex-explore','1')}catch(e){}")
    pg = c.new_page(); pg.goto(f'http://localhost:8766/{PAGE}?full=1', wait_until='networkidle'); time.sleep(9)
    pg.evaluate("()=>{ if(window.__phone) __phone.set(false); __zoom.still(); }"); time.sleep(1.5)
    return b, pg
def wheel(pg, x, y, dy, mode=0, ctrl=False, n=1):
    pg.evaluate("a=>{const c=document.querySelector('#stage canvas');for(let i=0;i<a[5];i++)c.dispatchEvent(new WheelEvent('wheel',{clientX:a[0],clientY:a[1],deltaY:a[2],deltaMode:a[3],ctrlKey:a[4],bubbles:true,cancelable:true}))}", [x, y, dy, mode, ctrl, n])
out = {}
with sync_playwright() as p:
    b, pg = page(p, {'width': 1440, 'height': 900})
    # 2. cursor anchoring: the world point under the cursor stays under it
    x, y = 1000, 300
    w = pg.evaluate("a=>__zoom.under(a[0],a[1])", [x, y])
    wheel(pg, x, y, -100, n=4); time.sleep(1.5)
    sx, sy = pg.evaluate("a=>__zoom.screen(a)", w); out['anchor_px_drift'] = round(((sx-x)**2 + (sy-y)**2)**.5, 2)
    pg.keyboard.press('r'); time.sleep(2.5); pg.evaluate('()=>__zoom.still()'); time.sleep(1)
    # 1. smooth steps: 10 mouse-wheel notches over ~0.5 s, record distance every frame
    d0 = pg.evaluate("()=>__zoom.dist()")
    pg.evaluate(REC, 2500)
    for _ in range(10): pg.mouse.move(720, 450); pg.mouse.wheel(0, -100); time.sleep(.05)
    r = rec_wait(pg); ds = [v for _, v in r]; tot = abs(ds[-1] - ds[0]) or 1e-9
    steps = [abs(ds[i+1] - ds[i]) for i in range(len(ds)-1)]
    out['wheel_steps'] = dict(start=round(d0, 2), end=round(ds[-1], 2), frames=len(ds), max_step_frac=round(max(steps)/tot, 3), monotonic=all(ds[i+1] <= ds[i] + 1e-6 for i in range(len(ds)-1)))
    # 3. line mode (deltaMode 1, 3 lines) matches ~48 px of pixel mode; 4. trackpad pinch (ctrl, deltaY 2 x50) zooms meaningfully
    def ratio(fn):
        a = pg.evaluate("()=>__zoom.dist()"); fn(); time.sleep(1.5); return pg.evaluate("()=>__zoom.dist()") / a
    rl = ratio(lambda: wheel(pg, 720, 450, 3, mode=1)); rp = ratio(lambda: wheel(pg, 720, 450, 48))
    rpinch = ratio(lambda: wheel(pg, 720, 450, -2, ctrl=True, n=50))
    rbig = ratio(lambda: wheel(pg, 720, 450, 5000)); rref = ratio(lambda: wheel(pg, 720, 450, 120))
    out['line_vs_pixel'] = [round(rl, 4), round(rp, 4)]; out['ctrl_pinch_ratio'] = round(rpinch, 3); out['clamped_5000_vs_120'] = [round(rbig, 3), round(rref, 3)]
    # 5. label layout skipped when idle
    pg.evaluate("()=>__zoom.still()"); time.sleep(2); a = pg.evaluate("()=>__zoom.labelRuns"); time.sleep(2); out['label_runs_idle_2s'] = pg.evaluate("()=>__zoom.labelRuns") - a
    # 6. frame cost during zoom
    pg.evaluate("""()=>{window.__ft=null;const t=[];let l=performance.now();const s=l;const f=()=>{const n=performance.now();t.push(n-l);l=n;if(n-s<2000)requestAnimationFrame(f);else{t.sort((a,b)=>a-b);window.__ft=[t[Math.floor(t.length*.5)],t[Math.floor(t.length*.95)]]}};requestAnimationFrame(f)}""")
    for _ in range(20): wheel(pg, 720, 450, 60 if _ % 2 else -60); time.sleep(.08)
    while not pg.evaluate("()=>window.__ft"): time.sleep(.1)
    out['frame_ms_p50_p95_swiftshader'] = [round(v, 1) for v in pg.evaluate("()=>window.__ft")]
    # 7. Reset (R) goes home and cancels any zoom target
    wheel(pg, 720, 450, -100, n=3); time.sleep(.05); pg.keyboard.press('r'); time.sleep(2.5)
    out['reset'] = dict(target_cleared=pg.evaluate("()=>__zoom.target===null"), dist_after=round(pg.evaluate("()=>__zoom.dist()"), 2))
    # 8. tours: start the first tour, wheel during its camera move, check the tour is not fought
    if pg.evaluate("()=>!!(window.__tours&&__tours.list.some(t=>!t.placeholder))"):
        tid = pg.evaluate("()=>__tours.list.filter(t=>!t.placeholder)[0].id"); pg.evaluate("id=>__tours.start(id)", tid); time.sleep(.3)
        pg.evaluate("()=>{const b=document.querySelector('#tourbar button.nx,#tourbar [data-a=next]');b&&b.click()}"); time.sleep(.2)
        busy = pg.evaluate("()=>__zoom.busy()"); wheel(pg, 720, 450, -100, n=3); tgt = pg.evaluate("()=>__zoom.target")
        time.sleep(2.5); out['tour'] = dict(id=tid, step=pg.evaluate("()=>__tours.step"), busy_during_move=busy, target_during_move=tgt); pg.evaluate("()=>__tours.stop()")
    else: out['tour'] = 'no tours in this build'
    # 9. Snip still works
    if not pg.evaluate("()=>!!window.__snip"): out['snip'] = 'no snip in this build'
    else:
     pg.keyboard.press('Escape'); time.sleep(.5); pg.keyboard.press('s'); time.sleep(.4)
     ov = pg.evaluate("()=>getComputedStyle(document.getElementById('snipov')).display")
     pg.mouse.move(300, 300); pg.mouse.down(); pg.mouse.move(500, 450, steps=5); pg.mouse.up(); time.sleep(2.5)
     out['snip'] = [ov, pg.evaluate("()=>getComputedStyle(document.getElementById('snipmod')).display")]
    b.close()
    # 10. reduced motion: instant
    b, pg = page(p, {'width': 1440, 'height': 900}, reduced=True)
    a = pg.evaluate("()=>__zoom.dist()"); wheel(pg, 720, 450, -100); bb = pg.evaluate("()=>__zoom.dist()")
    out['reduced_motion'] = dict(changed_same_tick=abs(bb - a) > 1e-3, target_left=pg.evaluate("()=>__zoom.target")); b.close()
    # 11. phone touch pinch (two fingers spreading) zooms in smoothly
    b, pg = page(p, {'width': 390, 'height': 844}, touch=True)
    cdp = pg.context.new_cdp_session(pg); a = pg.evaluate("()=>__zoom.dist()")
    pg.evaluate(REC, 2000)
    tp = lambda t, pts: cdp.send('Input.dispatchTouchEvent', {'type': t, 'touchPoints': [{'x': x, 'y': y, 'id': i} for i, (x, y) in enumerate(pts)]})
    tp('touchStart', [(170, 420), (220, 420)])
    for s in range(1, 21): tp('touchMove', [(170 - s*4, 420), (220 + s*4, 420)]); time.sleep(.02)
    tp('touchEnd', []); r = rec_wait(pg); ds = [v for _, v in r]; tot = abs(ds[-1]-ds[0]) or 1e-9
    out['phone_pinch'] = dict(start=round(a, 2), end=round(ds[-1], 2), max_step_frac=round(max(abs(ds[i+1]-ds[i]) for i in range(len(ds)-1))/tot, 3))
    b.close()
print(json.dumps(out, indent=1))
