import json
P='ideas.json'
ideas=json.load(open(P)); ids={i['id'] for i in ideas}; by={i['id']:i for i in ideas}
G='https://grokipedia.com/page/'
AX=["platonism","aristotelianism","stoicism","christianity","gnosticism","hermeticism","enlightenment_liberalism","marxism","darwinism","nietzsche","critical_theory","confucianism","daoism","buddhism","vedanta","islamic_philosophy","humor","irony","abstraction","hierarchy"]
LBL={"platonism":"Platonism","aristotelianism":"Aristotelianism","stoicism":"Stoicism","christianity":"Christianity","gnosticism":"Gnosticism","hermeticism":"Hermeticism","enlightenment_liberalism":"Enlightenment liberalism","marxism":"Marxism","darwinism":"Darwinism","nietzsche":"Nietzsche","critical_theory":"Critical theory","confucianism":"Confucianism","daoism":"Daoism","buddhism":"Buddhism","vedanta":"Vedanta","islamic_philosophy":"Islamic philosophy"}
ROOTYEAR={"darwinism":1859,"nietzsche":1883,"critical_theory":1923,"marxism":1848}
def node(id,name,year,approx,place,lat,lon,osrc,onote,thinkers,parents,plain,summary,scores,sources,domain):
    r={};why={}
    for a in AX:
        if a in scores: r[a],why[a]=scores[a]
        elif a=="humor": r[a],why[a]=0,"Not expressed through jokes or play."
        elif a=="irony": r[a],why[a]=0,"Makes its case directly, without ironic distance."
        elif a in ROOTYEAR and ROOTYEAR[a]>year: r[a],why[a]=0,f"Comes before {LBL[a]} existed, so it cannot descend from it."
        else: r[a],why[a]=0,f"No real link to {LBL[a]}."
    for p in parents: assert p in by or p in [n for n in NEWIDS], p
    return dict(id=id,name=name,root=False,root_axis=None,year=year,year_approx=approx,place=place,lat=lat,lon=lon,origin_src=osrc,origin_note=onote,thinkers=thinkers,parents=parents,plain=plain,summary=summary,ratings=r,rationale=why,stories=[],sources=sources,domain=domain)
