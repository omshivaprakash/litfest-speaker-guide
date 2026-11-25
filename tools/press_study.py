"""Steps 2 and 3 of the press study. Reads press_links.csv (from tools/press_extract.py), rebuilds headlines from link text or URL slugs,
tags outlet, language, year, topics and the speakers named, writes
  <bundle>/press_articles.csv   private working file (also holds a coarse tone for each headline)
  data/press.json               public file: festival, year, outlet, headline, link, topics, speakers. No article text, no tone.
Article bodies are not fetched (the outlets' hosts are not reachable from this environment), so everything is read from the link, its text and its URL.
Usage: python3 tools/press_study.py <bundle_dir>"""
import csv,re,json,os,sys,html,datetime,urllib.parse,collections
sys.path.insert(0,os.path.dirname(__file__))
from build_insights import gnorm
R=os.path.join(os.path.dirname(__file__),'..'); B=sys.argv[1]
OUTLET={'timesofindia.indiatimes.com':('The Times of India','English','national'),'deccanherald.com':('Deccan Herald','English','regional'),'thehindu.com':('The Hindu','English','national'),'starofmysore.com':('Star of Mysore','English','local'),'thesouthfirst.com':('The South First','English','regional'),'hindustantimes.com':('Hindustan Times','English','national'),'prajavani.net':('Prajavani','Kannada','regional'),'deccanchronicle.com':('Deccan Chronicle','English','regional'),'indianexpress.com':('The Indian Express','English','national'),'newindianexpress.com':('The New Indian Express','English','national'),'theprint.in':('ThePrint','English','national'),'mysoorunews.com':('Mysooru News','English','local'),'frontlist.in':('Frontlist','English','trade'),'yourstory.com':('YourStory','English','trade'),'scroll.in':('Scroll.in','English','national'),'lifestyle.livemint.com':('Mint Lounge','English','national'),'theweek.in':('The Week','English','national'),'newskarnataka.com':('News Karnataka','English','regional'),'citytoday.media':('City Today','English','local'),'andolana.in':('Andolana','Kannada','local'),'agniprapancha.com':('Agni Prapancha','Kannada','regional'),'andhrajyothy.com':('Andhra Jyothy','Telugu','regional'),'sakshi.com':('Sakshi','Telugu','regional'),'jeyamohan.in':('Jeyamohan (blog)','Tamil','blog'),'kalachuvadu.com':('Kalachuvadu','Tamil','magazine'),'andhimazhai.com':('Andhimazhai','Tamil','magazine'),'suneelkrishnan.in':('Suneel Krishnan (blog)','Tamil','blog'),'keralasabdam.in':('Kerala Sabdam','Malayalam','regional'),'thedailyguardian.com':('The Daily Guardian','English','national'),'telegraphindia.com':('The Telegraph India','English','national'),'epaper.starofmysore.com':('Star of Mysore (e-paper)','English','local')}
SKIP=re.compile(r'x\.com|makemytrip|intuit|spektrix|dotdigital|vimeo|policies\.google|jotform|creativescotland|edinburgh\.gov|cultureedinburgh|supercooldesign|goo\.gl|epaper\.(?!starofmysore)',re.I)
TOPICS=[('Children & young readers',r'child|kids?\b|young|school|story ?time|sudha murty|junior|teen'),('Translation & languages',r'translat|language|kannada|malayalam|tamil|telugu|hindi|bilingual|regional|indic'),('Awards & fellowships',r'award|prize|puraskar|fellowship|winner|honou?r|laureate'),('Festival news',r'announce|to be held|begins|inaugurat|gears up|returns|edition|programme|schedule|line-?up|curtain|concludes|kicks off|opens'),('Books & writers',r'book|author|novel|writer|poet|literat|reading|story|stories|fiction|memoir'),('Society & ideas',r'\bai\b|politic|enemy|caste|gender|women|rights?|freedom|ban\b|protest|media|climate|history|identity'),('Arts & culture',r'film|cinema|music|theatre|dance|\bart\b|folk|heritage|cultur|bollywood|mughal'),('Reading culture',r'reading|librar|bookstore|reader|community|revolution')]
POS=re.compile(r'celebrat|inaugurat|win|award|joy|grand|success|bridg|returns|gears up|announce|fellowship|honou?r|best|great',re.I); NEG=re.compile(r'controvers|protest|ban\b|cancel|slam|criticis|row\b|backlash|walk ?out|boycott|shut',re.I)
def slugify(u):
    p=urllib.parse.urlparse(u).path.strip('/'); parts=[x for x in p.split('/') if x]
    cand=[x for x in parts if re.search(r'[a-z]{3,}-[a-z]{2,}',x,re.I)]
    s=(cand[-1] if cand else (parts[-1] if parts else '')); s=urllib.parse.unquote(s); s=re.sub(r'\.(html|ece|cms|php|htm)$','',s,flags=re.I); s=re.sub(r'%20|article\d+|articleshow|cid\d+|-?\d{6,}$','',s); s=re.sub(r'^\d+-','',s)
    s=re.sub(r'[-_]+',' ',s).strip()
    return (s[:1].upper()+s[1:]) if s else ''
