"""Build festivals/ailf for the Ahmedabad International Literature Festival (11th edition, 24-25 Oct 2026) from ailf.co.in/speakers
(speaker cards with a pop-up bio). Usage: python3 tools/build_ailf.py"""
import re,json,os,sys,io,html,concurrent.futures as cf
sys.path.insert(0,os.path.dirname(__file__))
from pastlib import *
from PIL import Image
OUT=R+'/ailf'; os.makedirs(OUT+'/ph',exist_ok=True); NOW=2026
h=get('https://ailf.co.in/speakers') or ''; people={}
for blk in re.split(r'<div class="team-item">',h)[1:]:
    nm=re.search(r'<h3 class="team-name"[^>]*>\s*(?:<a[^>]*>)?\s*(.*?)\s*(?:</a>)?\s*</h3>',blk,re.S); 
    if not nm: continue
    n=clean(nm.group(1)); t=re.search(r'class="team-title"[^>]*>(.*?)</span>',blk,re.S); img=re.search(r'<img[^>]+src="([^"]+)"',blk)
    pop=re.search(r'href="#(rs_popupBox_\d+)"',blk)
    k=norm(n)
    if k and k not in people: people[k]={'n':n,'t':clean(t.group(1)) if t else '','img':img.group(1) if img else '','pop':pop.group(1) if pop else ''}
bio={}
for pid,body in re.findall(r'<div id="(rs_popupBox_\d+)"[^>]*>(.*?)(?=<div id="rs_popupBox_|<footer|</section>\s*<section)',h,re.S):
    d=re.search(r'class="team-des"[^>]*>(.*?)</div>',body,re.S); bio[pid]=clean(html.unescape(d.group(1))) if d else clean(body)
print(len(people),'speakers;',len(bio),'bios',flush=True)
def photo(p):
    return get(p['img'],True,30) if p['img'] else None
L=list(people.values())
with cf.ThreadPoolExecutor(8) as ex: raws=list(ex.map(photo,L))
S=[]
for p,raw in zip(L,raws):
    b=bio.get(p['pop'],''); b=(p['t']+'. '+b).strip() if p['t'] and not b.startswith(p['t']) else b; sl=slug(p['n']); ph=''
    if raw:
        try:
            im=Image.open(io.BytesIO(raw)).convert('RGB'); w,hh=im.size
            if w>373: im=im.resize((373,round(hh*373/w)),Image.LANCZOS)
            im.save(f'{OUT}/ph/{sl}.webp','WEBP',quality=78,method=6); ph=f'ph/{sl}.webp'
        except Exception: pass
    cc,cb=country(b) if b else ('Unknown',''); ro=role(b) if b else 'Speaker'
    S.append({'n':p['n'],'b':short(b),'f':b,'y':[NOW],'pre':[],'first':1,'g':gender(b) if b else 'u','t':'Speakers','p':0,'r':0,'a':'','l':'','s':[],'u':sl,'bk':[],'lg':[],'le':'','role':ro,'nonauth':0 if ro in('Author','Poet') else 1,'cc':cc,'cb':cb,'dia':0,'city':'Ahmedabad','ph':ph})
S.sort(key=lambda o:o['n'].lower()); json.dump(S,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
json.dump({'per':{'2026':{'total':len(S),'returning':0,'inNow':len(S)}},'lead':[],'hist':{'0':len(S)}},open(OUT+'/stats.json','w'))
json.dump({'2026':sorted(o['n'] for o in S)},open(OUT+'/history.json','w',encoding='utf8'),ensure_ascii=False)
print(len(S),'speakers;',sum(1 for o in S if o['ph']),'photos;',sum(1 for o in S if o['f']),'bios')
