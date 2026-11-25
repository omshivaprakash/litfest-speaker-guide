"""Build data/translators.json: who translates, between which languages, and which books, read from speakers' own bios.
 A person counts as a translator when their role is Translator or a bio sentence says they translate (not merely that their book was translated).
 Language pairs come from phrases such as "translates from Kannada into English", "Hindi-English translator", "from Bengali to English".
 Works come from phrases such as "her translation of S Hareesh's Moustache" or "translated Perumal Murugan's Poonachi".
 Everything is a lead read from text; the source sentence is kept so each claim can be checked. Usage: python3 tools/build_translators.py"""
import json,os,re,glob,datetime,collections,sys,time,urllib.request,urllib.parse,concurrent.futures as cf
sys.path.insert(0,os.path.dirname(__file__))
from build_insights import gnorm
R=os.path.join(os.path.dirname(__file__),'..')
LNG='Kannada|Tamil|Telugu|Malayalam|Hindi|Bengali|Bangla|Urdu|Marathi|Gujarati|Punjabi|Odia|Oriya|Assamese|Sanskrit|Konkani|Nepali|Santali|Dogri|Maithili|Sindhi|Kashmiri|Tulu|Manipuri|Bodo|Rajasthani|Bhojpuri|Awadhi|Braj|Pali|Prakrit|French|German|Spanish|Russian|Japanese|Korean|Chinese|Mandarin|Arabic|Persian|Farsi|Italian|Portuguese|Sinhala|Sinhalese|Hebrew|Turkish|Polish|Dutch|Swedish|Norwegian|Danish|Finnish|Hungarian|Czech|Ukrainian|Greek|Latin|Welsh|Irish|Gaelic|Lithuanian|Croatian|Serbian|Vietnamese|Thai|Indonesian|Swahili|English'
L1=r'(?:the )?(%s)'%LNG
CANON={'Bangla':'Bengali','Oriya':'Odia','Sinhalese':'Sinhala','Farsi':'Persian','Mandarin':'Chinese'}
def cap(z): z=z.capitalize(); return CANON.get(z,z)
ACTIVE=re.compile(r"\btranslator\b|\btranslates\b|\b(?:has|have|had|also|and|who|she|he|they|I)\s+(?:also\s+|since\s+|recently\s+|extensively\s+)?translated\b(?!\s+(?:in)?to\b)|\btranslations?\s+(?:of|from)\b|translation\s+(?:projects?|volumes?|work)",re.I)
PASSIVE=re.compile(r"\b(?:been|were|was|is|are|being|get|gets|got)\s+translated\b|\(also translated|\balso\s+translated\s+(?:in)?to\b|\btranslated\s+(?:in)?to\s+(?:over|more than|many|several|\d+|multiple|numerous|various|a dozen)|\btranslations?\s+in\s+\d+|\bhas\s+been\s+translated",re.I)
def sentences(b): return [s for s in re.split(r'(?<=[.!?])\s+',b) if s.strip()]
def pairs_in(s):
    out=[]
    for m in re.finditer(r'\bfrom '+L1+r'(?: and '+L1+r')?(?:\s*,?\s*(?:in)?to|\s+into|\s+to)\s+'+L1,s,re.I):
        for src in (m.group(1),m.group(2)):
            if src: out.append((cap(src),cap(m.group(3))))
    for m in re.finditer(r'\b('+LNG+r')\s*(?:[-–—/]|\bto\b|\binto\b)\s*('+LNG+r')\s+(?:literary\s+)?(?:translat|translator)',s,re.I): out.append((cap(m.group(1)),cap(m.group(2))))
    for m in re.finditer(r'translat\w*[^.]{0,90}?\bbetween '+L1+r' and '+L1,s,re.I): out.append((cap(m.group(1)),cap(m.group(2)))); out.append((cap(m.group(2)),cap(m.group(1))))
    if not out:
        for m in re.finditer(r'translat\w*[^.]{0,90}?\bfrom '+L1+r'(?: and '+L1+r')?',s,re.I):
            for src in (m.group(1),m.group(2)):
                if src: out.append((cap(src),''))
        for m in re.finditer(r'translat\w*[^.]{0,70}?\b(?:into|to) '+L1,s,re.I): out.append(('',cap(m.group(1))))
        for m in re.finditer(r'translator (?:of|from) '+L1,s,re.I): out.append((cap(m.group(1)),''))
    return list(dict.fromkeys(out))
TITLE=r"(?:[“\"‘]([^”\"’]{2,90})[”\"’]|(?-i:((?:[A-Z][\w:’'.-]*)(?:\s+(?:[A-Z][\w:’'.-]*|of|the|and|in|a|an|to|for|on))*(?:\s+[A-Z][\w:’'.-]*)?)))"
W1=re.compile(r"translat(?:ed|ion of|ions of|ing)\s+(?:the\s+)?(?:(?:novel|novels|book|collection|poems|poetry|memoir|stories|play|epic|classic|works?)\s+(?:of|by)?\s*)?(?:(?-i:(?:[A-Z][\w.-]*\s+){0,2}[A-Z][\w.-]*)[’']s\s+(?:(?:novel|book|collection|memoir|poems|stories|play)\s+)?)"+TITLE,re.I)
W2=re.compile(r"translat(?:ed|ion of|ions of|ing)\s+(?:the\s+)?(?:novel|book|collection|memoir|poems|stories|play|epic|classic|short story collection)\s+"+TITLE+r"\s+(?:by|from|into)",re.I)
W3=re.compile(r"(?:translation|translations)\s*\(?\s*(?:of\s+)?(?:the\s+)?"+TITLE+r"\s*\)?\s+(?:won|was|received|earned|bagged|is |has |were )",re.I)
def works_in(s):
    out=[]
    for rx in (W1,W2):
        for m in rx.finditer(s):
            t=(m.group(1) or m.group(2) or '').strip(' ,.;:')
            t=re.sub(r'\s+(?:from|into|to|and|which|that|who|for|in|by|won|was|is)$','',t,flags=re.I).strip()
            if 2<len(t)<=90 and not re.match(r'^(the|a|an|his|her|their|many|several|numerous|over|more)$',t,re.I) and not re.search(r'\b(Press|University|Prize|Award|Festival|Foundation|Library|Literary|Literature)\b',t): out.append(t)
    return list(dict.fromkeys(out))
