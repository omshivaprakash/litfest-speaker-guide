"""Combine every live festival's history.json into data/history-all.json so Search, Across and Explore load one small file.
Run after any build_*.py. Usage: python3 tools/build_index.py"""
import json,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from pastlib import unmoji
R=os.path.join(os.path.dirname(__file__),'..'); out={}; FJ=json.load(open(R+'/festivals.json',encoding='utf8'))
for f in json.load(open(R+'/festivals.json',encoding='utf8'))['festivals']:
    if f['status']!='live' or f.get('archive'): continue
    p=R+'/'+f['base']+'history.json'
    if os.path.exists(p): out[f['id']]={y:sorted(dict.fromkeys(unmoji(v)),key=str.lower) for y,v in json.load(open(p,encoding='utf8')).items()}   # safety net: repairs garbled characters in names
for f in FJ['festivals']:
    if os.path.exists(R+'/'+f['base']+'past.json'): f['past']=1
    else: f.pop('past',None)
json.dump(FJ,open(R+'/festivals.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
json.dump(out,open(R+'/data/history-all.json','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
print(len(out),'festivals,',os.path.getsize(R+'/data/history-all.json')//1024,'KB')
