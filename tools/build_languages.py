"""Build data/languages.json: how each festival represents regional (Indian) languages.
Per speaker we look for the language they write or publish in, from three signals (most to least reliable):
  1. books: the main language(s) of their Open Library titles (festivals/<id>/works.json). The top language counts, and any other language
     with at least 40% of the top language's titles (translations into many languages are ignored this way).
  2. bio: explicit statements ('Kannada poet', 'writes in Hindi and English', 'Malayalam cinema') and the stored `lg` field.
  3. programme: for Book Brahma, the language each session is held in.
Only speakers with a known language are counted; every festival carries its coverage (known / total) so the numbers are read honestly.
Class per speaker: en (English only), mix (English plus an Indian language), ind (Indian language(s) only), oth (another language).
Usage: python3 tools/build_languages.py"""
import json,re,os,glob,collections,datetime
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'); FJ=json.load(open(R+'/festivals.json',encoding='utf8'))['festivals']
CODE={'eng':'English','hin':'Hindi','urd':'Urdu','ben':'Bengali','mar':'Marathi','guj':'Gujarati','pan':'Punjabi','ori':'Odia','ory':'Odia','asm':'Assamese','kan':'Kannada','tam':'Tamil','tel':'Telugu','mal':'Malayalam','kok':'Konkani','san':'Sanskrit','mai':'Maithili','kas':'Kashmiri','snd':'Sindhi','nep':'Nepali','mni':'Manipuri','bho':'Bhojpuri','raj':'Rajasthani','tcy':'Tulu','kha':'Khasi','sat':'Santali','brx':'Bodo','doi':'Dogri'}
IND={'Hindi','Urdu','Bengali','Marathi','Gujarati','Punjabi','Odia','Assamese','Kannada','Tamil','Telugu','Malayalam','Konkani','Sanskrit','Maithili','Kashmiri','Sindhi','Nepali','Manipuri','Bhojpuri','Rajasthani','Tulu','Khasi','Santali','Bodo','Dogri','Dakhni','Kodava','Mizo','Garo'}
OTHER={'fre':'French','ger':'German','spa':'Spanish','ita':'Italian','por':'Portuguese','rus':'Russian','chi':'Chinese','jpn':'Japanese','ara':'Arabic','per':'Persian','dut':'Dutch','swe':'Swedish','kor':'Korean','pol':'Polish','tur':'Turkish'}
LNG='|'.join(sorted(list(IND)+['English','Korean','French','Spanish','German','Italian','Portuguese','Russian','Chinese','Japanese','Arabic','Persian','Welsh','Croatian','Lithuanian','Mexican'],key=len,reverse=True))
RX=[re.compile(r'\b(%s)[- ](?:language|poet|poetry|novelist|writer|author|literature|fiction|playwright|short stor|stories|translator|theatre|cinema|film|folk|scholar|critic)'%LNG,re.I),
    re.compile(r'\b(?:writes?|writing|written|poems?|poetry|novels?|stories|fiction|books?|translat\w+)\b[^.]{0,50}?\b(?:in|into|from|between) (?:both |the )?(%s)(?:(?:,| and| or) (%s))?(?:(?:,| and| or) (%s))?'%(LNG,LNG,LNG),re.I)]
STATE={'Karnataka':'Kannada','Kerala':'Malayalam','Tamil Nadu':'Tamil','Telangana':'Telugu','Andhra Pradesh':'Telugu','West Bengal':'Bengali','Maharashtra':'Marathi','Gujarat':'Gujarati','Odisha':'Odia','Assam':'Assamese','Punjab':'Punjabi','Goa':'Konkani','Uttar Pradesh':'Hindi','Rajasthan':'Hindi','Madhya Pradesh':'Hindi','Uttarakhand':'Hindi','Delhi':'Hindi'}
def cap(z): return z.strip().capitalize() if z else None
def from_bio(o):
    b=(o.get('f') or o.get('b') or '')+' '+(o.get('le') or ''); out=[]
    for rx in RX:
        for m in rx.finditer(b):
            for z in m.groups():
                z=cap(z)
                if z and z not in('Mexican','Welsh','Croatian','Lithuanian') and z not in out: out.append(z)
    for z in o.get('lg') or []:
        if z not in out and (z in IND or z=='English'): out.append(z)
    if re.search(r'\bwrites? in english\b|english[- ]language (?:author|writer|novelist|poet)',b,re.I) and 'English' not in out: out.append('English')
    return out
def from_works(w):
    if not w: return []
    c=collections.Counter()
    for t in w['w']:
        for code in set((t[2] or '').split()):
            n=CODE.get(code) or OTHER.get(code)
            if n: c[n]+=1
    if not c: return []
    top=c.most_common(1)[0][1]; return [l for l,k in c.most_common() if k>=max(2,.4*top) or (k==top)][:3]
def cls(L):
    e='English' in L; i=any(l in IND for l in L)
    return 'mix' if e and i else 'en' if e and not [l for l in L if l!='English'] else 'ind' if i else 'oth'
out={'built':datetime.date.today().isoformat(),'fest':{},'langs':{}}; tot=collections.Counter(); who=collections.defaultdict(set)
for f in FJ:
    if f['status']!='live': continue
    p=f"{R}/{f['base']}data.json"
    if not os.path.exists(p): continue
    d=json.load(open(p,encoding='utf8')); wp=f"{R}/{f['base']}works.json"; W=json.load(open(wp,encoding='utf8')) if os.path.exists(wp) else {}
    if isinstance(d,dict):
        ses=d.get('sessions') or []; c=collections.Counter(s['th'] for s in ses if s.get('th') in set(IND)|{'English'})
        if f['id']=='bbl' and c:
            out['fest'][f['id']]={'kind':'sessions','n':sum(c.values()),'total':len(ses),'by':dict(c)}
            for l,k in c.items(): tot[l]+=k
        continue
    rec={'kind':'speakers','total':len(d),'known':0,'en':0,'mix':0,'ind':0,'oth':0,'by':{}}
    for o in d:
        L=from_works(W.get(o.get('u'))) or from_bio(o)
        if not L: continue
        k=cls(L); rec['known']+=1; rec[k]+=1
        for l in L:
            rec['by'][l]=rec['by'].get(l,0)+1; who[l].add((f['id'],o['n']))
    if rec['known']: out['fest'][f['id']]=rec; rec['home']=STATE.get(f.get('state')) if (f.get('country')=='India') else None
for l,s in who.items(): out['langs'][l]=len(s)
for l,k in tot.items(): out['langs'][l]=out['langs'].get(l,0)+k
json.dump(out,open(R+'/data/languages.json','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
kn=sum(r.get('known',0) for r in out['fest'].values() if r['kind']=='speakers'); tt=sum(r['total'] for r in out['fest'].values() if r['kind']=='speakers')
ind=sum(r['mix']+r['ind'] for r in out['fest'].values() if r['kind']=='speakers')
print(len(out['fest']),'festivals;',kn,'of',tt,'speakers with a known language;',ind,'use an Indian language');print(sorted(out['langs'].items(),key=lambda x:-x[1])[:14])
for f,r in out['fest'].items(): print(f,{k:v for k,v in r.items() if k!='by'},dict(sorted(r['by'].items(),key=lambda x:-x[1])[:4]))
