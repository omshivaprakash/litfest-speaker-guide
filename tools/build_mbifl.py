"""Build festivals/mbifl/{data,stats,history}.json for the Mathrubhumi International Festival of Letters (MBIFL, Thiruvananthapuram).
Sources (www.mbifl.com, assets.mbifl.com, english.mathrubhumi.com): 2027 /api/speakers.php + assets detail JSON; 2026 speakers.html;
2025 english.mathrubhumi.com/json/mbifl-2025/speakers/<type> (first 20 per type); 2024 /2024/speakers/<type>/<type>.json;
2023 /2023/speakers-2023/ headings; 2018-2020 speakers JSON feeds. Edition years: 2018, 2019, 2020, 2023-2027.
Usage: python3 tools/build_mbifl.py"""
import re,json,os,html,io,time,unicodedata,urllib.request
from collections import Counter
from PIL import Image
OUT=os.path.join(os.path.dirname(__file__),'..','festivals','mbifl'); os.makedirs(OUT+'/ph',exist_ok=True); UA={'User-Agent':'Mozilla/5.0'}; NOW=2027; B='https://www.mbifl.com/'
def norm(n):
    n=unicodedata.normalize('NFKD',html.unescape(n)).encode('ascii','ignore').decode().lower()
    n=re.sub(r'\b(dr|prof|professor|mr|ms|mrs|shri|sri|smt|sir|adv|fr|rev|justice|amb|ambassador)\b','',n); return re.sub(r'\s+',' ',re.sub(r'[^a-z ]',' ',n)).strip()
def get(u,b=False):
    for _ in range(3):
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read(); return r if b else r.decode('utf8','ignore')
        except Exception: time.sleep(2)
def clean(x): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',x or '').replace('\xa0',' '))).strip()
def tc(n): n=clean(n); return n.title() if n.isupper() else n
def short(t,n=220): return t if len(t)<=n else t[:n].rsplit(' ',1)[0]+'…'
def feed(u):
    s=get(u) or ''
    try: return json.loads(s.strip().lstrip('﻿'))['_news']
    except Exception: return []
def gender(b):
    f=len(re.findall(r"\b(she|her|hers|herself)\b",b,re.I)); m=len(re.findall(r"\b(he|his|him|himself)\b",b,re.I))
    if f>=1 and f>=2*m: return 'f'
    if m>=1 and m>=2*f: return 'm'
    return 'u'
CTRY=[('India',r'\b(india|indian|kerala|delhi|mumbai|bengaluru|kolkata|chennai|thiruvananthapuram|malayalam|hindi)\b'),('United Kingdom',r'\b(british|uk|united kingdom|england|london|scotland|welsh|wales|irish|ireland)\b'),
 ('United States',r'\b(american|united states|usa|new york|california)\b'),('Australia',r'\b(australia|australian)\b'),('Canada',r'\b(canada|canadian)\b'),('Sri Lanka',r'\b(sri lanka|sri lankan)\b'),('Germany',r'\b(german|germany)\b'),('France',r'\b(french|france)\b'),('Iceland',r'\b(iceland|icelandic)\b'),('Tanzania',r'\b(tanzania|tanzanian)\b')]
def country(b):
    l=b.lower(); h=[(re.search(rx,l).start(),c) for c,rx in CTRY if re.search(rx,l)]
    return (sorted(h)[0][1],'named in bio') if h else ('Unknown','')
ROLES=[('Journalist',r'journalis|editor|anchor|correspondent|columnist'),('Poet',r'\bpoet|poetry|poem'),('Diplomat',r'diplomat|ambassador|\bifs\b'),('Civil servant',r'\bias\b|\bips\b|civil servant|bureaucrat'),('Academic',r'professor|academic|scholar|university|historian'),('Artist',r'\bartist|painter|sculpt|musician|singer|lyricist|dancer'),('Filmmaker',r'film|cinema|director|actor|actress'),('Author',r'author|writer|novel|books?\b')]
def role(b):
    for r,rx in ROLES:
        if re.search(rx,b,re.I): return r
    return 'Speaker'
by={}
for y,p in ((2018,'2018/speakers.json'),(2019,'2019/apps/speakers.json'),(2020,'2020/app/speakers.json')):
    by[y]={norm(tc(x['_title'])):tc(x['_title']) for x in feed(B+p) if x.get('_title')}
