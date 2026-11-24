"""Convert every JPEG photo and cover under festivals/ to WebP and rewrite the references in data.json, then delete the JPEGs.
Run after any build_*.py or add_books_ol.py (they write JPEGs). Safe to re-run. Usage: python3 tools/to_webp.py"""
import os,glob,json
from PIL import Image
R=os.path.join(os.path.dirname(__file__),'..'); n=0; saved=0
for f in glob.glob(R+'/festivals/*/**/*.jpg',recursive=True):
    w=f[:-4]+'.webp'
    try:
        im=Image.open(f).convert('RGB'); im.save(w,'WEBP',quality=78,method=6)
    except Exception as e: print('skip',f,e); continue
    saved+=os.path.getsize(f)-os.path.getsize(w); os.remove(f); n+=1
for d in glob.glob(R+'/festivals/*/data.json'):
    s=open(d,encoding='utf8').read(); t=s.replace('.jpg"','.webp"')
    if t!=s: open(d,'w',encoding='utf8').write(t)
print(n,'images converted,',round(saved/1e6,1),'MB saved')
