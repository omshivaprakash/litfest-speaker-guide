"""Build festivals/hlf/{data,stats}.json for the Hyderabad Literary Festival from its public pages.
Usage: python3 tools/build_hlf.py RAWDIR
RAWDIR holds saved pages: speakers.html, moderators.html (2027 line-up) and speakers-2026.html ...
speakers-2021.html, anuvaad-speakers-2022.html, kaavya-dhaara-speakers-2022.html (past years).
Profile pages and photos for the 2027 line-up are fetched from hydlitfest.org with 3 polite workers."""
import re,sys,json,os,html,io,time,unicodedata,urllib.request
import concurrent.futures as cf
from collections import Counter
from PIL import Image
RAW=sys.argv[1]; OUT=os.path.join(os.path.dirname(__file__),'..','festivals','hlf'); os.makedirs(OUT+'/ph',exist_ok=True)
UA={'User-Agent':'Mozilla/5.0'}; NOW=2027
def norm(n):
    n=unicodedata.normalize('NFKD',html.unescape(n)).encode('ascii','ignore').decode().lower()
    n=re.sub(r'\b(dr|prof|professor|mr|ms|mrs|shri|smt|sir|justice|lord|dame)\b','',n)
    return re.sub(r'\s+',' ',re.sub(r'[^a-z ]',' ',n)).strip()
def titles(fn): 
    s=open(f'{RAW}/{fn}',encoding='utf8',errors='ignore').read()
    out=[html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',t))).strip() for t in re.findall(r'<h3 class="elementor-image-box-title">(.*?)</h3>',s,re.S)]
    if not out:  # some years link each name to its profile page instead
        seen=set()
        for sl,t in re.findall(r'<a[^>]+href=["\']https://hydlitfest.org/speaker/([a-z0-9-]+)/?["\'][^>]*>(.*?)</a>',s,re.S):
            t=html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',t))).strip()
            if t and sl not in seen and sl not in ('moderators','mmb-authors'): seen.add(sl); out.append(t)
    return out
def get(u,b=False):
    for _ in range(3):
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40).read(); return r if b else r.decode('utf8','ignore')
        except Exception: time.sleep(2)
def short(t,n=220):
    if len(t)<=n: return t
    return t[:n].rsplit(' ',1)[0]+'…'
def gender(b):
    f=len(re.findall(r"\b(she|her|hers|herself)\b",b,re.I)); m=len(re.findall(r"\b(he|his|him|himself)\b",b,re.I))
    if f>=1 and f>=2*m: return 'f'
    if m>=1 and m>=2*f: return 'm'
    return 'u'
RULES=[(r'\b(nobel|booker prize|pulitzer)\b','Prize-winning author'),(r'\b(ambassador|diplomat)\b','Diplomat'),(r'\b(politician|member of parliament|mla|minister)\b','Politician'),
 (r'\b(ias officer|ips officer|civil servant|bureaucrat)\b','Civil servant'),(r'\b(film director|filmmaker|screenwriter|lyricist)\b','Filmmaker'),(r'\b(actor|actress)\b','Actor'),(r'\b(economist)\b','Economist'),
 (r'\b(publisher|literary agent|editor-in-chief|editorial director)\b','Publishing professional'),(r'\b(translator)\b','Translator'),(r'\b(singer|musician|composer|vocalist)\b','Musician'),
 (r'\b(scientist|physicist|astrophysicist|neuroscientist|biologist|doctor|physician|surgeon|ecologist|climate)\b','Scientist or doctor'),(r'\b(historian)\b','Historian'),
 (r'\b(professor|scholar|academic|lecturer)\b','Scholar'),(r'\b(journalist|correspondent|columnist|reporter|broadcaster)\b','Journalist'),(r'\b(poet)\b','Poet'),(r'\b(playwright|dramatist)\b','Playwright'),
 (r'\b(illustrator|cartoonist|artist|dancer)\b','Artist or illustrator'),(r'\b(entrepreneur|investor|ceo)\b','Entrepreneur'),(r'\b(novelist|author|writer|memoirist|essayist|biographer)\b','Author')]