s=get(B+'2023/speakers-2023/') or ''; t=re.sub(r'<script.*?</script>|<style.*?</style>','',s,flags=re.S)
hs=[clean(x) for x in re.findall(r'<h[2-6][^>]*>(.*?)</h[2-6]>',t,re.S)]; by[2023]={norm(n):n for n in hs[hs.index('2023 speakers')+1:] if norm(n)}
by[2024]={}
for ty in ('regional','national','international'):
    for x in feed(f'{B}2024/speakers/{ty}/{ty}.json'): by[2024][norm(tc(x['_title']))]=tc(x['_title'])
by[2025]={}
for ty in ('regional','national','international'):
    for x in feed(f'https://english.mathrubhumi.com/json/mbifl-2025/speakers/{ty}'): by[2025][norm(tc(x['_title']))]=tc(x['_title'])
s=get(B+'2026/speakers.html') or ''; by[2026]={}
for m in re.finditer(r'data-speaker-id="[^"]+" data-speaker-name="[^"]*">.*?alt="([^"]*)"',s,re.S): by[2026][norm(tc(m.group(1)))]=tc(m.group(1))
cur=json.loads(get(B+'api/speakers.php')); by[NOW]={}; cards={}
for c in cur:
    n=tc(c['speakerName']); by[NOW][norm(n)]=n; cards[norm(n)]={'name':n,'id':c['uniqueID'],'img':c['photoPortrait']}
for y in sorted(by): print(y,len(by[y]),flush=True)
yrs={}
for y,m in by.items():
    for k in m: yrs.setdefault(k,[]).append(y)
CAT={'R':'Regional','N':'National','I':'International'}; S=[]
for k,c in cards.items():
    d=get(f"https://assets.mbifl.com/json/{NOW}/speakers/{c['id']}.json") or '[]'
    try: d=json.loads(d)[0]
    except Exception: d={}
    bio=clean(d.get('enTxt','')); cat=CAT.get(d.get('speakerCategory'),'Speakers'); sl=re.sub(r'[^a-z0-9]+','-',c['name'].lower()).strip('-'); fn=f'{OUT}/ph/{sl}.jpg'; ok=os.path.exists(fn)
    if not ok:
        try:
            im=Image.open(io.BytesIO(get(c['img'],True))).convert('RGB'); w,hh=im.size
            if w>373: im=im.resize((373,round(hh*373/w)),Image.LANCZOS)
            im.save(fn,'JPEG',quality=82,optimize=True); ok=True
        except Exception: ok=False
    cc,cb=country(bio) if bio else ('Unknown','')
    if cat=='International' and cc=='India': cc,cb='Unknown',''
    ys=sorted(yrs[k]); past=[y for y in ys if y<NOW]; r=role(bio)
    S.append({'n':c['name'],'b':short(bio),'f':bio,'y':ys,'pre':[],'first':0 if past else 1,'g':gender(bio) if bio else 'u','t':cat,'p':0,'r':0,'a':'','l':'','s':[],'u':sl,'bk':[],'lg':[],'le':'','role':r,'nonauth':0 if r in('Author','Poet') else 1,'cc':cc,'cb':cb,'dia':0,'city':'','ph':f'ph/{sl}.jpg' if ok else ''}); time.sleep(.3)
S.sort(key=lambda o:o['n'].lower()); json.dump(S,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
YEARS=sorted(y for y in by if by[y]); per={}
for y in YEARS:
    ks=set(by[y]); prior=set().union(*[set(by[z]) for z in YEARS if z<y]) if y>YEARS[0] else set()
    per[str(y)]={'total':len(ks),'returning':len(ks&prior),'inNow':len(ks&set(by[NOW]))}
nm={kk:v for y in YEARS for kk,v in by[y].items()}; lead=sorted(yrs.items(),key=lambda kv:(-len(kv[1]),kv[0]))[:25]
json.dump({'per':per,'lead':[{'n':nm[kk],'y':v,'in26':NOW in v} for kk,v in lead],'hist':dict(Counter(str(sum(1 for y in yrs[norm(o['n'])] if y<NOW)) for o in S))},open(OUT+'/stats.json','w'))
json.dump({str(y):sorted(by[y].values()) for y in YEARS},open(OUT+'/history.json','w',encoding='utf8'),ensure_ascii=False)
print(len(S),'speakers',NOW,';',sum(o['first'] for o in S),'first-timers;',sum(1 for o in S if o['ph']),'photos;',sum(1 for o in S if o['b']),'bios')
