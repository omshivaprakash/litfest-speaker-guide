"""Build festivals/klm/{data,stats,history}.json for the Kolkata Literary Meet (KaLaM) from kolkatalitmeet.in.
Each year's site (/2020/ ... /2026/) lists its speakers; 2026 modals give bio, photo and sessions.
Usage: python3 tools/build_klm.py RAWDIR   (RAWDIR is created; writes titles.json for tools/add_books_ol.py)"""
import re,sys,json,os,html,io,time,unicodedata,urllib.request
import concurrent.futures as cf
from collections import Counter
from PIL import Image
RAW=sys.argv[1]; os.makedirs(RAW,exist_ok=True); OUT=os.path.join(os.path.dirname(__file__),'..','festivals','klm'); os.makedirs(OUT+'/ph',exist_ok=True); UA={'User-Agent':'Mozilla/5.0'}; NOW=2026
def norm(n):
    n=unicodedata.normalize('NFKD',html.unescape(n)).encode('ascii','ignore').decode().lower()
    n=re.sub(r'\b(dr|prof|professor|mr|ms|mrs|shri|smt|sir)\b','',n); return re.sub(r'\s+',' ',re.sub(r'[^a-z ]',' ',n)).strip()
def get(u,b=False):
    for _ in range(3):
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read(); return r if b else r.decode('utf8','ignore')
        except Exception: time.sleep(2)
def clean(x): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',x or '').replace('\xa0',' '))).strip()
def short(t,n=220): return t if len(t)<=n else t[:n].rsplit(' ',1)[0]+'…'
def gender(b):
    f=len(re.findall(r"\b(she|her|hers|herself)\b",b,re.I)); m=len(re.findall(r"\b(he|his|him|himself)\b",b,re.I))
    if f>=1 and f>=2*m: return 'f'
    if m>=1 and m>=2*f: return 'm'
    return 'u'
RULES=[(r'\b(nobel|booker prize|pulitzer)\b','Prize-winning author'),(r'\b(film director|filmmaker|screenwriter|lyricist)\b','Filmmaker'),(r'\b(actor|actress)\b','Actor'),
 (r'\b(publisher|literary agent|editor-in-chief)\b','Publishing professional'),(r'\b(translator)\b','Translator'),(r'\b(singer|musician|composer|vocalist)\b','Musician'),
 (r'\b(historian)\b','Historian'),(r'\b(professor|scholar|academic|lecturer)\b','Scholar'),(r'\b(journalist|correspondent|columnist|reporter|broadcaster)\b','Journalist'),
 (r'\b(poet)\b','Poet'),(r'\b(playwright|dramatist)\b','Playwright'),(r'\b(illustrator|cartoonist|artist|dancer)\b','Artist or illustrator'),(r'\b(entrepreneur|investor|ceo)\b','Entrepreneur'),
 (r'\b(novelist|author|writer|memoirist|essayist|biographer)\b','Author')]
def role(b):
    l=b.lower()
    for rx,lab in RULES:
        if re.search(rx,l): return lab
    return 'Speaker'
CTRY=[('India',r'\b(india|indian|kolkata|calcutta|bengal|bengali|delhi|mumbai|bengaluru|chennai|hyderabad|assam|odisha)\b'),('United Kingdom',r'\b(british|uk|united kingdom|england|london|scotland)\b'),
 ('United States',r'\b(american|united states|usa|new york|california|boston)\b'),('Canada',r'\b(canada|canadian)\b'),('Australia',r'\b(australia|australian)\b'),('Bangladesh',r'\b(bangladesh|bangladeshi|dhaka)\b'),
 ('Germany',r'\b(german|germany)\b'),('France',r'\b(french|france)\b'),('Slovakia',r'\b(slovak|slovakia)\b'),('Nepal',r'\b(nepal|nepali)\b'),('Bhutan',r'\b(bhutan|bhutanese)\b')]
def country(b):
    l=b.lower(); hits=[(re.search(rx,l).start(),c) for c,rx in CTRY if re.search(rx,l)]
    return (sorted(hits)[0][1],'named in bio') if hits else ('Unknown','')
CUE=re.compile(r'(author|authored|book|novel|memoir|collection|poem|poetry|essay|biograph|published|bestsell|latest|debut|titles|works|including|include|wrote|written|edited|translat|trilogy|series|sequel|anthology|story|stories)',re.I)
def italics(h):
    out=[]
    for m in re.finditer(r'<(?:em|i)>(.*?)</(?:em|i)>',h or '',re.S):
        t=clean(m.group(1)).strip(' ,.;:')
        if not t or len(t)>110: continue
        pre=clean((h or '')[max(0,m.start()-120):m.start()])
        if CUE.search(pre) or re.search(r'(\bby|\band|,)\s*$',pre+' '): out.append(t)
    return out
