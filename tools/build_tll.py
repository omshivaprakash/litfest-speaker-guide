"""Build festivals/tll/{data,stats,history}.json for Literature Live! The Mumbai LitFest (Tata Literature Live).
Reads the speakers index pages (2024-2026), each 2026 speaker page (bio, sessions) and the 'Books at the LitFest' pages
from www.litlive.in. Usage: python3 tools/build_tll.py RAWDIR   (RAWDIR holds fest26_speakers.html, fest25_speakers.html,
fest24_speakers.html, fest26_books.html and fest25_books.html saved from the site)"""
import re,sys,json,os,html,io,time,unicodedata,urllib.request
import concurrent.futures as cf
from collections import Counter
from PIL import Image
RAW=sys.argv[1]; OUT=os.path.join(os.path.dirname(__file__),'..','festivals','tll'); os.makedirs(OUT+'/ph',exist_ok=True); os.makedirs(OUT+'/bk',exist_ok=True)
UA={'User-Agent':'Mozilla/5.0'}; NOW=2026
def norm(n):
    n=unicodedata.normalize('NFKD',html.unescape(n)).encode('ascii','ignore').decode().lower()
    n=re.sub(r'\b(dr|prof|professor|mr|ms|mrs|shri|smt|sir|justice|lord|dame)\b','',n)
    return re.sub(r'\s+',' ',re.sub(r'[^a-z ]',' ',n)).strip()
def get(u,b=False):
    for _ in range(3):
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40).read(); return r if b else r.decode('utf8','ignore')
        except Exception: time.sleep(2)
def clean(x): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',x or '').replace('\xa0',' '))).strip()
def short(t,n=220): return t if len(t)<=n else t[:n].rsplit(' ',1)[0]+'…'
def gender(b):
    f=len(re.findall(r"\b(she|her|hers|herself)\b",b,re.I)); m=len(re.findall(r"\b(he|his|him|himself)\b",b,re.I))
    if f>=1 and f>=2*m: return 'f'
    if m>=1 and m>=2*f: return 'm'
    return 'u'
def cards(fn,fest):
    s=open(f'{RAW}/{fn}',encoding='utf8',errors='ignore').read(); out={}
    for it in s.split('role="listitem"')[1:]:
        m=re.search(r'href="https://www\.litlive\.in/'+fest+r'/speakers/([^"]+)"',it)
        if not m: continue
        h2=re.search(r'<h2[^>]*>(.*?)</h2>',it,re.S); p=re.findall(r'wixui-rich-text__text[^>]*>(.*?)</p>',it,re.S)
        img=re.search(r'(https://static\.wixstatic\.com/media/[^/"\' ]+~mv2\.[a-z]+)',it)
        if not h2: continue
        n=clean(h2.group(1)); d=clean(p[0]) if p else ''
        out[m.group(1)]={'slug':m.group(1),'name':n,'desc':d,'img':img.group(1) if img else ''}
    return out
C={2026:cards('fest26_speakers.html','fest26'),2025:cards('fest25_speakers.html','fest25'),2024:cards('fest24_speakers.html','fest24')}
byyear={y:{norm(c['name']):c['name'] for c in v.values() if norm(c['name'])} for y,v in C.items()}
def photo(url,fn):
    if not url or os.path.exists(fn): return os.path.exists(fn)
    raw=get(url,True)
    try:
        im=Image.open(io.BytesIO(raw)).convert('RGB'); w,h=im.size
        if w>373: im=im.resize((373,round(h*373/w)),Image.LANCZOS)
        im.save(fn,'JPEG',quality=82,optimize=True); return True
    except Exception: return False
def work(c):
    h=get('https://www.litlive.in/fest26/speakers/'+c['slug']) or ''
    t=clean(re.sub(r'<script.*?</script>|<style.*?</style>','',h,flags=re.S)); a=t.find('PRESENTED BY: Speakers'); bio=''
    if a>=0:
        seg=t[a+len('PRESENTED BY: Speakers'):]; k=seg.find(c['name']+' '+c['desc'][:12]) if c['desc'] else -1
        bio=(seg[:k] if k>0 else seg[:900]).strip()
    sess=[clean(x) for x in re.findall(r'mlf-speaker-session-title"[^>]*>(.*?)</div>',h,re.S) if clean(x)]
    ok=photo(c['img'],f"{OUT}/ph/{c['slug']}.jpg"); time.sleep(.2)
    return dict(c,bio=bio,sess=sess,ph=f"ph/{c['slug']}.jpg" if ok else '')
