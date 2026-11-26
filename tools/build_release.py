"""Build the open dataset: CSV files with stable IDs, a data package description, checksums and a changelog.
 dataset/latest/           the current release (always overwritten)
 dataset/releases/<ver>/   an immutable copy of every release
 dataset/CHANGELOG.md      what changed in each release, newest first
Versions are dates (CalVer): 2026.11.26, then 2026.11.26.2 if the data changes again the same day. With --auto a new version is only made
when the data differs from the last release. The facts are under CC BY 4.0 (see LICENSE-DATA.md); photos, logos, covers and bio text are not part of the dataset.
Usage: python3 tools/build_release.py [--auto]"""
import json,os,re,csv,sys,hashlib,datetime,shutil,collections
sys.path.insert(0,os.path.dirname(__file__))
from build_insights import gnorm
R=os.path.join(os.path.dirname(__file__),'..'); D=R+'/dataset'; AUTO='--auto' in sys.argv
def J(p): return json.load(open(R+'/'+p,encoding='utf8')) if os.path.exists(R+'/'+p) else None
F=J('festivals.json')['festivals']; FM={f['id']:f for f in F}
H=J('data/history-all.json') or {}
# ---- people: one record per normalised name, stable id = the normalised name with dashes
names=collections.defaultdict(collections.Counter)
for fid,h in H.items():
    for y,ns in h.items():
        for n in ns:
            k=gnorm(n)
            if k: names[k][n]+=1
def pid(k): return re.sub(r'\s+','-',k).strip('-')
attrs={}
for f in F:
    if f['status']!='live' or f.get('archive') or f.get('type')=='programme': continue
    for fn in ('data.json','past.json'):
        p=R+'/'+f['base']+fn
        if not os.path.exists(p): continue
        for o in json.load(open(p,encoding='utf8')):
            k=gnorm(o['n']); a=attrs.setdefault(k,{'role':'','cc':''})
            if o.get('role') and o['role'] not in('Speaker','Bio not published yet') and not a['role']: a['role']=o['role']
            if o.get('cc') and o['cc']!='Unknown' and not a['cc']: a['cc']=o['cc']
PEOPLE={}; APP=[]
for fid,h in sorted(H.items()):
    for y,ns in sorted(h.items()):
        for n in sorted(ns):
            k=gnorm(n)
            if not k: continue
            APP.append((pid(k),fid,int(y)))
APP=sorted(set(APP))
byp=collections.defaultdict(list)
for p,fid,y in APP: byp[p].append((fid,y))
for k,c in names.items():
    p=pid(k); L=byp.get(p,[])
    if not L: continue
    a=attrs.get(k,{'role':'','cc':''})
    PEOPLE[p]=[p,c.most_common(1)[0][0],a['role'],a['cc'],min(y for _,y in L),max(y for _,y in L),len({f for f,_ in L}),len(L)]
tables={}
tables['festivals.csv']=(['festival_id','name','short_name','status','city','state','country','official_site','next_edition_start','next_edition_end','first_year_in_data','latest_year_in_data'],
  [[f['id'],f['name'],f['short'],f['status'],f.get('city',''),f.get('state',''),f.get('country',''),f.get('url',''),f.get('start',''),f.get('end',''),f.get('from') if f['status']=='live' else '',f.get('to') if f['status']=='live' else ''] for f in F if not f.get('archive')])
tables['people.csv']=(['person_id','name','profession_guess','country_from_bio','first_year','last_year','festival_count','appearance_count'],sorted(PEOPLE.values()))
tables['appearances.csv']=(['person_id','festival_id','year'],[list(x) for x in APP])
PE=J('data/prize-effect.json')
if PE: tables['prize_wins.csv']=(['person_id','prize','year','source'],sorted({(pid(gnorm(r['n'])),r['p'],r['y'],'speaker bio') for r in PE['rows']}))
TR=J('data/translators.json')
if TR: tables['translators.csv']=(['person_id','translates_from','translates_into','language_pairs','translated_books_named'],[[pid(gnorm(p['n'])),'; '.join(p['from']),'; '.join(p['to']),'; '.join(a+' > '+b for a,b in p['pairs']),'; '.join(w['t']+(' ('+w['a']+')' if w.get('a') else '') for w in p['works'])] for p in TR['people']])
KD=J('data/kids.json')
if KD: tables['childrens_strands.csv']=(['festival_id','strand','edition_year','session','presenter','time_or_age_note'],[[s['id'],s['name'],i.get('y') or s.get('year',''),i.get('t',''),i.get('p',''),' · '.join(x for x in (i.get('tm'),i.get('age'),i.get('kind')) if x)] for s in KD['strands'] for i in s['items']])
PR=J('data/press.json')
if PR: tables['press_coverage.csv']=(['festival_id','year','outlet','language','headline','url','topics'],[[x['f'],x['y'] or '',x['o'],x['l'],x['h'],x['u'],'; '.join(x['t'])] for x in PR['items']])
def write(dirp,t):
    os.makedirs(dirp,exist_ok=True)
    for name,(hdr,rows) in t.items():
        with open(f'{dirp}/{name}','w',newline='',encoding='utf-8') as fh:
            w=csv.writer(fh,lineterminator='\n'); w.writerow(hdr); w.writerows(rows)
