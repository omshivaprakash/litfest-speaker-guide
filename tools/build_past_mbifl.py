"""Build festivals/mbifl/past.json: MBIFL speakers of earlier editions who are not in the 2027 list, where the festival sites still give a profile:
2026 (bio + photo from assets.mbifl.com) and 2024 (photo from the archived 2024 site; no bios there). Other years stay name-only in history.json.
Usage: python3 tools/build_past_mbifl.py"""
import json,os,re,sys,concurrent.futures as cf
sys.path.insert(0,os.path.dirname(__file__))
from pastlib import *
B='https://www.mbifl.com/'; P=Past('mbifl'); H=json.load(open(P.dir+'/history.json',encoding='utf8')); recs={}
def years(n): return sorted(int(y) for y,l in H.items() if norm(n) in {norm(x) for x in l})
def tc(n): n=clean(n); return n.title() if n.isupper() else n
# 2026
s=get(B+'2026/speakers.html') or ''
for m in re.finditer(r'data-speaker-id="([^"]+)" data-speaker-name="[^"]*">.*?src="([^"]+)"[^>]*alt="([^"]*)"',s,re.S):
    n=tc(m.group(3)); k=norm(n)
    if k and k not in P.cur: recs[k]={'n':n,'id':m.group(1),'img':m.group(2),'bio':'','y':set(years(n))|{2026}}
print('2026',len(recs),flush=True)
# 2024
for t in ('regional','national','international'):
    s=get(f'{B}2024/speakers/{t}/{t}.json') or ''
    try: items=json.loads(s.strip().lstrip('﻿'))['_news']
    except Exception: items=[]
    for x in items:
        n=tc(x['_title']); k=norm(n)
        if not k or k in P.cur: continue
        nid=x['news_id'].replace('.','_'); r=recs.setdefault(k,{'n':n,'id':None,'img':None,'bio':'','y':set(years(n))})
        r['y'].add(2024)
        if not r['img']: r['img']=f'{B}2024/speakers/{t}/images/{nid}.jpeg'
print('with 2024',len(recs),flush=True)
def one(r):
    bio=''
    if r['id']:
        try: bio=clean(json.loads(get(f"https://assets.mbifl.com/json/2026/speakers/{r['id']}.json"))[0].get('enTxt',''))
        except Exception: pass
    return bio,(get(r['img'],True,30) if r['img'] else None)
items=list(recs.values())
with cf.ThreadPoolExecutor(8) as ex: res=list(ex.map(one,items))
for r,(bio,raw) in zip(items,res): P.add(r['n'],sorted(r['y']),bio[:1800],raw,'Past speakers')
P.save()
