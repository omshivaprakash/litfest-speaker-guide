"""Build festivals/hayww/data.json (programme type) for Hay Festival Winter Weekend from the festival's public programme pages
(www.hayfestival.com/m-245-winter-weekend-2026.aspx, paged with pagenum). Venues become the forums, event formats the themes.
Usage: python3 tools/build_hayww.py"""
import re,json,os,html,time,urllib.request,datetime
OUT=os.path.join(os.path.dirname(__file__),'..','festivals','hayww'); os.makedirs(OUT,exist_ok=True)
URL='https://www.hayfestival.com/m-245-winter-weekend-2026.aspx?skinid=11&currencysetting=GBP&localesetting=en-GB&resetfilters=true&gridview=true&pagenum=%d'
def get(u):
    for _ in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=60).read().decode('utf8','ignore')
        except Exception: time.sleep(2)
    return ''
def clean(x): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',x or '').replace('\xa0',' '))).strip()
ev={}; p=1
while p<=12:
    h=get(URL%p); got=0
    for m in re.finditer(r'<div class="modal fade" id="modal(\d+)"(.*?)<div class="modal-footer">',h,re.S):
        pid,b=m.group(1),m.group(2); t=re.search(r'<h2 class="event">(.*?)(?:<a |</h2>)',b,re.S); 
        if not t: continue
        sub=re.search(r'<h3 class="subtitle">(.*?)</h3>',b,re.S); tm=re.search(r'<time datetime="([^"]+)">',b); ve=re.search(r'<span class="venue">(.*?)</span>',b,re.S)
        tt=re.search(r'<time[^>]*>(.*?)</time>',b,re.S); body=b.split('</h5>',1)[1] if '</h5>' in b else ''
        if pid in ev or not tm: continue
        got+=1; ev[pid]={'title':clean(t.group(1)),'sub':clean(sub.group(1)) if sub else '','dt':tm.group(1),'time':clean(tt.group(1)) if tt else '','venue':clean(ve.group(1)) if ve else '','desc':clean(body)[:400]}
    fmt=dict((i,clean(f)) for i,f in re.findall(r'id="ProductPic(\d+)".*?<span class="format[^"]*">',h,re.S)) if False else {}
    for pid,f in re.findall(r'<span class="format format-\d+">(.*?)</span><a href="javascript:void\(0\);" onclick="\$\(\'#modal(\d+)\'',h): 
        if f in ev: ev[f]['format']=clean(pid)
    print('page',p,got,len(ev),flush=True)
    if not got: break
    p+=1
def t12(dt):
    d=datetime.datetime.strptime(dt,'%Y-%m-%d %H:%M'); h=d.hour%12 or 12; return f'{h}:{d.minute:02d}'
NAME=re.compile(r"^[A-Z][A-Za-z'’\.\-]+(?: (?:de|van|von|of|the|le|la|bin|al|mc|Mc|[A-Z][A-Za-z'’\.\-]+)){1,4}$")
def people(h):
    """Names in a headline such as "A talks to B" or "A, B and C"; first group are speakers, the person after 'talks to' moderates."""
    s=re.sub(r'\b(MP|MBE|OBE|CBE|KC|Dr|Professor|Prof|Lord|Baroness|Sir|Dame|Rev)\b\.?','',h).strip(); s=re.sub(r'\s+',' ',s)
    m=re.match(r'^(.+?)\s+(?:talks? to|in conversation with|chats to|speaks to|in discussion with)\s+(.+)$',s)
    parts=[('p',x) for x in re.split(r'\s*(?:,| and | & | with )\s*',m.group(1))]+[('c',x) for x in re.split(r'\s*(?:,| and | & | with )\s*',m.group(2))] if m else [('p',x) for x in re.split(r'\s*(?:,| and | & | with )\s*',s)]
    parts=[(r,n.strip()) for r,n in parts if n.strip()]
    return parts if parts and all(NAME.match(n) for r,n in parts) else []
L=sorted(ev.values(),key=lambda e:(e['dt'],e['title']))
venues=[]; 
for e in L:
    if e['venue'] and e['venue'] not in venues: venues.append(e['venue'])
days=sorted({int(e['dt'][8:10]) for e in L}); wd=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
sess=[]
for e in L:
    d=datetime.datetime.strptime(e['dt'],'%Y-%m-%d %H:%M'); end=re.search(r'–\s*(\d{1,2})(?:\.(\d{2}))?\s*([ap]m)',e['time'])
    ts=t12(e['dt'])+('–'+f"{int(end.group(1))}:{int(end.group(2) or 0):02d}" if end else '')
    fm=e.get('format') or 'Event'; pp=people(e['title']) if (fm in ('Conversation','Talk','Panel','Workshop') or re.search(r' talks? to ',e['title'])) else []
    if not pp and e['sub'] and fm in ('Conversation','Talk','Panel') and ' talk' in e['sub']: pp=people(e['sub'])
    k=(e['sub'] or e['title']) if (pp and people(e['title'])) else e['title']; en=e['title'] if (pp and e['sub'] and people(e['title'])) else (e['sub'] if e['sub'] and e['sub']!=e['title'] else k)
    sess.append({'d':d.day,'f':venues.index(e['venue'])+1 if e['venue'] in venues else 0,'t':ts,'k':k,'e':en,'th':fm,'pp':[list(x) for x in pp]})
data={'sessions':sess,'en':{},'forums':[{'id':i+1,'k':v,'e':v} for i,v in enumerate(venues)],'days':[{'d':d,'l':wd[datetime.date(2026,11,d).weekday()]+f' {d} Nov'} for d in days],'forumLabel':'venue','themeLabel':'format'}
json.dump(data,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
print(len(sess),'events;',len(venues),'venues;',days,';',sum(len(s['pp']) for s in sess),'named people slots')
