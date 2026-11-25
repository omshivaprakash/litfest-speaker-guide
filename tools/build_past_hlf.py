"""Build festivals/hlf/past.json: Hyderabad speakers of 2021-2026 who are not in the 2027 list. Year pages give name + photo (image boxes);
the 2026 page also links profile pages (bio, photo). Usage: python3 tools/build_past_hlf.py"""
import json,os,re,sys,concurrent.futures as cf
sys.path.insert(0,os.path.dirname(__file__))
from pastlib import *
PAGES={2026:['speakers-2026'],2025:['speakers-2025'],2024:['speakers-2024'],2023:['speakers-2023'],2022:['anuvaad-speakers-2022','kaavya-dhaara-speakers-2022'],2021:['speakers-2021']}
P=Past('hlf'); recs={}
SKIP=('speaker','moderators','mmb authors','speakers','')
for y,ps in PAGES.items():
    for pg in ps:
        h=get(f'https://hydlitfest.org/{pg}/') or ''
        for blk in h.split('elementor-image-box-wrapper')[1:]:
            t=re.search(r'<h3 class="elementor-image-box-title">(.*?)</h3>',blk,re.S); im=re.search(r'<img[^>]+src="([^"]+)"',blk)
            if not t: continue
            n=clean(t.group(1))
            if n.lower() in SKIP or norm(n) in P.cur or not norm(n): continue
            r=recs.setdefault(norm(n),{'n':n,'y':set(),'img':None,'slug':None}); r['y'].add(y)
            if im and not r['img'] and 'wp-content' in im.group(1): r['img']=im.group(1)
        if y==2026:
            for sl,t in re.findall(r'<a[^>]+href=["\']https://hydlitfest.org/(?:speaker|moderators)/([a-z0-9-]+)/?["\'][^>]*>(.*?)</a>',h,re.S):
                n=clean(t)
                if sl in('moderators','mmb-authors') or not n or norm(n) in P.cur: continue
                r=recs.setdefault(norm(n),{'n':n,'y':set(),'img':None,'slug':None}); r['y'].add(2026); r['slug']=r['slug'] or sl
    print(y,len(recs),flush=True)
def one(r):
    bio='';raw=None
    if r['slug']:
        h=get(f"https://hydlitfest.org/speaker/{r['slug']}/") or ''
        t=re.sub(r'<script.*?</script>|<style.*?</style>','',h,flags=re.S); t=clean(t); a=t.find('Profile Home > ')
        if a>=0:
            seg=t[a:]; seg=seg[:seg.find('Get Involved')] if 'Get Involved' in seg else seg
            k=seg.find(r['n']); seg=seg[k+len(r['n']):].strip() if k>=0 else seg
            m=re.search(r'(?<=[.!?”’\)]) [A-Z][^.]{2,40}? (?:Speaker|Moderator)(?= |$)',seg); bio=(seg[:m.start()] if m else seg).strip()
        og=re.search(r'<meta property="og:image" content="([^"]+)"',h)
        if og: raw=get(og.group(1),True,30)
    if raw is None and r['img']: raw=get(r['img'],True,30)
    return bio,raw
items=list(recs.values())
with cf.ThreadPoolExecutor(6) as ex: res=list(ex.map(one,items))
for r,(bio,raw) in zip(items,res):
    P.add(r['n'],sorted(r['y']),bio[:1800],raw,'Past speakers')
    if r['slug'] and norm(r['n']) in P.rows: P.rows[norm(r['n'])]['url']=f"https://hydlitfest.org/speaker/{r['slug']}/"
P.save()