NEWIDS=["critical_legal_studies","liberal_feminism","socialist_feminism","radical_feminism","black_feminism","critical_race_theory","intersectionality","social_justice_movement","america_first","maga","postliberalism","national_conservatism"]
new=[
node("liberal_feminism","Liberal feminism",1792,False,"London",51.51,-0.13,G+"Liberal_feminism",
 "Mary Wollstonecraft publishes A Vindication of the Rights of Woman in 1792; Grokipedia places the strand's emergence in the Enlightenment",
 ["Mary Wollstonecraft","John Stuart Mill"],["enlightenment_liberalism"],
 "Liberal feminism applies Enlightenment ideas of reason and individual rights to women. It seeks equal schooling, legal rights and opportunity through reform, not revolution.",
 "Applies Enlightenment individual rights to women: equal education, law and opportunity, won by reform.",
 {"enlightenment_liberalism":(5,"Built directly on Locke-style individual rights and autonomy."),
  "christianity":(0,"Argues from reason and rights rather than scripture."),
  "abstraction":(-1,"Concerned with law, schooling and work; grounded in human reason."),
  "hierarchy":(-3,"Opposes legal rule of husbands over wives and sex-based barriers, but keeps liberal institutions.")},
 [G+"Liberal_feminism",G+"A_Vindication_of_the_Rights_of_Woman"],["politics","philosophy"]),
node("socialist_feminism","Socialist feminism",1896,True,"Germany",None,None,G+"Socialist_feminism",
 "Grokipedia: emerged in the late 19th and early 20th centuries; Clara Zetkin's 'Proletarian Woman and Socialism' dates to 1896",
 ["Clara Zetkin","Alexandra Kollontai","Heidi Hartmann"],["marxism"],
 "Socialist feminism holds that women are held down by both capitalism and male dominance, including unpaid housework, and that both must end together.",
 "Holds that capitalism and male dominance hold women down together, so both must be overturned.",
 {"marxism":(5,"Zetkin and Kollontai worked inside the Marxist movement and used its class analysis."),
  "enlightenment_liberalism":(-2,"Treats legal equality alone as too little without economic change."),
  "christianity":(-1,"Secular and materialist; Kollontai wanted the family itself remade."),
  "abstraction":(-4,"Explains women's position through labor and economic structures."),
  "hierarchy":(-5,"Seeks to end both class rule and male rule.")},
 [G+"Socialist_feminism",G+"Marxist_feminism"],["politics"]),
node("radical_feminism","Radical feminism",1967,False,"New York City",40.71,-74.01,G+"Radical_feminism",
 "New York Radical Women formed in 1967 (Firestone, Pam Allen); women left New Left and civil rights groups to form it",
 ["Shulamith Firestone","Kate Millett","Catharine MacKinnon"],["new_left"],
 "Radical feminism broke away from the 1960s New Left. It sees patriarchy, men's rule over women, as the root problem, to be uprooted in family, sexuality and culture.",
 "Sees patriarchy as the root of women's subordination and aims to uproot it in family, sex and culture.",
 {"marxism":(2,"Took up the language of oppression and revolution, but made sex, not class, the primary divide."),
  "critical_theory":(2,"Like the New Left it came from, it reads culture as carrying domination."),
  "enlightenment_liberalism":(-2,"Rejects liberal feminism's step-by-step legal reform as too shallow."),
  "christianity":(-2,"Challenges marriage and the nuclear family as Christian tradition upholds them."),
  "abstraction":(-2,"Focuses on bodies, sexuality and reproduction."),
  "hierarchy":(-5,"Aims to abolish male domination entirely.")},
 [G+"Radical_feminism",G+"New_Left"],["politics","culture"]),
node("black_feminism","Black feminism",1977,False,"Boston",42.36,-71.06,G+"Black_feminism",
 "The Combahee River Collective (Boston, 1974-1980), socialists who came out of socialist-feminist and civil rights circles, issued its statement in 1977; Anna Julia Cooper's A Voice from the South (1892) is an earlier root",
 ["Anna Julia Cooper","Barbara Smith","Beverly Smith","Demita Frazier"],["socialist_feminism","civil_rights_movement"],
 "Black feminism holds that Black women face race, sex and class oppression at once, and that these interlock. Its key text is the 1977 Combahee River Collective statement.",
 "Holds that race, sex and class oppression interlock in Black women's lives and must be fought together.",
 {"marxism":(2,"The Combahee statement named capitalism among the systems to be dismantled."),
  "critical_theory":(2,"Analyzes interlocking structures of power and domination."),
  "enlightenment_liberalism":(-1,"Faults mainstream rights movements for missing Black women's position."),
  "christianity":(0,"Its 1977 statement is secular, though Cooper wrote from a Christian frame."),
  "abstraction":(-2,"Rooted in lived experience and material conditions."),
  "hierarchy":(-5,"Aims to dismantle racial, sexual and class domination together.")},
 [G+"Black_feminism",G+"Combahee_River_Collective"],["politics","culture"]),
node("critical_legal_studies","Critical legal studies",1977,False,"Madison, Wisconsin",43.07,-89.40,G+"Critical_legal_studies",
 "The first Conference on Critical Legal Studies met at the University of Wisconsin-Madison in 1977; its founders had been 1960s law students active in civil rights and anti-war protest",
 ["Duncan Kennedy","Roberto Mangabeira Unger","Morton Horwitz"],["new_left","frankfurt_school","marxism"],
 "Critical legal studies is a school of American law professors. It holds that law is not neutral: legal rules are shaped by politics and tend to protect those who already hold power.",
 "Law professors who argue that law is politics in disguise and tends to protect existing power.",
 {"marxism":(3,"Grounded in historical materialism and Marxist critique of law as a tool of domination."),
  "critical_theory":(3,"Frankfurt School ideas shaped its view of law as ideology."),
  "enlightenment_liberalism":(-3,"Attacks liberal legalism and the claim that law stands above politics."),
  "abstraction":(-2,"Explains law through social interests and power."),
  "hierarchy":(-4,"Aims to expose and undo the hierarchies it says law hides.")},
 [G+"Critical_legal_studies"],["politics","philosophy"]),
node("critical_race_theory","Critical race theory",1979,True,"Cambridge, Massachusetts",42.38,-71.12,G+"Critical_race_theory",
 "Grokipedia: originated in the late 1970s in US legal scholarship, drawing key foundations from critical legal studies; Derrick Bell (Harvard Law) began the shift with Race, Racism, and American Law (1973)",
 ["Derrick Bell","Richard Delgado","Kimberlé Crenshaw"],["critical_legal_studies","civil_rights_movement","marxism"],
 "Critical race theory, from American law schools, holds that racism is built into laws and institutions, that race is socially made, and that color-blind law can keep inequality.",
 "Holds that racism is built into laws and institutions, not only individual acts, and that color-blind law can preserve it.",
 {"marxism":(3,"Adapts Marxist oppressor-and-oppressed analysis, with race in place of class."),
  "critical_theory":(3,"Through its parent, critical legal studies, it draws on the Frankfurt School's ideology critique."),
  "enlightenment_liberalism":(-3,"Challenges color-blind liberalism and step-by-step civil rights reform."),
  "abstraction":(-2,"Explains outcomes through social and legal structures."),
  "hierarchy":(-5,"Aims to expose and end racial subordination.")},
 [G+"Critical_race_theory",G+"Critical_legal_studies"],["politics","philosophy"]),
node("intersectionality","Intersectionality",1989,False,"Chicago",41.79,-87.60,G+"Intersectionality",
 "Kimberlé Crenshaw's 1989 essay 'Demarginalizing the Intersection of Race and Sex' in the University of Chicago Legal Forum",
 ["Kimberlé Crenshaw","Patricia Hill Collins"],["black_feminism","critical_race_theory","frankfurt_school"],
 "Intersectionality studies how race, sex, class and other identities overlap. Crenshaw showed Black women could fall through laws that looked at race or sex only one at a time.",
 "Studies how race, sex, class and other identities overlap to shape discrimination and advantage.",
 {"critical_theory":(3,"Grokipedia calls it a critical social theory extending Frankfurt School critiques of power to identity."),
  "marxism":(1,"Keeps class as one axis but moves away from class-first analysis."),
  "enlightenment_liberalism":(-1,"Faults single-axis anti-discrimination law, while working inside the courts."),
  "abstraction":(-2,"Grounded in lived experience and legal cases."),
  "hierarchy":(-4,"Maps systems of power in order to oppose them.")},
 [G+"Intersectionality",G+"Kimberlé_Crenshaw"],["politics","philosophy"]),
node("social_justice_movement","Social justice (woke)",2014,False,"Ferguson, Missouri",38.74,-90.31,G+"Woke",
 "'Stay woke' spread nationally through the protests after the 9 August 2014 shooting of Michael Brown in Ferguson; the broad current took shape around 2016-2020",
 [],["intersectionality","critical_race_theory"],
 "Supporters call it social justice: staying 'woke', or alert, to racism and other overlapping injustices and changing institutions to fix them. 'Woke' began as Black slang; now mostly critics use it.",
 "Supporters call it social justice: alertness ('woke') to overlapping injustices and changing institutions to fix them.",
 {"critical_theory":(4,"Grokipedia ties it to critical theory frameworks of power and equity."),
  "marxism":(1,"Shares the oppressor-and-oppressed frame but centers identity over class."),
  "enlightenment_liberalism":(1,"Appeals to equality and rights, while doubting color-blind neutrality."),
  "christianity":(-1,"Secular; often clashes with traditional Christian teaching on sex and family."),
  "abstraction":(-1,"About social structures and everyday speech and conduct."),
  "hierarchy":(-4,"Aims to dismantle hierarchies of race, sex and other identities.")},
 [G+"Woke",G+"Social_justice",G+"Intersectionality"],["politics","culture"]),
node("america_first","America First",1940,False,"United States",None,None,G+"America_First_Committee",
 "The America First Committee was founded on 4 September 1940 by Yale Law students; Pat Buchanan revived the phrase in 1990; Trump made it central from 2016; the Groypers (from 2017) claim it",
 ["R. Douglas Stuart Jr.","Charles Lindbergh","Pat Buchanan","Donald Trump","Nick Fuentes"],["old_right","nationalism"],
 "America First puts US interests first: no foreign wars, firm borders, protected industry. Born in 1940, revived by Buchanan and Trump, and the banner of the Groypers around Nick Fuentes.",
 "Put US interests first: no foreign wars, firm borders, protected industry. From 1940, revived in the 1990s and 2010s.",
 {"enlightenment_liberalism":(0,"Appeals to the founders' warning against entangling alliances, but distrusts free trade and open borders."),
  "christianity":(1,"The 1940 committee was secular; its Groyper wing stresses traditional Christian ethics."),
  "irony":(1,"Its Groyper wing works through online trolling and memes."),
  "humor":(1,"Groyper activists use meme humor, like the cartoon frog."),
  "abstraction":(-3,"About borders, jobs, trade and war."),
  "hierarchy":(2,"Puts the nation and its citizens first, ahead of foreigners and global bodies.")},
 [G+"America_First",G+"America_First_Committee",G+"Groypers"],["politics"]),
node("maga","MAGA (Make America Great Again)",2015,False,"New York City",40.76,-73.97,G+"Make_America_Great_Again",
 "Trump adopted the slogan on 7 November 2012 and launched his campaign with it at Trump Tower on 16 June 2015; Reagan used 'Let's Make America Great Again' in 1980",
 ["Donald Trump"],["america_first","populism"],
 "MAGA is the movement around Donald Trump's slogan. Supporters seek to reverse national decline by reviving industry, strict immigration enforcement, tariffs and avoiding foreign entanglements.",
 "Trump's movement to reverse national decline: revive industry, strict immigration, tariffs, America First abroad.",
 {"enlightenment_liberalism":(0,"Keeps elections and constitutional rule, but rejects free-trade globalism."),
  "christianity":(1,"Draws many religious voters, though its platform is mainly economic and national."),
  "abstraction":(-3,"Focused on jobs, borders, trade and prices."),
  "hierarchy":(1,"Rallies behind one leader against elites; puts citizens before outsiders.")},
 [G+"Make_America_Great_Again",G+"America_First"],["politics","culture"]),
node("postliberalism","Postliberalism",2018,True,"United States",None,None,G+"Postliberalism",
 "Grokipedia: gained traction since the 2010s; Patrick Deneen's Why Liberalism Failed (2018) is its key text",
 ["Patrick Deneen","Adrian Vermeule"],["catholic_integralism","catholic_social_teaching","communitarianism"],
 "Postliberals say liberalism's focus on individual choice has worn away family, community and shared morals. They want politics aimed openly at the common good, after Aristotle and Aquinas.",
 "Argues liberalism has eroded family and community and wants politics aimed openly at the common good.",
 {"aristotelianism":(3,"Wants politics ordered to a purpose, after Aristotle and Aquinas."),
  "christianity":(4,"Draws heavily on Catholic social doctrine; Vermeule writes through an integralist lens."),
  "enlightenment_liberalism":(-5,"Defined by its rejection of liberalism as a failed project."),
  "marxism":(-1,"Some left-leaning postliberals share its critique of markets, but the core is religious-conservative."),
  "abstraction":(2,"Orders public life toward moral and spiritual ends."),
  "hierarchy":(3,"Wants state power used to uphold moral order and the common good.")},
 [G+"Postliberalism"],["politics","philosophy"]),
node("national_conservatism","National conservatism",2019,False,"London",51.51,-0.13,G+"National_conservatism",
 "The first National Conservatism Conference, run by Yoram Hazony's Edmund Burke Foundation, met in London in 2019, after his 2018 book The Virtue of Nationalism",
 ["Yoram Hazony"],["burkean_conservatism","nationalism"],
 "National conservatives see the independent nation-state as the home of self-government, and defend its borders, religion, customs and families against global bodies.",
 "Holds the independent nation-state, with its religion, customs and families, as the base of free government.",
 {"enlightenment_liberalism":(-2,"Rejects liberal universalism and open borders, while keeping self-government."),
  "christianity":(3,"Calls for public recognition of the nation's religious traditions, chiefly Bible-based ones."),
  "abstraction":(0,"Mixes material concerns like borders and trade with religion and tradition."),
  "hierarchy":(3,"Upholds inherited authority of nation, family and religion.")},
 [G+"National_conservatism",G+"Edmund_Burke"],["politics"]),
]
for n in new:
    assert n['id'] not in ids
    for p in n['parents']:
        py=(by.get(p) or next(x for x in new if x['id']==p))['year']; assert py<=n['year'],(n['id'],p)
    ideas.append(n)
