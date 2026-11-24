"""Write festivals/<id>/history.json = {year: [names]} used by the cross-festival search.
blf: archive speaker lists (tools/history_src/blf_yrspk.json) plus the 2026 line-up in data.json.
jlf: JLF API output (RAWDIR/y2018.json ... y2027.json). hlf: written by build_hlf.py.
sjm, jn, bbl: the people named in their programmes. Usage: python3 tools/build_history.py [JLF_RAWDIR]"""
import json,os,sys,re
R=os.path.join(os.path.dirname(__file__),'..','festivals')
def w(fid,h): json.dump(h,open(f'{R}/{fid}/history.json','w',encoding='utf8'),ensure_ascii=False); print(fid,{y:len(v) for y,v in h.items()})
y=json.load(open(os.path.join(os.path.dirname(__file__),'history_src','blf_yrspk.json')))
h={yr:sorted(set(v.values())) for yr,v in y.items()}
d=json.load(open(f'{R}/blf/data.json',encoding='utf8')); h['2026']=sorted(o['n'] for o in d); w('blf',h)
if len(sys.argv)>1:
    h={}
    for yr in range(2018,2028):
        a=json.load(open(f'{sys.argv[1]}/y{yr}.json'))['authors']
        h[str(yr)]=sorted({re.sub(r'\s+',' ',(x['first_name']+' '+(x.get('last_name') or '')).strip()) for x in a})
    w('jlf',h)
for fid,yr in (('sjm','2026'),('jn','2026'),('bbl','2026')):
    d=json.load(open(f'{R}/{fid}/data.json',encoding='utf8'))
    w(fid,{yr:sorted({n for s in d['sessions'] for _,n in s['pp']})})
