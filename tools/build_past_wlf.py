"""Build festivals/wlf/past.json from the archived-edition builds (festivals/wlf24, wlf22): everyone who spoke in 2022 or 2024 but not in 2026,
with bio, photo and years. Usage: python3 tools/build_past_wlf.py"""
import json,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from pastlib import *
P=Past('wlf')
for fid in ('wlf22','wlf24'):
    d=json.load(open(f'{R}/{fid}/data.json',encoding='utf8'))
    for o in d:
        ph=f'{R}/{fid}/{o["ph"]}' if o['ph'] else ''
        raw=open(ph,'rb').read() if ph and os.path.exists(ph) else None
        P.add(o['n'],o['y'],o['f'],raw,'Past speakers')
P.save()