json.dump(ideas,open(P,'w'),indent=1,ensure_ascii=False)
print(len(ideas))

for i in ideas:
    if i['id']=='post_vatican_ii_catholicism': i['name']='Vatican II Catholicism'
    if i['id']=='old_right': i['name']='Old Right'
json.dump(ideas,open(P,'w'),indent=1,ensure_ascii=False)

# --- extra edges and ideas (the owner + ResearchBot proposals) ---
by={i['id']:i for i in ideas}
def addp(c,p,src=None):
    if p not in by[c]['parents']: by[c]['parents'].append(p)
    if src and src not in by[c]['sources']: by[c]['sources'].append(src)
addp('fascism','leninism',G+'Fascism')            # Mussolini saw the Bolshevik revolution as a model of violent renewal (contested)
addp('trotskyism','leninism',G+'Trotskyism')
addp('existentialism','existential_phenomenology',G+'Existentialism')
X=[
node("holiness_movement","Holiness movement",1835,True,"United States",None,None,G+"Holiness_movement",
 "Grokipedia: coalesced within the Second Great Awakening revivals of the 1830s-1840s; Finney lectured on sanctification at Oberlin from 1835",
 ["Phoebe Palmer","Charles Grandison Finney","Asa Mahan"],["methodism"],
 "The Holiness movement grew out of American Methodism. It teaches that after conversion a believer can receive 'entire sanctification', a second work of grace that makes holy living possible.",
 "Methodist revival teaching a second work of grace, entire sanctification, after conversion.",
 {"christianity":(5,"A Protestant renewal movement rooted in John Wesley's teaching on Christian perfection."),
  "enlightenment_liberalism":(0,"A revival of personal piety, not a political theory."),
  "abstraction":(4,"Centers on grace, the Holy Spirit and the state of the soul."),
  "hierarchy":(1,"Upholds God's authority and strict moral codes; its camp meetings were open to all.")},
 [G+"Holiness_movement"],["religion"]),
node("brentano_intentionality","Brentano's intentionality",1874,False,"Vienna",48.21,16.37,G+"Franz_Brentano",
 "Brentano's Psychology from an Empirical Standpoint (1874), the year he took a chair at the University of Vienna",
 ["Franz Brentano"],["aristotelian_teleology","thomism"],
 "Franz Brentano argued that every mental act is 'directed toward' something: we see something, wish for something, judge something. He called this intentionality and made it the mark of the mental.",
 "Every mental act is directed toward an object; Brentano made this 'intentionality' the mark of the mind.",
 {"aristotelianism":(3,"Brentano drew on Aristotle, whom he interpreted at length; his dissertation was on Aristotle's theory of being."),
  "christianity":(1,"Revived the medieval scholastic idea of intentio, from Aquinas's tradition; he was a priest until 1873."),
  "abstraction":(2,"Studies the mind's acts by inner perception rather than by physiology."),
  "hierarchy":(0,"A theory of mind, with no view on ranked social order.")},
 [G+"Franz_Brentano",G+"Intentionality"],["philosophy"]),
]
for n in X:
    assert n['id'] not in by; ideas.append(n); by[n['id']]=n
addp('pentecostalism','holiness_movement',G+'Holiness_movement')
addp('phenomenology','brentano_intentionality',G+'Franz_Brentano')
json.dump(ideas,open(P,'w'),indent=1,ensure_ascii=False)
