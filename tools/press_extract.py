"""Step 1 of the press study: list the news links found on each festival's saved press / media / news pages.
Reads a private raw-pages folder (the one built for the internal bundle: raw/<festival>/*.html.gz), writes press_links.csv next to it.
Only links to other sites are kept. Usage: python3 tools/press_extract.py <bundle_dir>"""
import gzip,glob,re,os,sys,csv,html,urllib.parse,collections
B=sys.argv[1]; OUT=B+'/press_links.csv'
SOCIAL=re.compile(r'facebook|twitter|instagram|youtube|youtu\.be|linkedin|^x\.com|whatsapp|wa\.me|threads\.net|tiktok|dribbble|goo\.gl|google\.com/maps|maps\.app|drive\.google|docs\.google|bit\.ly|wikipedia|amazon\.|flipkart|bookmyshow|paytm|razorpay|eventbrite|mailto|tel:',re.I)
PAGE=re.compile(r'press|media|news|coverage|report|clip|dispatch|blog',re.I)
rows=[]; seen=set()
def clean(x): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',x or '').replace('\xa0',' '))).strip()
for f in sorted(glob.glob(B+'/raw/*/*.html.gz')):
    fid=f.split('/')[-2]; name=os.path.basename(f)[:-8]
    if not PAGE.search(name): continue
    h=gzip.open(f,'rt',encoding='utf8',errors='ignore').read(); src=h.split('\n',1)[0].replace('<!--','').replace('-->','').strip(); own=urllib.parse.urlparse(src).netloc.replace('www.','')
    for m in re.finditer(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',h,re.S):
        u=html.unescape(m.group(1)).strip(); t=clean(m.group(2))
        if not u.startswith('http') or SOCIAL.search(u): continue
        dom=urllib.parse.urlparse(u).netloc.lower().replace('www.','')
        if not dom or dom==own or own.split('.')[0] in dom.split('.')[:2]: continue
        if re.search(r'\.(jpg|jpeg|png|gif|webp|pdf|zip|svg)(\?|$)',u,re.I): continue
        if u in seen: continue
        seen.add(u); yr=re.search(r'(20[12]\d)',u+' '+t+' '+name); rows.append([fid,name,yr.group(1) if yr else '',dom,t[:200],u])
with open(OUT,'w',newline='',encoding='utf-8-sig') as fh:
    w=csv.writer(fh); w.writerow(['festival_id','from_page','year_hint','outlet_domain','link_text','url']); w.writerows(rows)
c=collections.Counter(r[0] for r in rows); d=collections.Counter(r[3] for r in rows)
print(len(rows),'links;',dict(c)); print(d.most_common(40))
