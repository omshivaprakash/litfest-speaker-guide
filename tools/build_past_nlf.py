"""Build festivals/nlf/past.json: Neev speakers of 2017-2025 who are not in the 2026 list, from the festival's WordPress API (bio, photo, years).
Usage: python3 tools/build_past_nlf.py"""
import json,os,sys,concurrent.futures as cf
sys.path.insert(0,os.path.dirname(__file__))
from pastlib import *
API='https://www.neevliteraturefestival.org/wp-json/wp/v2/'
terms={t['id']:int(t['name']) for t in json.loads(get(API+'event_year?per_page=100&_fields=id,name'))}
posts=[];p=1
while True:
    d=json.loads(get(f'{API}speaker?per_page=100&page={p}&_fields=id,slug,title,content,featured_media,event_year') or '[]')
    if not d: break
    posts+=d;p+=1
    if len(d)<100: break
P=Past('nlf'); todo=[o for o in posts if clean(o['title']['rendered']) and norm(clean(o['title']['rendered'])) not in P.cur]
def media(o):
    if not o.get('featured_media'): return None
    try:
        m=json.loads(get(f"{API}media/{o['featured_media']}?_fields=source_url,media_details")); sz=(m.get('media_details') or {}).get('sizes',{})
        u=(sz.get('medium_large') or sz.get('large') or sz.get('medium') or {}).get('source_url') or m['source_url']; return get(u,True)
    except Exception: return None
with cf.ThreadPoolExecutor(6) as ex: raws=list(ex.map(media,todo))
for o,raw in zip(todo,raws): P.add(clean(o['title']['rendered']),[terms[t] for t in o['event_year'] if t in terms],clean(o['content']['rendered'])[:1500],raw,'Past speakers')
P.save()
