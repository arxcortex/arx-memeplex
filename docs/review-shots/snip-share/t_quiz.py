# Quiz test (desktop + phone). Run from this folder: python3 t_quiz.py   (set SHOTS=dir to save screenshots there)
# 1. The page's JS scorer (QUIZ SCORE block) gives the same results as quiz/score.py on fixed, made-up answer sets.
# 2. Each quiz is taken by clicking the five answer buttons with fixed answers; results render and match quiz/score.py.
# 3. Show on map lights the matched ideas; the share card renders; the share link reopens the results with the ideas lit.
# 4. Full/Short choice when a bank has more than 50; Short and Combined draws are balanced; scenario questions are labelled;
#    a bank copy with a separate setting field shows it above the question (counts are read from the file, no code change).
# 5. No page errors or console errors.
import asyncio,subprocess,sys,socket,os,json,random,copy
from playwright.async_api import async_playwright
R='../../../'; SHOTS=os.environ.get('SHOTS')
sys.path.insert(0,R+'quiz'); import score as PY
PY.load(R,R+'quiz/quiz-bank.json'); BANK=json.load(open(R+'quiz/quiz-bank.json'))
with socket.socket() as _s: _s.bind(('127.0.0.1',0)); PORT=_s.getsockname()[1]
def norm(r): return json.loads(json.dumps({k:r[k] for k in ('status','plane','top','per_country')}))
def lists(b):
  q=b['quizzes']; return {'politics':q['politics'],'philosophy':q['philosophy'],'combined':q['politics']+q['philosophy']+[i for i in q.get('combined',[]) if i not in q['politics']+q['philosophy']]}
# made-up answer sets: the reference profiles, restricted to each quiz, plus seeded random sets
def answer_sets():
  out={}; L=lists(BANK); rnd=random.Random(7)
  for n,a in PY.profiles().items():
    out[n+' / all']=a
    for k,ids in L.items(): out[n+' / '+k]={i:a[i] for i in ids}
  for k,ids in L.items():
    for j in range(8): out[f'random {k} {j}']={i:rnd.choice([-2,-1,0,1,2]) for i in ids}
    for v in (2,-2,0): out[f'flat {k} {v}']={i:v for i in ids}
    out[f'partial {k}']={i:rnd.choice([-2,2]) for i in ids[::3]}
  return out
def fixed(ids,k):  # deterministic click pattern for a quiz run: answer by the sign of the summed marxism+liberalism+abstraction weight
  Q=PY.QS; sg=lambda x:(x>0)-(x<0)
  ax={'politics':('marxism','hierarchy'),'philosophy':('abstraction','christianity'),'combined':('hierarchy','enlightenment_liberalism')}[k]
  return {i:2*sg(sum(Q[i]['weights'].get(a,0) for a in ax)) if any(a in Q[i]['weights'] for a in ax) else (1 if int(i[1:])%2 else -1) for i in ids}
def setting_bank():  # test copy: p51 given a separate 'setting' field (the bank may add one later)
  b=copy.deepcopy(BANK); q=next(x for x in b['questions'] if x['id']=='p51'); q['setting']='TEST SETTING p51'; return b
def cover(L,pool,mins):
  Q=PY.QS; bad=[]
  for a in PY.AX:
    for sg in (1,-1):
      have=sum(1 for i in pool if (Q[i]['weights'].get(a,0)>0)-(Q[i]['weights'].get(a,0)<0)==sg)
      got=sum(1 for i in L if (Q[i]['weights'].get(a,0)>0)-(Q[i]['weights'].get(a,0)<0)==sg)
      if got<min(have,mins(a)): bad.append((a,sg,got,have))
  return bad
