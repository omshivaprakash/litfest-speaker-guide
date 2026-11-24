"""Build festivals/nlf/{data,stats,history}.json for the Neev Literature Festival from neevliteraturefestival.org.
The site's speakers page lists only the featured speakers for each year (about ten), selected with ?y=YEAR for 2023-2026.
Usage: python3 tools/build_nlf.py"""
import re,json,os,html,io,time,unicodedata,urllib.request
from collections import Counter
from PIL import Image
OUT=os.path.join(os.path.dirname(__file__),'..','festivals','nlf'); os.makedirs(OUT+'/ph',exist_ok=True); UA={'User-Agent':'Mozilla/5.0'}; NOW=2026
def norm(n):
    n=unicodedata.normalize('NFKD',html.unescape(n)).encode('ascii','ignore').decode().lower()
    n=re.sub(r'\b(dr|prof|professor|mr|ms|mrs)\b','',n); return re.sub(r'\s+',' ',re.sub(r'[^a-z ]',' ',n)).strip()
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
CTRY=[('India',r'\b(india|indian|bengaluru|bangalore|delhi|mumbai|chennai|kolkata)\b'),('United Kingdom',r'\b(british|uk|united kingdom|england|london|scotland|welsh|wales|irish|ireland)\b'),
 ('United States',r'\b(american|united states|usa|new york|california)\b'),('Australia',r'\b(australia|australian)\b'),('Netherlands',r'\b(dutch|netherlands)\b'),('Canada',r'\b(canada|canadian)\b')]
def country(b):
    l=b.lower(); h=[(re.search(rx,l).start(),c) for c,rx in CTRY if re.search(rx,l)]
    return (sorted(h)[0][1],'named in bio') if h else ('Unknown','')
by={};cards={}
for y in range(2023,NOW+1):
    h=get(f'https://www.neevliteraturefestival.org/speakers-at-nlf/?y={y}') or ''; names={}
    for sl,img,nm in re.findall(r'<article[^>]*speaker[^>]*>.*?href="https://www\.neevliteraturefestival\.org/speaker/([^"/]+)/?".*?<img[^>]*src="([^"]+)".*?<p>(.*?)</p>',h,re.S):
        n=clean(nm)
        if n: names[norm(n)]=n; cards.setdefault(norm(n),{'slug':sl,'img':img,'name':n})
    by[y]=names; time.sleep(1)
yrs={}
for y,m in by.items():
    for k in m: yrs.setdefault(k,[]).append(y)
S=[]
for k,n in by[NOW].items():
    c=cards[k]; h=get(f"https://www.neevliteraturefestival.org/speaker/{c['slug']}/") or ''
    t=clean(re.sub(r'<script.*?</script>|<style.*?</style>','',h,flags=re.S)); a=t.find(c['name'],t.find('Blog')+4)
    seg=t[a+len(c['name']):] if a>=0 else ''
    for stop in ('Share this','Related','Previous','Next ›','Skip to','Back to'): 
        j=seg.find(stop)
        if j>0: seg=seg[:j]
    bio=seg.strip()[:1500]
    fn=f"{OUT}/ph/{c['slug']}.jpg"; ok=os.path.exists(fn)
    if not ok:
        try:
            im=Image.open(io.BytesIO(get(c['img'],True))).convert('RGB'); w,hh=im.size
            if w>373: im=im.resize((373,round(hh*373/w)),Image.LANCZOS)
            im.save(fn,'JPEG',quality=82,optimize=True); ok=True
        except Exception: ok=False
    cc,cb=country(bio) if bio else ('Unknown','')
    ys=sorted(yrs[k]); past=[y for y in ys if y<NOW]
    S.append({'n':c['name'],'b':short(bio),'f':bio,'y':ys,'pre':[],'first':0 if past else 1,'g':gender(bio) if bio else 'u','t':'Children’s authors','p':0,'r':0,'a':'','l':'','s':[],'u':c['slug'],'bk':[],'lg':[],'le':'',
      'role':'Author','nonauth':0,'cc':cc,'cb':cb,'dia':0,'city':'','ph':f"ph/{c['slug']}.jpg" if ok else ''}); time.sleep(.5)
S.sort(key=lambda o:o['n'].lower()); json.dump(S,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
YEARS=sorted(by); per={}
for y in YEARS:
    ks=set(by[y]); prior=set().union(*[set(by[z]) for z in YEARS if z<y]) if y>YEARS[0] else set()
    per[str(y)]={'total':len(ks),'returning':len(ks&prior),'inNow':len(ks&set(by[NOW]))}
nm={k:v for y in YEARS for k,v in by[y].items()}; lead=sorted(yrs.items(),key=lambda kv:(-len(kv[1]),kv[0]))[:25]
json.dump({'per':per,'lead':[{'n':nm[k],'y':v,'in26':NOW in v} for k,v in lead],'hist':dict(Counter(str(sum(1 for y in yrs[norm(o['n'])] if y<NOW)) for o in S))},open(OUT+'/stats.json','w'))
json.dump({str(y):sorted(by[y].values()) for y in YEARS},open(OUT+'/history.json','w',encoding='utf8'),ensure_ascii=False)
print(len(S),'speakers',{y:per[str(y)]['total'] for y in YEARS},sum(1 for o in S if o['f']),'bios',sum(1 for o in S if o['ph']),'photos')
