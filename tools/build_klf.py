"""Build festivals/klf/{data,stats,history}.json for the Kerala Literature Festival.
Sources (all public, used by the festival's own website): the speakers and sessions JSON files in its public S3 bucket,
its speakers API (published list and photos), and the program pages on archives.keralaliteraturefestival.com for 2023 and 2024.
Usage: python3 tools/build_klf.py RAWDIR   (RAWDIR is created if missing; writes titles.json for tools/add_books_ol.py)"""
import re,sys,json,os,html,io,time,unicodedata,urllib.request,urllib.parse
import concurrent.futures as cf
from collections import Counter
from PIL import Image
RAW=sys.argv[1]; os.makedirs(RAW,exist_ok=True); OUT=os.path.join(os.path.dirname(__file__),'..','festivals','klf'); os.makedirs(OUT+'/ph',exist_ok=True)
UA={'User-Agent':'Mozilla/5.0'}; NOW=2026
S3='https://themagweb-klfsessions.s3.ap-south-1.amazonaws.com/'; API='https://api.keralaliteraturefestival.com'
def norm(n):
    n=unicodedata.normalize('NFKD',html.unescape(n)).encode('ascii','ignore').decode().lower()
    n=re.sub(r'\b(dr|prof|professor|mr|ms|mrs|shri|smt|sir|justice|lord|dame)\b','',n)
    return re.sub(r'\s+',' ',re.sub(r'[^a-z ]',' ',n)).strip()
def get(u,b=False):
    for _ in range(3):
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40).read(); return r if b else r.decode('utf8','ignore')
        except Exception: time.sleep(2)
def short(t,n=220):
    if len(t)<=n: return t
    return t[:n].rsplit(' ',1)[0]+'…'
def gender(b):
    f=len(re.findall(r"\b(she|her|hers|herself)\b",b,re.I)); m=len(re.findall(r"\b(he|his|him|himself)\b",b,re.I))
    if f>=1 and f>=2*m: return 'f'
    if m>=1 and m>=2*f: return 'm'
    return 'u'
RULES=[(r'\b(nobel|booker prize|pulitzer)\b','Prize-winning author'),(r'\b(ambassador|diplomat)\b','Diplomat'),(r'\b(politician|member of parliament|mla|minister)\b','Politician'),
 (r'\b(ias officer|ips officer|civil servant|bureaucrat)\b','Civil servant'),(r'\b(film director|filmmaker|screenwriter|lyricist)\b','Filmmaker'),(r'\b(actor|actress)\b','Actor'),(r'\b(economist)\b','Economist'),
 (r'\b(publisher|literary agent|editor-in-chief|editorial director)\b','Publishing professional'),(r'\b(translator)\b','Translator'),(r'\b(singer|musician|composer|vocalist)\b','Musician'),
 (r'\b(scientist|physicist|astrophysicist|neuroscientist|biologist|doctor|physician|surgeon|ecologist|climate)\b','Scientist or doctor'),(r'\b(historian)\b','Historian'),
 (r'\b(professor|scholar|academic|lecturer)\b','Scholar'),(r'\b(journalist|correspondent|columnist|reporter|broadcaster)\b','Journalist'),(r'\b(poet)\b','Poet'),(r'\b(playwright|dramatist)\b','Playwright'),
 (r'\b(illustrator|cartoonist|artist|dancer)\b','Artist or illustrator'),(r'\b(entrepreneur|investor|ceo)\b','Entrepreneur'),(r'\b(novelist|author|writer|memoirist|essayist|biographer)\b','Author')]
def role(b):
    l=b.lower()
    for rx,lab in RULES:
        if re.search(rx,l): return lab
    return 'Speaker'