with cf.ThreadPoolExecutor(3) as ex: cur=list(ex.map(work,C[NOW].values()))
# books pages: item = cover image, title (p), author (h2)
def books(fn):
    s=open(f'{RAW}/{fn}',encoding='utf8',errors='ignore').read(); out=[]
    for it in s.split('role="listitem"')[1:]:
        h2=re.search(r'<h2[^>]*>(.*?)</h2>',it,re.S); p=re.findall(r'wixui-rich-text__text[^>]*>(.*?)</p>',it,re.S); img=re.search(r'(https://static\.wixstatic\.com/media/[^/"\' ]+~mv2\.[a-z]+)',it)
        if h2 and p: out.append({'t':clean(p[0]),'a':clean(h2.group(1)),'img':img.group(1) if img else ''})
    return out
bk={}
for fn in ('fest26_books.html','fest25_books.html'):
    if os.path.exists(f'{RAW}/{fn}'):
        for b in books(fn):
            for a in re.split(r'\s*(?:,| and | & )\s*',b['a']): bk.setdefault(norm(a),{}).setdefault(b['t'],b['img'])
yrs={}
for y,m in byyear.items():
    for k in m: yrs.setdefault(k,[]).append(y)
S=[];nb=0
for c in cur:
    n=c['name']; k=norm(n); ys=sorted(yrs[k]); past=[y for y in ys if y<NOW]; full=c['bio']
    role,_,country=c['desc'].rpartition(',') if ',' in c['desc'] else (c['desc'],'','')
    country={'USA':'United States','UK':'United Kingdom','Scotland':'United Kingdom','England':'United Kingdom','Wales':'United Kingdom'}.get(country.strip(),country.strip()) or 'Unknown'; role=role.strip() or 'Speaker'
    bl=[]
    for t,img in bk.get(k,{}).items():
        fn=f"{OUT}/bk/{re.sub(r'[^a-z0-9]+','-',t.lower())[:40]}.jpg"
        cv=f"bk/{os.path.basename(fn)}" if photo(img,fn) else ''
        if cv:
            try:
                im=Image.open(fn); im.thumbnail((200,300)); im.save(fn,'JPEG',quality=80)
            except Exception: pass
        bl.append({'t':t,'c':cv,'b':1}); nb+=1
    S.append({'n':n,'b':short(full),'f':full,'y':ys,'pre':[],'first':0 if past else 1,'g':gender(full) if full else 'u','t':role,'p':0,'r':0,'a':'','l':'',
      's':[[NOW,x.title() if x.isupper() else x] for x in c['sess']],'u':c['slug'],'bk':bl,'lg':[],'le':'','role':role,'nonauth':0 if re.search(r'author|writer|poet|novelist',role,re.I) else 1,
      'cc':country,'cb':'stated by the festival','dia':0,'city':'Mumbai' if country=='India' and re.search(r'mumbai',full,re.I) else '','ph':c['ph']})
fr=sorted([o for o in S if sum(1 for y in o['y'] if y<NOW)>=2],key=lambda o:(-len(o['y']),o['n']))
for i,o in enumerate(fr,1): o['p']=1;o['r']=i
S.sort(key=lambda o:o['n'].lower()); json.dump(S,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
YEARS=sorted(byyear); per={}
for y in YEARS:
    ks=set(byyear[y]); prior=set().union(*[set(byyear[z]) for z in YEARS if z<y]) if y>YEARS[0] else set()
    per[str(y)]={'total':len(ks),'returning':len(ks&prior),'inNow':len(ks&set(byyear[NOW]))}
nm={k:v for y in YEARS for k,v in byyear[y].items()}; lead=sorted(yrs.items(),key=lambda kv:(-len(kv[1]),kv[0]))[:25]
json.dump({'per':per,'lead':[{'n':nm[k],'y':v,'in26':NOW in v} for k,v in lead],'hist':dict(Counter(str(sum(1 for y in yrs[norm(o['n'])] if y<NOW)) for o in S))},open(OUT+'/stats.json','w'))
json.dump({str(y):sorted(byyear[y].values()) for y in YEARS},open(OUT+'/history.json','w',encoding='utf8'),ensure_ascii=False)
print(len(S),'speakers;',sum(o['first'] for o in S),'first-timers;',{y:per[str(y)]['total'] for y in YEARS},sum(1 for o in S if o['s']),'with sessions',sum(1 for o in S if o['f']),'bios',sum(1 for o in S if o['ph']),'photos',nb,'books',Counter(o['cc'] for o in S).most_common(8))
