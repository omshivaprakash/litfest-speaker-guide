"""Build festivals/klf2/{data,stats,history}.json for the Kalinga Literary Festival (Bhubaneswar) from kalingaliteraryfestival.com.
The /klf-speakers/ page lists speakers with a category per edition: the current edition (category 'klf-speakers-2025', the 12th KLF held
in January 2026) is complete; older editions (2021, 2022, 2024) list only a few featured names.
Usage: python3 tools/build_kalinga.py RAWDIR   (RAWDIR holds sp.html saved from /klf-speakers/; writes titles.json)"""
import re,sys,json,os,html,io,time,unicodedata,urllib.request
import concurrent.futures as cf
from collections import Counter
from PIL import Image
RAW=sys.argv[1]; os.makedirs(RAW,exist_ok=True); OUT=os.path.join(os.path.dirname(__file__),'..','festivals','klf2'); os.makedirs(OUT+'/ph',exist_ok=True); UA={'User-Agent':'Mozilla/5.0'}; NOW=2026
CAT={'klf-speakers-2025':2026,'klf-speakers-2024':2024,'klf-speakers-2022':2022,'klf-speakers-2021':2021}
def norm(n):
    n=unicodedata.normalize('NFKD',html.unescape(n)).encode('ascii','ignore').decode().lower()
    n=re.sub(r'\b(dr|prof|professor|mr|ms|mrs|shri|smt|sir)\b','',n); return re.sub(r'\s+',' ',re.sub(r'[^a-z ]',' ',n)).strip()
def get(u,b=False):
    for _ in range(3):
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40).read(); return r if b else r.decode('utf8','ignore')
        except Exception: time.sleep(2)
def clean(x): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',x or '').replace('\xa0',' '))).strip()
def short(t,n=220): return t if len(t)<=n else t[:n].rsplit(' ',1)[0]+'…'
def gender(b):
    f=len(re.findall(r"\b(she|her|hers|herself)\b",b,re.I)); m=len(re.findall(r"\b(he|his|him|himself)\b",b,re.I))
    if f>=1 and f>=2*m: return 'f'
    if m>=1 and m>=2*f: return 'm'
    return 'u'
RULES=[(r'\b(nobel|booker prize|pulitzer)\b','Prize-winning author'),(r'\b(film director|filmmaker|screenwriter|lyricist)\b','Filmmaker'),(r'\b(actor|actress)\b','Actor'),
 (r'\b(politician|member of parliament|minister|governor)\b','Politician'),(r'\b(ias officer|ips officer|civil servant|bureaucrat)\b','Civil servant'),(r'\b(publisher|literary agent|editor-in-chief)\b','Publishing professional'),
 (r'\b(translator)\b','Translator'),(r'\b(singer|musician|composer|vocalist)\b','Musician'),(r'\b(historian)\b','Historian'),(r'\b(professor|scholar|academic|lecturer)\b','Scholar'),
 (r'\b(journalist|correspondent|columnist|reporter|broadcaster)\b','Journalist'),(r'\b(poet)\b','Poet'),(r'\b(playwright|dramatist)\b','Playwright'),(r'\b(artist|dancer)\b','Artist or illustrator'),
 (r'\b(entrepreneur|investor|ceo|industrialist)\b','Entrepreneur'),(r'\b(novelist|author|writer|memoirist|essayist|biographer)\b','Author')]
def role(b):
    l=b.lower()
    for rx,lab in RULES:
        if re.search(rx,l): return lab
    return 'Speaker'
CTRY=[('India',r'\b(india|indian|odisha|odia|bhubaneswar|delhi|mumbai|kolkata|bengal|kerala|assam)\b'),('Nepal',r'\b(nepal|nepali|kathmandu)\b'),('Sri Lanka',r'\b(sri lanka|sri lankan)\b'),('Bhutan',r'\b(bhutan|bhutanese)\b'),
 ('United Kingdom',r'\b(british|uk|united kingdom|england|london|scotland)\b'),('United States',r'\b(american|united states|usa|new york|california)\b'),('Japan',r'\b(japan|japanese)\b'),('Indonesia',r'\b(indonesia|indonesian)\b'),
 ('Spain',r'\b(spain|spanish)\b'),('France',r'\b(france|french)\b'),('Bangladesh',r'\b(bangladesh|bangladeshi)\b')]
def country(b):
    l=b.lower(); h=[(re.search(rx,l).start(),c) for c,rx in CTRY if re.search(rx,l)]
    return (sorted(h)[0][1],'named in bio') if h else ('Unknown','')
CUE=re.compile(r'(author|authored|book|novel|memoir|collection|poem|poetry|essay|biograph|published|bestsell|latest|debut|titles|works|including|include|wrote|written|edited|translat|trilogy|series|anthology|story|stories)',re.I)
def italics(h):
    out=[]
    for m in re.finditer(r'<(?:em|i)>(.*?)</(?:em|i)>',h or '',re.S):
        t=clean(m.group(1)).strip(' ,.;:')
        if not t or len(t)>110: continue
        pre=clean((h or '')[max(0,m.start()-120):m.start()])
        if CUE.search(pre) or re.search(r'(\bby|\band|,)\s*$',pre+' '): out.append(t)
    return out
