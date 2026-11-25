"""Build festivals/galf/past.json: Goa Arts and Literary Festival speakers of 2023-2025 who are not in the 2026 list (name, photo, short bio where given) from goaartlitfest.com.
Usage: python3 tools/build_past_galf.py"""
import json,os,re,sys,time,concurrent.futures as cf
sys.path.insert(0,os.path.dirname(__file__))
from pastlib import *
P=Past('galf'); recs={}
for y in (2023,2024,2025):
    p=1
    while p<15:
        h=get(f'https://goaartlitfest.com/speaker-{y}/'+(f'page/{p}/' if p>1 else '')) or ''; new=0
        for it in re.split(r'(?=<article class="wpr-grid-item)',h)[1:]:
            m=re.search(r'wpr-grid-item-title.*?<a\s+href="https://goaartlitfest\.com/([a-z0-9-]+)/">(.*?)</a>',it,re.S); alt=re.search(r'<img[^>]*alt="([^"]*)"',it); img=re.search(r'data-src="([^"]+)"',it)
            if m: n=clean(m.group(2))
            elif alt and len(alt.group(1))<60 and img: n=clean(alt.group(1))
            else: continue
            k=norm(n)
            if not k or k in P.cur: continue
            r=recs.setdefault(k,{'n':n,'y':set(),'img':None,'bio':''}); 
            if y not in r['y']: new+=1
            r['y'].add(y); b=clean(alt.group(1)) if alt else ''
            if b and b.lower()!=n.lower() and len(b)>len(r['bio']): r['bio']=b
            if img and not r['img']: r['img']=img.group(1)
        for n in re.findall(r'<h2 class="profile-title">.*?<a[^>]*>(.*?)</a>',h,re.S):
            n=clean(n); k=norm(n)
            if k and k not in P.cur:
                r=recs.setdefault(k,{'n':n,'y':set(),'img':None,'bio':''})
                if y not in r['y']: new+=1
                r['y'].add(y)
        if not new: break
        p+=1; time.sleep(.5)
    print(y,len(recs),flush=True)
def one(r): return get(r['img'],True,30) if r['img'] else None
items=list(recs.values())
with cf.ThreadPoolExecutor(6) as ex: raws=list(ex.map(one,items))
for r,raw in zip(items,raws): P.add(r['n'],sorted(r['y']),r['bio'][:1500],raw,'Past speakers')
P.save()