def interp(x,A):
    """Year from a running article id, interpolated between ids whose dates are known. Rough: good to a year, not to a month."""
    if x<=A[0][0]: return A[0][1]
    for (x0,y0),(x1,y1) in zip(A,A[1:]):
        if x<=x1: return y0+(y1-y0)*(x-x0)/(x1-x0)
    return A[-1][1]
TOI=[(70000000,2020.0),(87000000,2022.0),(96500000,2023.0),(106000000,2024.0),(116500000,2025.0),(128000000,2026.0)]
HINDU=[(65000000,2023.0),(67709889,2024.03),(68399856,2024.58),(68513382,2024.67),(70000000,2025.2),(71000000,2025.8),(72000000,2026.4)]
DH=[(591395,2018.4),(773702,2019.8),(1128225,2022.55),(3095577,2024.55),(3805284,2025.9),(4061504,2026.45)]
def year_of(u,t,hint):
    m=re.search(r'articleshow/(\d+)',u)
    if m and 'timesofindia' in u: return int(interp(int(m.group(1)),TOI))
    m=re.search(r'article(\d{7,9})\.ece',u)
    if m and 'thehindu' in u: return int(interp(int(m.group(1)),HINDU))
    m=re.search(r'-(\d{6,7})$',u.rstrip('/'))
    if m and 'deccanherald' in u: return int(interp(int(m.group(1)),DH))
    m=re.search(r'/(\d{2})(\d{2})(\d{2})/',u)
    if m and 'deccanchronicle' in u and 1<=int(m.group(2))<=12: return 2000+int(m.group(3))

    m=re.search(r'/(20[12]\d)/(?:\d{1,2}/)?',u) or re.search(r'(?:^|[-_/=])(20[12]\d)(?:[-_/.]|$)',u)
    if m: return int(m.group(1))
    m=re.search(r'-(?:10|11)(1\d{12})(?:\.html|$)',u)
    if m:
        try: return datetime.datetime.fromtimestamp(int(m.group(1))/1000,datetime.timezone.utc).year
        except Exception: pass
    m=re.search(r'\b(20[12]\d)\b',t)
    if m: return int(m.group(1))
    return int(hint) if hint else 0
F={f['id']:f for f in json.load(open(R+'/festivals.json',encoding='utf8'))['festivals']}
H=json.load(open(R+'/data/history-all.json',encoding='utf8')); names={}
for fid,h in H.items():
    for y,ns in h.items():
        for n in ns:
            k=gnorm(n)
            if len(k.split())>=2: names[k]=n
rows=list(csv.reader(open(B+'/press_links.csv',encoding='utf-8-sig')))[1:]; out=[]; seen=set()
for fid,page,hint,dom,text,u in rows:
    if SKIP.search(u+dom): continue
    o=OUTLET.get(dom)
    if not o: continue
    text=text.strip()
    h=text if len(text)>14 and not re.match(r'(?i)^(read more|click here|view|more|here|know more|source|read)$',text) else slugify(u)
    if not h or len(h.split())<3: continue
    key=re.sub(r'[^a-z]','',h.lower())[:50]
    if (fid,key) in seen: continue
    seen.add((fid,key)); y=year_of(u,text,hint); low=h.lower()
    tp=[n for n,rx in TOPICS if re.search(rx,low)]
    toks=re.findall(r"[A-Za-z]+",low); sp=[]
    for n in (2,3,4):
        for i in range(len(toks)-n+1):
            g=' '.join(toks[i:i+n]); 
            if g in names and names[g] not in sp: sp.append(names[g])
    tone='critical' if NEG.search(h) else ('positive' if POS.search(h) else 'neutral')
    out.append({'f':fid,'y':y,'o':o[0],'l':o[1],'k':o[2],'h':h[:160],'u':u,'t':tp,'s':sp[:4],'tone':tone})
out.sort(key=lambda x:(x['f'],-x['y'],x['o']))
with open(B+'/press_articles.csv','w',newline='',encoding='utf-8-sig') as fh:
    w=csv.writer(fh); w.writerow(['festival','year','outlet','language','outlet_type','headline','topics','speakers_named','tone_coarse','url'])
    for x in out: w.writerow([F[x['f']]['short'],x['y'] or '',x['o'],x['l'],x['k'],x['h'],'; '.join(x['t']),'; '.join(x['s']),x['tone'],x['u']])
pub=[{k:x[k] for k in ('f','y','o','l','k','h','u','t','s')} for x in out]
json.dump({'built':datetime.date.today().isoformat(),'note':'Links listed on each festival\'s own press page, so this is the coverage a festival chose to show, not everything the media said. Headlines are read from the link text or the web address; articles themselves were not read.','fest':{k:F[k]['short'] for k in {x['f'] for x in out}},'items':pub},open(R+'/data/press.json','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
c=collections.Counter(x['f'] for x in out); yc=collections.Counter(x['y'] for x in out); oc=collections.Counter(x['o'] for x in out); tc=collections.Counter(t for x in out for t in x['t'])
print(len(out),'articles;',dict(c)); print('years',dict(sorted(yc.items()))); print(oc.most_common(8)); print(tc.most_common()); print('with speakers named:',sum(1 for x in out if x['s']),[x['s'] for x in out if x['s']][:6])
