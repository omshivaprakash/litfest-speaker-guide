"""Daily check: has a festival changed its published speaker list?
For each speaker-type festival it reads the live source (the same pages and APIs the builders use), compares the names with the last snapshot in
data/snapshots/<id>.json, and writes data/updates.json (latest run) and data/updates-log.json (every change ever seen, newest first).
A source that returns nothing, or far fewer names than before, is reported as a fetch problem and never overwrites the snapshot.
The first run for a festival only records a baseline. Usage: python3 tools/check_updates.py   (exit code 0 always; see data/updates.json)"""
import json,os,re,sys,html,time,datetime,unicodedata,urllib.request,concurrent.futures as cf
R=os.path.join(os.path.dirname(__file__),'..'); UA={'User-Agent':'Mozilla/5.0 (LitFest Guide update check)'}
def get(u,t=45):
    for _ in range(2):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t).read().decode('utf8','ignore')
        except Exception: time.sleep(2)
    return ''
def clean(x): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',x or '').replace('\xa0',' '))).strip()
def norm(n):
    n=unicodedata.normalize('NFKD',html.unescape(n)).encode('ascii','ignore').decode().lower()
    n=re.sub(r'\b(dr|prof|professor|mr|ms|mrs|shri|smt|sir|adv|fr|rev|justice)\b\.?',' ',n); return re.sub(r'\s+',' ',re.sub(r'[^a-z ]',' ',n)).strip()
def tc(n): n=clean(n); return n.title() if n.isupper() else n
def js(u):
    try: return json.loads(get(u).strip().lstrip('﻿') or 'null')
    except Exception: return None
# ---- probes: each returns a list of names currently published ----
def p_hlf():
    out=[]
    for kind,page in (('speaker','speakers'),('moderators','moderators')):
        h=get(f'https://hydlitfest.org/{page}/')
        for sl,t in re.findall(r'<a[^>]+href=["\']https://hydlitfest.org/'+kind+r'/([a-z0-9-]+)/?["\'][^>]*>(.*?)</a>',h,re.S):
            if sl not in('moderators','mmb-authors') and clean(t): out.append(clean(t))
    return out
def p_blf():
    h=get('https://bangaloreliteraturefestival.org/year-2026/speakers/')
    return [clean(n) for _,n in re.findall(r'<h3 class="participant-name">\s*<a [^>]*href="(https://bangaloreliteraturefestival.org/participant/[^"]+)"[^>]*>\s*(.*?)\s*</a>',h,re.S)] or [clean(t) for t in re.findall(r'href="https://bangaloreliteraturefestival.org/participant/[^"]+"[^>]*>([^<]{3,60})</a>',h)]
def p_jlf():
    d=js('https://api.jaipurliteraturefestival.org/api/authorsPage?lang=en&limit=1000&year=2027&skip=0&search=') or {}
    return [re.sub(r'\s+',' ',(a['first_name']+' '+(a.get('last_name') or '')).strip()) for a in d.get('authors',[])]
def p_klf():
    out=[]
    for p in range(1,9):
        d=((js(f'https://api.keralaliteraturefestival.com/speakers/list-site?page={p}&size=100&search=') or {}).get('data') or {}).get('items') or []
        if not d: break
        out+=[x['heading'] for x in d]
    return out
def p_mbifl(): return [tc(x['speakerName']) for x in (js('https://www.mbifl.com/api/speakers.php') or [])]
def p_wlf(): return [clean(x['title']['rendered']) for x in (js('https://wlfwayanad.com/wp-json/wp/v2/wlf_speaker?per_page=100&_fields=title') or [])]
def p_nlf():
    t=js('https://www.neevliteraturefestival.org/wp-json/wp/v2/event_year?per_page=100&_fields=id,name') or []; yid=[x['id'] for x in t if x['name']=='2026']
    out=[];p=1
    while yid:
        d=js(f'https://www.neevliteraturefestival.org/wp-json/wp/v2/speaker?per_page=100&page={p}&event_year={yid[0]}&_fields=title') or []
        out+=[clean(x['title']['rendered']) for x in d]; p+=1
        if len(d)<100: break
    return out
