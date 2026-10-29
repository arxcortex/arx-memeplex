import asyncio,subprocess,json
from playwright.async_api import async_playwright
R='/workspace/amrepo/'
I={d['id']:d for d in json.load(open(R+'ideas.json'))}
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8785"],cwd="site-v3",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  await asyncio.sleep(1); errs=[]; fails=[]
  def ok(c,m):
    print(("  PASS " if c else "  FAIL ")+m); c or fails.append(m)
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for tag,vp,mob in [("desk",dict(width=1440,height=900),False),("mobile",dict(width=390,height=844),True)]:
      print(tag)
      ctx=await b.new_context(viewport=vp,is_mobile=mob,has_touch=mob); pg=await ctx.new_page(); pg.on("pageerror",lambda e:errs.append(str(e)))
      for f in ['ideas.json','thinkers.json','axes.json']:
        await pg.route("**/arx-memeplex/"+f,(lambda f:(lambda r:r.fulfill(status=200,content_type="application/json",body=open(R+f).read())))(f))
      await pg.add_init_script("localStorage.setItem('memeplex-help-seen','1')")
      await pg.goto("http://localhost:8785/memeplex.html?intro=none"); await pg.wait_for_function("window.__games"); await pg.wait_for_timeout(4000)
      ok(await pg.evaluate("!document.querySelector('#tb [data-k=memele]')") and await pg.is_visible("#tb [data-k=games]"),"single Games button (visible)")
      await pg.click("#tb [data-k=games]"); await pg.wait_for_timeout(300)
      g=await pg.evaluate("[...document.querySelectorAll('#games .gm-pick')].map(b=>b.dataset.g)"); ok(g==['memele','ladder','odd','thinker'],"picker lists "+str(g))
      await pg.screenshot(path=f"shots/views/games-picker-{tag}.png")
      await pg.click("#games .gm-pick[data-g=memele]"); await pg.wait_for_timeout(300); ok(await pg.evaluate("document.getElementById('memele').classList.contains('open')"),"picker opens Memele"); await pg.evaluate("__memele.close()")
      # data validity across 30 days
      bad=[]
      for k in range(30):
        d=f"2026-{11+k//30:02d}-{k%30+1:02d}"
        L=await pg.evaluate("k=>__games.puzzle('ladder',k)",d); c=L['chain']
        if not all(c[i] in I[c[i+1]]['parents'] for i in range(3)): bad.append(('ladder',d,c))
        O=await pg.evaluate("k=>__games.puzzle('odd',k)",d)
        for q in O['rounds']:
          fa=set(await pg.evaluate("i=>__games.fam(i)",q['a'])); fb=set(await pg.evaluate("i=>__games.fam(i)",q['b']))
          if not(q['odd'] in fb and q['odd'] not in fa and all(x in fa and x not in fb for x in q['opts'] if x!=q['odd'])): bad.append(('odd',d,q))
        if len(O['rounds'])<5: bad.append(('odd-short',d))
        T=await pg.evaluate("k=>__games.puzzle('thinker',k)",d)
        for q in T['rounds']:
          if q['th'] not in I[q['ans']]['thinkers'] or any(q['th'] in I[x].get('thinkers',[]) for x in q['opts'] if x!=q['ans']): bad.append(('thinker',d,q))
        if len(T['rounds'])<5: bad.append(('thinker-short',d))
      ok(not bad,"30 days of puzzles verified against ideas.json "+str(bad[:2]))
      # Ladder
      await pg.click("#tb [data-k=games]"); await pg.click("#games .gm-pick[data-g=ladder]"); await pg.wait_for_timeout(200)
      ch=await pg.evaluate("__games.puzzle('ladder').chain")
      for x in reversed(ch): await pg.click(f"#games .gm-o[data-id={x}]")
      await pg.screenshot(path=f"shots/views/games-ladder-{tag}.png")
      await pg.click("#games [data-a=check]"); await pg.wait_for_timeout(150)
      s=await pg.evaluate("__games.state"); ok(len(s['tries'])==1 and not s['done'],"wrong order counts a try")
      await pg.click("#games [data-a=giveup]"); ok("Reveal answer?" in await pg.inner_text("#games .mm-gu"),"ladder give-up confirm")
      await pg.click("#games [data-a=giveup]"); await pg.wait_for_timeout(150)
      s=await pg.evaluate("__games.state"); sh=await pg.evaluate("__games.shareText()"); print("   ladder share:",json.dumps(sh,ensure_ascii=False))
      ok(s['done'] and s['gaveUp'] and "🏳️" in sh and not any(I[x]['name'] in sh for x in ch),"ladder gave-up, 🏳️ share, no spoiler")
      rv=await pg.inner_text("#games .mm-rev"); ok(all(I[x]['name'] in rv for x in ch),"ladder reveals real lineage")
      cd=await pg.evaluate("__games.cardData()"); ok(cd['gaveUp'] and cd['lines'][0].startswith('🏳️'),"ladder card gave-up line")
      await pg.screenshot(path=f"shots/views/games-ladder-done-{tag}.png")
      # Odd one out: answer 3 right, 1 wrong, 1 I-don't-know
      await pg.evaluate("__games.play('odd')"); await pg.wait_for_timeout(200)
      O=await pg.evaluate("__games.puzzle('odd').rounds")
      await pg.screenshot(path=f"shots/views/games-odd-{tag}.png")
      for i,q in enumerate(O[:4]):
        pick=q['odd'] if i<3 else [x for x in q['opts'] if x!=q['odd']][0]
        await pg.click(f"#games .gm-o[data-id={pick}]"); await pg.wait_for_timeout(80)
      await pg.click("#games [data-a=giveup]"); await pg.click("#games [data-a=giveup]"); await pg.wait_for_timeout(150)
      sh=await pg.evaluate("__games.shareText()"); print("   odd share:",json.dumps(sh,ensure_ascii=False))
      ok(sh.split('\n')[0].endswith("3/5 · 🏳️1") and "🟩🟩🟩⬛🏳️" in sh,"odd score + skip in share")
      await pg.screenshot(path=f"shots/views/games-odd-done-{tag}.png")
      # Thinker
      await pg.evaluate("__games.play('thinker')"); await pg.wait_for_timeout(200)
      T=await pg.evaluate("__games.puzzle('thinker').rounds")
      await pg.screenshot(path=f"shots/views/games-thinker-{tag}.png")
      for q in T: await pg.click(f"#games .gm-o[data-id={q['ans']}]"); await pg.wait_for_timeout(80)
      cd=await pg.evaluate("__games.cardData()"); ok(cd['solved'] and cd['tries']==5,"thinker 5/5 card")
      await pg.screenshot(path=f"shots/views/games-thinker-done-{tag}.png")
      blob=await pg.evaluate("(async()=>{const b=await ArxGameCard.result(__games.cardData());return b&&b.size})()"); ok(blob and blob>10000,f"card png renders ({blob} bytes)")
      await pg.reload(); await pg.wait_for_function("window.__games"); await pg.wait_for_timeout(1500)
      await pg.evaluate("__games.play('ladder')"); ok(await pg.evaluate("__games.state.gaveUp"),"ladder state persists after reload")
      await pg.evaluate("__games.play('thinker')"); ok(await pg.evaluate("__games.state.done"),"thinker state persists")
      await ctx.close()
    print("errors",errs); print("FAILS",fails)
  srv.terminate()
asyncio.run(run())
