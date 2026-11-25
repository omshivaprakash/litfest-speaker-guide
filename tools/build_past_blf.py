"""BLF past editions: (1) read the 2012-2017 archive speaker pages and add them to tools/history_src/blf_yrspk.json (url -> name per year, as 2018-2025 already are);
(2) fetch every participant page (bio, photo) for people who are not in the 2026 list and write festivals/blf/past.json.
Then run tools/build_history.py, tools/build_index.py and tools/blf_stats.py (below does stats itself). Usage: python3 tools/build_past_blf.py"""
import json,os,re,sys,concurrent.futures as cf
sys.path.insert(0,os.path.dirname(__file__))
from pastlib import *
SRC=os.path.join(os.path.dirname(__file__),'history_src','blf_yrspk.json'); Y=json.load(open(SRC,encoding='utf8'))
B='https://bangaloreliteraturefestival.org/archives/year-%d/%s/'
PAGES={2012:'authors',2013:'authors',2014:'authors',2015:'participants',2016:'participants',2017:'speakers%e2%80%8b'}
for y,pg in PAGES.items():
    if str(y) in Y and len(Y[str(y)])>20: continue
    h=get(B%(y,pg)) or ''; m={}
    for u,n in re.findall(r'<h3 class="participant-name">\s*<a [^>]*href="(https://bangaloreliteraturefestival.org/participant/[^"]+)"[^>]*>\s*(.*?)\s*</a>',h,re.S):
        n=clean(n)
        if n: m[u]=n
    Y[str(y)]=m; print(y,len(m),flush=True)
json.dump(Y,open(SRC,'w',encoding='utf8'),ensure_ascii=False)
P=Past('blf'); urls={}; yrs={}
for y,m in Y.items():
    for u,n in m.items():
        if norm(n) in P.cur: continue
        urls.setdefault(u,n); yrs.setdefault(u,set()).add(int(y))
print(len(urls),'participant pages to fetch',flush=True)
def one(u):
    h=get(u) or ''
    b=re.search(r'<div class="participant-bio">(.*?)</div>\s*(?:<div|</section|<h)',h,re.S) or re.search(r'class="participant-bio">(.*?)</div>',h,re.S)
    bio=clean(b.group(1)) if b else ''
    og=re.search(r'og:image" content="([^"]+)"',h); raw=get(og.group(1),True,30) if og else None
    return bio,raw
items=list(urls)
with cf.ThreadPoolExecutor(8) as ex: res=list(ex.map(one,items))
for u,(bio,raw) in zip(items,res):
    P.add(urls[u],sorted(yrs[u]),bio[:1800],raw,'Past speakers')
    r=P.rows.get(norm(urls[u]))
    if r: r['url']=u
P.save()
