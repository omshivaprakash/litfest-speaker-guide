"""Build festivals/jlf/{data,stats}.json from the Jaipur Literature Festival public speakers API.
Usage: python3 tools/build_jlf.py RAWDIR   (RAWDIR holds y2018.json ... y2027.json from
  https://api.jaipurliteraturefestival.org/api/authorsPage?lang=en&limit=1000&year=YYYY&skip=0&search=)
Photos are downloaded from the same host, resized to 373px wide JPEG."""
import json,re,html,sys,os,unicodedata,io,time,urllib.request
from collections import Counter
RAW=sys.argv[1]; OUT=os.path.join(os.path.dirname(__file__),'..','festivals','jlf')
YEARS=list(range(2018,2028)); NOW=2027
def norm(n):
    n=unicodedata.normalize('NFKD',html.unescape(n)).encode('ascii','ignore').decode().lower()
    n=re.sub(r'\b(dr|prof|professor|mr|ms|mrs|shri|smt|sir|justice|lord|dame)\b','',n)
    return re.sub(r'\s+',' ',re.sub(r'[^a-z ]',' ',n)).strip()
def clean(h):
    t=re.sub(r'<[^>]+>',' ',h or ''); t=html.unescape(t).replace('\xa0',' ')
    return re.sub(r'\s+',' ',t).strip()
def short(t,n=220):
    if len(t)<=n: return t
    c=t[:n].rsplit(' ',1)[0]; return c+'…'
def gender(b):
    f=len(re.findall(r"\b(she|her|hers|herself)\b",b,re.I)); m=len(re.findall(r"\b(he|his|him|himself)\b",b,re.I))
    if f>=1 and f>=2*m: return 'f'
    if m>=1 and m>=2*f: return 'm'
    return 'u'
RULES=[(r'\b(nobel|booker prize|pulitzer)\b','Prize-winning author'),(r'\b(ambassador|diplomat|foreign secretary)\b','Diplomat'),
 (r'\b(politician|member of parliament|mla|minister|lok sabha|rajya sabha)\b','Politician'),(r'\b(ias officer|ips officer|civil servant|bureaucrat|election commissioner)\b','Civil servant'),
 (r'\b(film director|filmmaker|screenwriter|lyricist|film maker)\b','Filmmaker'),(r'\b(actor|actress)\b','Actor'),(r'\b(economist)\b','Economist'),
 (r'\b(publisher|literary agent|editor-in-chief|editorial director)\b','Publishing professional'),(r'\b(translator)\b','Translator'),
 (r'\b(singer|musician|composer|vocalist)\b','Musician'),(r'\b(scientist|physicist|astrophysicist|neuroscientist|biologist|doctor|physician|surgeon)\b','Scientist or doctor'),
 (r'\b(historian)\b','Historian'),(r'\b(professor|scholar|academic|lecturer)\b','Scholar'),(r'\b(journalist|correspondent|columnist|reporter|broadcaster)\b','Journalist'),
 (r'\b(poet)\b','Poet'),(r'\b(playwright|dramatist)\b','Playwright'),(r'\b(illustrator|cartoonist|artist)\b','Artist or illustrator'),
 (r'\b(entrepreneur|founder|investor|ceo)\b','Entrepreneur'),(r'\b(novelist|author|writer|memoirist|essayist|biographer)\b','Author')]
def role(b):
    l=b.lower()
    for rx,lab in RULES:
        if re.search(rx,l): return lab
    return 'Speaker'
CTRY=[('India',r'\b(india|indian|jaipur|rajasthan|delhi|mumbai|bengaluru|bangalore|kolkata|calcutta|chennai|hyderabad|pune|kerala|lucknow|ahmedabad|bhopal|punjab|gujarat|bihar|assam|kashmir)\b'),
 ('United Kingdom',r'\b(british|uk|united kingdom|england|english|scottish|scotland|welsh|wales|london|oxford|cambridge|britain)\b'),('United States',r'\b(american|united states|u\.s\.|usa|new york|california|washington|boston|harvard|yale|princeton|texas|chicago)\b'),
 ('Pakistan',r'\b(pakistan|pakistani|lahore|karachi|islamabad)\b'),('Bangladesh',r'\b(bangladesh|bangladeshi|dhaka)\b'),('Sri Lanka',r'\b(sri lanka|sri lankan|colombo)\b'),('Nepal',r'\b(nepal|nepali|nepalese|kathmandu)\b'),
 ('Canada',r'\b(canada|canadian|toronto|vancouver|montreal)\b'),('Australia',r'\b(australia|australian|sydney|melbourne)\b'),('France',r'\b(french|france|paris)\b'),('Germany',r'\b(german|germany|berlin)\b'),
 ('Poland',r'\b(polish|poland)\b'),('Israel',r'\b(israeli|israel)\b'),('Palestine',r'\b(palestinian|palestine)\b'),('Nigeria',r'\b(nigerian|nigeria)\b'),('Kenya',r'\b(kenyan|kenya)\b'),
 ('South Africa',r'\b(south african|south africa)\b'),('Egypt',r'\b(egyptian|egypt)\b'),('China',r'\b(chinese|china|beijing)\b'),('Japan',r'\b(japanese|japan|tokyo)\b'),('Russia',r'\b(russian|russia)\b'),
 ('Italy',r'\b(italian|italy)\b'),('Spain',r'\b(spanish|spain)\b'),('Ireland',r'\b(irish|ireland)\b'),('Turkey',r'\b(turkish|turkey)\b'),('Brazil',r'\b(brazilian|brazil)\b'),('Mexico',r'\b(mexican|mexico)\b'),
 ('United Arab Emirates',r'\b(emirati|uae|dubai|abu dhabi)\b'),('Netherlands',r'\b(dutch|netherlands)\b'),('Sweden',r'\b(swedish|sweden)\b'),('New Zealand',r'\b(new zealand)\b'),('Afghanistan',r'\b(afghan|afghanistan)\b')]
