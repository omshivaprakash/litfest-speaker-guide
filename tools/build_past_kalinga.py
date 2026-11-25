"""Build festivals/klf2/past.json: Kalinga Literary Festival speakers of 2021-2024 who are not in the 2026 list (profile pages: bio, photo) from kalingaliteraryfestival.com/klf-speakers/.
Usage: python3 tools/build_past_kalinga.py"""
import json,os,re,sys,concurrent.futures as cf
sys.path.insert(0,os.path.dirname(__file__))
from pastlib import *
CAT={'klf-speakers-2025':2026,'klf-speakers-2024':2024,'klf-speakers-2022':2022,'klf-speakers-2021':2021}
P=Past('klf2'); s=get('https://kalingaliteraryfestival.com/klf-speakers/') or ''; people={}
for it in re.split(r'(?=<div class="team-container)',s)[1:]:
    cl=re.search(r'class="([^"]*dt_team[^"]*)"',it)
    if not cl: continue
    cats=[CAT[k] for k in re.findall(r'dt_team_category-([a-z0-9-]+)',cl.group(1)) if k in CAT]
    m=re.search(r'team-author-name"><a href=" ?https://kalingaliteraryfestival\.com/speakers/([a-z0-9-]+)/ ?">(.*?)</a>',it,re.S)
    if not m or not cats: continue
    img=re.search(r'data-src="([^"]+)"',it); n=clean(m.group(2)); k=norm(n)
    if k in P.cur: continue
    p=people.setdefault(k,{'slug':m.group(1),'name':n,'img':img.group(1) if img else '','years':set()}); p['years'].update(cats)
print(len(people),flush=True)
def one(p):
    h=get(f"https://kalingaliteraryfestival.com/speakers/{p['slug']}/") or ''; body=''
    for blk in re.findall(r'<div class="wpb_text_column[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>',h,re.S):
        if len(clean(blk))>len(clean(body)): body=blk
    return clean(body),(get(p['img'],True,30) if p['img'] else None)
items=list(people.values())
with cf.ThreadPoolExecutor(6) as ex: res=list(ex.map(one,items))
for p,(bio,raw) in zip(items,res):
    P.add(p['name'],sorted(p['years']),bio[:1800],raw,'Past speakers'); P.rows[norm(p['name'])]['url']=f"https://kalingaliteraryfestival.com/speakers/{p['slug']}/"
P.save()
