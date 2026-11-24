"""Build festivals/nlf/{data,stats,history}.json for the Neev Literature Festival from neevliteraturefestival.org's public WordPress API
(speaker posts tagged by event year, 2017-2026). The 2026 edition is the current list; earlier years feed the history.
Usage: python3 tools/build_nlf.py"""
import re,json,os,html,io,time,unicodedata,urllib.request
from collections import Counter
from PIL import Image
OUT=os.path.join(os.path.dirname(__file__),'..','festivals','nlf'); os.makedirs(OUT+'/ph',exist_ok=True); UA={'User-Agent':'Mozilla/5.0'}; NOW=2026; API='https://www.neevliteraturefestival.org/wp-json/wp/v2/'
def norm(n):
    n=unicodedata.normalize('NFKD',html.unescape(n)).encode('ascii','ignore').decode().lower()
    n=re.sub(r'\b(dr|prof|professor|mr|ms|mrs)\b','',n); return re.sub(r'\s+',' ',re.sub(r'[^a-z ]',' ',n)).strip()
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
CTRY=[('India',r'\b(india|indian|bengaluru|bangalore|delhi|mumbai|chennai|kolkata|hyderabad|pune)\b'),('United Kingdom',r'\b(british|uk|united kingdom|england|london|scotland|edinburgh|welsh|wales|irish|ireland)\b'),
 ('United States',r'\b(american|united states|usa|new york|california)\b'),('Australia',r'\b(australia|australian)\b'),('Netherlands',r'\b(dutch|netherlands)\b'),('Canada',r'\b(canada|canadian)\b')]
def country(b):
    l=b.lower(); h=[(re.search(rx,l).start(),c) for c,rx in CTRY if re.search(rx,l)]
    return (sorted(h)[0][1],'named in bio') if h else ('Unknown','')
terms={t['id']:int(t['name']) for t in json.loads(get(API+'event_year?per_page=100&_fields=id,name'))}
posts=[]; p=1
while True:
    r=get(f'{API}speaker?per_page=100&page={p}&_fields=id,slug,title,link,content,featured_media,event_year,event_category')
    try: d=json.loads(r)
    except Exception: break
    if not d: break
    posts+=d; p+=1
    if len(d)<100: break
print(len(posts),'speaker posts',flush=True)
by={}; cards={}
for o in posts:
    n=clean(o['title']['rendered'])
    if not n: continue
    k=norm(n)
    for t in o['event_year']:
        y=terms.get(t)
        if y: by.setdefault(y,{})[k]=n
    if NOW in [terms.get(t) for t in o['event_year']] or k not in cards: cards.setdefault(k,o)
    if NOW in [terms.get(t) for t in o['event_year']]: cards[k]=o
yrs={}
for y,m in by.items():
    for k in m: yrs.setdefault(k,[]).append(y)
cur=[cards[k] for k in by[NOW]]
ids=[str(o['featured_media']) for o in cur if o.get('featured_media')]; media={}
for i in ids:
    try:
        m=json.loads(get(f"{API}media/{i}?_fields=id,source_url,media_details")); sz=(m.get('media_details') or {}).get('sizes',{}); media[m['id']]=(sz.get('medium_large') or sz.get('large') or sz.get('medium') or {}).get('source_url') or m['source_url']
    except Exception: pass
    time.sleep(.15)
S=[]
for o in cur:
    n=clean(o['title']['rendered']); k=norm(n); sl=o['slug']; bio=clean(o['content']['rendered'])[:1500]
    fn=f'{OUT}/ph/{sl}.jpg'; ok=os.path.exists(fn); u=media.get(o.get('featured_media'))
    if not ok and u:
        try:
            im=Image.open(io.BytesIO(get(u,True))).convert('RGB'); w,hh=im.size
            if w>373: im=im.resize((373,round(hh*373/w)),Image.LANCZOS)
            im.save(fn,'JPEG',quality=82,optimize=True); ok=True
        except Exception: ok=False
    cc,cb=country(bio) if bio else ('Unknown','')
    ys=sorted(yrs[k]); past=[y for y in ys if y<NOW]; chall=3 not in o['event_category']
    S.append({'n':n,'b':short(bio),'f':bio,'y':ys,'pre':[],'first':0 if past else 1,'g':gender(bio) if bio else 'u','t':'Reading Challenge authors' if chall else 'Featured speakers','p':0,'r':0,'a':'','l':'','s':[],'u':sl,'bk':[],'lg':[],'le':'','role':'Author','nonauth':0,'cc':cc,'cb':cb,'dia':0,'city':'','ph':f'ph/{sl}.jpg' if ok else ''}); time.sleep(.1)
S.sort(key=lambda o:o['n'].lower()); json.dump(S,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
YEARS=sorted(by); per={}
for y in YEARS:
    ks=set(by[y]); prior=set().union(*[set(by[z]) for z in YEARS if z<y]) if y>YEARS[0] else set()
    per[str(y)]={'total':len(ks),'returning':len(ks&prior),'inNow':len(ks&set(by[NOW]))}
nm={k:v for y in YEARS for k,v in by[y].items()}; lead=sorted(yrs.items(),key=lambda kv:(-len(kv[1]),kv[0]))[:25]
json.dump({'per':per,'lead':[{'n':nm[k],'y':v,'in26':NOW in v} for k,v in lead],'hist':dict(Counter(str(sum(1 for y in yrs[norm(o['n'])] if y<NOW)) for o in S))},open(OUT+'/stats.json','w'))
json.dump({str(y):sorted(by[y].values()) for y in YEARS},open(OUT+'/history.json','w',encoding='utf8'),ensure_ascii=False)
print(len(S),'speakers',{y:per[str(y)]['total'] for y in YEARS},sum(1 for o in S if o['f']),'bios',sum(1 for o in S if o['ph']),'photos')
