"""Build festivals/galf/{data,stats,history}.json for the Goa Arts and Literature Festival from goaartlitfest.com.
Each year's /speaker-YYYY/ page lists its speakers 12 at a time ('Load More' = /page/N/); the image alt text carries the bio.
Usage: python3 tools/build_galf.py"""
import re,json,os,html,io,time,unicodedata,urllib.request
from collections import Counter
from PIL import Image
OUT=os.path.join(os.path.dirname(__file__),'..','festivals','galf'); os.makedirs(OUT+'/ph',exist_ok=True); UA={'User-Agent':'Mozilla/5.0'}; NOW=2026
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
RULES=[(r'\b(nobel|booker prize|pulitzer)\b','Prize-winning author'),(r'\b(film director|filmmaker|screenwriter|lyricist)\b','Filmmaker'),(r'\b(actor|actress)\b','Actor'),(r'\b(publisher|literary agent|editor-in-chief)\b','Publishing professional'),
 (r'\b(translator)\b','Translator'),(r'\b(singer|musician|composer|vocalist)\b','Musician'),(r'\b(historian)\b','Historian'),(r'\b(professor|scholar|academic|lecturer)\b','Scholar'),
 (r'\b(journalist|correspondent|columnist|reporter|broadcaster)\b','Journalist'),(r'\b(poet)\b','Poet'),(r'\b(playwright|dramatist)\b','Playwright'),(r'\b(artist|dancer|painter|photographer)\b','Artist or illustrator'),
 (r'\b(novelist|author|writer|memoirist|essayist|biographer)\b','Author')]
def role(b):
    l=b.lower()
    for rx,lab in RULES:
        if re.search(rx,l): return lab
    return 'Speaker'
CTRY=[('India',r'\b(india|indian|goa|goan|konkani|mumbai|delhi|kolkata|bengaluru|bangalore|kerala|chennai)\b'),('Slovenia',r'\b(slovenian|slovenia)\b'),('United Kingdom',r'\b(british|uk|united kingdom|england|london|scotland)\b'),
 ('United States',r'\b(american|united states|usa|new york|california)\b'),('Portugal',r'\b(portuguese|portugal|lisbon)\b'),('France',r'\b(french|france)\b'),('Germany',r'\b(german|germany)\b')]
def country(b):
    l=b.lower(); h=[(re.search(rx,l).start(),c) for c,rx in CTRY if re.search(rx,l)]
    return (sorted(h)[0][1],'named in bio') if h else ('Unknown','')
by={};cards={}
for y in range(2023,NOW+1):
    names={};p=1
    while p<15:
        h=get(f'https://goaartlitfest.com/speaker-{y}/'+(f'page/{p}/' if p>1 else '')) or ''
        items=re.split(r'(?=<article class="wpr-grid-item)',h)[1:]; new=0
        for it in items:
            m=re.search(r'wpr-grid-item-title.*?<a\s+href="https://goaartlitfest\.com/([a-z0-9-]+)/">(.*?)</a>',it,re.S)
            alt=re.search(r'<img[^>]*alt="([^"]*)"',it); img=re.search(r'data-src="([^"]+)"',it)
            if m: sl,n=m.group(1),clean(m.group(2))
            elif alt and len(alt.group(1))<60 and img: n=clean(alt.group(1)); sl=re.sub(r'[^a-z0-9]+','-',n.lower()).strip('-')
            else: continue
            k=norm(n)
            if not k or k in names: continue
            names[k]=n; new+=1
            bio=clean(alt.group(1)) if alt else ''
            c=cards.setdefault(k,{'slug':sl,'name':n,'bio':'','img':''})
            if y==NOW:
                c['bio']=bio if len(bio)>len(c['bio']) and bio.lower()!=n.lower() else c['bio']; c['img']=img.group(1) if img else c['img']
        for n in re.findall(r'<h2 class="profile-title">.*?<a[^>]*>(.*?)</a>',h,re.S):
            n=clean(n); k=norm(n)
            if k and k not in names: names[k]=n; new+=1; cards.setdefault(k,{'slug':re.sub(r'[^a-z0-9]+','-',n.lower()).strip('-'),'name':n,'bio':'','img':''})
        if not new: break
        p+=1; time.sleep(1)
    by[y]=names; print(y,len(names),flush=True)
yrs={}
for y,m in by.items():
    for k in m: yrs.setdefault(k,[]).append(y)
S=[]
for k,n in by[NOW].items():
    c=cards[k]; full=c['bio']; sl=c['slug']; fn=f'{OUT}/ph/{sl}.jpg'; ok=os.path.exists(fn)
    if not ok and c['img']:
        try:
            im=Image.open(io.BytesIO(get(c['img'],True))).convert('RGB'); w,hh=im.size
            if w>373: im=im.resize((373,round(hh*373/w)),Image.LANCZOS)
            im.save(fn,'JPEG',quality=82,optimize=True); ok=True
        except Exception: ok=False
    time.sleep(.15)
    cc,cb=country(full) if full else ('Unknown',''); r=role(full) if full else 'Speaker'; ys=sorted(yrs[k]); past=[y for y in ys if y<NOW]
    S.append({'n':n,'b':short(full),'f':full,'y':ys,'pre':[],'first':0 if past else 1,'g':gender(full) if full else 'u','t':r if r!='Speaker' else 'Other voices','p':0,'r':0,'a':'','l':'','s':[],'u':sl,'bk':[],
      'lg':[],'le':'','role':r,'nonauth':0 if r in('Author','Prize-winning author','Poet','Playwright') else 1,'cc':cc,'cb':cb,'dia':0,'city':'Goa' if re.search(r'\bgoa\b',full,re.I) else '','ph':f'ph/{sl}.jpg' if ok else ''})
fr=sorted([o for o in S if sum(1 for y in o['y'] if y<NOW)>=2],key=lambda o:(-len(o['y']),o['n']))
for i,o in enumerate(fr,1): o['p']=1;o['r']=i
S.sort(key=lambda o:o['n'].lower()); json.dump(S,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
YEARS=sorted(by); per={}
for y in YEARS:
    ks=set(by[y]); prior=set().union(*[set(by[z]) for z in YEARS if z<y]) if y>YEARS[0] else set()
    per[str(y)]={'total':len(ks),'returning':len(ks&prior),'inNow':len(ks&set(by[NOW]))}
nm={k:v for y in YEARS for k,v in by[y].items()}; lead=sorted(yrs.items(),key=lambda kv:(-len(kv[1]),kv[0]))[:25]
json.dump({'per':per,'lead':[{'n':nm[k],'y':v,'in26':NOW in v} for k,v in lead],'hist':dict(Counter(str(sum(1 for y in yrs[norm(o['n'])] if y<NOW)) for o in S))},open(OUT+'/stats.json','w'))
json.dump({str(y):sorted(by[y].values()) for y in YEARS},open(OUT+'/history.json','w',encoding='utf8'),ensure_ascii=False)
print(len(S),'speakers;',sum(o['first'] for o in S),'first-timers;',{y:per[str(y)]['total'] for y in YEARS},sum(1 for o in S if o['f']),'bios',sum(1 for o in S if o['ph']),'photos',Counter(o['g'] for o in S))
