"""Sahitya Akademi (Kendra) awards for Kannada vs the festivals' speaker lists -> data/sahitya-kannada.json.
Source: Wikipedia, List of Sahitya Akademi Award winners for Kannada (main award, Bhasha Samman, Translation, Yuva Puraskar, Bala Sahitya Puraskar).
The raw page is cached at $SA_HTML (default /tmp/sa/k.html); fetch it first with curl. Names are matched to every person in data/history-all.json
(all festival editions) and to the current rosters (festivals/<id>/data.json), using normalised names with a fuzzy fallback; the result is reviewed by eye
and the confirmed matches are kept in MATCH_OK below (each is a name we checked, not a guess).
Usage: python3 tools/build_sa.py [--review]"""
import re,html,json,os,sys,unicodedata,difflib,datetime,glob
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
SRC=os.environ.get('SA_HTML','/tmp/sa/k.html')
CATS=[(1,'Main award'),(2,'Bhasha Samman'),(3,'Translation'),(4,'Yuva Puraskar'),(5,'Bala Sahitya Puraskar')]
def norm(n):
    n=unicodedata.normalize('NFKD',html.unescape(n)).encode('ascii','ignore').decode().lower()
    n=re.sub(r'\b(dr|prof|professor|mr|ms|mrs|shri|smt|sir)\b','',n); n=re.sub(r'[^a-z ]',' ',n)
    return re.sub(r'\s+',' ',re.sub(r'\b([a-z]) (?=[a-z]\b)',r'\1',n)).strip()
def cells(r): return [re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',re.sub(r'<sup.*?</sup>','',x,flags=re.S)))).strip() for x in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>',r,re.S)]
def winners():
    h=open(SRC,encoding='utf8',errors='ignore').read(); tabs=re.findall(r'<table class="wikitable.*?</table>',h,re.S); out=[]
    for ti,cat in CATS:
        yr=None
        for r in re.findall(r'<tr.*?</tr>',tabs[ti],re.S)[1:]:
            c=cells(r)
            if not c: continue
            m=re.match(r'(\d{4})',c[0])
            if m: yr=int(m.group(1)); c=c[1:]
            if len(c)<2 or 'no award' in ' '.join(c).lower(): continue
            names=c[1] if len(c)>=4 else c[0]; works=c[2] if len(c)>=4 else c[1]
            for nm in re.split(r',| and | & ',names):
                nm=re.sub(r'\[.*?\]|†','',nm).strip()
                if nm and len(nm)>2: out.append({'name':nm,'year':yr,'cat':cat,'work':re.sub(r'\[.*?\]','',works).strip()})
    return out
# winner name (as on the list) -> spellings found in the festival lists, checked by hand. m=1 same person beyond reasonable doubt, m=2 probable.
OK={'Chandrashekhara Kambara':(['Chandrashekhara Kambara'],1),'Girish Karnad':(['Girish Karnad'],1),'M. M. Kalburgi':(['M M Kalburgi'],1),'Kum. Veerabhadrappa':(['Kum Vee Bhadrappa'],1),
 'Vaidehi':(['Vaidehi'],1),'Gopalakrishna Pai':(['Gopal Krishna Pai'],2),'H. S. Shivaprakash':(['HS Shivaprakash'],1),'C. N. Ramachandran':(['CN Ramachandran'],1),
 'K. V. Tirumalesh':(['Prof. K. V. Tirumalesh'],1),'Bolwar Mahammad Kunhi':(['Bolwar Mahammed Kunhi','Bolwar Mahamad Kunhi'],1),'Vijaya':(['Dr. Vijaya'],2),
 'Veerappa Moily':(['Veerappa Moily'],1),'Mudnakudu Chinnaswamy':(['Mudnakudu Chinnaswamy'],1),'T. V. Venkatachala Sastry':(['Venkatachala Shastry'],1),
 'Hampa Nagarajaiah':(['Hampa Nagarajaiah'],1),'S. Shettar':(['Dr. S. Settar'],1),'H. S. Venkateshamurthy':(['H.S. Venkatesha Murthy','H S Venkatesh Murthy'],1),
 'N. Damodara Shetty':(['N Damodara Shetty'],1),'Giraddi Govindaraj':(['Giraddi Govindaraju'],1),'Veeranna Madiwalara':(['Veeranna Madivalar'],1),
 'Vikrama Hatwara':(['Vikram Hatwar','Vikram Hathwar'],1),'Shanti K. Appanna':(['Shanthi K Appanna'],1),'Shruthi B R':(['Shruthi BR'],1)}
