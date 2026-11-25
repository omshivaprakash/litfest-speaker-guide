"""Build festivals/bplf/past.json: Bhopal speakers of 2019-2026 who are not in the 2027 list. Listing pages give name + photo (+ profile link from 2023);
profile pages give bios. Usage: python3 tools/build_past_bplf.py"""
import json,os,re,sys,concurrent.futures as cf
sys.path.insert(0,os.path.dirname(__file__))
from pastlib import *
B='https://www.bhopalliteraturefestival.com/event/blf-%d/speakers'
P=Past('bplf'); recs={}
for y in range(2019,2027):
    h=get(B%y) or ''
    for blk in h.split('<div class="card">')[1:]:
        nm=re.search(r'<h6 class="card-title">(.*?)</h6>',blk,re.S); img=re.search(r'<img src="([^"]+)"',blk)
        if not nm: continue
        n=clean(nm.group(1)); n=n.title() if n.isupper() else n
        k=norm(n)
        if not k or k in P.cur: continue
        pre=h[:h.find(blk)][-400:]; sl=re.findall(r'/author/([a-z0-9\-]+)"',pre)
        r=recs.setdefault(k,{'n':n,'y':set(),'img':None,'prof':None}); r['y'].add(y)
        if img and not r['img']: r['img']=img.group(1)
        if sl: r['prof']=(y,sl[-1])
    print(y,len(recs),flush=True)
def one(r):
    raw=get(r['img'],True,30) if r['img'] else None; bio=''
    if r['prof']:
        y,sl=r['prof']; h=get(f'https://www.bhopalliteraturefestival.com/event/blf-{y}/author/{sl}') or ''
        t=clean(re.sub(r'<script.*?</script>|<style.*?</style>','',h,flags=re.S)); a=t.find('Introduction'); b=t.find('Other Profiles')
        bio=t[a+12:b].strip() if a>=0 and b>a else ''
    return bio,raw
items=list(recs.values())
with cf.ThreadPoolExecutor(8) as ex: res=list(ex.map(one,items))
for r,(bio,raw) in zip(items,res): P.add(r['n'],sorted(r['y']),bio[:1800],raw,'Past speakers')
P.save()
