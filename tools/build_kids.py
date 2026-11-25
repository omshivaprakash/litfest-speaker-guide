"""Build data/kids.json: the children's strands of the festivals, and which speakers write or perform for young readers.
 strands: official children's programmes (read from the festival's own pages) and strands visible in our own programme data.
 people:  per festival, names whose session titles, role or bio clearly point to children's or young-adult work (a lead, not a fact).
Usage: python3 tools/build_kids.py   (needs network for the two official pages; keeps the old strands if a page does not answer)"""
import json,os,re,sys,html,datetime
sys.path.insert(0,os.path.dirname(__file__))
from pastlib import get,unmoji
R=os.path.join(os.path.dirname(__file__),'..'); OUT=R+'/data/kids.json'
def clean(x): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',x or '').replace('\xa0',' '))).strip()
FJ={f['id']:f for f in json.load(open(R+'/festivals.json',encoding='utf8'))['festivals']}
old=json.load(open(OUT,encoding='utf8')) if os.path.exists(OUT) else {'strands':[]}; OLD={s['id']:s for s in old['strands']}
KS=re.compile(r"children['’]s\b|(?<!grand)\bchildren\b(?! of the| in conflict)|\bkids?\b(?! *$)|\bteen(s|agers?)?\b|\btweens?\b|young adult|picture books?|chinnara|\bbal(a)? sahitya|story ?time|junior(?! *kolkata)",re.I)
KB=re.compile(r"children['’]s (author|writer|book|books|literature|fiction|illustrator|publisher|poet|story|stories|imprint|novelist|series|theatre|publishing|content)|(writes?|writing|wrote|written|books|stories|poems|poetry|verse|content|plays) (for|to) (young|children|kids|teen|school)|picture books?|young[- ]adult|\bbal sahitya|for young readers|kids['’] (author|books)|author of (several )?children['’]?s? ?(book|stor|poem|novel|fiction)",re.I)
KR=re.compile(r"children|picture book|young adult|storytell",re.I)
def hlf():
    h=get('https://hydlitfest.org/hlf-2026-dreamcatchers/')
    if not h: return None
    i=h.find('<h1') if '<h1' in h else 0; t=re.sub(r'<script.*?</script>|<style.*?</style>',' ',h[h.find('Dreamcatchers</h'):] if 'Dreamcatchers</h' in h else h,flags=re.S)
    L=[clean(x) for x in re.split(r'<[^>]+>',t) if clean(x)]; items=[]
    for j,s in enumerate(L):
        if s=='Duration:' and j>=2:
            # title, presenter precede "Duration:"; duration then "Age group:" then ages
            p=L[j-1]; ttl=L[j-2]; dur=L[j+1] if j+1<len(L) else ''; age=L[j+3] if j+3<len(L) and L[j+2]=='Age group:' else ''
            items.append({'t':ttl,'p':p,'age':age,'dur':dur})
    return items
def bpf():
    h=get('https://bengalurupoetryfestival.org/childrens_fest_schedule.php'); fac=get('https://bengalurupoetryfestival.org/childrens-fest-facilitators.php')
    if not h: return None
    L=[clean(x) for x in re.split(r'<[^>]+>',re.sub(r'<script.*?</script>|<style.*?</style>',' ',h,flags=re.S)) if clean(x)]
    items=[]; day=''; i=0
    tm=re.compile(r'^\d{1,2}[.:]\d\d [AP]M\s*-\s*\d{1,2}[.:]\d\d [AP]M$',re.I)
    while i<len(L):
        if tm.match(L[i]) and i+2<len(L):
            ttl=L[i+1]; nxt=L[i+2:i+5]; kind=''; who=''
            for z in nxt:
                if re.match(r'^(Theatre|Storytelling|Activity|Book Reading|Workshop|Music|Performance|Art|Play|Poetry|Dance)',z,re.I) and len(z)<40: kind=z; break
                if not who and len(z)<50: who=z
            items.append({'tm':L[i],'t':ttl,'p':who if who!=kind else '','kind':kind})
        i+=1
    names=[clean(x) for x in re.findall(r'<h[2-5][^>]*>\s*([^<]{3,60})\s*</h[2-5]>',fac or '') if clean(x) not in('Registration',"Children's Fest Facilitators")]
    return items,names
def sess(fid,rx_forum=None):
    D=json.load(open(R+f'/festivals/{fid}/data.json',encoding='utf8')); return D
