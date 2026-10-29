# Applies loose-links batch 1 to ideas.json. Run from repo root.
import json
I=json.load(open('ideas.json')); by={d['id']:d for d in I}
G='https://grokipedia.com/page/'
def note(child,parent,status,typ,src,txt):
  by[child].setdefault('edge_notes',{})[parent]={'status':status,'type':typ,'src':src,'note':txt}
def mk(id,name,year,place,lat,lon,parents,dom,src,onote,thinkers,plain,summary,r,rat,sources):
  AX=list(by['romanticism']['ratings'])
  d={'id':id,'name':name,'root':False,'year':year,'year_approx':False,'place':place,'lat':lat,'lon':lon,
     'origin_src':src,'origin_note':onote,'thinkers':thinkers,'parents':parents,'plain':plain,'summary':summary,
     'ratings':{a:r.get(a,0) for a in AX},
     'rationale':{a:rat.get(a,f"No clear debt to, or quarrel with, {by['romanticism']['rationale'][a].split('with, ')[-1].rstrip('.') if 'with, ' in by['romanticism']['rationale'][a] else a}.") for a in AX},
     'sources':sources,'stories':[],'domain':dom}
  for a in AX:
    if a not in rat: d['rationale'][a]=by['romanticism']['rationale'][a] if a not in('hermeticism','enlightenment_liberalism','nietzsche','irony','hierarchy','abstraction') else 'No clear link.'
  I.append(d); by[id]=d
# 1 Böhme
mk('bohmean_theosophy','Böhmean theosophy',1612,'Görlitz',51.15,14.99,['hermetic_correspondence','protestantism'],['religion','philosophy'],
   G+'Jakob_Böhme','Böhme writes Aurora, 1612',['Jakob Böhme'],
   'A Lutheran shoemaker in Görlitz recast the Hermetic and Paracelsian cosmos as a drama inside God.',
   'Jakob Böhme\'s mystical theosophy, read two centuries later by the Jena Romantics.',
   {'hermeticism':3,'christianity':3,'abstraction':4,'hierarchy':0},
   {'hermeticism':'Read visionaries such as Paracelsus and recast their cosmos.','christianity':'A Lutheran layman writing about God and creation.',
    'enlightenment_liberalism':'Comes before the Enlightenment existed, so it cannot descend from it.','marxism':'Comes before Marxism existed, so it cannot descend from it.',
    'darwinism':'Comes before Darwinism existed, so it cannot descend from it.','nietzsche':'Comes before Nietzsche existed, so it cannot descend from it.',
    'critical_theory':'Comes before Critical theory existed, so it cannot descend from it.','irony':'Writes in earnest visionary terms.',
    'hierarchy':'No clear stance on social rank.','abstraction':'Deals in visions of God, spirit and cosmos.'},
   [G+'Jakob_Böhme',G+'Novalis'])
by['romanticism']['parents']=[p if p!='hermetic_correspondence' else 'bohmean_theosophy' for p in by['romanticism']['parents']]
note('romanticism','bohmean_theosophy','documented','documented reading',G+'Novalis','Novalis studied the works of Jakob Böhme under Tieck\'s influence.')
note('bohmean_theosophy','hermetic_correspondence','documented','influence',G+'Jakob_Böhme','Böhme read visionaries such as Paracelsus, Weigel and Schwenckfeld.')
# 6 Blumenbach
mk('racial_classification','Blumenbach\'s racial classification',1795,'Göttingen',51.54,9.93,['enlightenment_liberalism'],['culture','politics'],
   G+'Johann_Friedrich_Blumenbach','Blumenbach\'s five-part classification, 1795',['Johann Friedrich Blumenbach'],
   'Göttingen\'s anatomist sorted humanity into five varieties by skull. He insisted they were one species.',
   'Blumenbach\'s five human varieties, later reused by race theorists who dropped his one-species view.',
   {'enlightenment_liberalism':1,'abstraction':-2,'hierarchy':2},
   {'enlightenment_liberalism':'Part of Enlightenment natural history; how far the Enlightenment is responsible is debated.',
    'marxism':'Comes before Marxism existed, so it cannot descend from it.','darwinism':'Comes before Darwinism existed, so it cannot descend from it.',
    'nietzsche':'Comes before Nietzsche existed, so it cannot descend from it.','critical_theory':'Comes before Critical theory existed, so it cannot descend from it.',
    'hermeticism':'No clear link to Hermeticism.','irony':'Makes its case directly, without ironic distance.',
    'hierarchy':'Sorted people into varieties while holding they were one species.','abstraction':'Built on skull measurements.'},
   [G+'Johann_Friedrich_Blumenbach',G+'Scientific_racism'])
note('racial_classification','enlightenment_liberalism','contested','influence',G+'Johann_Friedrich_Blumenbach','Enlightenment natural history; whether the Enlightenment as such is responsible is debated.')
by['scientific_racism']['parents']=['racial_classification' if p=='enlightenment_liberalism' else p for p in by['scientific_racism']['parents']]
note('scientific_racism','racial_classification','documented','influence',G+'Arthur_de_Gobineau','Blumenbach\'s categories were taken up by later race theory such as Gobineau\'s (1853–55).')
# 3 Mohism
note('mohism','confucian_ethics','contested','reaction','https://plato.stanford.edu/entries/mohism/','Mozi argued against the Ru; the Han-era claim that he was a former Confucian is unsupported by the Mozi.')
# 4 Shinto
note('shinto','buddhas_dharma','contested','syncretic influence',G+'Shinbutsu-shūgō','Scholars debate whether Buddhism shaped Shinto or the two only coexisted (shinbutsu-shūgō).')
# 5 Manichaeism
by['manichaeism']['parents'].append('buddhas_dharma')
note('manichaeism','buddhas_dharma','documented','influence',G+'Manichaeism','Manichaeism drew on Buddhism among other traditions and counts the Buddha among its prophets.')
# 9 Civil rights
by['civil_rights_movement']['parents']=['protestantism' if p=='christianity' else p for p in by['civil_rights_movement']['parents']]
note('civil_rights_movement','protestantism','documented','direct handoff',G+'Martin_Luther_King_Jr.','King was a Baptist minister trained at Crozer Theological Seminary.')
# 10 Spinoza -> Hegel
by['hegelian_dialectic']['parents'].append('spinozism')
note('hegelian_dialectic','spinozism','documented','documented reading',G+'Pantheism_controversy','The pantheism controversy of 1785 revived Spinoza; Hegel\'s biography records his attention to it.')
# 11 Erasmus -> Reformation
by['protestantism']['parents'].append('renaissance_humanism')
note('protestantism','renaissance_humanism','documented','direct handoff',G+'Erasmus','Erasmus\'s Greek New Testament (1516) influenced Luther, Melanchthon, Zwingli and Calvin.')
json.dump(I,open('ideas.json','w'),ensure_ascii=False,indent=1); open('ideas.json','a').write('\n')
