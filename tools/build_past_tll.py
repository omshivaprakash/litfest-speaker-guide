"""Build festivals/tll/past.json: Tata Literature Live speakers of 2024-2025 who are not in the 2026 list (name, short description, photo) from litlive.in.
Usage: python3 tools/build_past_tll.py"""
import json,os,re,sys,concurrent.futures as cf
sys.path.insert(0,os.path.dirname(__file__))
from pastlib import *
P=Past('tll'); recs={}
for y,fest in ((2024,'fest24'),(2025,'fest25')):
    h=get(f'https://www.litlive.in/{fest}/speakers') or ''
    for it in h.split('role="listitem"')[1:]:
        m=re.search(r'href="https://www\.litlive\.in/'+fest+r'/speakers/([^"]+)"',it)
        h2=re.search(r'<h2[^>]*>(.*?)</h2>',it,re.S)
        if not m or not h2: continue
        n=clean(h2.group(1)); k=norm(n)
        if not k or k in P.cur: continue
        p=re.findall(r'wixui-rich-text__text[^>]*>(.*?)</p>',it,re.S); img=re.search(r'(https://static\.wixstatic\.com/media/[^/"\' ]+~mv2\.[a-z]+)',it)
        r=recs.setdefault(k,{'n':n,'y':set(),'img':None,'bio':'','url':None}); r['y'].add(y)
        d=clean(p[0]) if p else ''
        if len(d)>len(r['bio']): r['bio']=d
        if img and not r['img']: r['img']=img.group(1)
        r['url']=f'https://www.litlive.in/{fest}/speakers/{m.group(1)}'
    print(y,len(recs),flush=True)
def one(r): return get(r['img'],True,30) if r['img'] else None
items=list(recs.values())
with cf.ThreadPoolExecutor(6) as ex: raws=list(ex.map(one,items))
for r,raw in zip(items,raws):
    P.add(r['n'],sorted(r['y']),r['bio'][:1500],raw,'Past speakers'); P.rows[norm(r['n'])]['url']=r['url']
P.save()