def main():
    S=[]
    # --- official pages
    it=hlf()
    if it: S.append({'id':'hlf','name':'Dreamcatchers','year':2026,'who':'children and teens','url':'https://hydlitfest.org/hlf-2026-dreamcatchers/','official':1,'items':it})
    elif 'hlf' in OLD: S.append(OLD['hlf'])
    b=bpf()
    if b: S.append({'id':'bpf','name':"Children’s Fest",'year':2026,'who':'young children, with their families','url':'https://bengalurupoetryfestival.org/childrens_fest_schedule.php','official':1,'items':b[0],'facilitators':b[1]})
    elif 'bpf' in OLD: S.append(OLD['bpf'])
    # --- from our own programme data
    kl=json.load(open(R+'/festivals/klf/data.json',encoding='utf8')); its=[]; seen=set()
    for o in kl:
        for y,t in o.get('s',[]):
            if re.match(r"Children['’]s KLF",t) and (t,o['n']) not in seen: seen.add((t,o['n'])); its.append({'t':re.sub(r"^Children['’]s KLF:\s*",'',t),'p':o['n']})
    if its: S.append({'id':'klf','name':'Children’s KLF','year':2026,'who':'young readers','url':'','official':0,'items':its,'from':'session titles in the published speaker list'})
    for fid,fo in (('jsw',2),('bbl',7)):
        D=json.load(open(R+f'/festivals/{fid}/data.json',encoding='utf8')); fm={f['id']:f for f in D['forums']}
        ss=[s for s in D['sessions'] if s['f']==fo or re.search('Children',s.get('th','') or '')]
        if ss: S.append({'id':fid,'name':fm[fo]['k'],'year':2026,'who':'children','url':'','official':0,'forum':fo,'items':[{'tm':s['t'],'t':(s.get('e') or s.get('k') or 'Session'),'p':', '.join(p[1] for p in s.get('pp',[])),'kind':s.get('th','')} for s in ss],'from':'the festival’s programme'})
    # BLF: C|L|F (Children | Literature | Fun), from the festival's own schedule pages for each year
    BU={2025:'year-2025/clf',2024:'archives/year-2024/clf/',2023:'archives/year-2023/clf/',2022:'archives/year-2022/clf/',2019:'archives/year-2019/clf/',2018:'archives/year-2018/c-l-f/',2017:'archives/year-2017/c-l-f/',2016:'archives/year-2016/c-l-f/'}
    its=[]
    for y,u in sorted(BU.items(),reverse=True):
        h=get('https://bangaloreliteraturefestival.org/'+u)
        if not h or 'Children|Literature|Fun' not in h: continue
        h=h[h.find('Children|Literature|Fun (C|L|F)',h.find('page anc id')):]
        L=[clean(x) for x in re.split(r'<[^>]+>',re.sub(r'<script.*?</script>|<style.*?</style>',' ',h,flags=re.S)) if clean(x)]
        day=''; i=0; tm=re.compile(r'^\d{1,2}:\d\d [ap]m$',re.I); n0=len(its)
        while i<len(L):
            if re.match(r'^Day \d',L[i]): day=L[i]
            if tm.match(L[i]) and i+1<len(L):
                ttl=L[i+1]; j=i+2; ps=[]
                while j<len(L) and not tm.match(L[j]) and not re.match(r'^Day \d|^Digital|^Partners|^Venue|^Register|^#|^Sat \||^Sun \|',L[j]) and len(ps)<3 and len(L[j])<70: ps.append(L[j]); j+=1
                pp=re.sub(r'\s*\|\s*Venue:.*$','',', '.join(ps))
                if ttl in ('Malgudi','Narnia') or pp.startswith('Ages:'): i+=1; continue   # 2018 layout lists the venue first; skipped rather than guessed
                its.append({'y':y,'tm':L[i],'t':ttl,'p':pp,'kind':day.split('|')[0].strip()})
            i+=1
        print('blf clf',y,len(its)-n0)
    if its: S.append({'id':'blf','name':'C|L|F: Children | Literature | Fun','year':max(i['y'] for i in its),'who':'children of all ages, with their parents','url':'https://bangaloreliteraturefestival.org/year-2025/clf','official':1,'items':its})
    elif 'blf' in OLD: S.append(OLD['blf'])
    # Neev: children's books are the festival
    nl=json.load(open(R+'/festivals/nlf/data.json',encoding='utf8'))
    S.append({'id':'nlf','name':'Neev, a children’s books festival','year':2026,'who':'young readers','url':'https://www.neevliteraturefestival.org/','official':1,'whole':1,'items':[],'count':len(nl),'from':'the festival describes itself as children’s books and author events'})
    # --- people
    P={}
    for f in FJ.values():
        if f['status']!='live' or f.get('archive') or f.get('type')=='programme': continue
        names={}
        for fn in ('data.json','past.json'):
            p=R+'/'+f['base']+fn
            if not os.path.exists(p): continue
            for o in json.load(open(p,encoding='utf8')):
                b=o.get('f') or o.get('b') or ''; ss=[t for y,t in o.get('s',[]) if KS.search(t)]; why=''
                if re.match(r"Children['’]s",o.get('role','')) or KR.search(o.get('role','')): why='role'
                elif ss: why='session'
                elif KB.search(b): why='bio'
                if why: names[o['n']]=why
        if names: P[f['id']]=names
    json.dump({'built':datetime.date.today().isoformat(),'strands':S,'people':P},open(OUT,'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print(len(S),'strands:',[(s['id'],len(s['items'])) for s in S]); print({k:len(v) for k,v in P.items()})
main()
