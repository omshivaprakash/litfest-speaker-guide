"""Build festivals/bblf/data.json (programme type) for Book Brahma Literature Festival 2026 from
the festival's published schedule PDF text and speaker pages (see fetch_bblf.py).
Usage: python3 tools/build_bblf.py SCHEDULE_TXT SPEAKERS_JSON   (SCHEDULE_TXT = pdftotext -layout of the schedule PDF)"""
import re,sys,json,os,unicodedata
TXT,SPK=sys.argv[1],sys.argv[2]; OUT=os.path.join(os.path.dirname(__file__),'..','festivals','bbl','data.json')
spk=json.load(open(SPK,encoding='utf8'))
def nk(n): return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',n).encode('ascii','ignore').decode().lower())
names=sorted({s['name'] for s in spk},key=lambda n:-len(n))
STAGES=[('MANTAPA','Mantapa'),('MATHANA','Mathana'),('AKSHARA','Akshara'),('ANGALA','Angala'),('MUKHAMUKHI','Mukha Mukhi'),('ANAVARANA','Anavarana'),('CHINNARA LOKA','Chinnara Loka'),('POETTREE','PoeTTree'),('NEWZEN','NewZen')]
FID={e:i+1 for i,(_,e) in enumerate(STAGES)}
LANGS='Kannada|English|Telugu|Tamil|Malayalam|Bengali|Tulu|Konkani|Kodava|Byari|Hindi|Marathi|Urdu|Sanskrit|Odia|Assamese|Gujarati|Punjabi|Multilingual|Bilingual'
TIME=re.compile(r'(\d{1,2})\.(\d{2})\s*([AP]M)')
lines=open(TXT,encoding='utf8').read().split('\n')
day=None;stage=None;sess=[];cur=None
def flush():
    global cur
    if cur: sess.append(cur); cur=None
for ln in lines:
    m=re.search(r'AUGUST (\d+), 2026',ln)
    if m: flush(); day=int(m.group(1)); stage=None; continue
    up=ln.upper().replace('Ó','O')
    sm=None
    for key,e in STAGES:
        if key in up and re.search(r'Aug \d+\s*$',ln) and ('Parallel' in ln or 'Main' in ln): sm=e
    if sm: flush(); stage=sm; d2=int(re.search(r'Aug (\d+)',ln).group(1)); day=d2; continue
    if day is None or stage is None: continue
    rm=re.match(r'^\s*(\d{1,2})\s+(\d{1,2}\.\d{2}\s*[AP]M)(.*)$',ln)
    if rm:
        flush(); cur={'d':day,'stage':stage,'n':int(rm.group(1)),'left':[rm.group(2)+rm.group(3)[:0]],'right':[]}
        rest=rm.group(3); cells=re.split(r'\s{2,}',rest.strip(),maxsplit=1) if rest.strip() else ['']
        if len(cells)==2: cur['left'][0]+=' '+cells[0]; cur['right'].append(cells[1])
        elif cells[0]:
            if re.fullmatch(r'(to|\d.*[AP]M)',cells[0].strip()): cur['left'][0]+=' '+cells[0]
            else: cur['right'].append(cells[0])
        continue
    if not cur or not ln.strip(): continue
    if re.fullmatch(r'\s*\d{1,3}\s*',ln) or re.fullmatch(r'\s*(MANTAPA|MATHANA|AKSHARA|ANGALA|MUKHAMUKHI|ANAVARANA|NEWZEN|PoeTTree)\s*',ln,re.I): continue
    ind=len(ln)-len(ln.lstrip())
    cells=re.split(r'\s{2,}',ln.strip(),maxsplit=1)
    c0=cells[0]
    if (re.match(r'^(to\s+)?\d{1,2}\.\d{2}\s*[AP]M',c0) or re.fullmatch(LANGS,c0.strip(),re.I) or c0.strip().lower()=='to') and ind<26:
        cur['left'].append(c0)
        if len(cells)==2: cur['right'].append(cells[1])
    else: cur['right'].append(ln.strip())