CTRY=[('India',r'\b(india|indian|hyderabad|telangana|delhi|mumbai|bengaluru|bangalore|kolkata|chennai|pune|kerala|lucknow|punjab|gujarat|bihar|assam|kashmir|odisha|andhra)\b'),
 ('United Kingdom',r'\b(british|uk|united kingdom|england|english|scottish|scotland|welsh|wales|london|oxford|cambridge|britain)\b'),('United States',r'\b(american|united states|u\.s\.|usa|new york|california|boston|harvard|yale|princeton|texas|chicago)\b'),
 ('Pakistan',r'\b(pakistan|pakistani|lahore|karachi)\b'),('Bangladesh',r'\b(bangladesh|bangladeshi|dhaka)\b'),('Sri Lanka',r'\b(sri lanka|sri lankan|colombo)\b'),('Nepal',r'\b(nepal|nepali|kathmandu)\b'),
 ('Canada',r'\b(canada|canadian|toronto)\b'),('Australia',r'\b(australia|australian|sydney|melbourne)\b'),('France',r'\b(french|france|paris)\b'),('Germany',r'\b(german|germany|berlin)\b'),
 ('Ireland',r'\b(irish|ireland)\b'),('Italy',r'\b(italian|italy)\b'),('Japan',r'\b(japanese|japan)\b'),('China',r'\b(chinese|china)\b'),('Israel',r'\b(israeli|israel)\b'),('Netherlands',r'\b(dutch|netherlands)\b'),
 ('Sweden',r'\b(swedish|sweden)\b'),('Spain',r'\b(spanish|spain)\b'),('Russia',r'\b(russian|russia)\b'),('Turkey',r'\b(turkish|turkey)\b'),('New Zealand',r'\b(new zealand)\b'),('Afghanistan',r'\b(afghan|afghanistan)\b')]
CITY=[('Delhi / NCR',r'\b(delhi|gurugram|gurgaon|noida)\b'),('Mumbai',r'\bmumbai\b'),('Bengaluru',r'\b(bengaluru|bangalore)\b'),('Kolkata',r'\b(kolkata|calcutta)\b'),('Chennai',r'\bchennai\b'),('Hyderabad',r'\b(hyderabad|secunderabad)\b'),('Pune',r'\bpune\b')]
def country(b):
    l=b.lower(); hits=[(re.search(rx,l).start(),c) for c,rx in CTRY if re.search(rx,l)]
    return (sorted(hits)[0][1],'named in bio') if hits else ('Unknown','')

CUE=re.compile(r'(author|authored|book|novel|memoir|collection|poem|poetry|essay|biograph|published|bestsell|latest|debut|titles|works|including|include|wrote|written|edited|translat|trilogy|series|sequel|anthology|story|stories)',re.I)
def clean(h): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',h or '').replace('\xa0',' '))).strip()
def italics(h):
    out=[]
    for m in re.finditer(r'<(?:em|i)>(.*?)</(?:em|i)>',h or '',re.S):
        t=clean(m.group(1)).strip(' ,.;:')
        if not t or len(t)>110: continue
        pre=clean((h or '')[max(0,m.start()-120):m.start()])
        if CUE.search(pre) or re.search(r'(\bby|\band|,)\s*$',pre+' '): out.append(t)
    return out
spk=json.loads(get(S3+'speakers.json')); ses=json.loads(get(S3+'sessions.json'))
pub={}
for p in range(1,8):
    r=json.loads(get(f'{API}/speakers/list-site?page={p}&size=100&search=') or '{}').get('data',{}).get('items',[])
    if not r: break
    for x in r: pub[str(x['id'])]=x
    time.sleep(.5)
spk=[x for x in spk if str(x['id']) in pub]
# sessions per speaker (2026)
bysp={}
for e in ses:
    ids=[(q.get('speaker') or {}).get('id') for q in (e.get('session_speackers') or [])+(e.get('session_moderators') or [])]
    for i in set(ids):
        if i is not None: bysp.setdefault(str(i),[]).append(e)
# history: archive program pages
def names_from(u):
    h=get(u) or ''; return sorted({html.unescape(t).strip() for t in re.findall(r"class='user-avatar[^']*'\s+title='([^']+)'",h) if t.strip()})
