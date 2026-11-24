"""Build festivals/bpf/{data,stats,history}.json for the Bengaluru Poetry Festival from bengalurupoetryfestival.org.
2026 poets (bio, photo) come from poets.php; past years from archive/<year>.php (poet names in image alt text).
Usage: python3 tools/build_bpf.py RAWDIR   (RAWDIR holds poets.php.html and a2016.html ... a2025.html saved from the site)"""
import re,sys,json,os,html,io,time,unicodedata,urllib.request
from collections import Counter
from PIL import Image
RAW=sys.argv[1]; OUT=os.path.join(os.path.dirname(__file__),'..','festivals','bpf'); os.makedirs(OUT+'/ph',exist_ok=True); UA={'User-Agent':'Mozilla/5.0'}; NOW=2026
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
CTRY=[('India',r'\b(india|indian|bengaluru|bangalore|delhi|mumbai|kolkata|chennai|hyderabad|kerala|kannada|tamil|telugu|malayalam|hindi|urdu|marathi|bengali|odisha|assam|punjab)\b'),
 ('United Kingdom',r'\b(british|uk|united kingdom|england|london|scotland)\b'),('United States',r'\b(american|united states|usa|new york|california|boston)\b'),
 ('Canada',r'\b(canada|canadian)\b'),('Australia',r'\b(australia|australian)\b'),('Singapore',r'\b(singapore|singaporean)\b'),('United Arab Emirates',r'\b(emirati|uae|dubai|abu dhabi)\b'),
 ('Sri Lanka',r'\b(sri lanka|sri lankan)\b'),('Nepal',r'\b(nepal|nepali)\b'),('Germany',r'\b(german|germany)\b'),('France',r'\b(french|france)\b')]
LANG=['Kannada','Tamil','Telugu','Malayalam','Hindi','Urdu','Marathi','Bengali','English','Odia','Punjabi','Gujarati','Konkani','Tulu','Assamese','Sanskrit']
def country(b):
    l=b.lower(); hits=[(re.search(rx,l).start(),c) for c,rx in CTRY if re.search(rx,l)]
    return (sorted(hits)[0][1],'named in bio') if hits else ('Unknown','')
s=open(f'{RAW}/poets.php.html',encoding='utf8',errors='ignore').read(); cur=[]
for card in s.split('<div class="lg:col-1/5')[1:]:
    a=re.search(r'<img[^>]+src="([^"]+)"[^>]+alt="([^"]+)"',card)
    if not a: continue
    nm=html.unescape(a.group(2)).strip(); m=re.search(r'data-uc-modal="overlay: true">(.*)',card,re.S)
    txt=clean(m.group(1)) if m else ''
    txt=re.sub(r'^\s*'+re.escape(nm)+r'\s*','',txt); txt=re.sub(r'\s*'+re.escape(nm)+r'\s*$','',txt)
    cur.append({'name':nm,'img':a.group(1),'bio':txt})
hist={NOW:[c['name'] for c in cur]}
for y in (2016,2017,2018,2019,2020,2022,2023,2024,2025):
    h=open(f'{RAW}/a{y}.html',encoding='utf8',errors='ignore').read(); names=[]
    for n in re.findall(r'<img[^>]+alt="([^"]{3,60})"',h):
        n=html.unescape(n).strip()
        if n.upper()!='BPF' and n not in names: names.append(n)
    hist[y]=names
byyear={y:{norm(n):n for n in v if norm(n)} for y,v in hist.items()}
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
S=[]
for c in cur:
    n=c['name']; k=norm(n); ys=sorted(yrs[k]); past=[y for y in ys if y<NOW]; full=c['bio']; sl=re.sub(r'[^a-z0-9]+','-',n.lower()).strip('-')
    ok=photo(c['img'],f'{OUT}/ph/{sl}.jpg'); time.sleep(.15)
    cc,cb=country(full) if full else ('Unknown','')
    langs=[l for l in LANG if re.search(r'\b'+l+r'\b',full)]
    S.append({'n':n,'b':short(full),'f':full,'y':ys,'pre':[],'first':0 if past else 1,'g':gender(full) if full else 'u','t':'Poets','p':0,'r':0,'a':'','l':'','s':[],'u':sl,'bk':[],
      'lg':langs[:3],'le':'named in bio' if langs else '','role':'Poet','nonauth':0,'cc':cc,'cb':cb,'dia':0,'city':'Bengaluru' if re.search(r'bengaluru|bangalore',full,re.I) else '','ph':f'ph/{sl}.jpg' if ok else ''})
fr=sorted([o for o in S if sum(1 for y in o['y'] if y<NOW)>=3],key=lambda o:(-len(o['y']),o['n']))
for i,o in enumerate(fr,1): o['p']=1;o['r']=i
S.sort(key=lambda o:o['n'].lower()); json.dump(S,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
YEARS=sorted(byyear); per={}
for y in YEARS:
    ks=set(byyear[y]); prior=set().union(*[set(byyear[z]) for z in YEARS if z<y]) if y>YEARS[0] else set()
    per[str(y)]={'total':len(ks),'returning':len(ks&prior),'inNow':len(ks&set(byyear[NOW]))}
nm={k:v for y in YEARS for k,v in byyear[y].items()}; lead=sorted(yrs.items(),key=lambda kv:(-len(kv[1]),kv[0]))[:25]
json.dump({'per':per,'lead':[{'n':nm[k],'y':v,'in26':NOW in v} for k,v in lead],'hist':dict(Counter(str(sum(1 for y in yrs[norm(o['n'])] if y<NOW)) for o in S))},open(OUT+'/stats.json','w'))
json.dump({str(y):sorted(byyear[y].values()) for y in YEARS},open(OUT+'/history.json','w',encoding='utf8'),ensure_ascii=False)
print(len(S),'poets;',sum(o['first'] for o in S),'first-timers;',{y:per[str(y)]['total'] for y in YEARS},sum(1 for o in S if o['f']),'bios',sum(1 for o in S if o['ph']),'photos',Counter(o['g'] for o in S))
