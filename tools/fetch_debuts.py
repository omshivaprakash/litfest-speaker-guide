"""Find each author's earliest first_publish_year on Open Library (exact author-name match only) -> data/debut.json {name:{y,n}}.
Candidates: speakers who are authors (nonauth=0) or have books, across speaker-type festivals. Usage: python3 tools/fetch_debuts.py"""
import json,re,time,html,unicodedata,urllib.request,urllib.parse,os,concurrent.futures as cf
R=os.path.join(os.path.dirname(__file__),'..'); OUT=R+'/data/debut.json'
def norm(n):
    n=unicodedata.normalize('NFKD',html.unescape(n)).encode('ascii','ignore').decode().lower()
    n=re.sub(r'\b(dr|prof|professor|mr|ms|mrs|shri|smt|sir|justice|lord|dame)\b',' ',n); return re.sub(r'\s+',' ',re.sub(r'[^a-z ]',' ',n)).strip()
names={}
for f in json.load(open(R+'/festivals.json'))['festivals']:
    try: D=json.load(open(R+'/'+f['base']+'data.json',encoding='utf8'))
    except Exception: continue
    if not isinstance(D,list): continue
    for o in D:
        if (o.get('bk') or not o.get('nonauth',1)) and len(norm(o['n']).split())>=2: names.setdefault(norm(o['n']),o['n'])
res=json.load(open(OUT)) if os.path.exists(OUT) else {}
def one(item):
    k,n=item
    if n in res: return n,res[n]
    q=urllib.parse.urlencode({'author':n,'limit':100,'sort':'old','fields':'title,author_name,first_publish_year'})
    for _ in range(3):
        try:
            docs=json.load(urllib.request.urlopen(urllib.request.Request('https://openlibrary.org/search.json?'+q,headers={'User-Agent':'litfest-speaker-guide/1.0'}),timeout=40))['docs']; break
        except Exception: time.sleep(2); docs=None
    if docs is None: return n,None
    ys=[d['first_publish_year'] for d in docs if d.get('first_publish_year') and 1900<=d['first_publish_year']<=2026 and k in [norm(z) for z in d.get('author_name',[])] and len(d.get('author_name',[]))<=2]
    time.sleep(.2); return n,({'y':min(ys),'n':len(ys)} if len(ys)>=2 else {})
todo=list(names.items()); print(len(todo),'authors',flush=True); done=0
with cf.ThreadPoolExecutor(4) as ex:
    for n,r in ex.map(one,todo):
        if r is not None: res[n]=r
        done+=1
        if done%100==0: json.dump(res,open(OUT,'w',encoding='utf8'),ensure_ascii=False); print(done,flush=True)
json.dump(res,open(OUT,'w',encoding='utf8'),ensure_ascii=False); print('done',sum(1 for v in res.values() if v),'with years')
