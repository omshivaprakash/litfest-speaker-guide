"""Prize effect: for people whose bio says they won a prize in a named year, how close was that year to a festival appearance?
Writes data/prize-effect.json. Read from bio sentences ("won the 2021 Booker Prize"), so these are leads, not facts, and the result shows
association, never cause. Usage: python3 tools/build_insights.py   (run after build_index.py)"""
import json,os,re,unicodedata,glob,collections,datetime
R=os.path.join(os.path.dirname(__file__),'..')
GALIAS={'abhijit vinayak banerjee':'abhijit banerjee','chitra divakaruni':'chitra banerjee divakaruni','ed luce':'edward luce','andre kurkov':'andrei kurkov','bahuleyan jeyamohan':'b jeyamohan','amaan ali bangash ayaan ali bangash':'amaan ali bangash'}
def gnorm(n):
    s=unicodedata.normalize('NFKD',n); s=''.join(c for c in s if not unicodedata.combining(c)).lower()
    s=re.sub(r'\b(dr|prof|professor|mr|ms|mrs|shri|smt|sir)\b\.?',' ',s); s=re.sub(r'[^\w ]+',' ',s,flags=re.U).replace('_',' '); s=re.sub(r'\s+',' ',s).strip()
    o=[]
    for w in s.split(' '):
        if len(w)==1 and o and o[-1][1]: o[-1][0]+=w
        else: o.append([w,len(w)==1])
    r=[x[0] for x in o]
    if len(r)>=3: r=[w for i,w in enumerate(r) if not(0<i<len(r)-1 and len(w)==1)]
    k=' '.join(r); return GALIAS.get(k,k)
PRIZES=[('Booker Prize',r'\bbooker\b'),('Nobel Prize',r'\bnobel\b'),('Pulitzer Prize',r'\bpulitzer\b'),('Sahitya Akademi Award',r'sahitya akademi|sahitya academy'),('Jnanpith Award',r'jnanpith|gyanpith'),('Padma honours',r'padma (shri|bhushan|vibhushan)'),('JCB Prize for Literature',r'jcb prize'),('Yuva Puraskar',r'yuva puraskar'),('Bal Sahitya Puraskar',r'bal sahitya'),('Commonwealth Prize',r'commonwealth (writers|book|short story|prize)'),('National Award (film or other)',r'national film award|national award'),('Crossword Book Award',r'crossword (book )?award'),('DSC Prize',r'dsc prize'),('Tata Literature Live award',r'tata literature live'),('Ramon Magsaysay Award',r'magsaysay'),('Saraswati Samman',r'saraswati samman'),('Vyas Samman',r'vyas samman'),('International Booker',r'international booker')]
NOTWIN=re.compile(r'short-?list|long-?list|nominat|finalist|judge|jury|chair of|member of the|curat|named after|runner|contend|selection committee|trustee',re.I)
WINCUE=re.compile(r'\bwon\b|\bwin\b|winner|winning|awarded|received|recipient|bagged|conferred|honou?red|laureate|\bgiven\b|bestowed|\btook\b|\bearned\b|\bgarnered\b|\bclaimed\b|\bgrant(ed)?\b|\bshared\b|\bcarried\b|\bnamed\b|\bfor whic?h?\b|\bhas the\b|\bwith the\b',re.I)
STATE=re.compile(r'(karnataka|kerala|tamil|bengal|maharashtra|gujarat|rajasthan|state|delhi|punjab|andhra|telangana|assam|odisha|orissa|bihar|haryana|himachal|goa|national film|filmfare|kendra)\W*(\w+\W+){0,2}$',re.I)
def sentences(b): return re.split(r'(?<=[.!?])\s+',b)
def wins(bio):
    """Yield (prize, year) for each prize named near a year with a winning verb and no shortlist/judge wording close by."""
    out=[]; seen=set()
    for se in sentences(bio):
        taken=[]
        for pn,rx in PRIZES:
            for m in re.finditer(rx,se,re.I):
                if any(a<=m.start()<b for a,b in taken): continue
                pre=se[max(0,m.start()-26):m.start()]
                if pn in('Sahitya Akademi Award','Yuva Puraskar','Bal Sahitya Puraskar') and STATE.search(pre) and not re.search(r'sahitya akademi\W*$',pre[-1:]+''): 
                    if re.search(r'(karnataka|kerala|tamil|bengal|maharashtra|gujarat|rajasthan|state|delhi|punjab|andhra|telangana|assam|odisha|bihar|haryana|himachal|goa|kendra)\W*$',pre,re.I): continue
                if pn=='Sahitya Akademi Award' and re.search(r'yuva puraskar|bal sahitya',se,re.I): continue
                w0,w1=max(0,m.start()-70),min(len(se),m.end()+70); win=se[w0:w1]
                if NOTWIN.search(se[max(0,m.start()-45):m.end()+45]): continue
                if not WINCUE.search(win): continue
                ys=[(abs((y.start()+w0)-m.start()),int(y.group(0))) for y in re.finditer(r'\b(19[5-9]\d|20[0-2]\d)\b',win)]
                if not ys: continue
                y=min(ys)[1]
                if (pn,y) in seen: continue
                seen.add((pn,y)); taken.append((m.start(),m.end())); out.append((pn,y,se[:220]))
    return out
