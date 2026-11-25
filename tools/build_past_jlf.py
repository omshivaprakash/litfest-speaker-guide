"""Build festivals/jlf/past.json: Jaipur speakers of 2018-2026 who are not in the 2027 list, from the festival's public speakers API
(bio, cover photo, years). Usage: python3 tools/build_past_jlf.py"""
import json,os,sys,re,concurrent.futures as cf
sys.path.insert(0,os.path.dirname(__file__))
from pastlib import *
API='https://api.jaipurliteraturefestival.org'
P=Past('jlf'); recs={}
for y in range(2018,2027):
    d=json.loads(get(f'{API}/api/authorsPage?lang=en&limit=1000&year={y}&skip=0&search=') or '{}')
    L=d.get('authors',[])
    print(y,len(L),flush=True)
    for a in L:
        a['name']=re.sub(r'\s+',' ',(a['first_name']+' '+(a.get('last_name') or '')).strip()).title() if (a['first_name']+(a.get('last_name') or '')).isupper() else re.sub(r'\s+',' ',(a['first_name']+' '+(a.get('last_name') or '')).strip())
        k=norm(a['name'])
        if not k or k in P.cur: continue
        r=recs.setdefault(k,{'n':a['name'],'y':set(),'bio':'','img':None})
        r['y'].add(y); full=clean(a.get('details')) or clean(a.get('bio'))
        if len(full)>len(r['bio']): r['bio']=full
        if a.get('cover_image') and not r['img']: r['img']=a['cover_image']
def photo(r):
    if not r['img']: return None
    return get(API+r['img'],True,30)
items=list(recs.values())
with cf.ThreadPoolExecutor(8) as ex: raws=list(ex.map(photo,items))
for r,raw in zip(items,raws): P.add(r['n'],sorted(r['y']),r['bio'][:1800],raw,'Past speakers')
P.save()
