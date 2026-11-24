"""Build festivals/bhopal/{data,stats,history}.json for the Bhopal Literature & Art Festival (Heartland Stories).
Source: bhopalliteraturefestival.com /event/blf-YYYY/speakers (2019-2027) and, for the 2027 edition, /event/blf-2027/author/<slug> bios.
Usage: python3 tools/build_bhopal.py RAWDIR   (RAWDIR holds spYYYY.html saved from the site; author pages are fetched)"""
import re,sys,json,os,html,io,time,unicodedata,urllib.request
from collections import Counter
from PIL import Image
RAW=sys.argv[1]; OUT=os.path.join(os.path.dirname(__file__),'..','festivals','bplf'); os.makedirs(OUT+'/ph',exist_ok=True); UA={'User-Agent':'Mozilla/5.0'}; NOW=2027
def norm(n):
    n=unicodedata.normalize('NFKD',html.unescape(n)).encode('ascii','ignore').decode().lower()
    n=re.sub(r'\b(dr|prof|professor|mr|ms|mrs|shri|smt|sir|col|maj|gen|retd|justice|amb|ambassador)\b','',n); return re.sub(r'\s+',' ',re.sub(r'[^a-z ]',' ',n)).strip()
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
CTRY=[('India',r'\b(india|indian|bhopal|delhi|mumbai|bengaluru|kolkata|chennai|madhya pradesh)\b'),('United Kingdom',r'\b(british|uk|united kingdom|england|london|scotland|welsh|wales|irish|ireland)\b'),
 ('United States',r'\b(american|united states|usa|new york|california)\b'),('Australia',r'\b(australia|australian)\b'),('Canada',r'\b(canada|canadian)\b'),('Pakistan',r'\b(pakistan|pakistani)\b'),('Bangladesh',r'\b(bangladesh|bangladeshi)\b'),('Nepal',r'\b(nepal|nepali)\b'),('Germany',r'\b(german|germany)\b'),('France',r'\b(french|france)\b')]
def country(b):
    l=b.lower(); h=[(re.search(rx,l).start(),c) for c,rx in CTRY if re.search(rx,l)]
    return (sorted(h)[0][1],'named in bio') if h else ('Unknown','')
ROLES=[('Journalist',r'journalis|editor|anchor|correspondent|columnist'),('Poet',r'\bpoet|poetry|poem'),('Diplomat',r'diplomat|ambassador|\bifs\b'),('Civil servant',r'\bias\b|\bips\b|civil servant|bureaucrat'),('Academic',r'professor|academic|scholar|university|historian'),('Artist',r'\bartist|painter|sculpt|musician|singer|dancer'),('Filmmaker',r'film|cinema|director|actor|actress'),('Author',r'author|writer|novel|books?\b')]
def role(b):
    for r,rx in ROLES:
        if re.search(rx,b,re.I): return r
    return 'Speaker'
by={}; cards={}
for y in range(2019,NOW+1):
    p=f'{RAW}/sp{y}.html'; h=open(p,encoding='utf8',errors='ignore').read() if os.path.exists(p) else (get(f'https://www.bhopalliteraturefestival.com/event/blf-{y}/speakers') or '')
    names={}
    for blk in h.split('<div class="card">')[1:]:
        nm=re.search(r'<h6 class="card-title">(.*?)</h6>',blk,re.S); img=re.search(r'<img src="([^"]+)"',blk)
        if not nm: continue
        n=clean(nm.group(1))
        if n.isupper(): n=n.title()
        names[norm(n)]=n
        pre=h[:h.find(blk)][-400:]; sl=re.findall(r'/author/([a-z0-9\-]+)"',pre)
        if y==NOW: cards[norm(n)]={'name':n,'img':img.group(1) if img else '','slug':sl[-1] if sl else re.sub(r'[^a-z0-9]+','-',n.lower()).strip('-')}
    by[y]=names; print(y,len(names),flush=True)
yrs={}
for y,m in by.items():
    for k in m: yrs.setdefault(k,[]).append(y)
S=[]
for k,c in cards.items():
    sl=c['slug']; h=get(f'https://www.bhopalliteraturefestival.com/event/blf-{NOW}/author/{sl}') or ''
    t=clean(re.sub(r'<script.*?</script>|<style.*?</style>','',h,flags=re.S)); a=t.find('Introduction'); b=t.find('Other Profiles')
    bio=t[a+12:b].strip() if a>=0 and b>a else ''
    fn=f'{OUT}/ph/{sl}.jpg'; ok=os.path.exists(fn)
    if not ok and c['img']:
        try:
            im=Image.open(io.BytesIO(get(c['img'],True))).convert('RGB'); w,hh=im.size
            if w>373: im=im.resize((373,round(hh*373/w)),Image.LANCZOS)
            im.save(fn,'JPEG',quality=82,optimize=True); ok=True
        except Exception: ok=False
    cc,cb=country(bio) if bio else ('Unknown','')
    ys=sorted(yrs[k]); past=[y for y in ys if y<NOW]; r=role(bio)
    S.append({'n':c['name'],'b':short(bio),'f':bio,'y':ys,'pre':[],'first':0 if past else 1,'g':gender(bio) if bio else 'u','t':'Speakers','p':0,'r':0,'a':'','l':'','s':[],'u':sl,'bk':[],'lg':[],'le':'','role':r,'nonauth':0 if r in('Author','Poet') else 1,'cc':cc,'cb':cb,'dia':0,'city':'','ph':f'ph/{sl}.jpg' if ok else ''}); time.sleep(.3)
S.sort(key=lambda o:o['n'].lower()); json.dump(S,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
YEARS=sorted(y for y in by if by[y]); per={}
for y in YEARS:
    ks=set(by[y]); prior=set().union(*[set(by[z]) for z in YEARS if z<y]) if y>YEARS[0] else set()
    per[str(y)]={'total':len(ks),'returning':len(ks&prior),'inNow':len(ks&set(by[NOW]))}
nm={kk:v for y in YEARS for kk,v in by[y].items()}; lead=sorted(yrs.items(),key=lambda kv:(-len(kv[1]),kv[0]))[:25]
json.dump({'per':per,'lead':[{'n':nm[kk],'y':v,'in26':NOW in v} for kk,v in lead],'hist':dict(Counter(str(sum(1 for y in yrs[norm(o['n'])] if y<NOW)) for o in S))},open(OUT+'/stats.json','w'))
json.dump({str(y):sorted(by[y].values()) for y in YEARS},open(OUT+'/history.json','w',encoding='utf8'),ensure_ascii=False)
print(len(S),'speakers',NOW,';',sum(o['first'] for o in S),'first-timers;',sum(1 for o in S if o['ph']),'photos;',sum(1 for o in S if o['b']),'bios')