def p_bplf():
    h=get('https://www.bhopalliteraturefestival.com/event/blf-2027/speakers'); return [tc(n) for n in re.findall(r'<h6 class="card-title">(.*?)</h6>',h,re.S)]
def p_klm():
    h=get('https://kolkatalitmeet.in/2026/'); return [clean(x) for x in re.findall(r'id="speaker_content_\d+".*?<h2 class="title t_u">(.*?)</h2>',h,re.S)]
def p_tll():
    h=get('https://www.litlive.in/fest26/speakers'); out=[]
    for it in h.split('role="listitem"')[1:]:
        if re.search(r'href="https://www\.litlive\.in/fest26/speakers/',it):
            m=re.search(r'<h2[^>]*>(.*?)</h2>',it,re.S)
            if m: out.append(clean(m.group(1)))
    return out
def p_bpf():
    h=get('https://www.bengalurupoetryfestival.org/poets.php'); return [clean(a) for a in re.findall(r'<img[^>]+class="[^"]*poets-image[^"]*"[^>]*alt="([^"]+)"',h)] or [clean(a) for a in re.findall(r'<img[^>]+src="[^"]+"[^>]+alt="([^"]{3,60})"',h) if a.upper()!='BPF']
def p_galf():
    out=[];p=1
    while p<15:
        h=get('https://goaartlitfest.com/speaker-2026/'+(f'page/{p}/' if p>1 else '')); new=0
        for it in re.split(r'(?=<article class="wpr-grid-item)',h)[1:]:
            m=re.search(r'wpr-grid-item-title.*?<a\s+href="https://goaartlitfest\.com/[a-z0-9-]+/">(.*?)</a>',it,re.S)
            if m: out.append(clean(m.group(1))); new+=1
        if not new: break
        p+=1
    return out
def p_ddlf():
    h=get('https://www.dehradunliteraturefestival.com/team'); return [clean(x) for x in re.findall(r'<h2[^>]*>(.*?)</h2>',h.split('role="listitem"',1)[-1],re.S) if 0<len(clean(x))<60]
def p_klf2():
    h=get('https://kalingaliteraryfestival.com/klf-speakers/'); out=[]
    for it in re.split(r'(?=<div class="team-container)',h)[1:]:
        if 'dt_team_category-klf-speakers-2025' in it:
            m=re.search(r'team-author-name"><a [^>]*>(.*?)</a>',it,re.S)
            if m: out.append(clean(m.group(1)))
    return out
def p_hayww():
    out=[];p=1
    while p<12:
        h=get(f'https://www.hayfestival.com/m-245-winter-weekend-2026.aspx?skinid=11&currencysetting=GBP&localesetting=en-GB&resetfilters=true&gridview=true&pagenum={p}'); new=[clean(x) for x in re.findall(r'<h2 class="event">(.*?)(?:<a |</h2>)',h,re.S)]
        if not new: break
        out+=new; p+=1
    return out
def p_koshala():
    h=get('https://koshalaliteraturefestival.com/speakers'); panes=re.split(r'<div class="tab-pane',h)[1:]; out=[]
    for p in panes:
        if re.search(r'id="nav-5"',p[:300],re.S): out=[clean(n) for n in re.findall(r'speakerdetails/\d+">.*?<img src="[^"]+"\s+alt="([^"]*)"',p,re.S)]
    return out
def p_ailf():
    h=get('https://ailf.co.in/speakers'); return [clean(n) for n in re.findall(r'<h3 class="team-name"[^>]*>\s*(?:<a[^>]*>)?\s*(.*?)\s*(?:</a>)?\s*</h3>',h,re.S)]
def p_mlf():
    out=[]
    for p in (1,2,3):
        d=js(f'https://www.mysuruliteraturefestival.com/wp-json/wp/v2/speakers?per_page=100&page={p}&_fields=title') or []
        if not d: break
        out+=[clean(x['title']['rendered']).replace('\u2060','') for x in d]
    return out
def p_shillong():
    h=get('https://shillonglitfest.com/speakers'); return [clean(n) for n in re.findall(r'aria-label="Read the bio of ([^"]+)"',h)]
