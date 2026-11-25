"""Build festivals/shillong for the Shillong Literary Festival (Edition VI, 12-14 Nov 2026, Ward's Lake) from shillonglitfest.com/speakers
(speaker cards with bio on the flip side; the site shows earlier editions only as photo pages we cannot read). Usage: python3 tools/build_shillong.py"""
import re,json,os,sys,io
sys.path.insert(0,os.path.dirname(__file__))
from pastlib import *
from PIL import Image
OUT=R+'/shillong'; os.makedirs(OUT+'/ph',exist_ok=True); NOW=2026; B='https://shillonglitfest.com'
h=get(B+'/speakers') or ''; S=[]
for blk in h.split('<li class="group')[1:]:
    nm=re.search(r'aria-label="Read the bio of ([^"]+)"',blk); img=re.search(r'<img alt="[^"]*"[^>]*src="([^"]+)"',blk); bio=re.search(r'<p class="font-sans text-left[^>]*>(.*?)</p>',blk,re.S)
    if not nm: continue
    n=clean(nm.group(1)); b=clean(bio.group(1)) if bio else ''; sl=slug(n); ph=''
    if img:
        raw=get(B+img.group(1),True,30)
        try:
            im=Image.open(io.BytesIO(raw)).convert('RGB'); w,hh=im.size
            if w>373: im=im.resize((373,round(hh*373/w)),Image.LANCZOS)
            im.save(f'{OUT}/ph/{sl}.webp','WEBP',quality=78,method=6); ph=f'ph/{sl}.webp'
        except Exception: pass
    cc,cb=country(b) if b else ('Unknown',''); ro=role(b) if b else 'Speaker'
    S.append({'n':n,'b':short(b),'f':b,'y':[NOW],'pre':[],'first':1,'g':gender(b) if b else 'u','t':'Speakers','p':0,'r':0,'a':'','l':'','s':[],'u':sl,'bk':[],'lg':[],'le':'','role':ro,'nonauth':0 if ro in('Author','Poet') else 1,'cc':cc,'cb':cb,'dia':0,'city':'Shillong','ph':ph})
S.sort(key=lambda o:o['n'].lower()); json.dump(S,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
json.dump({'per':{'2026':{'total':len(S),'returning':0,'inNow':len(S)}},'lead':[],'hist':{'0':len(S)}},open(OUT+'/stats.json','w'))
json.dump({'2026':sorted(o['n'] for o in S)},open(OUT+'/history.json','w',encoding='utf8'),ensure_ascii=False)
print(len(S),'speakers;',sum(1 for o in S if o['ph']),'photos;',sum(1 for o in S if o['f']),'bios')
