"""Check the data before it ships: files exist, photos and covers resolve, dates are sane, names are not duplicated within a festival.
Usage: python3 tools/validate.py   (exit 1 when something is wrong)"""
import json,os,sys,datetime
R=os.path.join(os.path.dirname(__file__),'..'); bad=[]; warn=[]
def chk(c,m):
    if not c: bad.append(m)
F=json.load(open(R+'/festivals.json',encoding='utf8'))['festivals']; ids=set()
for f in F:
    chk(f['id'] not in ids,'duplicate festival id '+f['id']); ids.add(f['id'])
    chk(os.path.exists(R+'/'+f['logo']),f'{f["id"]}: logo missing {f["logo"]}')
    for k in ('country','state','city'):
        if not f.get(k): bad.append(f'{f["id"]}: missing {k}')
    for k in ('start','end'):
        if f.get(k):
            try: datetime.date.fromisoformat(f[k])
            except Exception: bad.append(f'{f["id"]}: bad {k} {f[k]}')
    if f.get('start') and f.get('end'): chk(f['start']<=f['end'],f'{f["id"]}: start after end')
    if f['status']!='live': continue
    b=R+'/'+f['base']
    for fn in (('data.json','history.json') if f.get('type')!='programme' else ('data.json',)):
        chk(os.path.exists(b+fn),f'{f["id"]}: {fn} missing')
    if f.get('type')=='programme' or not os.path.exists(b+'data.json'): continue
    D=json.load(open(b+'data.json',encoding='utf8')); names=set()
    for o in D:
        n=o['n'].strip().lower()
        if n in names: warn.append(f'{f["id"]}: duplicate name {o["n"]}')
        names.add(n)
        if o.get('ph'): chk(os.path.exists(b+o['ph']),f'{f["id"]}: photo missing {o["ph"]} ({o["n"]})')
        for bk in o.get('bk',[]):
            if bk.get('c'): chk(os.path.exists(b+bk['c']),f'{f["id"]}: cover missing {bk["c"]}')
        for y in o.get('y',[]): chk(1990<=y<=2035,f'{f["id"]}: odd year {y} for {o["n"]}')
for f in F:
    pj=R+'/'+f['base']+'past.json'
    if f['status']=='live' and os.path.exists(pj):
        for o in json.load(open(pj,encoding='utf8')):
            if o.get('ph'): chk(os.path.exists(R+'/'+f['base']+o['ph']),f'{f["id"]}: past photo missing {o["ph"]} ({o["n"]})')
print(f'{len(F)} festivals checked; {len(warn)} warnings')
for w in warn[:15]: print('warn',w)
for m in bad[:40]: print('FAIL',m)
sys.exit(1 if bad else 0)
