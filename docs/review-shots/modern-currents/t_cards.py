import asyncio,subprocess,json,base64
from playwright.async_api import async_playwright
OUT='/workspace/mc-wt/docs/review-shots/modern-currents/'
async def run():
  srv=subprocess.Popen(["python3","-m","http.server","8795"],cwd="/workspace/mc-serve",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); await asyncio.sleep(1); fails=[]
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    ctx=await b.new_context(viewport=dict(width=1280,height=900)); pg=await ctx.new_page(); pg.on("pageerror",lambda e:fails.append(str(e)))
    async def h(route,request=None):
      f=route.request.url.split('/')[-1].split('?')[0]
      await route.fulfill(status=200,content_type="application/json",body=open('/workspace/mc-wt/'+f).read(),headers={"Access-Control-Allow-Origin":"*"})
    await pg.route("**/arx-memeplex/*.json",h)
    await pg.goto("http://localhost:8795/after/memeplex.html?intro=none"); await pg.wait_for_timeout(9000)
    # longest ideas by drawn content
    ids=await pg.evaluate("""(()=>{const I=__memeplex.ideas;const kids=id=>I.filter(x=>(x.parents||[]).includes(id)).length;
      return [...I].sort((a,b)=>(b.name.length*3+b.plain.length+(b.thinkers||[]).join().length+kids(b.id)*20)-(a.name.length*3+a.plain.length+(a.thinkers||[]).join().length+kids(a.id)*20)).slice(0,6).map(d=>d.id)})()""")
    pairs=[["post_vatican_ii_catholicism","tridentine_catholicism"],[ids[0],ids[1]],["social_justice_movement","maga"],["hellenism_revival","tridentine_catholicism"]]
    cases=[("hub",g) for g in ("odd","thinker","ladder")]+[("single",i) for i in ids]+[("compare",p) for p in pairs]+[("game",n) for n in (1,6)]
    for kind,arg in cases:
      js={"hub":open("/workspace/mc-serve/hub.js").read().strip(),"single":"a=>__memeplex.cardIdea(a)","compare":"a=>__memeplex.cardCompare(a[0],a[1])",
          "game":"n=>ArxGameCard.result({game:'Memele',number:12,dateLabel:'2026-10-28',solved:n<6,tries:n,max:6,rows:Array.from({length:n},(_,i)=>({tone:i==n-1&&n<6?'hit':['far','mid','near'][i%3],arrow:i%2?'↑':'↓'})),lines:['💡 2 hints used','Clues: lineage, thinkers, timeframe, domain','An extra long line of text that would go on and on past the right edge of the card if not trimmed down','Line four','Line five','Line six']})"}[kind]
      res=await pg.evaluate(f"""async a=>{{const bl=await ({js})(a);const r=new FileReader();const u=await new Promise(z=>{{r.onload=()=>z(r.result);r.readAsDataURL(bl)}});
        const S=['game','hub'].includes('{kind}')?ArxGameCard:ArxShareCard;return {{u,low:S.lastBottom,safe:S.SAFE}}}}""",arg)
      name=f"card-{kind}-{arg if isinstance(arg,(str,int)) else '-vs-'.join(arg)}.png"
      open(OUT+name,'wb').write(base64.b64decode(res['u'].split(',')[1]))
      ok=0<res['low']<=res['safe']; print(("PASS" if ok else "FAIL"),name,"bottom",round(res['low']),"safe",res['safe'])
      if not ok: fails.append(name)
    await b.close()
  srv.terminate(); print("FAILS",fails)
asyncio.run(run())
