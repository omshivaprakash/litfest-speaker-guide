"""Build festivals/ddlf/{data,stats,history}.json for the Dehradun Literature Festival (8th edition, 27-29 Nov 2026).
Sources (Wix pages on www.dehradunliteraturefestival.com): /team (2026 speakers, names and photos only) and /archives
(the 2025 speaker list; the other year tabs on that page load on demand and are not included).
Usage: python3 tools/build_ddlf.py RAWDIR   (RAWDIR holds team.html and archives.html saved from the site)"""
import re,sys,json,os,html,io,time,unicodedata,urllib.request
from collections import Counter
from PIL import Image
RAW=sys.argv[1]; OUT=os.path.join(os.path.dirname(__file__),'..','festivals','ddlf'); os.makedirs(OUT+'/ph',exist_ok=True); UA={'User-Agent':'Mozilla/5.0'}; NOW=2026
def norm(n):
    n=unicodedata.normalize('NFKD',html.unescape(n)).encode('ascii','ignore').decode().lower()
    n=re.sub(r'\b(dr|prof|professor|mr|ms|mrs|shri|smt|sir|col|maj|gen|retd|hon ble|justice)\b','',n); return re.sub(r'\s+',' ',re.sub(r'[^a-z ]',' ',n)).strip()
def get(u,b=False):
    for _ in range(3):
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40).read(); return r if b else r.decode('utf8','ignore')
        except Exception: time.sleep(2)
def clean(x): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',x or '').replace('\xa0',' '))).strip()
t=open(f'{RAW}/team.html',encoding='utf8',errors='ignore').read(); cur=[]; seen=set()
for it in t.split('role="listitem"')[1:]:
    h=re.search(r'<h2[^>]*>(.*?)</h2>',it,re.S); img=re.search(r'(https://static\.wixstatic\.com/media/[^/"\' ]+~mv2\.[a-z]+)',it)
    if not h: continue
    n=clean(h.group(1))
    if n and norm(n) not in seen: seen.add(norm(n)); cur.append({'name':n,'img':img.group(1) if img else ''})
a=open(f'{RAW}/archives.html',encoding='utf8',errors='ignore').read(); k=a.find('>2017<'); old=[]
for m in re.finditer(r'<h2[^>]*>(.*?)</h2>',a[k:],re.S):
    n=clean(m.group(1))
    if n and n not in old and len(n)<60: old.append(n)
by={2025:{norm(n):n for n in old if norm(n)},NOW:{norm(c['name']):c['name'] for c in cur}}
S=[]
for c in cur:
    k=norm(c['name']); sl=re.sub(r'[^a-z0-9]+','-',c['name'].lower()).strip('-'); fn=f'{OUT}/ph/{sl}.jpg'; ok=os.path.exists(fn)
    if not ok and c['img']:
        try:
            im=Image.open(io.BytesIO(get(c['img'],True))).convert('RGB'); w,h=im.size
            if w>373: im=im.resize((373,round(h*373/w)),Image.LANCZOS)
            im.save(fn,'JPEG',quality=82,optimize=True); ok=True
        except Exception: ok=False
    time.sleep(.15); ys=[y for y in (2025,NOW) if k in by[y]]; past=[y for y in ys if y<NOW]
    S.append({'n':c['name'],'b':'','f':'','y':ys,'pre':[],'first':0 if past else 1,'g':'u','t':'Speakers','p':0,'r':0,'a':'','l':'','s':[],'u':sl,'bk':[],'lg':[],'le':'','role':'Speaker','nonauth':1,'cc':'Unknown','cb':'','dia':0,'city':'','ph':f'ph/{sl}.jpg' if ok else ''})
S.sort(key=lambda o:o['n'].lower()); json.dump(S,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
YEARS=sorted(by); per={}
for y in YEARS:
    ks=set(by[y]); prior=set().union(*[set(by[z]) for z in YEARS if z<y]) if y>YEARS[0] else set()
    per[str(y)]={'total':len(ks),'returning':len(ks&prior),'inNow':len(ks&set(by[NOW]))}
yrs={}
for y,m in by.items():
    for kk in m: yrs.setdefault(kk,[]).append(y)
nm={kk:v for y in YEARS for kk,v in by[y].items()}; lead=sorted(yrs.items(),key=lambda kv:(-len(kv[1]),kv[0]))[:25]
json.dump({'per':per,'lead':[{'n':nm[kk],'y':v,'in26':NOW in v} for kk,v in lead],'hist':dict(Counter(str(sum(1 for y in yrs[norm(o['n'])] if y<NOW)) for o in S))},open(OUT+'/stats.json','w'))
json.dump({str(y):sorted(by[y].values()) for y in YEARS},open(OUT+'/history.json','w',encoding='utf8'),ensure_ascii=False)
print(len(S),'speakers 2026;',len(old),'in 2025;',sum(o['first'] for o in S),'first-timers;',sum(1 for o in S if o['ph']),'photos')