def role(b):
    l=b.lower()
    for rx,lab in RULES:
        if re.search(rx,l): return lab
    return 'Speaker'
CTRY=[('India',r'\b(india|indian|hyderabad|telangana|delhi|mumbai|bengaluru|bangalore|kolkata|chennai|pune|kerala|lucknow|punjab|gujarat|bihar|assam|kashmir|odisha|andhra)\b'),
 ('United Kingdom',r'\b(british|uk|united kingdom|england|english|scottish|scotland|welsh|wales|london|oxford|cambridge|britain)\b'),('United States',r'\b(american|united states|u\.s\.|usa|new york|california|boston|harvard|yale|princeton|texas|chicago)\b'),
 ('Pakistan',r'\b(pakistan|pakistani|lahore|karachi)\b'),('Bangladesh',r'\b(bangladesh|bangladeshi|dhaka)\b'),('Sri Lanka',r'\b(sri lanka|sri lankan|colombo)\b'),('Nepal',r'\b(nepal|nepali|kathmandu)\b'),
 ('Canada',r'\b(canada|canadian|toronto)\b'),('Australia',r'\b(australia|australian|sydney|melbourne)\b'),('France',r'\b(french|france|paris)\b'),('Germany',r'\b(german|germany|berlin)\b'),
 ('Ireland',r'\b(irish|ireland)\b'),('Italy',r'\b(italian|italy)\b'),('Japan',r'\b(japanese|japan)\b'),('China',r'\b(chinese|china)\b'),('Israel',r'\b(israeli|israel)\b'),('Netherlands',r'\b(dutch|netherlands)\b'),
 ('Sweden',r'\b(swedish|sweden)\b'),('Spain',r'\b(spanish|spain)\b'),('Russia',r'\b(russian|russia)\b'),('Turkey',r'\b(turkish|turkey)\b'),('New Zealand',r'\b(new zealand)\b'),('Afghanistan',r'\b(afghan|afghanistan)\b')]
CITY=[('Delhi / NCR',r'\b(delhi|gurugram|gurgaon|noida)\b'),('Mumbai',r'\bmumbai\b'),('Bengaluru',r'\b(bengaluru|bangalore)\b'),('Kolkata',r'\b(kolkata|calcutta)\b'),('Chennai',r'\bchennai\b'),('Hyderabad',r'\b(hyderabad|secunderabad)\b'),('Pune',r'\bpune\b')]
def country(b):
    l=b.lower(); hits=[(re.search(rx,l).start(),c) for c,rx in CTRY if re.search(rx,l)]
    return (sorted(hits)[0][1],'named in bio') if hits else ('Unknown','')
# history
hist={2026:titles('speakers-2026.html'),2025:titles('speakers-2025.html'),2024:titles('speakers-2024.html'),2023:titles('speakers-2023.html'),
 2022:titles('anuvaad-speakers-2022.html')+titles('kaavya-dhaara-speakers-2022.html'),2021:titles('speakers-2021.html')}
hist={y:[t for t in v if t and t.lower() not in ('speaker','moderators','mmb authors','speakers')] for y,v in hist.items()}
byyear={y:{norm(n):n for n in v if norm(n)} for y,v in hist.items()}
# 2027 line-up
people=[]
for fn,kind in (('speakers.html','speaker'),('moderators.html','moderators')):
    s=open(f'{RAW}/{fn}',encoding='utf8',errors='ignore').read(); seen={}
    for sl,t in re.findall(r'<a[^>]+href=["\']https://hydlitfest.org/'+kind+r'/([a-z0-9-]+)/?["\'][^>]*>(.*?)</a>',s,re.S):
        t=html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',t))).strip()
        if sl in ('moderators','mmb-authors'): continue
        if t and sl not in seen: seen[sl]=t
    for sl,t in seen.items(): people.append({'slug':sl,'name':t,'kind':kind})