PROBES={'mlf':p_mlf,'koshala':p_koshala,'ailf':p_ailf,'shillong':p_shillong,'blf':p_blf,'jlf':p_jlf,'hlf':p_hlf,'klf':p_klf,'mbifl':p_mbifl,'wlf':p_wlf,'nlf':p_nlf,'bplf':p_bplf,'klm':p_klm,'tll':p_tll,'bpf':p_bpf,'galf':p_galf,'ddlf':p_ddlf,'klf2':p_klf2,'hayww':p_hayww}
def main():
    os.makedirs(R+'/data/snapshots',exist_ok=True); F={f['id']:f for f in json.load(open(R+'/festivals.json',encoding='utf8'))['festivals']}
    cm=R+'/data/last-changes.md'
    if os.path.exists(cm): os.remove(cm)
    now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'); res={}; log_new=[]
    def run(f):
        try: return f()
        except Exception as e: print('probe error',e); return []
    with cf.ThreadPoolExecutor(5) as ex: live=dict(zip(PROBES,ex.map(run,PROBES.values())))
    for fid,names in live.items():
        names=sorted({n for n in names if norm(n)},key=str.lower); sp=f'{R}/data/snapshots/{fid}.json'
        old=json.load(open(sp,encoding='utf8')) if os.path.exists(sp) else None
        r={'name':F.get(fid,{}).get('short',fid),'count':len(names),'previous':len(old) if old is not None else None,'added':[],'removed':[],'status':'ok'}
        if not names or (old and len(names)<0.5*len(old)):
            r['status']='fetch problem: source returned %d names (was %s); snapshot kept'%(len(names),len(old) if old is not None else '-')
        elif old is None: r['status']='baseline recorded'; json.dump(names,open(sp,'w',encoding='utf8'),ensure_ascii=False)
        else:
            on={norm(n) for n in old}; nn={norm(n) for n in names}
            r['added']=[n for n in names if norm(n) not in on]; r['removed']=[n for n in old if norm(n) not in nn]
            if r['added'] or r['removed']:
                r['status']='changed'; json.dump(names,open(sp,'w',encoding='utf8'),ensure_ascii=False)
                log_new.append({'date':now,'id':fid,'name':r['name'],'added':r['added'],'removed':r['removed'],'count':len(names)})
        try:
            D=json.load(open(f'{R}/{F[fid]["base"]}data.json',encoding='utf8'))
            if isinstance(D,list):
                have={norm(o['n']) for o in D}; r['not_in_app']=[n for n in names if norm(n) not in have]
        except Exception: pass
        res[fid]=r
    json.dump({'checked':now,'festivals':res},open(R+'/data/updates.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
    lp=R+'/data/updates-log.json'; log=json.load(open(lp,encoding='utf8')) if os.path.exists(lp) else []
    if log_new or not os.path.exists(lp): json.dump((log_new+log)[:300],open(lp,'w',encoding='utf8'),ensure_ascii=False,indent=1)
    for fid,r in res.items(): print(f"{fid:6} {r['count']:5} live  +{len(r['added'])} -{len(r['removed'])}  not in app: {len(r.get('not_in_app',[]))}  {r['status']}")
    if log_new:
        md=['Speaker lists changed on the festivals\' sites (checked '+now+'):','']
        for e in log_new: md.append(f"- **{e['name']}**: {len(e['added'])} added"+(f" ({', '.join(e['added'][:12])}{'…' if len(e['added'])>12 else ''})" if e['added'] else '')+(f", {len(e['removed'])} removed ({', '.join(e['removed'][:12])})" if e['removed'] else ''))
        md+=['','Names live on the sites but not yet in the app:']+[f"- {r['name']}: {len(r['not_in_app'])}" for r in res.values() if r.get('not_in_app')]
        open(cm,'w',encoding='utf8').write('\n'.join(md)+'\n')
        print('\nCHANGES')
        for e in log_new: print(f"- {e['name']}: +{len(e['added'])} added"+(f" ({', '.join(e['added'][:8])}{'…' if len(e['added'])>8 else ''})" if e['added'] else '')+(f"; {len(e['removed'])} removed ({', '.join(e['removed'][:8])})" if e['removed'] else ''))
if __name__=='__main__': main()
