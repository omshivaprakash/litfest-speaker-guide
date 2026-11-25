"""Remove past-speaker photos that are really a shared placeholder (the same image used for 4 or more people in one festival, e.g. a festival logo).
Safe to re-run. Usage: python3 tools/drop_placeholder_photos.py"""
import glob,hashlib,json,os,collections
R=os.path.join(os.path.dirname(__file__),'..','festivals')
for pj in glob.glob(R+'/*/past.json'):
    d=os.path.dirname(pj); L=json.load(open(pj,encoding='utf8')); H=collections.defaultdict(list)
    for o in L:
        if o.get('ph') and os.path.exists(d+'/'+o['ph']): H[hashlib.md5(open(d+'/'+o['ph'],'rb').read()).hexdigest()].append(o)
    bad={h for h,v in H.items() if len(v)>=4}; n=0
    for h in bad:
        for o in H[h]:
            try: os.remove(d+'/'+o['ph'])
            except OSError: pass
            o['ph']=''; n+=1
    if n: json.dump(L,open(pj,'w',encoding='utf8'),ensure_ascii=False)
    print(os.path.basename(d),n,'placeholder photos dropped in',len(bad),'distinct images')
