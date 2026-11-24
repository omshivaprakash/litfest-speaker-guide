"""Stamp one build id into index.html (BUILD) and sw.js (VERSION) so browsers and installed copies refresh.
Run before committing a change to index.html, explore.js or data. Usage: python3 tools/stamp.py"""
import re,os,datetime,subprocess
R=os.path.join(os.path.dirname(__file__),'..')
try: g=subprocess.check_output(['git','rev-parse','--short','HEAD'],cwd=R,text=True).strip()
except Exception: g='x'
bid=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M')+g
p=R+'/index.html'; s=open(p,encoding='utf8').read(); s=re.sub(r"BUILD='[^']*'","BUILD='%s'"%bid,s,count=1); open(p,'w',encoding='utf8').write(s)
p=R+'/sw.js'; s=open(p).read(); s=re.sub(r"VERSION='[^']*'","VERSION='litfest-%s'"%bid,s,count=1); open(p,'w').write(s)
print('stamped',bid)