dd={}
for p in people: dd.setdefault(norm(p['name']),p)
people=list(dd.values())
byyear[NOW]={norm(p['name']):p['name'] for p in people}
def work(p):
    h=get(f"https://hydlitfest.org/{p['kind']}/{p['slug']}/") or ''
    t=re.sub(r'<script.*?</script>|<style.*?</style>','',h,flags=re.S); t=html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',t)))
    a=t.find('Profile Home > '); bio=''
    if a>=0:
        seg=t[a:]; seg=seg[:seg.find('Get Involved')] if 'Get Involved' in seg else seg
        k=seg.find(p['name']); seg=seg[k+len(p['name']):].strip() if k>=0 else seg
        m=re.search(r'(?<=[.!?”’\)]) [A-Z][^.]{2,40}? (?:Speaker|Moderator)(?= |$)',seg); bio=(seg[:m.start()] if m else seg).strip()
    og=re.search(r'<meta property="og:image" content="([^"]+)"',h); ph=''
    if og:
        fn=f"{OUT}/ph/{p['slug']}.jpg"
        if not os.path.exists(fn):
            raw=get(og.group(1),True)
            try:
                im=Image.open(io.BytesIO(raw)).convert('RGB'); w,hh=im.size
                if w>373: im=im.resize((373,round(hh*373/w)),Image.LANCZOS)
                im.save(fn,'JPEG',quality=82,optimize=True)
            except Exception: fn=None
        if fn: ph=f"ph/{p['slug']}.jpg"
    time.sleep(.2); return dict(p,bio=bio,ph=ph)
with cf.ThreadPoolExecutor(3) as ex: info=list(ex.map(work,people))
yrs={}
for y,m in byyear.items():
    for k in m: yrs.setdefault(k,[]).append(y)
S=[]
for p in info:
    k=norm(p['name']); ys=sorted(yrs[k]); past=[y for y in ys if y<NOW]; full=p['bio']
    cc,cb=country(full) if full else ('Unknown','')
    city=next((c for c,rx in CITY if full and re.search(rx,full.lower())),'')
    r='Moderator' if p['kind']=='moderators' and not full else (role(full) if full else 'Speaker')
    S.append({'n':p['name'],'b':short(full),'f':full,'y':ys,'pre':[],'first':0 if past else 1,'g':gender(full) if full else 'u','t':r if r!='Speaker' else 'Other voices',
      'p':0,'r':0,'a':'','l':'','s':[],'u':('speaker/' if p['kind']=='speaker' else 'moderators/')+p['slug'],'bk':[],'lg':[],'le':'','role':r,'nonauth':0 if r in('Author','Prize-winning author','Poet','Playwright') else 1,
      'cc':cc,'cb':cb,'dia':0,'city':city,'ph':p['ph']})
# picks = most frequent returning speakers
fr=sorted([o for o in S if sum(1 for y in o['y'] if y<NOW)>=3],key=lambda o:(-len(o['y']),o['n']))
for i,o in enumerate(fr,1): o['p']=1;o['r']=i
S.sort(key=lambda o:o['n'].lower())
json.dump(S,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
YEARS=sorted(byyear)
per={}
for y in YEARS:
    ks=set(byyear[y]); prior=set().union(*[set(byyear[z]) for z in YEARS if z<y]) if y>YEARS[0] else set()
    per[str(y)]={'total':len(ks),'returning':len(ks&prior),'inNow':len(ks&set(byyear[NOW]))}
name_of={k:v for y in YEARS for k,v in byyear[y].items()}
lead=sorted(yrs.items(),key=lambda kv:(-len(kv[1]),kv[0]))[:25]
json.dump({'per':per,'lead':[{'n':name_of[k],'y':v,'in26':NOW in v} for k,v in lead],'hist':dict(Counter(str(sum(1 for y in yrs[norm(o['n'])] if y<NOW)) for o in S))},open(OUT+'/stats.json','w'))
print(len(S),'people;',sum(o['first'] for o in S),'first-timers;',{y:per[str(y)]['total'] for y in YEARS},Counter(o['g'] for o in S),sum(1 for o in S if o['f']),'with bios',sum(1 for o in S if o['ph']),'photos')
