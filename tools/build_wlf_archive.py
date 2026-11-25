"""Build festivals/wlf24 and festivals/wlf22 (speaker-type, archived editions) for the Wayanad Literature Festival from the archive
sites' WordPress APIs (wlfwayanad.com/2024 and /2022): every speaker post with bio and photo. wlf24 knows who also spoke in 2022.
Usage: python3 tools/build_wlf_archive.py"""
import re,json,os,html,io,time,unicodedata,urllib.request
import concurrent.futures as cf
from collections import Counter
from PIL import Image
R=os.path.join(os.path.dirname(__file__),'..','festivals'); UA={'User-Agent':'Mozilla/5.0'}; B='https://wlfwayanad.com/'
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
CTRY=[('India',r'\b(india|indian|kerala|malayalam|malayali|delhi|mumbai|bengaluru|bangalore|kolkata|chennai|kozhikode|thiruvananthapuram|kochi|wayanad|thrissur|kannur|hyderabad)\b'),('United Kingdom',r'\b(british|uk|united kingdom|england|london|scotland|wales)\b'),('United States',r'\b(american|united states|usa|new york|california)\b'),('Australia',r'\b(australia|australian)\b'),('Canada',r'\b(canada|canadian)\b'),('Germany',r'\b(german|germany)\b'),('France',r'\b(french|france)\b')]
def country(b):
    l=b.lower(); h=[(re.search(rx,l).start(),c) for c,rx in CTRY if re.search(rx,l)]
    return (sorted(h)[0][1],'named in bio') if h else ('Unknown','')
ROLES=[('Journalist',r'journalis|editor|anchor|correspondent|columnist'),('Politician',r'\bmla\b|\bmp\b|minister|member of parliament|politic|legislat'),('Poet',r'\bpoet|poetry'),('Filmmaker',r'film|cinema|director|actor|actress|screenwrit'),('Academic',r'professor|academic|scholar|university|historian|researcher'),('Artist',r'\bartist|painter|sculpt|musician|singer|dancer|theatre'),('Activist',r'activist|lawyer|advocate|campaign'),('Author',r'author|writer|novel|books?\b|story|stories')]
def role(b):
    for r,rx in ROLES:
        if re.search(rx,b,re.I): return r
    return 'Speaker'
def api(base):
    out=[];p=1
    while True:
        try: d=json.loads(get(f'{base}wp-json/wp/v2/speaker?per_page=100&page={p}&_fields=id,slug,title,link,content,featured_media'))
        except Exception: break
        if not d: break
        out+=d; p+=1
        if len(d)<100: break
    return out
E24=api(B+'2024/'); E22=api(B+'2022/'); print(len(E24),len(E22),flush=True)
names={y:{norm(clean(o['title']['rendered'])):clean(o['title']['rendered']) for o in L if clean(o['title']['rendered'])} for y,L in ((2022,E22),(2024,E24))}
def build(fid,year,L,base,prior):
    OUT=f'{R}/{fid}'; os.makedirs(OUT+'/ph',exist_ok=True); S=[]; seen=set(); todo=[]
    for o in L:
        n=clean(o['title']['rendered']); k=norm(n)
        if not n or k in seen: continue
        seen.add(k); todo.append((o,n,k))
    def photo(o):
        sl=o['slug']; fn=f'{OUT}/ph/{sl}.jpg'
        if os.path.exists(fn) or os.path.exists(fn[:-4]+'.webp'): return True
        if not o.get('featured_media'): return False
        try:
            u=json.loads(get(f"{base}wp-json/wp/v2/media/{o['featured_media']}?_fields=source_url"))['source_url']
            im=Image.open(io.BytesIO(get(u,True))).convert('RGB'); w,hh=im.size
            if w>373: im=im.resize((373,round(hh*373/w)),Image.LANCZOS)
            im.save(fn,'JPEG',quality=82,optimize=True); return True
        except Exception: return False
    with cf.ThreadPoolExecutor(8) as ex: oks=list(ex.map(photo,[t[0] for t in todo]))
    for (o,n,k),ok in zip(todo,oks):
        sl=o['slug']; bio=clean(o['content']['rendered'])[:1800]
        cc,cb=country(bio) if bio else ('Unknown','')
        ys=sorted([y for y in prior if k in names[y]]+[year]); r=role(bio)
        S.append({'n':n,'b':short(bio),'f':bio,'y':ys,'pre':[],'first':0 if len(ys)>1 else 1,'g':gender(bio) if bio else 'u','t':'Speakers','p':0,'r':0,'a':'','l':'','s':[],'u':sl,'bk':[],'lg':[],'le':'','role':r,'nonauth':0 if r in('Author','Poet') else 1,'cc':cc,'cb':cb,'dia':0,'city':'','ph':f'ph/{sl}.jpg' if ok else ''})
    S.sort(key=lambda o:o['n'].lower()); json.dump(S,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
    YEARS=sorted(set(prior)|{year}); per={}
    for y in YEARS:
        ks=set(norm(n) for n in names[y].values()); pr=set().union(*[set(names[z]) for z in YEARS if z<y]) if y>YEARS[0] else set()
        per[str(y)]={'total':len(ks),'returning':len(ks&pr),'inNow':len(ks&set(names[year]))}
    json.dump({'per':per,'lead':[],'hist':dict(Counter(str(len(o['y'])-1) for o in S))},open(OUT+'/stats.json','w'))
    json.dump({str(y):sorted(names[y].values()) for y in YEARS},open(OUT+'/history.json','w',encoding='utf8'),ensure_ascii=False)
    print(fid,len(S),'speakers;',sum(o['first'] for o in S),'first-timers;',sum(1 for o in S if o['ph']),'photos',flush=True)
build('wlf24',2024,E24,B+'2024/',[2022]); build('wlf22',2022,E22,B+'2022/',[])