async def run():
  srv=subprocess.Popen(["python3","-m","http.server",str(PORT)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); fail=[]; errs=[]
  async def shot(pg,n):
    if SHOTS: await pg.screenshot(path=os.path.join(SHOTS,n+'.png'))
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    async def page(hash='',mob=False,bank=None,qs=''):
      ctx=await b.new_context(viewport=dict(width=390,height=844) if mob else dict(width=1440,height=900),is_mobile=mob,has_touch=mob,device_scale_factor=2 if mob else 1); pg=await ctx.new_page()
      tag='phone' if mob else 'desk'; pg.on("pageerror",lambda e:errs.append(f"{tag}: {e}"))
      pg.on("console",lambda m:errs.append(f"{tag} console: {m.text}") if m.type=='error' and 'Failed to load resource' not in m.text else None)
      for f in ['ideas.json','thinkers.json','axes.json','currents.json','politics.json','national.json','impact.json']:
        await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
      body=json.dumps(bank) if bank else open(R+'quiz/quiz-bank.json').read()
      await pg.route("**/arx-memeplex/quiz/quiz-bank.json",lambda r,q=None:r.fulfill(status=200,content_type="application/json",body=body))
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      await pg.goto(f"http://localhost:{PORT}/memeplex.html?intro=none{'&full=1' if mob else ''}{qs}{hash}"); await pg.wait_for_function("window.__quiz && window.__memeplex && __memeplex.ideas.length",polling=500,timeout=30000); await pg.wait_for_timeout(3000)
      await pg.evaluate("__memeplex.controls.autoRotate=false"); return ctx,pg
    async def take(pg,k,mode,tag,shots=True):
      """open the menu, pick the quiz, click every answer; returns the answers given"""
      await pg.click('#menubtn'); await pg.wait_for_timeout(300)
      if not await pg.evaluate("!!document.querySelector('#menu [data-k=quiz]')"): fail.append((tag,'no Quizzes in the menu')); return {}
      await pg.click('#menu [data-k=quiz]'); await pg.wait_for_selector(f'#quiz [data-q={k}][data-m={mode}]',timeout=15000)
      if shots and (k=='politics' or tag=='phone'): await shot(pg,f'quiz-{tag}-menu')
      await pg.click(f'#quiz [data-q={k}][data-m={mode}]'); await pg.wait_for_timeout(200)
      ids=await pg.evaluate("__quiz.state.list"); ans=fixed(ids,k)
      for j,i in enumerate(ids):
        st=await pg.evaluate("({id:__quiz.state.list[__quiz.state.i],n:document.querySelectorAll('#quiz .qz-ans button').length,lab:[...document.querySelectorAll('#quiz .qz-ans button')].map(b=>b.textContent),set:(document.querySelector('#quiz .qz-set')||{}).textContent||''})")
        if st['id']!=i or st['n']!=5: fail.append((tag,k,'question',j,st)); break
        if j==0 and (st['lab'][0]!='Strongly agree' or st['lab'][-1]!='Strongly disagree'): fail.append((tag,k,'button order',st['lab']))
        if shots and j==3: await shot(pg,f'quiz-{tag}-{k}-question')
        if j==1 and k=='politics' and mode=='full':  # Back keeps the answer and returns to it
          await pg.click('#quiz [data-a=back]'); await pg.wait_for_timeout(100)
          if await pg.evaluate("document.querySelector('#quiz .qz-ans button[aria-pressed=true]').dataset.v")!=str(ans[ids[0]]): fail.append((tag,'back lost the answer'))
          await pg.click(f'#quiz .qz-ans button[data-v="{ans[ids[0]]}"]'); await pg.wait_for_timeout(80)
        if tag=='phone': await pg.tap(f'#quiz .qz-ans button[data-v="{ans[i]}"]')
        else: await pg.click(f'#quiz .qz-ans button[data-v="{ans[i]}"]')
        await pg.wait_for_timeout(40)
      await pg.wait_for_selector('#quiz .qz-plane svg',timeout=10000); return ans,ids
    async def check_results(pg,k,ans,tag):
      got=await pg.evaluate("({r:{status:__quiz.last.status,plane:__quiz.last.plane,top:__quiz.last.top,per_country:__quiz.last.per_country},li:document.querySelectorAll('#quiz .qz-top li').length,open:__quiz.open})")
      ordered={i:ans[i] for i in lists(BANK).get(k,[]) if i in ans} or ans
      want=norm(PY.score(ordered))
      if got['r']!=want: fail.append((tag,k,'results differ from score.py',got['r'],want))
      if not got['open'] or (want['status']!='not enough signal' and got['li']!=5): fail.append((tag,k,'results not shown',got['li'],got['open']))
      return got['r']
    # ---- 1. scorer parity, in the page
    ctx,pg=await page(); sets=answer_sets(); bad=0
    await pg.evaluate("__quiz.loadBank()")
    res=await pg.evaluate("S=>{return Object.fromEntries(Object.entries(S).map(([n,a])=>{const r=__quizScore.score(a,__quiz.bank,__quiz.axes,__memeplex.ideas);return [n,{status:r.status,plane:r.plane,top:r.top,per_country:r.per_country}]}))}",sets)
    for n,a in sets.items():
      if norm(PY.score(a))!=res[n]: bad+=1; fail.append(('parity',n,res[n],norm(PY.score(a)))); print('PARITY DIFF',n,json.dumps(res[n])[:600],json.dumps(norm(PY.score(a)))[:600])
    print('parity',len(sets)-bad,'of',len(sets),'answer sets identical to quiz/score.py')
    # ---- 2+3. desktop: each quiz with fixed answers
    runs={}
    for k,mode in (('politics','full'),('philosophy','short' if len(BANK['quizzes']['philosophy'])>50 else 'full'),('combined','full')):
      ans,ids=await take(pg,k,mode,'desk'); r=await check_results(pg,k,ans,'desk'); runs[k]=r
      print('desk',k,len(ids),'answers',r['status'],r['top'][:3],r['plane'])
      if k=='politics': await shot(pg,'quiz-desk-results')
      await pg.click('#quiz .x'); await pg.wait_for_timeout(200)
    # show on map (politics again, from a fresh run)
    ans,ids=await take(pg,'politics','short','desk',False); r=await check_results(pg,'politics',ans,'desk')
    await pg.evaluate("document.querySelector('#quiz .box').scrollIntoView()"); await pg.click('#quiz [data-a=map]'); await pg.wait_for_timeout(2200)
    m=await pg.evaluate("({hl:[...__quizHL],bar:document.getElementById('quizbar').classList.contains('open'),open:__quiz.open,qz:document.querySelectorAll('.lbl.qz').length,lit:__memeplex.ideas.filter(d=>d.star.halo.material.opacity>0.5).map(d=>d.id),hash:location.hash})")
    if sorted(m['hl'])!=sorted(i for i,_ in r['top']) or not m['bar'] or m['open']: fail.append(('desk','show on map',m))
    if sorted(m['lit'])!=sorted(m['hl']): fail.append(('desk','map lit set',m['lit']))
    await pg.wait_for_timeout(600); h=await pg.evaluate("location.hash")
    if 'quiz=politics' not in h or 'qa=' not in h: fail.append(('desk','hash missing quiz state',h))
    await shot(pg,'quiz-desk-map')
    # Results button on the bar reopens; share card renders 1080x1920
    await pg.click('#quizbar [data-a=res]'); await pg.wait_for_timeout(300)
    await pg.click('#quiz [data-a=card]'); await pg.wait_for_function("document.getElementById('sharecard')&&getComputedStyle(document.getElementById('sharecard')).display!=='none'&&document.querySelector('#sharecard img').naturalWidth>0",timeout=15000)
    c=await pg.evaluate("({w:document.querySelector('#sharecard img').naturalWidth,h:document.querySelector('#sharecard img').naturalHeight,dl:document.querySelector('#sharecard .sc-dl').download})")
    if (c['w'],c['h'])!=(1080,1920) or c['dl']!='memeplex-quiz-politics.png': fail.append(('desk','share card',c))
    await shot(pg,'quiz-desk-card')
    if SHOTS:
      png=await pg.evaluate("fetch(document.querySelector('#sharecard img').src).then(r=>r.arrayBuffer()).then(b=>Array.from(new Uint8Array(b)))"); open(os.path.join(SHOTS,'quiz-card-politics.png'),'wb').write(bytes(png))
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(200)
    if not await pg.evaluate("__quiz.open"): fail.append(('desk','Escape on the card closed the quiz too'))
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(200)
    if await pg.evaluate("__quiz.open"): fail.append(('desk','Escape did not close the quiz'))
    link=await pg.evaluate("__quiz.link()"); top0=r['top']
    # Clear on the bar puts the map back
    await pg.click('#quizbar [data-a=clr]'); await pg.wait_for_timeout(900)
    m=await pg.evaluate("({hl:__quizHL.size,bar:document.getElementById('quizbar').classList.contains('open'),qz:document.querySelectorAll('.lbl.qz').length})")
    if m['hl'] or m['bar'] or m['qz']: fail.append(('desk','clear',m))
    await ctx.close()
    # share link reopens the results with the matched ideas lit
    ctx,pg=await page('#'+link.split('#',1)[1]); await pg.wait_for_function("__quiz.open && __quiz.last",timeout=20000); await pg.wait_for_timeout(2500)
    m=await pg.evaluate("({top:__quiz.last.top,hl:[...__quizHL],bar:document.getElementById('quizbar').classList.contains('open'),li:document.querySelectorAll('#quiz .qz-top li').length,lit:__memeplex.ideas.filter(d=>d.star.halo.material.opacity>0.5).map(d=>d.id)})")
    if m['top']!=top0 or sorted(m['hl'])!=sorted(i for i,_ in top0) or not m['bar'] or m['li']!=5 or sorted(m['lit'])!=sorted(m['hl']): fail.append(('desk','link reopen',m,top0))
    await shot(pg,'quiz-desk-link-reopened'); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(1500); await shot(pg,'quiz-desk-link-map')
    await ctx.close()
    # ---- 4. Full/Short, balanced draws, scenario label, setting field
    BB=setting_bank(); ctx,pg=await page('',False,BB); Q=PY.QS; P=BANK['quizzes']
    await pg.click('#menubtn'); await pg.wait_for_timeout(200); await pg.click('#menu [data-k=quiz]'); await pg.wait_for_selector('#quiz [data-m=full]')
    opts=await pg.evaluate("[...document.querySelectorAll('#quiz [data-q]')].map(b=>b.dataset.q+':'+b.dataset.m+':'+b.textContent)")
    n=len(P['politics'])
    if n>50 and (not any(f'politics:full:Full · {n}' in o for o in opts) or not any('politics:short:Short · 50' in o for o in opts)): fail.append(('bank','full/short options',opts))
    epi=await pg.evaluate("(document.querySelector('#quiz .qz-epi')||{}).textContent||''")
    if 'footnotes to Plato' not in epi or 'Whitehead' not in epi: fail.append(('bank','philosophy epigraph',epi))
    await shot(pg,'quiz-desk-menu-epigraph'); worst={}
    for t in range(6):
      for k in ('politics','philosophy','combined'):
        L=await pg.evaluate(f"__quiz.questionsFor('{k}','short')"); pool=P['politics']+P['philosophy'] if k=='combined' else P[k]
        if len(L)!=min(50,len(pool)) or len(set(L))!=len(L) or any(i not in pool for i in L): fail.append(('bank','draw size',k,len(L)))
        if k=='combined' and len(pool)>=50 and sorted(Q[i]['quiz'] for i in L).count('politics')!=25: fail.append(('bank','combined not 25+25',L))
        bad=cover(L,pool,lambda a:1)  # both directions on every axis where the pool has them
        if bad: fail.append(('bank','draw misses a direction',k,bad))
        worst[k]=max(worst.get(k,0),len(cover(L,pool,lambda a:3 if a in ('abstraction','hierarchy') else 2)))
    print('draws: every axis direction covered at least once; (axis,direction) pairs short of the 2/3 target, worst of 6 draws:',worst)
    await pg.click('#quiz [data-q=politics][data-m=full]'); await pg.wait_for_timeout(100)
    i51=P['politics'].index('p51') if 'p51' in P['politics'] else None
    if i51 is not None:
      for j in range(i51): await pg.click('#quiz .qz-ans button[data-v="1"]' if j%2 else '#quiz .qz-ans button[data-v="-1"]'); await pg.wait_for_timeout(15)
      st=await pg.evaluate("({id:__quiz.state.list[__quiz.state.i],set:(document.querySelector('#quiz .qz-set')||{}).textContent||'',st:document.querySelector('#quiz .qz-st').textContent})")
      if st['id']!='p51' or st['set']!='TEST SETTING p51' or st['st']!=Q['p51']['statement']: fail.append(('bank','setting line',st))
      await ctx.close(); ctx,pg=await page()
      await pg.evaluate("__quiz.loadBank().then(()=>{__quiz.menu();})"); await pg.wait_for_selector('#quiz [data-q=politics][data-m=full]'); await pg.click('#quiz [data-q=politics][data-m=full]')
      for j in range(i51): await pg.click('#quiz .qz-ans button[data-v="1"]' if j%2 else '#quiz .qz-ans button[data-v="-1"]'); await pg.wait_for_timeout(15)
      st=await pg.evaluate("({set:(document.querySelector('#quiz .qz-set')||{}).textContent||'',st:document.querySelector('#quiz .qz-st').textContent})")
      if st['set']!='Scenario' or st['st']!=Q['p51']['statement']: fail.append(('bank','scenario label',st))
      await shot(pg,'quiz-desk-scenario')
    await ctx.close()
    # ---- phone: take the Short philosophy quiz by tapping, results, map, card
    ctx,pg=await page('',True)
    ans,ids=await take(pg,'philosophy','short' if len(BANK['quizzes']['philosophy'])>50 else 'full','phone'); r=await check_results(pg,'philosophy',ans,'phone')
    await shot(pg,'quiz-phone-results')
    w=await pg.evaluate("({sw:document.querySelector('#quiz .box').scrollWidth,cw:document.querySelector('#quiz .box').clientWidth,vw:innerWidth,bw:document.querySelector('#quiz .box').getBoundingClientRect().width})")
    if w['sw']>w['cw']+1 or w['bw']>w['vw']: fail.append(('phone','overflow',w))
    await pg.evaluate("document.querySelector('#quiz [data-a=map]').scrollIntoView()"); await pg.tap('#quiz [data-a=map]'); await pg.wait_for_timeout(2200)
    if await pg.evaluate("__quizHL.size")!=5: fail.append(('phone','show on map'))
    await shot(pg,'quiz-phone-map'); await ctx.close(); await b.close()
  srv.terminate(); print('errors',errs,'FAILS',fail); sys.exit(1 if fail or errs else 0)
asyncio.run(run())
