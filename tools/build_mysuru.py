"""Build festivals/mlf for the Mysuru Literature Festival from mysuruliteraturefestival.com.
 - 2026 (10th edition, 4-5 Jul 2026): every speaker with bio and photo, from the site's WordPress API (the 11th edition is 3-4 Jul 2027; speakers not announced yet).
 - 2017 to 2022: name lists from each edition's page (2020 and 2021 were online editions). 2023 to 2025 pages show pictures only, so those years are not captured.
Usage: python3 tools/build_mysuru.py"""
import re,json,os,sys,io,html,concurrent.futures as cf
sys.path.insert(0,os.path.dirname(__file__))
from pastlib import *
from PIL import Image
B='https://www.mysuruliteraturefestival.com/'; OUT=R+'/mlf'; os.makedirs(OUT+'/ph',exist_ok=True); NOW=2026
def api(p):
    return json.loads(get(B+f'wp-json/wp/v2/speakers?per_page=100&page={p}&_embed=wp:featuredmedia&_fields=id,slug,title,content,link,date,_embedded,_links') or '[]')
A=[]
for p in (1,2,3):
    try: d=api(p)
    except Exception: break
    if not d: break
    A+=d
print(len(A),'speakers from the API',flush=True)
PAGES={2017:'lit-fest-2017/',2018:'lit-fest-2018/',2019:'lit-fest-2019/',2020:'lit-fest-2020/',2021:'lit-fest-2021/',2022:'lit-fest-2022/'}
def lines(h):
    t=re.sub(r'<script.*?</script>|<style.*?</style>',' ',h,flags=re.S); L=[clean(x) for x in re.split(r'<[^>]+>',t)]; return [x for x in L if x]
def names_for(y):
    raw=get(B+PAGES[y]) or ''; L=lines(raw); out=[]
    def ok(n): return 2<len(n)<=45 and not n.startswith('[') and ' - ' not in n and not re.match(r'^(Speakers|Panels|About Us|Schedule|Gallery|Contact|Facebook|Instagram|Twitter|Youtube|Home|\+)$',n)
    if y in(2019,2020):
        i=[k for k,x in enumerate(L) if x==f'Lit Fest {y} Speakers'][0]
        out=[L[k] for k in range(i+1,len(L)-1) if L[k+1]=='+' and ok(L[k])]
    elif y in(2021,2022):
        i=[k for k,x in enumerate(L) if x==f'Lit Fest {y} Speakers'][0]
        out=[L[k-1] for k in range(i+2,len(L)) if re.match(r'^\d{1,2} [A-Za-z]{3,9} 20\d\d$',L[k]) and ok(L[k-1])]
    elif y==2018:      # the page keeps its speaker tab as shortcodes: tt_Content_team title="Name"
        out=[clean(x) for x in re.findall(r'tt_Content_team title=["\u201d\u201c]([^"\u201d\u201c]+)["\u201d\u201c]',html.unescape(raw))]
    else:
        i=[k for k,x in enumerate(L) if x=='Speakers'][0]; j=next((k for k in range(i+1,len(L)) if L[k] in('Panels','About Us')),len(L))
        out=[x for x in L[i+1:j] if ok(x) and len(x)<=40]
    out=[re.sub(r'\s*\([^)]*\)\s*$','',n).strip() for n in out]
    seen=set(); res=[]
    for n in out:
        k=norm(n)
        if k and k not in seen: seen.add(k); res.append(n)
    return res
H={y:names_for(y) for y in PAGES}
for y,v in H.items(): print(y,len(v),v[:4])
def photo(a):
    try:
        m=a['_embedded']['wp:featuredmedia'][0]; u=m['source_url']; return get(u,True,40)
    except Exception: return None
with cf.ThreadPoolExecutor(8) as ex: raws=list(ex.map(photo,A))
HY={y:{norm(n) for n in v} for y,v in H.items()}; S=[]
_best={}
for a,raw in zip(A,raws):      # the site lists a few people twice; keep the longer bio
    k=norm(clean(a['title']['rendered']).replace('\u2060',''))
    if k not in _best or len(a['content']['rendered'])>len(_best[k][0]['content']['rendered']): _best[k]=(a,raw)
A=[v[0] for v in _best.values()]; raws=[v[1] for v in _best.values()]
for a,raw in zip(A,raws):
    n=clean(a['title']['rendered']).replace('⁠','').strip(); c=a['content']['rendered']
    m=re.search(r'>\s*Bio\s*<',c); b=clean(c[m.end()-1:]) if m else clean(c)
    b=re.sub(r'^Bio\s*','',b); sl=slug(n)+('-'+str(a['id']) if False else ''); ph=''
    if raw:
        try:
            im=Image.open(io.BytesIO(raw)).convert('RGB'); w,hh=im.size
            if w>373: im=im.resize((373,round(hh*373/w)),Image.LANCZOS)
            im.save(f'{OUT}/ph/{sl}.webp','WEBP',quality=78,method=6); ph=f'ph/{sl}.webp'
        except Exception: pass
    ys=sorted([y for y in HY if norm(n) in HY[y]]+[NOW]); cc,cb=country(b) if b else ('Unknown','')
    ro=role(b) if b else 'Speaker'
    S.append({'n':n,'b':short(b),'f':b,'y':ys,'pre':[],'first':1 if len(ys)==1 else 0,'g':gender(b) if b else 'u','t':'Speakers','p':0,'r':0,'a':'','l':'','s':[],'u':a['slug'],'bk':[],'lg':[],'le':'','role':ro,'nonauth':0 if ro in('Author','Poet') else 1,'cc':cc,'cb':cb,'dia':0,'city':'','ph':ph})
S.sort(key=lambda o:o['n'].lower()); json.dump(S,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
hist={str(y):sorted(v,key=str.lower) for y,v in H.items() if v}; hist[str(NOW)]=sorted((o['n'] for o in S),key=str.lower)
json.dump(hist,open(OUT+'/history.json','w',encoding='utf8'),ensure_ascii=False)
per={}
cur={norm(o['n']) for o in S}
for y,v in sorted(hist.items()):
    ks={norm(n) for n in v}; per[y]={'total':len(v),'returning':len([1 for o in S if str(NOW)!=y and norm(o['n']) in ks and False]),'inNow':len(ks&cur)}
for y in per:
    ks={norm(n) for n in hist[y]}; earlier={norm(n) for yy,v in hist.items() if yy<y for n in v}; per[y]['returning']=len(ks&earlier)
lead=sorted([{'n':o['n'],'y':o['y'],'in26':True} for o in S if len(o['y'])>1],key=lambda x:-len(x['y']))[:12]
json.dump({'per':per,'lead':lead,'hist':{str(k):sum(1 for o in S if len(o['y'])==k) for k in sorted({len(o['y']) for o in S})}},open(OUT+'/stats.json','w'))
print(len(S),'speakers;',sum(1 for o in S if o['ph']),'photos;',sum(1 for o in S if o['f']),'bios;',sum(1 for o in S if len(o['y'])>1),'also in earlier editions')
