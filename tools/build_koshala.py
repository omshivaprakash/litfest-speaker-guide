"""Build festivals/koshala (speaker-type) for the Koshala Literature Festival, Lucknow, from koshalaliteraturefestival.com/speakers
(year tabs 2022-2026, each speaker with a detail page: role, bio, photo). 2026 = current edition; earlier years become history.json + past.json.
Usage: python3 tools/build_koshala.py"""
import re,json,os,sys,concurrent.futures as cf
sys.path.insert(0,os.path.dirname(__file__))
from pastlib import *
from PIL import Image
OUT=R+'/koshala'; os.makedirs(OUT+'/ph',exist_ok=True); NOW=2026; BASE='https://koshalaliteraturefestival.com/'
h=get(BASE+'speakers'); panes=re.split(r'<div class="tab-pane',h)[1:]
YEAR={'nav-1':2022,'nav-2':2023,'nav-3':2024,'nav-4':2025,'nav-5':2026}; by={}; recs={}
for p in panes:
    m=re.match(r'[^>]*?id="(nav-\d)"',p,re.S)
    if not m or m.group(1) not in YEAR: continue
    y=YEAR[m.group(1)]; by[y]={}
    for href,img,name,pos in re.findall(r'href="https://koshalaliteraturefestival.com/speakerdetails/(\d+)">.*?<img src="([^"]+)"\s+alt="([^"]*)".*?<h4 class="td-team-2-position">(.*?)</h4>',p,re.S):
        n=clean(name); k=norm(n)
        if not k: continue
        by[y][k]=n; r=recs.setdefault(k,{'n':n,'id':href,'img':img,'pos':clean(pos),'y':set()}); r['y'].add(y)
        if y>=max(r['y']): r['id'],r['img'],r['pos']=href,img,clean(pos) or r['pos']
print({y:len(v) for y,v in by.items()},flush=True)
def one(r):
    d=get(f"{BASE}speakerdetails/{r['id']}") or ''; t=clean(re.sub(r'<script.*?</script>|<style.*?</style>','',d,flags=re.S)); i=t.find(r['n'])
    seg=t[i+len(r['n']):] if i>=0 else ''
    if r['pos'] and seg.startswith(' '+r['pos']): seg=seg[len(r['pos'])+1:]
    for stop in ('Related','Share','Our Partners','Subscribe','Quick Links','Contact','Copyright'):
        j=seg.find(stop)
        if j>200: seg=seg[:j]
    bio=seg.strip(' -|>')
    return (r['pos']+'. '+bio if r['pos'] and not bio.startswith(r['pos']) else bio).strip(),get(r['img'],True,30) if r['img'] else None
items=list(recs.values())
with cf.ThreadPoolExecutor(8) as ex: res=list(ex.map(one,items))
info={norm(r['n']):(bio,raw) for r,(bio,raw) in zip(items,res)}
S=[]
for k,n in by[NOW].items():
    r=recs[k]; bio,raw=info[k]; sl=slug(n)+'-'+r['id']; ph=''
    if raw:
        try:
            im=Image.open(__import__('io').BytesIO(raw)).convert('RGB'); w,hh=im.size
            if w>373: im=im.resize((373,round(hh*373/w)),Image.LANCZOS)
            im.save(f'{OUT}/ph/{sl}.webp','WEBP',quality=78,method=6); ph=f'ph/{sl}.webp'
        except Exception: pass
    ys=sorted(r['y']); cc,cb=country(bio) if bio else ('Unknown',''); ro=role(bio) if bio else 'Speaker'
    S.append({'n':n,'b':short(bio),'f':bio,'y':ys,'pre':[],'first':0 if len(ys)>1 else 1,'g':gender(bio) if bio else 'u','t':'Speakers','p':0,'r':0,'a':'','l':'','s':[],'u':r['id'],'bk':[],'lg':[],'le':'','role':ro,'nonauth':0 if ro in('Author','Poet') else 1,'cc':cc,'cb':cb,'dia':0,'city':'','ph':ph})
S.sort(key=lambda o:o['n'].lower()); json.dump(S,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
YEARS=sorted(by); per={}
for y in YEARS:
    ks=set(by[y]); pr=set().union(*[set(by[z]) for z in YEARS if z<y]) if y>YEARS[0] else set()
    per[str(y)]={'total':len(ks),'returning':len(ks&pr),'inNow':len(ks&set(by[NOW]))}
from collections import Counter
json.dump({'per':per,'lead':[],'hist':dict(Counter(str(len(o['y'])-1) for o in S))},open(OUT+'/stats.json','w'))
json.dump({str(y):sorted(by[y].values()) for y in YEARS},open(OUT+'/history.json','w',encoding='utf8'),ensure_ascii=False)
print(len(S),'current speakers;',sum(o['first'] for o in S),'first-timers;',sum(1 for o in S if o['ph']),'photos;',sum(1 for o in S if o['f']),'bios',flush=True)
P=Past('koshala')
for k,r in recs.items():
    if k in P.cur: continue
    bio,raw=info[k]; P.add(r['n'],sorted(r['y']),bio,raw,'Past speakers'); P.rows[k]['url']=f"{BASE}speakerdetails/{r['id']}"
P.save()
