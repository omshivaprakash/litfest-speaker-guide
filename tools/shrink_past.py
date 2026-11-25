"""Re-encode festivals/*/pph/*.webp to at most 280px wide at quality 66 (past-speaker photos are only shown small). Safe to re-run."""
import glob,os
from PIL import Image
R=os.path.join(os.path.dirname(__file__),'..','festivals'); a=b=0
for f in glob.glob(R+'/*/pph/*.webp'):
    im=Image.open(f).convert('RGB'); s0=os.path.getsize(f)
    if im.width<=280 and s0<9000: continue
    if im.width>280: im=im.resize((280,round(im.height*280/im.width)),Image.LANCZOS)
    im.save(f,'WEBP',quality=66,method=6); a+=s0; b+=os.path.getsize(f)
print(round(a/1e6,1),'MB ->',round(b/1e6,1),'MB')