A='https://archives.keralaliteraturefestival.com/'
hist={2023:names_from(A+'program_new_2023.aspx'),2024:names_from(A+'program_new.aspx')}
byyear={y:{norm(n):n for n in v if norm(n)} for y,v in hist.items()}
byyear[NOW]={norm(x['heading']):x['heading'] for x in spk}
def work(x):
    ph=''
    if x.get('photo'):
        sl=re.sub(r'[^a-z0-9]+','-',x['heading'].lower()).strip('-')+'-'+str(x['id']); fn=f'{OUT}/ph/{sl}.jpg'
        if not os.path.exists(fn):
            raw=get(API+'/'+urllib.parse.quote(x['photo']),True)
            try:
                im=Image.open(io.BytesIO(raw)).convert('RGB'); w,hh=im.size
                if w>373: im=im.resize((373,round(hh*373/w)),Image.LANCZOS)
                im.save(fn,'JPEG',quality=82,optimize=True)
            except Exception: fn=None
        if fn: ph=f'ph/{sl}.jpg'
    time.sleep(.1); return ph
with cf.ThreadPoolExecutor(3) as ex: photos=list(ex.map(work,spk))
yrs={}
for y,m in byyear.items():
    for k in m: yrs.setdefault(k,[]).append(y)
S=[];TJ={}
for x,ph in zip(spk,photos):
    n=x['heading'].strip(); k=norm(n); ys=sorted(yrs.get(k,[NOW])); past=[y for y in ys if y<NOW]; full=clean(x['content'])
    cc,cb=country(full) if full else ('Unknown','')
    city=next((c for c,rx in CITY if full and re.search(rx,full.lower())),'')
    r=role(full) if full else 'Speaker'
    sl=re.sub(r'[^a-z0-9]+','-',n.lower()).strip('-')+'-'+str(x['id'])
    sess=sorted(bysp.get(str(x['id']),[]),key=lambda e:(e['date'],e['time_from']))
    S.append({'n':n,'b':short(full),'f':full,'y':ys,'pre':[],'first':0 if past else 1,'g':gender(full) if full else 'u','t':r if r!='Speaker' else 'Other voices','p':0,'r':0,'a':'','l':'',
      's':[[2026,e['name'].strip()] for e in sess],'u':str(x['id']),'bk':[],'lg':[],'le':'','role':r,'nonauth':0 if r in('Author','Prize-winning author','Poet','Playwright') else 1,
      'cc':cc,'cb':cb,'dia':0,'city':city,'ph':ph})
    TJ[str(x['id'])]=italics(x['content'])
fr=sorted([o for o in S if sum(1 for y in o['y'] if y<NOW)>=2],key=lambda o:(-len(o['y']),o['n']))
for i,o in enumerate(fr,1): o['p']=1;o['r']=i
S.sort(key=lambda o:o['n'].lower())
json.dump(S,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
json.dump(TJ,open(RAW+'/titles.json','w',encoding='utf8'),ensure_ascii=False)
YEARS=sorted(byyear); per={}
for y in YEARS:
    ks=set(byyear[y]); prior=set().union(*[set(byyear[z]) for z in YEARS if z<y]) if y>YEARS[0] else set()
    per[str(y)]={'total':len(ks),'returning':len(ks&prior),'inNow':len(ks&set(byyear[NOW]))}
name_of={k:v for y in YEARS for k,v in byyear[y].items()}
lead=sorted(yrs.items(),key=lambda kv:(-len(kv[1]),kv[0]))[:25]
json.dump({'per':per,'lead':[{'n':name_of[k],'y':v,'in26':NOW in v} for k,v in lead],'hist':dict(Counter(str(sum(1 for y in yrs.get(norm(o['n']),[]) if y<NOW)) for o in S))},open(OUT+'/stats.json','w'))
json.dump({str(y):sorted(byyear[y].values()) for y in YEARS},open(OUT+'/history.json','w',encoding='utf8'),ensure_ascii=False)
print(len(S),'speakers;',sum(o['first'] for o in S),'first-timers;',{y:per[str(y)]['total'] for y in YEARS},sum(1 for o in S if o['s']),'with 2026 sessions',sum(1 for o in S if o['ph']),'photos',sum(1 for v in TJ.values() if v),'with bio italics')
