# Adds the New Atheism -> online right ideas and tour from the fact-checked research file. Run from this folder.
import json,sys
R='../../../'; SRC=sys.argv[1]
rb=json.load(open(SRC)); ideas=json.load(open(R+'ideas.json')); AX=[a['id'] for a in json.load(open(R+'axes.json'))]
LAB={a['id']:a['label'] for a in json.load(open(R+'axes.json'))}
ids={d['id'] for d in ideas}
EDGE={(e['from'],e['to']):e for e in rb['proposed_edges']}
# Short texts condensed from the research captions (no new facts).
TXT={
 'new_atheism':("A public movement of assertive atheism after 9/11, known through bestsellers by Harris, Dawkins, Dennett and Hitchens.",
   "Assertive atheism of the 2000s; many scholars treat the label as journalistic.",'politics' and ['religion','philosophy'],False,"Harris's The End of Faith (2004), the first of the movement's best-known texts"),
 'atheism_plus':("A 2012 faction in online atheism that joined atheism to feminism, antiracism and transgender rights.",
   "Online atheist faction of 2012, after the 2011 'Elevatorgate' dispute; Grokipedia says it alienated some atheists.",['religion','culture'],False,"Launched in 2012 after the 2011 'Elevatorgate' dispute"),
 'anti_sjw_youtube':("YouTube commentary, much of it from the online atheist and skeptic scene, that turned from religion to critiques of feminism and social-justice activism.",
   "Skeptic YouTube's turn to anti-feminist critique, seen in Thunderf00t's and Carl Benjamin's 2013 videos.",['culture','politics'],True,"Thunderf00t's and Carl Benjamin's 2013 video series"),
 'gamergate':("An online campaign from August 2014, organized on 4chan, 8chan and Reddit. Supporters framed it as about games-journalism ethics; Wikipedia's sources describe harassment.",
   "2014 online campaign; Grokipedia and Wikipedia characterize its nature and aims very differently.",['culture','politics'],False,"A blog post by Eron Gjoni in August 2014"),
 'alt_right':("A movement Wikipedia describes as white nationalist. Richard Spencer launched The Alternative Right webzine in March 2010; the term traces to Paul Gottfried in 2008.",
   "Movement named by Spencer's 2010 webzine; Wikipedia says it drew wide attention in 2015 through Breitbart and its support for Trump.",['politics','culture'],False,"Spencer launches The Alternative Right webzine in March 2010"),
 'alt_lite':("A label for pro-Trump, culturally nationalist commentators who rejected the alt-right's ethnic nationalism. Hawley says white nationalists coined it as a pejorative.",
   "Mostly an outside label; the split from the alt-right followed Spencer's November 2016 'Hail Trump' speech.",['politics','culture'],True,"The term entered wide use in late 2016"),
 'online_right':("A loose umbrella term for the internet-native right-wing commentary and subcultures that coalesced around the 2016 US election.",
   "Loose, contested umbrella term with no defining source or founding date.",['politics','culture'],True,"Coalesced around the 2016 US election; no founding date"),
}
SCORE={'new_atheism':{'darwinism':(3,"Dawkins argues from natural selection against design (The God Delusion)."),
                      'enlightenment_liberalism':(3,"Hitchens calls for a renewed Enlightenment (God Is Not Great).")}}
PEND="Not yet scored from sources; placeholder 0 pending review."
new=[]
for n in rb['proposed_nodes']:
  i=n['id']; assert i not in ids, i
  for p in n['parents']: assert p in ids or p in TXT, p
  plain,summ,dom,appx,onote=TXT[i]
  grok=[u for u in n['sources'] if u.startswith('https://grokipedia.com/')]
  r={a:0 for a in AX}; ra={a:PEND for a in AX}
  for a,(v,t) in SCORE.get(i,{}).items(): r[a]=v; ra[a]=t
  en={}
  for p in n['parents']:
    e=EDGE.get((p,i)); c=(e or {}).get('contested','')
    if e: en[p]={'status':'documented' if c.lower().startswith('low') and not c.lower().startswith('low-moderate') else 'contested','type':e['link_type'],'src':e['evidence'],'note':c}
    elif p=='paleoconservatism': en[p]={'status':'contested','type':'term origin (Gottfried)','src':'https://en.wikipedia.org/wiki/Alt-right','note':n['paleo_note']}
    else: en[p]={'status':'contested','type':'umbrella','src':n['sources'][0],'note':'Parent from the proposed node; no edge-level evidence in the research file.'}
  d={'id':i,'name':n['name'],'root':False,'year':n['year'],'year_approx':appx,'place':None,'lat':None,'lon':None,
     'origin_src':grok[0],'origin_note':onote,'thinkers':n['thinkers'],'parents':n['parents'],'plain':plain,'summary':summ,
     'ratings':r,'rationale':ra,'stories':[],'sources':list(dict.fromkeys(n['sources'])),'domain':dom,'edge_notes':en,
     'caption':n['caption'],'contested':n['contested']}
  if i=='atheism_plus': d['aliases']=['Atheism+']
  new.append(d)
ideas+=new
open(R+'ideas.json','w').write(json.dumps(ideas,ensure_ascii=False,indent=1)+'\n')
t=rb['tour']; by={d['id']:d for d in ideas}
stops=[];steps=[]
for k,s in enumerate(t['stops']):
  i=s['node']; prev=t['stops'][k-1]['node'] if k else None
  e=EDGE.get((prev,i)) if prev else None
  if prev: assert prev in by[i]['parents'], (prev,i)
  src=e['evidence'] if e else by[i]['origin_src']
  stops.append({'id':i,'caption':s['caption'],'source':src,'sources':by[i]['sources'],
    'link_from_previous':None if not e else {'type':e['link_type'],'evidence':e.get('evidence_quote') or e['contested'],'evidence_url':e['evidence'],'contested':e['contested']}})
  steps.append({'id':i,'cap':s['caption'],'src':src})
tv=json.load(open('../loose-links/tours-v3.json'))
tv['tours'].append({'id':t['id'],'title':t['title'],'summary':t['summary'],'stops':stops,'kind':t['kind']})
json.dump(tv,open('tours.json','w'),ensure_ascii=False,indent=2)
h=open('memeplex.html').read(); a=h.index('const TOUR_DATA = ')+len('const TOUR_DATA = '); b=h.index('];\n',a)+1
td=json.loads(h[a:b]); td.append({'id':t['id'],'name':t['title'],'kind':t['kind'],'summary':t['summary'],'steps':steps})
open('memeplex.html','w').write(h[:a]+json.dumps(td,ensure_ascii=False)+h[b:])
print('added',[d['id'] for d in new],'tour stops',len(steps))
