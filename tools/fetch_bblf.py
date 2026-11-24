"""Fetch Book Brahma Literature Festival speaker bios and photos from the festival site (public pages).
Writes RAW/speakers.json = [{id,slug,name,bio,ph}] and photos to festivals/bbl/ph/.
Usage: python3 tools/fetch_bblf.py RAWDIR   (RAWDIR must contain speakers.html saved from /speakers/)
Uses 3 workers with short pauses to stay polite."""
import re,sys,json,os,html,time,io,urllib.request,threading
import concurrent.futures as cf
RAW=sys.argv[1]; OUT=os.path.join(os.path.dirname(__file__),'..','festivals','bbl')
from PIL import Image
UA={'User-Agent':'Mozilla/5.0'}
def get(u,b=False):
    for _ in range(3):
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40).read()
            return r if b else r.decode('utf8','ignore')
        except Exception: time.sleep(2)
    return None
idx=open(RAW+'/speakers.html',encoding='utf8').read(); seen={}
for m in re.finditer(r'<a[^>]+href=["\']https://bookbrahmalitfest.com/speaker/(\d+)-([a-z0-9-]+)["\'][^>]*>(.*?)</a>',idx,re.S):
    i,sl,t=m.groups(); n=html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',t))).strip()
    if i not in seen and n: seen[i]={'id':int(i),'slug':sl,'name':n}
os.makedirs(OUT+'/ph',exist_ok=True); out=[]; lock=threading.Lock()
def work(sp):
    h=get(f"https://bookbrahmalitfest.com/speaker/{sp['id']}-{sp['slug']}")
    if not h: return dict(sp,bio='',ph='',fail=1)
    t=re.sub(r'<script.*?</script>|<style.*?</style>','',h,flags=re.S); t=html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',t)))
    a=t.find('Contact Us',t.find('Hotel Guide')); b=t.find('Book Brahma Foundation Social')
    seg=t[a+10:b].strip() if a>0 and b>a else ''; nm=sp['name']
    if seg.startswith(nm+' '+nm): seg=seg[len(nm)*2+2:].strip()
    elif seg.startswith(nm): seg=seg[len(nm):].strip()
    img=re.findall(r'<img[^>]+src=["\'](https://bookbrahmalitfest.com/guru/uploads/[^"\']+)["\']',h); ph=''
    if img:
        fn=OUT+'/ph/'+sp['slug']+'.jpg'
        if not os.path.exists(fn):
            raw=get(img[0],True)
            try:
                im=Image.open(io.BytesIO(raw)).convert('RGB'); w,hh=im.size
                if w>373: im=im.resize((373,round(hh*373/w)),Image.LANCZOS)
                im.save(fn,'JPEG',quality=82,optimize=True)
            except Exception: fn=None
        if fn: ph='ph/'+sp['slug']+'.jpg'
    time.sleep(.2); return dict(sp,bio=seg,ph=ph)
todo=sorted(seen.values(),key=lambda x:x['id'])
with cf.ThreadPoolExecutor(3) as ex:
    for k,r in enumerate(ex.map(work,todo)):
        out.append(r)
        if k%25==0: print(k,len(todo),flush=True); json.dump(out,open(RAW+'/speakers.json','w'),ensure_ascii=False)
json.dump(out,open(RAW+'/speakers.json','w'),ensure_ascii=False)
print('done',len(out),sum(1 for o in out if o['ph']),sum(1 for o in out if o['bio']),sum(1 for o in out if o.get('fail')))