def load():
    P={}
    for f in json.load(open(R+'/festivals.json',encoding='utf8'))['festivals']:
        if f['status']!='live' or f.get('archive') or f.get('type')=='programme': continue
        for fn in ('data.json','past.json'):
            p=R+'/'+f['base']+fn
            if not os.path.exists(p): continue
            for o in json.load(open(p,encoding='utf8')):
                k=gnorm(o['n']); e=P.setdefault(k,{'n':o['n'],'bio':'','role':'','src':[]})
                b=o.get('f') or o.get('b') or ''
                if len(b)>len(e['bio']): e['bio']=b
                e['src'].append((f['id'],o))
    return P
def appearances(H):
    app=collections.defaultdict(lambda:collections.defaultdict(set))
    for fid,h in H.items():
        for y,names in h.items():
            for n in names: app[gnorm(n)][fid].add(int(y))
    return app

W0,W1=2013,2027
def build():
    P=load(); H=json.load(open(R+'/data/history-all.json',encoding='utf8')); app=appearances(H)
    F={f['id']:f for f in json.load(open(R+'/festivals.json',encoding='utf8'))['festivals']}
    rows=[]
    for k,e in P.items():
        for pn,y,se in wins(e['bio']):
            ap=sorted((y2,fid) for fid,ys in app.get(k,{}).items() for y2 in ys)
            rows.append({'k':k,'n':e['n'],'p':pn,'y':y,'ap':[[fid,y2] for y2,fid in ap],'s':se})
    # one row per person and prize and year
    seen=set(); R2=[]
    for r in rows:
        key=(r['k'],r['p'],r['y'])
        if key in seen: continue
        seen.add(key); R2.append(r)
    rows=R2
    # appearance years of each person (any festival)
    yrs={k:{y for fid,ys in v.items() for y in ys} for k,v in app.items()}
    wins_by={}
    for r in rows: wins_by.setdefault(r['k'],set()).add(r['y'])
    def inwin(k,y): return any(y in(w,w+1) for w in wins_by.get(k,()))
    b={'before':0,'same':0,'next':0,'later23':0,'later4':0}
    for r in rows:
        r['first']=0; r['d']=None
        a=[(y2-r['y'],fid,y2) for fid,y2 in r['ap']]
        near=[x for x in a if x[0] in(0,1)]
        if near:
            r['d']=min(x[0] for x in near); r['hit']=[[fid,y2] for d,fid,y2 in near]
            fy=min(y for _,y in [(0,x[2]) for x in a]) if a else 0
            r['first']=1 if min(x[2] for x in near)==min(x[2] for x in a) else 0
    # in-window vs nearby other-years appearance rate, pooled over persons with a win in range
    inn=[0,0]; out=[0,0]
    for k,ws in wins_by.items():
        for w in ws:
            if not(W0<=w<=W1-1): continue
            for y in (w,w+1):
                if W0<=y<=W1: inn[1]+=1; inn[0]+= y in yrs.get(k,())
            for y in (w-3,w-2,w-1,w+2,w+3,w+4):
                if W0<=y<=W1 and not inwin(k,y): out[1]+=1; out[0]+= y in yrs.get(k,())
    sel=[r for r in rows if W0<=r['y']<=W1-1]
    cnt=lambda f: sum(1 for r in sel if f(r))
    bypz={}
    for r in sel: z=bypz.setdefault(r['p'],{'p':r['p'],'wins':0,'hit':0,'first':0}); z['wins']+=1; z['hit']+= r['d'] is not None; z['first']+= bool(r['first'] and r['d'] is not None)
    # for each festival edition: speakers in the edition who won a prize that year or the year before
    ed={}
    for fid,h in H.items():
        for y,names in h.items():
            y=int(y); ks={gnorm(n) for n in names}
            hit=[r for r in rows if r['k'] in ks and r['y'] in(y-1,y)]
            ppl={r['k'] for r in hit}
            ed.setdefault(fid,{})[y]=[len(ks),len(ppl)]
    summary={'wins':len(sel),'people':len({r['k'] for r in sel}),'hit':cnt(lambda r:r['d'] is not None),'same':cnt(lambda r:r['d']==0),'next':cnt(lambda r:r['d']==1),'first':cnt(lambda r:r['d'] is not None and r['first']),
             'rate_in':[inn[0],inn[1]],'rate_out':[out[0],out[1]],'window':[W0,W1]}
    out_rows=[{'n':r['n'],'p':r['p'],'y':r['y'],'ap':r['ap'],'d':r['d'],'first':r['first']} for r in rows if r['y']>=1990]
    json.dump({'built':datetime.date.today().isoformat(),'summary':summary,'byPrize':sorted(bypz.values(),key=lambda z:-z['wins']),'editions':ed,'rows':out_rows,'fest':{k:F[k]['short'] for k in H if k in F}},open(R+'/data/prize-effect.json','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print(summary); print([ (z['p'],z['wins'],z['hit']) for z in sorted(bypz.values(),key=lambda z:-z['wins'])][:8])
    ex=[r for r in sel if r['d'] is not None][:0]
if __name__=='__main__': build()
