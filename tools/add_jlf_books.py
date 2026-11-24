"""Add books to festivals/jlf/data.json.
Sources: (1) titles in italics in the speaker's bio that follow a book cue ('author of', 'novel', ...);
(2) Open Library works whose author name matches the speaker exactly.
Each book: {t: title, c: cover path or '', b: 1 named in bio | 2 Open Library}.
Usage: python3 tools/add_jlf_books.py RAWDIR   (RAWDIR with y2027.json from build_jlf.py)"""
import json,re,sys,os,html,time,io,urllib.request,urllib.parse,unicodedata
RAW=sys.argv[1]; BASE=os.path.join(os.path.dirname(__file__),'..','festivals','jlf')
from PIL import Image
def norm(n):
    n=unicodedata.normalize('NFKD',html.unescape(n)).encode('ascii','ignore').decode().lower()
    n=re.sub(r'\b(dr|prof|professor|mr|ms|mrs|shri|smt|sir|justice|lord|dame)\b','',n)
    return re.sub(r'\s+',' ',re.sub(r'[^a-z ]',' ',n)).strip()
def tkey(t): return re.sub(r'[^a-z0-9]','',re.sub(r'^(the|a|an)\s+','',t.lower()))
NOTBOOK=re.compile(r'(times|guardian|new yorker|post|tribune|hindu|express|economist|telegraph|today|magazine|news|review of books|podcast|bbc|npr|cnn|wire|scroll|quint|forbes|atlantic|vogue|wired|time$|mint|herald|journal|indian express|outlook|lit hub|granta)',re.I)
CUE=re.compile(r'(author|authored|book|novel|memoir|collection|poem|poetry|essay|biograph|published|bestsell|latest|debut|titles|works|including|include|wrote|written|edited|translat|trilogy|series|sequel|anthology)',re.I)
d=json.load(open(BASE+'/data.json')); raw={}
for a in json.load(open(RAW+'/y2027.json'))['authors']: raw[a['slug']]=a
def bio_titles(h):
    out=[]
    for m in re.finditer(r'<(?:em|i)>(.*?)</(?:em|i)>',h or ''):
        t=html.unescape(re.sub(r'<[^>]+>','',m.group(1))).replace('\xa0',' ').strip(' ,.;:')
        if len(t)<3 or len(t)>110 or NOTBOOK.search(t): continue
        pre=re.sub(r'<[^>]+>',' ',(h or '')[max(0,m.start()-110):m.start()])
        if CUE.search(pre) or re.search(r'\b(by|and|,)\s*$',pre.strip()+' '): out.append(t)
    return out
def ol(name):
    q=urllib.parse.urlencode({'author':name,'limit':25,'fields':'title,author_name,first_publish_year,edition_count,cover_i,language'})
    for _ in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request('https://openlibrary.org/search.json?'+q,headers={'User-Agent':'litfest-speaker-guide/1.0'}),timeout=30))['docs']
        except Exception: time.sleep(2)
    return []
os.makedirs(BASE+'/bk',exist_ok=True); stats={'bio':0,'ol':0,'cov':0,'covfail':0}
for o in d:
    if o['bk']: continue
    a=raw.get(o['u']); books=[]; seen=set()
    for t in bio_titles(a['details'] if a else ''):
        k=tkey(t)
        if k and k not in seen: seen.add(k); books.append({'t':t,'c':'','b':1}); stats['bio']+=1
    nk=norm(o['n']); docs=[x for x in ol(o['n']) if nk in [norm(z) for z in x.get('author_name',[])] and len(x.get('author_name',[]))<=2]
    docs=[x for x in docs if x['title'] and tkey(x['title']) not in ('',)]
    has_bio=bool(o['f'])
    # without a bio only trust authors with several works under the exact name
    if not has_bio and (len(nk.split())<2 or len(docs)<3): docs=[]
    docs.sort(key=lambda x:(-(x.get('edition_count') or 0)))
    for x in docs:
        if len(books)>=5: break
        k=tkey(x['title'])
        if k in seen: 
            for b in books:
                if tkey(b['t'])==k and not b['c'] and x.get('cover_i'): b['_cov']=x['cover_i']
            continue
        seen.add(k); b={'t':x['title'],'c':'','b':2}
        if x.get('cover_i'): b['_cov']=x['cover_i']
        books.append(b); stats['ol']+=1
    for b in books:
        cv=b.pop('_cov',None)
        if cv:
            fn=BASE+'/bk/'+str(cv)+'.jpg'
            if not os.path.exists(fn):
                try:
                    raw_=urllib.request.urlopen(urllib.request.Request(f'https://covers.openlibrary.org/b/id/{cv}-M.jpg',headers={'User-Agent':'litfest-speaker-guide/1.0'}),timeout=30).read()
                    im=Image.open(io.BytesIO(raw_)).convert('RGB')
                    if im.size[0]<60: raise ValueError('placeholder')
                    im.thumbnail((200,300)); im.save(fn,'JPEG',quality=80,optimize=True); stats['cov']+=1
                except Exception as e: stats['covfail']+=1; continue
            b['c']='bk/'+str(cv)+'.jpg'
    o['bk']=books; time.sleep(.3)
json.dump(d,open(BASE+'/data.json','w'),ensure_ascii=False)
print(stats,sum(1 for o in d if o['bk']),'speakers with books')