hist={}; pages={}
for y in range(2020,NOW+1):
    h=get(f'https://kolkatalitmeet.in/{y}/') or ''; pages[y]=h
    ids=re.findall(r'id="speaker_content_\d+".*?<h2 class="title t_u">(.*?)</h2>',h,re.S)
    hist[y]=[clean(x) for x in ids if clean(x)]
    time.sleep(1)
byyear={y:{norm(n):n for n in v if norm(n)} for y,v in hist.items() if v}
yrs={}
for y,m in byyear.items():
    for k in m: yrs.setdefault(k,[]).append(y)
def photo(url,fn):
    if os.path.exists(fn): return True
    raw=get(url,True)
    try:
        im=Image.open(io.BytesIO(raw)).convert('RGB'); w,h=im.size
        if w>373: im=im.resize((373,round(h*373/w)),Image.LANCZOS)
        im.save(fn,'JPEG',quality=82,optimize=True); return True
    except Exception: return False
cards=[]
for blk in re.split(r'(?=<div class="container m-2 mx-auto" id="speaker_content_)',pages[NOW])[1:]:
    nm=re.search(r'<h2 class="title t_u">(.*?)</h2>',blk,re.S)
    if not nm: continue
    img=re.search(r'<img src="([^"]+)"',blk); body=blk.split('<h2 class="title t_u">',2)
    bio_html=body[1].split('</h2>',1)[1] if len(body)>1 else ''
    sess_html=body[2] if len(body)>2 else ''
    sess=[(clean(a),clean(b)) for a,b in re.findall(r'<span class="date">(.*?)</span>\s*<br\s*/?>\s*(.*?)(?=<span class="date">|$)',sess_html,re.S)]
    cards.append({'name':clean(nm.group(1)),'img':img.group(1) if img else '','bio_html':bio_html,'sess':sess})
def work(c):
    sl=re.sub(r'[^a-z0-9]+','-',c['name'].lower()).strip('-'); ok=photo(c['img'],f'{OUT}/ph/{sl}.jpg') if c['img'] else False; time.sleep(.1); return sl,ok
with cf.ThreadPoolExecutor(3) as ex: ph=list(ex.map(work,cards))
S=[];TJ={}
for c,(sl,ok) in zip(cards,ph):
    n=c['name']; k=norm(n); ys=sorted(yrs.get(k,[NOW])); past=[y for y in ys if y<NOW]; full=clean(c['bio_html'])
    cc,cb=country(full) if full else ('Unknown',''); r=role(full) if full else 'Speaker'
    sess=[[NOW,t.split(' : ')[0].strip(' :')] for d,t in c['sess'] if t]
    S.append({'n':n,'b':short(full),'f':full,'y':ys,'pre':[],'first':0 if past else 1,'g':gender(full) if full else 'u','t':r if r!='Speaker' else 'Other voices','p':0,'r':0,'a':'','l':'','s':sess,'u':sl,'bk':[],
      'lg':[],'le':'','role':r,'nonauth':0 if r in('Author','Prize-winning author','Poet','Playwright') else 1,'cc':cc,'cb':cb,'dia':0,'city':'Kolkata' if re.search(r'kolkata|calcutta',full,re.I) else '','ph':f'ph/{sl}.jpg' if ok else ''})
    TJ[sl]=italics(c['bio_html'])
fr=sorted([o for o in S if sum(1 for y in o['y'] if y<NOW)>=3],key=lambda o:(-len(o['y']),o['n']))
for i,o in enumerate(fr,1): o['p']=1;o['r']=i
S.sort(key=lambda o:o['n'].lower()); json.dump(S,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
json.dump(TJ,open(RAW+'/titles.json','w',encoding='utf8'),ensure_ascii=False)
YEARS=sorted(byyear); per={}
for y in YEARS:
    ks=set(byyear[y]); prior=set().union(*[set(byyear[z]) for z in YEARS if z<y]) if y>YEARS[0] else set()
    per[str(y)]={'total':len(ks),'returning':len(ks&prior),'inNow':len(ks&set(byyear[NOW]))}
nm={k:v for y in YEARS for k,v in byyear[y].items()}; lead=sorted(yrs.items(),key=lambda kv:(-len(kv[1]),kv[0]))[:25]
json.dump({'per':per,'lead':[{'n':nm[k],'y':v,'in26':NOW in v} for k,v in lead],'hist':dict(Counter(str(sum(1 for y in yrs.get(norm(o['n']),[]) if y<NOW)) for o in S))},open(OUT+'/stats.json','w'))
json.dump({str(y):sorted(byyear[y].values()) for y in YEARS},open(OUT+'/history.json','w',encoding='utf8'),ensure_ascii=False)
print(len(S),'speakers;',sum(o['first'] for o in S),'first-timers;',{y:per[str(y)]['total'] for y in YEARS},sum(1 for o in S if o['s']),'with sessions',sum(1 for o in S if o['ph']),'photos',Counter(o['g'] for o in S),'years',YEARS)
