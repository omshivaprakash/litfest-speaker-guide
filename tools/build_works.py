"""Build festivals/<id>/works.json: every book Open Library lists for each speaker, in any language.
Matching (precision first, because Open Library has namesakes and split author records):
  - candidate author records = exact normalised-name matches from /search/authors.json
  - a record is 'verified' (m=1) when at least one of its titles appears in the speaker's bio or in the books already stored for them
  - if nothing verifies and exactly one record matches with >=3 works for a speaker flagged as an author, it is kept as 'matched by name only' (m=2)
  - otherwise nothing is added (ambiguous or unknown)
Output {u: {m, ol:[author ids], n:total, w:[[title, first year, 'lang lang', ...]]}} sorted by editions, capped at 250 titles per person.
Raw API answers are cached under $AUTHCACHE (default /tmp/olcache) so reruns do not hit the network again.
Usage: python3 tools/build_works.py [festival ids...]"""
import json,re,os,sys,time,html,unicodedata,urllib.request,urllib.parse,concurrent.futures as cf
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','festivals'); C=os.environ.get('AUTHCACHE','/tmp/olcache'); os.makedirs(C,exist_ok=True)
def norm(n):
    n=unicodedata.normalize('NFKD',html.unescape(n)).encode('ascii','ignore').decode().lower()
    n=re.sub(r'\b(dr|prof|professor|mr|ms|mrs|shri|smt|sir|justice|lord|dame|lady|late|hon)\b','',n)
    return re.sub(r'\s+',' ',re.sub(r'[^a-z ]',' ',n)).strip()
def tkey(t): return re.sub(r'[^a-z0-9]','',re.sub(r'^(the|a|an)\s+','',t.lower()))
def call(u,tag):
    fn=f'{C}/{tag}.json'
    if os.path.exists(fn): return json.load(open(fn))
    for i in range(4):
        try:
            d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'litfest-speaker-guide/1.0 (open data project)'}),timeout=40))
            json.dump(d,open(fn,'w')); return d
        except Exception: time.sleep(2+i*2)
    return None
def authors(name):
    d=call('https://openlibrary.org/search/authors.json?'+urllib.parse.urlencode({'q':name,'limit':10}),'a_'+re.sub(r'\W+','_',name.lower())[:80])
    nk=norm(name); out=[]
    for a in (d or {}).get('docs',[]):
        names=[a.get('name','')]+(a.get('alternate_names') or [])
        if norm(a.get('name',''))==nk or (nk in [norm(x) for x in names] and len(nk.split())>=2): out.append(a)
    return out
def works(key):
    d=call('https://openlibrary.org/search.json?'+urllib.parse.urlencode({'author':key,'fields':'title,first_publish_year,language,edition_count,key','limit':600}),'w_'+key)
    return (d or {}).get('docs',[])
def known(o): return {tkey(b['t']) for b in (o.get('bk') or [])}
def one(o):
    nk=norm(o['n'])
    if len(nk.split())<2: return None
    cands=authors(o['n'])
    if not cands: return None
    txt=' '.join([o.get('f') or '',o.get('b') or '']).lower(); tx=re.sub(r'[^a-z0-9]','',txt); kn=known(o); res=[]
    for a in cands[:4]:
        ws=[w for w in works(a['key']) if w.get('title')]
        ver=any((len(tkey(w['title']))>=6 and tkey(w['title']) in tx) or tkey(w['title']) in kn for w in ws)
        res.append((a,ws,ver))
    ok=[r for r in res if r[2]]; m=1
    if not ok:
        r1=[r for r in res if len(r[1])>=3]
        if len(res)==1 and r1 and not o.get('nonauth'): ok=r1; m=2
        else: return None
    seen={};
    for a,ws,_ in ok:
        for w in sorted(ws,key=lambda x:-(x.get('edition_count') or 0)):
            k=tkey(w['title'])
            if k and k not in seen: seen[k]=[w['title'],w.get('first_publish_year') or 0,' '.join(w.get('language') or [])]
    L=list(seen.values())
    return {'m':m,'ol':[a['key'] for a,_,_ in ok],'n':len(L),'w':L[:250]}
def festival(fid):
    p=f'{R}/{fid}/data.json'; d=json.load(open(p,encoding='utf8'))
    if isinstance(d,dict):
        ks=[x for x in d if isinstance(d[x],list) and d[x] and isinstance(d[x][0],dict) and 'n' in d[x][0]]; d=d[ks[0]] if ks else []
    d=[o for o in d if o.get('u')]
    with cf.ThreadPoolExecutor(5) as ex: rs=list(ex.map(one,d))
    out={o['u']:r for o,r in zip(d,rs) if r}
    if out: json.dump(out,open(f'{R}/{fid}/works.json','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    v=sum(1 for r in out.values() if r['m']==1); print(fid,len(d),'people ->',len(out),'with works (',v,'verified,',len(out)-v,'by name only),',sum(r['n'] for r in out.values()),'titles',flush=True)
if __name__=='__main__':
    ids=sys.argv[1:] or [f for f in sorted(os.listdir(R)) if os.path.exists(f'{R}/{f}/data.json')]
    for f in ids: festival(f)

    # flag festivals that have a works file so the app only asks for it when it exists
    FJ=json.load(open(R+'/../festivals.json',encoding='utf8'))
    for f in FJ['festivals']:
        if os.path.exists(f'{R}/{f["id"]}/works.json'): f['works']=1
        else: f.pop('works',None)
    json.dump(FJ,open(R+'/../festivals.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
