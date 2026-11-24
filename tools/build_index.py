"""Combine every live festival's history.json into data/history-all.json so Search, Across and Explore load one small file.
Run after any build_*.py. Usage: python3 tools/build_index.py"""
import json,os
R=os.path.join(os.path.dirname(__file__),'..'); out={}
for f in json.load(open(R+'/festivals.json',encoding='utf8'))['festivals']:
    if f['status']!='live': continue
    p=R+'/'+f['base']+'history.json'
    if os.path.exists(p): out[f['id']]=json.load(open(p,encoding='utf8'))
json.dump(out,open(R+'/data/history-all.json','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
print(len(out),'festivals,',os.path.getsize(R+'/data/history-all.json')//1024,'KB')
