"""Add books to festivals/<id>/data.json for speaker-type festivals.
Sources: (1) italic titles in the bio that follow a book cue (TITLES_JSON maps speaker key 'u' -> italic strings);
(2) Open Library works whose author name matches exactly. Each book {t, c, b} (b: 1 bio, 2 Open Library).
For speakers with no bio, Open Library titles are kept only when at least three have covers.
Usage: python3 tools/add_books_ol.py festivals/hlf TITLES_JSON"""
import json,re,sys,os,html,time,io,urllib.request,urllib.parse,unicodedata
from PIL import Image
BASE=sys.argv[1]; TJ=json.load(open(sys.argv[2],encoding='utf8')) if len(sys.argv)>2 else {}
def norm(n):
    n=unicodedata.normalize('NFKD',html.unescape(n)).encode('ascii','ignore').decode().lower()
    n=re.sub(r'\b(dr|prof|professor|mr|ms|mrs|shri|smt|sir|justice|lord|dame)\b','',n)
    return re.sub(r'\s+',' ',re.sub(r'[^a-z ]',' ',n)).strip()
def tkey(t): return re.sub(r'[^a-z0-9]','',re.sub(r'^(the|a|an)\s+','',t.lower()))
NOTBOOK=re.compile(r'(times|guardian|new yorker|post|tribune|hindu|express|economist|telegraph|today|magazine|news|review of books|podcast|bbc|npr|cnn|wire|scroll|quint|forbes|atlantic|vogue|wired|mint|herald|journal|outlook|granta|festival|university|institute)',re.I)
def ol(name):
    q=urllib.parse.urlencode({'author':name,'limit':25,'fields':'title,author_name,edition_count,cover_i'})
    for _ in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request('https://openlibrary.org/search.json?'+q,headers={'User-Agent':'litfest-speaker-guide/1.0'}),timeout=30))['docs']
        except Exception: time.sleep(2)
    return []
os.makedirs(BASE+'/bk',exist_ok=True); d=json.load(open(BASE+'/data.json',encoding='utf8')); st={'bio':0,'ol':0,'cov':0}
for o in d:
    if o['bk']: continue
    books=[];seen=set()
    for t in TJ.get(o['u'],[]):
        k=tkey(t)
        if 3<=len(t)<=110 and not NOTBOOK.search(t) and k and k not in seen and not t.lower().startswith(('he ','she ')):
            seen.add(k);books.append({'t':t,'c':'','b':1});st['bio']+=1
    nk=norm(o['n']); docs=[x for x in ol(o['n']) if nk in [norm(z) for z in x.get('author_name',[])] and len(x.get('author_name',[]))<=2 and x.get('title')]
    if not o['f'] and (len(nk.split())<2 or len(docs)<3): docs=[]
    docs.sort(key=lambda x:-(x.get('edition_count') or 0)); cand=[]
    for x in docs:
        if len(books)+len(cand)>=5: break
        k=tkey(x['title'])
        if k in seen:
            for b in books:
                if tkey(b['t'])==k and x.get('cover_i'): b['_cov']=x['cover_i']
            continue
        seen.add(k);cand.append({'t':x['title'],'c':'','b':2,'_cov':x.get('cover_i')})
    if not o['f'] and sum(1 for b in cand if b['_cov'])<3: cand=[]
    books+=cand;st['ol']+=len(cand)
    for b in books:
        cv=b.pop('_cov',None)
        if cv:
            fn=f'{BASE}/bk/{cv}.jpg'
            if not os.path.exists(fn):
                try:
                    r=urllib.request.urlopen(urllib.request.Request(f'https://covers.openlibrary.org/b/id/{cv}-M.jpg',headers={'User-Agent':'litfest-speaker-guide/1.0'}),timeout=30).read()
                    im=Image.open(io.BytesIO(r)).convert('RGB')
                    if im.size[0]<60: raise ValueError
                    im.thumbnail((200,300));im.save(fn,'JPEG',quality=80,optimize=True);st['cov']+=1
                except Exception: continue
            b['c']=f'bk/{cv}.jpg'
    o['bk']=books;time.sleep(.3)
json.dump(d,open(BASE+'/data.json','w',encoding='utf8'),ensure_ascii=False)
print(st,sum(1 for o in d if o['bk']),'speakers with books')
