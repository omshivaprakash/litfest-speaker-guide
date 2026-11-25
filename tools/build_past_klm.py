"""Build festivals/klm/past.json: Kolkata Literary Meet speakers of 2023-2025 who are not in the 2026 list (name, bio, photo) from the yearly pages.
Usage: python3 tools/build_past_klm.py"""
import json,os,re,sys,concurrent.futures as cf
sys.path.insert(0,os.path.dirname(__file__))
from pastlib import *
P=Past('klm'); recs={}
for y in (2020,2021,2022,2023,2024,2025):
    h=get(f'https://kolkatalitmeet.in/{y}/') or ''
    for blk in re.split(r'(?=<div class="container m-2 mx-auto" id="speaker_content_)',h)[1:]:
        nm=re.search(r'<h2 class="title t_u">(.*?)</h2>',blk,re.S)
        if not nm: continue
        n=clean(nm.group(1)); k=norm(n)
        if not k or k in P.cur: continue
        img=re.search(r'<img src="([^"]+)"',blk); body=blk.split('<h2 class="title t_u">',2); bio=clean(body[1].split('</h2>',1)[1]) if len(body)>1 else ''
        r=recs.setdefault(k,{'n':n,'y':set(),'img':None,'bio':''}); r['y'].add(y)
        if img and not r['img']: r['img']=img.group(1)
        if len(bio)>len(r['bio']): r['bio']=bio
    print(y,len(recs),flush=True)
def one(r): return get(r['img'],True,30) if r['img'] else None
items=list(recs.values())
with cf.ThreadPoolExecutor(6) as ex: raws=list(ex.map(one,items))
for r,raw in zip(items,raws): P.add(r['n'],sorted(r['y']),r['bio'][:1800],raw,'Past speakers')
P.save()
