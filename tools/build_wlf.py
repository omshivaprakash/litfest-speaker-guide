"""Build festivals/wlf/{data,stats,history}.json for the Wayanad Literature Festival (wlfwayanad.com).
2026 speakers: the site's WordPress API (wlf_speaker posts) plus photos from /speakers/; earlier editions: /2022 and /2024 archive sites (speaker posts).
There was no festival in 2023 or 2025. Usage: python3 tools/build_wlf.py"""
import re,json,os,html,io,time,unicodedata,urllib.request
from collections import Counter
from PIL import Image
OUT=os.path.join(os.path.dirname(__file__),'..','festivals','wlf'); os.makedirs(OUT+'/ph',exist_ok=True); UA={'User-Agent':'Mozilla/5.0'}; NOW=2026; B='https://wlfwayanad.com/'
def norm(n):
    n=unicodedata.normalize('NFKD',html.unescape(n)).encode('ascii','ignore').decode().lower()
    n=re.sub(r'\b(dr|prof|professor|mr|ms|mrs|shri|smt|sir|adv|fr|rev|justice|hon)\b','',n); n=re.sub(r'\b([a-z]) (?=[a-z]\b)',r'\1',re.sub(r'[^a-z ]',' ',n)); return re.sub(r'\s+',' ',n).strip()
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
CTRY=[('India',r'\b(india|indian|kerala|malayalam|malayali|delhi|mumbai|bengaluru|bangalore|kolkata|chennai|kozhikode|thiruvananthapuram|kochi|wayanad|thrissur|kannur|hyderabad)\b'),('United Kingdom',r'\b(british|uk|united kingdom|england|london|scotland|wales)\b'),
 ('United States',r'\b(american|united states|usa|new york|california)\b'),('Australia',r'\b(australia|australian)\b'),('Canada',r'\b(canada|canadian)\b'),('Germany',r'\b(german|germany)\b'),('France',r'\b(french|france)\b'),('Sri Lanka',r'\b(sri lanka|sri lankan)\b')]
def country(b):
    l=b.lower(); h=[(re.search(rx,l).start(),c) for c,rx in CTRY if re.search(rx,l)]
    return (sorted(h)[0][1],'named in bio') if h else ('Unknown','')
ROLES=[('Journalist',r'journalis|editor|anchor|correspondent|columnist'),('Politician',r'\bmla\b|\bmp\b|minister|member of parliament|politic|legislat'),('Poet',r'\bpoet|poetry'),('Filmmaker',r'film|cinema|director|actor|actress|screenwrit'),('Academic',r'professor|academic|scholar|university|historian|researcher'),('Artist',r'\bartist|painter|sculpt|musician|singer|dancer|theatre'),('Activist',r'activist|lawyer|advocate|campaign'),('Author',r'author|writer|novel|books?\b|story|stories')]
def role(b):
    for r,rx in ROLES:
        if re.search(rx,b,re.I): return r
    return 'Speaker'
def api(base,t):
    out=[];p=1
    while True:
        try: d=json.loads(get(f'{base}wp-json/wp/v2/{t}?per_page=100&page={p}&_fields=id,slug,title,link,content'))
        except Exception: break
        if not d: break
        out+=d; p+=1
        if len(d)<100: break
    return out
by={}
for y,base,t in ((2022,B+'2022/','speaker'),(2024,B+'2024/','speaker'),(NOW,B,'wlf_speaker')):
    L=api(base,t); by[y]={}
    for o in L:
        n=clean(o['title']['rendered'])
        if n: by[y][norm(n)]=n
    print(y,len(by[y]),flush=True)
    if y==NOW: cur=L
page=get(B+'speakers/') or ''; img={}
for a in re.finditer(r'<a class="wlf-speaker-card__photo" href="https://wlfwayanad.com/speakers/([a-z0-9\-]+)/".*?<img[^>]*src="([^"]+)"',page,re.S): img[a.group(1)]=a.group(2)
yrs={}
for y,m in by.items():
    for k in m: yrs.setdefault(k,[]).append(y)
S=[]
for o in cur:
    n=clean(o['title']['rendered']); k=norm(n); sl=o['slug']; bio=clean(o['content']['rendered'])[:1800]
    fn=f'{OUT}/ph/{sl}.jpg'; ok=os.path.exists(fn); u=img.get(sl)
    if not ok and u:
        try:
            im=Image.open(io.BytesIO(get(u,True))).convert('RGB'); w,hh=im.size
            if w>373: im=im.resize((373,round(hh*373/w)),Image.LANCZOS)
            im.save(fn,'JPEG',quality=82,optimize=True); ok=True
        except Exception: ok=False
    cc,cb=country(bio) if bio else ('Unknown','')
    ys=sorted(yrs[k]); past=[y for y in ys if y<NOW]; r=role(bio)
    S.append({'n':n,'b':short(bio),'f':bio,'y':ys,'pre':[],'first':0 if past else 1,'g':gender(bio) if bio else 'u','t':'Speakers','p':0,'r':0,'a':'','l':'','s':[],'u':sl,'bk':[],'lg':[],'le':'','role':r,'nonauth':0 if r in('Author','Poet') else 1,'cc':cc,'cb':cb,'dia':0,'city':'','ph':f'ph/{sl}.jpg' if ok else ''}); time.sleep(.15)
S.sort(key=lambda o:o['n'].lower()); json.dump(S,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
YEARS=sorted(y for y in by if by[y]); per={}
for y in YEARS:
    ks=set(by[y]); prior=set().union(*[set(by[z]) for z in YEARS if z<y]) if y>YEARS[0] else set()
    per[str(y)]={'total':len(ks),'returning':len(ks&prior),'inNow':len(ks&set(by[NOW]))}
nm={kk:v for y in YEARS for kk,v in by[y].items()}; lead=sorted(yrs.items(),key=lambda kv:(-len(kv[1]),kv[0]))[:25]
json.dump({'per':per,'lead':[{'n':nm[kk],'y':v,'in26':NOW in v} for kk,v in lead],'hist':dict(Counter(str(sum(1 for y in yrs[norm(o['n'])] if y<NOW)) for o in S))},open(OUT+'/stats.json','w'))
json.dump({str(y):sorted(by[y].values()) for y in YEARS},open(OUT+'/history.json','w',encoding='utf8'),ensure_ascii=False)
print(len(S),'speakers',NOW,';',sum(o['first'] for o in S),'first-timers;',sum(1 for o in S if o['ph']),'photos;',sum(1 for o in S if o['b']),'bios')
