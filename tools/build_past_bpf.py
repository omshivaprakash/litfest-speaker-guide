"""Build festivals/bpf/past.json: Bengaluru Poetry Festival poets of 2016-2025 who are not in the 2026 list (name + photo from the archive pages; the archive
pages carry no bios). Usage: python3 tools/build_past_bpf.py"""
import json,os,re,sys,concurrent.futures as cf
sys.path.insert(0,os.path.dirname(__file__))
from pastlib import *
P=Past('bpf'); recs={}
for y in (2016,2017,2018,2019,2020,2022,2023,2024,2025):
    h=get(f'https://www.bengalurupoetryfestival.org/archive/{y}.php') or ''
    for src,alt in re.findall(r'<img[^>]+src="([^"]+)"[^>]*alt="([^"]{3,60})"',h)+[(b,a) for a,b in re.findall(r'<img[^>]+alt="([^"]{3,60})"[^>]*src="([^"]+)"',h)]:
        n=clean(alt)
        if n.upper()=='BPF' or not norm(n) or norm(n) in P.cur: continue
        r=recs.setdefault(norm(n),{'n':n,'y':set(),'img':None}); r['y'].add(y)
        if not r['img'] and 'assets/images' in src: r['img']=src if src.startswith('http') else 'https://bengalurupoetryfestival.org/'+src.lstrip('./')
    print(y,len(recs),flush=True)
def one(r): return get(r['img'].replace(' ','%20'),True,30) if r['img'] else None
items=list(recs.values())
with cf.ThreadPoolExecutor(6) as ex: raws=list(ex.map(one,items))
for r,raw in zip(items,raws): P.add(r['n'],sorted(r['y']),'',raw,'Past poets')
P.save()