def run():
    W=winners(); H=json.load(open(R+'/data/history-all.json',encoding='utf8')); F={f['id']:f for f in json.load(open(R+'/festivals.json',encoding='utf8'))['festivals']}
    by={}
    for f,ys in H.items():
        for y,ns in ys.items():
            for n in ns: by.setdefault(n,{}).setdefault(f,[]).append(int(y))
    out=[]
    for w in W:
        r=dict(w); r['fest']={}; r['m']=0
        if w['name'] in OK:
            sp,m=OK[w['name']]; r['m']=m
            for s in sp:
                for f,ys in by.get(s,{}).items(): r['fest'].setdefault(f,[]); r['fest'][f]=sorted(set(r['fest'][f]+ys))
        out.append(r)
    seen={}
    for r in out: seen.setdefault(r['name'],r)
    people=len(seen); inv=[r for r in out if r['fest']]; invp={r['name'] for r in inv}
    rec=[r for r in out if r['year'] and r['year']>=2000]; recp={r['name'] for r in rec}
    def rel(r):
        ys=[y for v in r['fest'].values() for y in v]; return {'same':any(y==r['year'] for y in ys),'next':any(y==r['year']+1 for y in ys),'after':any(y>r['year'] for y in ys),'before':any(y<r['year'] for y in ys)}
    for r in out:
        if r['fest']: r['rel']=rel(r)
    S={'entries':len(out),'people':people,'invited_people':len(invp),'recent_entries':len(rec),'recent_people':len(recp),'recent_invited':len({r['name'] for r in rec if r['fest']}),
       'by_festival':{f:len({r['name'] for r in inv if f in r['fest']}) for f in sorted({f for r in inv for f in r['fest']})},
       'same_or_next':len({r['name'] for r in inv if r['rel']['same'] or r['rel']['next']}),'before_win':len({r['name'] for r in inv if r['rel']['before'] and not r['rel']['after']}),'after_win':len({r['name'] for r in inv if r['rel']['after']}),
       'by_cat':{}}
    for c in (c[1] for c in CATS):
        e=[r for r in out if r['cat']==c]; S['by_cat'][c]={'entries':len(e),'invited':len({r['name'] for r in e if r['fest']})}
    json.dump({'built':datetime.date.today().isoformat(),'source':'Wikipedia, List of Sahitya Akademi Award winners for Kannada','summary':S,'winners':out},open(R+'/data/sahitya-kannada.json','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    import csv
    with open(R+'/data/sahitya-kannada.csv','w',newline='',encoding='utf-8-sig') as fh:
        w=csv.writer(fh); w.writerow(['winner','award_year','award','work','spoke_at_a_tracked_festival','match_confidence','festivals_and_years','same_or_next_year_as_award','spoke_before_award','spoke_after_award'])
        for r in sorted(out,key=lambda r:(r['year'] or 0,r['cat'],r['name'])):
            fs='; '.join('%s: %s'%(F[f]['short'] if f in F else f,', '.join(map(str,ys))) for f,ys in sorted(r['fest'].items())); rl=r.get('rel') or {}
            w.writerow([r['name'],r['year'],r['cat'],r['work'],'yes' if r['fest'] else 'no',{0:'',1:'certain',2:'probable'}[r['m']],fs,'yes' if rl.get('same') or rl.get('next') else ('no' if r['fest'] else ''),'yes' if rl.get('before') else ('no' if r['fest'] else ''),'yes' if rl.get('after') else ('no' if r['fest'] else '')])
    return S,out
if __name__=='__main__':
    S,out=run(); print(json.dumps(S,indent=1)); 
    for r in out:
        if r['fest']: print(r['name'],r['year'],r['cat'],'m'+str(r['m']),r['fest'],r['rel'])