CITY=[('Jaipur / Rajasthan',r'\b(jaipur|rajasthan|udaipur|jodhpur)\b'),('Delhi / NCR',r'\b(delhi|gurugram|gurgaon|noida)\b'),('Mumbai',r'\bmumbai\b'),('Bengaluru',r'\b(bengaluru|bangalore)\b'),('Kolkata',r'\b(kolkata|calcutta)\b'),('Chennai',r'\bchennai\b'),('Hyderabad',r'\bhyderabad\b'),('Pune',r'\bpune\b')]
def country(b):
    l=b.lower()
    hits=[(re.search(rx,l).start(),c) for c,rx in CTRY if re.search(rx,l)]
    if not hits: return 'Unknown',''
    # first named place or nationality in the bio wins
    return sorted(hits)[0][1],'named in bio'
byyear={}
for y in YEARS:
    d=json.load(open(f'{RAW}/y{y}.json'))['authors']; seen={}
    for a in d:
        n=re.sub(r'\s+',' ',(a['first_name']+' '+(a.get('last_name') or '')).strip())
        k=norm(n)
        if k and k not in seen: seen[k]=dict(a,name=n)
    byyear[y]=seen
cur=byyear[NOW]
yrs={}
for y,m in byyear.items():
    for k in m: yrs.setdefault(k,[]).append(y)
S=[];pc=0
order=sorted(cur.values(),key=lambda a:a['created_at'])
for a in cur.values():
    k=norm(a['name']); full=clean(a['details']) or clean(a['bio']); ys=sorted(yrs[k]); past=[y for y in ys if y<NOW]
    cc,cb=country(full) if full else ('Unknown','')
    city=''
    for c,rx in CITY:
        if full and re.search(rx,full.lower()): city=c;break
    r=role(full) if full else 'Speaker'
    o={'n':a['name'],'b':short(full) if full else '','f':full,'y':ys,'pre':[],'first':0 if past else 1,'g':gender(full) if full else 'u','t':r if r!='Speaker' else 'Other voices',
       'p':1 if a['is_imp'] else 0,'r':0,'a':'','l':'','s':[],'u':a['slug'],'bk':[],'lg':[],'le':'','role':r,'nonauth':0 if r in('Author','Prize-winning author','Poet','Playwright') else 1,
       'cc':cc,'cb':cb,'dia':0,'city':city,'ph':'','_img':a.get('cover_image')}
    S.append(o)
S.sort(key=lambda o:o['n'].lower())
# ranks among picks, by announcement order
pk=[o for o in sorted(S,key=lambda o:[a['created_at'] for a in cur.values() if a['slug']==o['u']][0]) if o['p']]
for i,o in enumerate(pk,1): o['r']=i
# photos
os.makedirs(OUT+'/ph',exist_ok=True)
from PIL import Image
for o in S:
    img=o.pop('_img'); 
    if not img: continue
    sl=o['u'].replace('/','_'); fn=OUT+'/ph/'+sl+'.jpg'
    if not os.path.exists(fn):
        try:
            raw=urllib.request.urlopen(urllib.request.Request('https://api.jaipurliteraturefestival.org'+img,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read()
            im=Image.open(io.BytesIO(raw)).convert('RGB'); w,h=im.size
            if w>373: im=im.resize((373,round(h*373/w)),Image.LANCZOS)
            im.save(fn,'JPEG',quality=82,optimize=True); time.sleep(.15)
        except Exception as e: print('photo fail',o['u'],e); continue
    o['ph']='ph/'+sl+'.jpg'
json.dump(S,open(OUT+'/data.json','w'),ensure_ascii=False)
per={}
for y in YEARS:
    ks=set(byyear[y]); prior=set().union(*[set(byyear[z]) for z in YEARS if z<y]) if y>YEARS[0] else set()
    per[str(y)]={'total':len(ks),'returning':len(ks&prior),'inNow':len(ks&set(cur))}
lead=sorted(yrs.items(),key=lambda kv:(-len(kv[1]),kv[0]))[:25]
name_of={}
for y in YEARS:
    for k,a in byyear[y].items(): name_of[k]=a['name']
st={'per':per,'lead':[{'n':name_of[k],'y':v,'in26':NOW in v} for k,v in lead],
    'hist':dict(Counter(str(sum(1 for y in yrs[norm(o['n'])] if y<NOW)) for o in S))}
json.dump(st,open(OUT+'/stats.json','w'))
print(len(S),Counter(o['g'] for o in S),Counter(o['cc'] for o in S).most_common(8),sum(o['first'] for o in S),Counter(o['role'] for o in S).most_common(8))