tmp=D+'/.tmp'; shutil.rmtree(tmp,ignore_errors=True); write(tmp,tables)
def sums(d): return {f:hashlib.sha256(open(f'{d}/{f}','rb').read()).hexdigest() for f in sorted(os.listdir(d)) if f.endswith('.csv')}
new=sums(tmp); prev=None
if os.path.exists(D+'/latest/manifest.json'): prev=json.load(open(D+'/latest/manifest.json'))
if AUTO and prev and prev['files']==new: print('no data change; no new release'); shutil.rmtree(tmp); sys.exit(0)
today=datetime.date.today().strftime('%Y.%m.%d'); ver=today
if prev and prev['version'].startswith(today):
    n=prev['version'].split('.'); k=int(n[3]) if len(n)>3 else 1; ver=f'{today}.{k+1}'
def rd(path):
    if not os.path.exists(path): return []
    return list(csv.reader(open(path,encoding='utf-8')))[1:]
oldA={tuple(r) for r in rd(D+'/latest/appearances.csv')}; newA={tuple(map(str,r)) for r in tables['appearances.csv'][1]}
oldP={r[0] for r in rd(D+'/latest/people.csv')}; newP={r[0] for r in tables['people.csv'][1]}
oldF={r[0] for r in rd(D+'/latest/festivals.csv')}; newF={r[0] for r in tables['festivals.csv'][1]}
add_p=sorted(newP-oldP); rem_p=sorted(oldP-newP); add_a=sorted(newA-oldA); rem_a=sorted(oldA-newA)
counts={n:len(rows) for n,(h,rows) in tables.items()}
man={'version':ver,'built':datetime.date.today().isoformat(),'licence':'CC BY 4.0','counts':counts,'files':new}
dest=f'{D}/releases/{ver}'; shutil.rmtree(dest,ignore_errors=True); shutil.copytree(tmp,dest); json.dump(man,open(dest+'/manifest.json','w'),indent=1)
shutil.rmtree(D+'/latest',ignore_errors=True); shutil.copytree(tmp,D+'/latest'); json.dump(man,open(D+'/latest/manifest.json','w'),indent=1); shutil.rmtree(tmp)
pkg={'name':'litfest-guide','title':'LitFest Guide open dataset','version':ver,'licenses':[{'name':'CC-BY-4.0','path':'https://creativecommons.org/licenses/by/4.0/','title':'Creative Commons Attribution 4.0'}],
 'homepage':'https://omshivaprakash.github.io/litfest-speaker-guide/','sources':[{'title':'Each festival\'s own public pages','path':'https://omshivaprakash.github.io/litfest-speaker-guide/'}],
 'resources':[{'name':n[:-4],'path':n,'format':'csv','mediatype':'text/csv','encoding':'utf-8','schema':{'fields':[{'name':h} for h in hdr]}} for n,(hdr,_) in tables.items()]}
for d in (dest,D+'/latest'): json.dump(pkg,open(d+'/datapackage.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
ent=[f'## {ver} ({datetime.date.today().isoformat()})','',f"- {counts['festivals.csv']} festivals, {counts['people.csv']:,} people, {counts['appearances.csv']:,} appearances"+(f", {counts.get('prize_wins.csv',0)} dated prize wins, {counts.get('translators.csv',0)} translators, {counts.get('childrens_strands.csv',0)} children's sessions, {counts.get('press_coverage.csv',0)} press links" if True else '')]
if prev is None: ent.append('- First release.')
else:
    ent.append(f"- People: +{len(add_p)} / −{len(rem_p)}. Appearances: +{len(add_a)} / −{len(rem_a)}. Festivals: +{len(newF-oldF)} / −{len(oldF-newF)}.")
    fest=collections.Counter(a[1] for a in add_a)
    if fest: ent.append('- Appearances added by festival: '+', '.join(f'{k} {v}' for k,v in fest.most_common(8))+'.')
    if rem_a: ent.append('- Appearances removed (a festival changed or corrected its list): '+', '.join(f'{k} {v}' for k,v in collections.Counter(a[1] for a in rem_a).most_common(6))+'.')
    chg=[n for n in new if prev['files'].get(n)!=new[n]]; ent.append('- Files changed: '+(', '.join(chg) or 'none')+'.')
ent.append('')
cl=D+'/CHANGELOG.md'; old=open(cl,encoding='utf8').read().split('\n',3)[3] if os.path.exists(cl) else ''
open(cl,'w',encoding='utf8').write('# LitFest Guide dataset: changelog\n\nVersions are dates. Newest first. Data licence: CC BY 4.0 (see LICENSE-DATA.md).\n\n'+'\n'.join(ent)+'\n'+old)
print(ver,counts,'| new people',len(add_p),'new appearances',len(add_a))