def load():
    P={}
    F={f['id']:f for f in json.load(open(R+'/festivals.json',encoding='utf8'))['festivals']}
    for fid,f in F.items():
        if f['status']!='live' or f.get('archive') or f.get('type')=='programme': continue
        for fn in ('data.json','past.json'):
            p=R+'/'+f['base']+fn
            if not os.path.exists(p): continue
            for o in json.load(open(p,encoding='utf8')):
                k=gnorm(o['n']); e=P.setdefault(k,{'n':o['n'],'bio':'','role':o.get('role',''),'f':set(),'ph':'','lg':set()}); e['lg'].update(o.get('lg') or [])
                b=o.get('f') or o.get('b') or ''
                if len(b)>len(e['bio']): e['bio']=b
                e['f'].add(fid)
                if o.get('role')=='Translator': e['role']='Translator'
    return P,F
def ol_translated(name):
    """Books Open Library credits to this person as translator (it often has none, so this only adds)."""
    q=urllib.parse.urlencode({'q':'contributor:"%s"'%name,'fields':'title,author_name,contributor,first_publish_year','limit':20}); nk=gnorm(name); out=[]
    for _ in range(2):
        try:
            d=json.load(urllib.request.urlopen(urllib.request.Request('https://openlibrary.org/search.json?'+q,headers={'User-Agent':'litfest-speaker-guide/1.0'}),timeout=30))['docs']; break
        except Exception: d=[]; time.sleep(1.5)
    for x in d:
        for c in x.get('contributor',[]):
            if re.search(r'translat',c,re.I) and gnorm(re.sub(r'\s*\(.*$','',c))==nk and x.get('title'):
                out.append({'t':x['title'],'a':', '.join(x.get('author_name',[])[:2]),'y':x.get('first_publish_year') or 0}); break
    return out
def main():
    P,F=load(); people=[]; LF=collections.Counter(); LT=collections.Counter(); PR=collections.Counter()
    for k,e in P.items():
        ss=sentences(e['bio']); act=[s for s in ss if ACTIVE.search(s) and not (PASSIVE.search(s) and not re.search(r'\btranslator\b|\b(?:has|have|also)\s+translated\b|translat\w+\s+(?:of|from)\b',s,re.I))]
        is_tr=e['role']=='Translator' or bool(act)
        if not is_tr: continue
        pr=[]; wk=[]; ev=[]
        for s in (act or [s for s in ss if re.search('translat',s,re.I)]):
            pr+=pairs_in(s); wk+=works_in(s); ev.append(s[:260])
        pr=list(dict.fromkeys(pr)); wk=list(dict.fromkeys(wk))
        full=[p for p in pr if p[0] and p[1]]; part=[p for p in pr if not(p[0] and p[1])]
        # a half-known pair is completed only when the other side is named in the same person's other pairs
        srcs={p[0] for p in pr if p[0]}; tgts={p[1] for p in pr if p[1]}
        if not full and len(srcs)==1 and len(tgts)==1: full=[(next(iter(srcs)),next(iter(tgts)))]
        frm=sorted(srcs); to=sorted(tgts)
        for p in full: PR[p]+=1
        for s in frm: LF[s]+=1
        for t in to: LT[t]+=1
        people.append({'n':e['n'],'f':sorted(e['f']),'role':e['role'],'pairs':[list(p) for p in full],'from':frm,'to':to,'langs':sorted(e['lg']),'works':[{'t':w,'a':'','y':0} for w in wk],'ev':ev[:2]})
    people.sort(key=lambda p:p['n'].lower())
    with cf.ThreadPoolExecutor(4) as ex: found=list(ex.map(lambda p:ol_translated(p['n']),people))
    for p,f in zip(people,found):
        have={re.sub(r'[^a-z0-9]','',w['t'].lower()) for w in p['works']}
        for w in f:
            k=re.sub(r'[^a-z0-9]','',w['t'].lower())
            if k not in have: have.add(k); p['works'].append(w)
        p['works']=p['works'][:12]
    inv=collections.Counter()
    for p in people:
        for l in set(p['from'])|set(p['to'])|set(p['langs']): inv[l]+=1
    out={'built':datetime.date.today().isoformat(),'people':people,'from':dict(LF.most_common()),'to':dict(LT.most_common()),'pairs':[[a,b,n] for (a,b),n in PR.most_common()],
         'involve':dict(inv.most_common()),'fest':{k:F[k]['short'] for k in F}}
    json.dump(out,open(R+'/data/translators.json','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print(len(people),'translators;',sum(1 for p in people if p['pairs']),'with a language pair;',sum(1 for p in people if p['works']),'with named works;',sum(len(p['works']) for p in people),'works')
    print('with works after Open Library:',sum(1 for p in people if p['works']),'; works',sum(len(p['works']) for p in people));print('languages involved:',list(inv.most_common(8)));print('top from:',list(LF.most_common(8)));print('top to:',list(LT.most_common(5)));print('top pairs:',PR.most_common(8))
if __name__=='__main__': main()