flush()
def t24(x): 
    m=TIME.search(x);h=int(m.group(1))%12+(12 if m.group(3)=='PM' else 0);return h,int(m.group(2))
def fmt(h,mi): 
    ap='AM' if h<12 else 'PM';hh=h%12 or 12;return f'{hh}:{mi:02d}'
D=[];
for s in sess:
    lt=' '.join(s['left']); ts=TIME.findall(lt)
    if not ts: continue
    a=t24(lt); rest=lt[TIME.search(lt).end():]; b=t24(rest) if TIME.search(rest) else None
    lang=(re.search(r'\b('+LANGS+r')\b',lt,re.I) or [None,''])[1] if re.search(r'\b('+LANGS+r')\b',lt,re.I) else ''
    txt=re.sub(r'\s+',' ',' '.join(s['right'])).strip()
    # mark moderators "(M)" then find known speaker names
    found=[];work=txt
    for nm in names:
        for m in re.finditer(r'(?<![A-Za-z])'+re.escape(nm)+r'(?![A-Za-z])',work):
            found.append((m.start(),nm,bool(re.match(r'\s*\(M\)',work[m.end():m.end()+6]))))
            work=work[:m.start()]+' '*(m.end()-m.start())+work[m.end():]
    found.sort()
    # title: text before first found name (or whole first sentence)
    title=txt
    if found and found[0][0]>=8: title=txt[:found[0][0]].strip(' :-–,')
    if len(title)<4 or (found and found[0][0]<8): title=txt[:110]
    title=re.sub(r'\s+(with|by|and|from)\s*$','',title.strip(),flags=re.I)
    title=re.sub(r'\s*(in conversation with|A conversation with|Chief Guest:?|Guests?:?)\s*$','',title,flags=re.I).strip(' :-–,')
    pp=[]
    for _,nm,mod in found:
        if any(p[1]==nm for p in pp): continue
        pp.append(['c' if mod else 'p',nm])
    D.append({'d':s['d'],'f':FID[s['stage']],'t':f'{fmt(*a)}–{fmt(*b)}' if b else fmt(*a),'k':title or txt[:80],'e':title or txt[:80],'th':lang or 'Language not stated','n':s['n'],'pp':pp,'raw':txt})
# performances (evening) on 14-16 Aug from the programme pages
perf=[(14,'Ramakka and I: Shilpa Mudbi and Ramavva Jogathi','Kannada'),(15,'Melodies from the South: Paramapada & Team','Kannada'),(16,'Rhythm of a New Generation: Sunidhi Ganesh Live','Multilingual')]
for d,t,l in perf:
    D.append({'d':d,'f':0,'t':'6:30–8:30','k':t,'e':t,'th':l,'n':0,'pp':[],'raw':t})
D.sort(key=lambda s:(s['d'],tt:=s['t'],s['f']))
def tkey(s):
    h,mi=s['t'].split('–')[0].split(':');h=int(h);h=h+12 if h<8 else h;return (s['d'],h*60+int(mi),s['f'])
D.sort(key=tkey)
for s in D: s.pop('n',None)
bios={}
for s in spk:
    if s['bio'] or s['ph']: bios[s['name']]={'b':s['bio'],'ph':s['ph']}
days=[{'d':14,'l':'Fri 14 Aug'},{'d':15,'l':'Sat 15 Aug'},{'d':16,'l':'Sun 16 Aug'},{'d':21,'l':'Fri 21 Aug'},{'d':22,'l':'Sat 22 Aug'},{'d':23,'l':'Sun 23 Aug'}]
forums=[{'id':FID[e],'k':e,'e':e} for _,e in STAGES]
json.dump({'sessions':D,'en':{},'forums':forums,'days':days,'bios':bios,'speakers':len(spk)},open(OUT,'w',encoding='utf8').write and open(OUT,'w',encoding='utf8'),ensure_ascii=False)
import collections
print(len(D),'sessions;',len({n for s in D for _,n in s['pp']}),'speakers placed of',len(spk));print(collections.Counter(s['d'] for s in D));print(collections.Counter(s['f'] for s in D))