s=open(f'{RAW}/sp.html',encoding='utf8',errors='ignore').read(); people={}
for it in re.split(r'(?=<div class="team-container)',s)[1:]:
    cl=re.search(r'class="([^"]*dt_team[^"]*)"',it).group(1); cats=[CAT[k] for k in re.findall(r'dt_team_category-([a-z0-9-]+)',cl) if k in CAT]
    m=re.search(r'team-author-name"><a href=" ?https://kalingaliteraryfestival\.com/speakers/([a-z0-9-]+)/ ?">(.*?)</a>',it,re.S)
    if not m or not cats: continue
    img=re.search(r'data-src="([^"]+)"',it); n=clean(m.group(2)); k=norm(n)
    p=people.setdefault(k,{'slug':m.group(1),'name':n,'img':img.group(1) if img else '','years':set()}); p['years'].update(cats)
byyear={}
for p in people.values():
    for y in p['years']: byyear.setdefault(y,{})[norm(p['name'])]=p['name']
yrs={norm(p['name']):sorted(p['years']) for p in people.values()}
def photo(url,fn):
    if os.path.exists(fn): return True
    if not url: return False
    raw=get(url,True)
    try:
        im=Image.open(io.BytesIO(raw)).convert('RGB'); w,h=im.size
        if w>373: im=im.resize((373,round(h*373/w)),Image.LANCZOS)
        im.save(fn,'JPEG',quality=82,optimize=True); return True
    except Exception: return False
def work(p):
    h=get(f"https://kalingaliteraryfestival.com/speakers/{p['slug']}/") or ''
    m=re.search(r'<div class="wpb_wrapper">(.*?)</div>\s*</div>\s*</div>',h,re.S)
    body=''
    for blk in re.findall(r'<div class="wpb_text_column[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>',h,re.S):
        if len(clean(blk))>len(clean(body)): body=blk
    ok=photo(p['img'],f"{OUT}/ph/{p['slug']}.jpg"); time.sleep(.15); return p,body,ok
cur=[p for p in people.values() if NOW in p['years']]
with cf.ThreadPoolExecutor(3) as ex: res=list(ex.map(work,cur))
S=[];TJ={}
for p,body,ok in res:
    n=p['name']; full=clean(body); ys=sorted(p['years']); past=[y for y in ys if y<NOW]
    cc,cb=country(full) if full else ('Unknown',''); r=role(full) if full else 'Speaker'
    S.append({'n':n,'b':short(full),'f':full,'y':ys,'pre':[],'first':0 if past else 1,'g':gender(full) if full else 'u','t':r if r!='Speaker' else 'Other voices','p':0,'r':0,'a':'','l':'','s':[],'u':p['slug'],'bk':[],
      'lg':[],'le':'','role':r,'nonauth':0 if r in('Author','Prize-winning author','Poet','Playwright') else 1,'cc':cc,'cb':cb,'dia':0,'city':'','ph':f"ph/{p['slug']}.jpg" if ok else ''})
    TJ[p['slug']]=italics(body)
fr=sorted([o for o in S if len(o['y'])>=2],key=lambda o:(-len(o['y']),o['n']))
for i,o in enumerate(fr,1): o['p']=1;o['r']=i
S.sort(key=lambda o:o['n'].lower()); json.dump(S,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
json.dump(TJ,open(RAW+'/titles.json','w',encoding='utf8'),ensure_ascii=False)
YEARS=sorted(byyear); per={}
for y in YEARS:
    ks=set(byyear[y]); prior=set().union(*[set(byyear[z]) for z in YEARS if z<y]) if y>YEARS[0] else set()
    per[str(y)]={'total':len(ks),'returning':len(ks&prior),'inNow':len(ks&set(byyear[NOW]))}
nm={k:v for y in YEARS for k,v in byyear[y].items()}; lead=sorted(((k,v) for k,v in yrs.items()),key=lambda kv:(-len(kv[1]),kv[0]))[:25]
json.dump({'per':per,'lead':[{'n':nm[k],'y':v,'in26':NOW in v} for k,v in lead],'hist':dict(Counter(str(sum(1 for y in yrs[norm(o['n'])] if y<NOW)) for o in S))},open(OUT+'/stats.json','w'))
json.dump({str(y):sorted(byyear[y].values()) for y in YEARS},open(OUT+'/history.json','w',encoding='utf8'),ensure_ascii=False)
print(len(S),'speakers;',sum(o['first'] for o in S),'first-timers;',{y:per[str(y)]['total'] for y in YEARS},sum(1 for o in S if o['f']),'bios',sum(1 for o in S if o['ph']),'photos',Counter(o['g'] for o in S))
