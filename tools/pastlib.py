"""Shared helpers for building festivals/<id>/past.json: profiles (bio, photo, years) of people who spoke in earlier editions but are not in
the current edition's data.json. Same record shape as data.json so the app can open the same profile sheet.
Usage in a builder: P=Past('nlf'); P.add(name, years, bio='', photo_bytes_or_None, extra...); P.save()"""
import os,re,io,json,html,unicodedata,time,urllib.request
from PIL import Image
R=os.path.join(os.path.dirname(__file__),'..','festivals'); UA={'User-Agent':'Mozilla/5.0'}
def get(u,b=False,t=60):
    for _ in range(3):
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t).read(); return r if b else r.decode('utf8','ignore')
        except Exception: time.sleep(2)
def clean(x): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',x or '').replace('\xa0',' '))).strip()
def norm(n):
    n=unicodedata.normalize('NFKD',html.unescape(n)).encode('ascii','ignore').decode().lower()
    n=re.sub(r'\b(dr|prof|professor|mr|ms|mrs|shri|smt|sir|adv|fr|rev|justice|hon|lord|dame)\b\.?',' ',n); n=re.sub(r'\b([a-z]) (?=[a-z]\b)',r'\1',re.sub(r'[^a-z ]',' ',n)); return re.sub(r'\s+',' ',n).strip()
def short(t,n=220): return t if len(t)<=n else t[:n].rsplit(' ',1)[0]+'…'
def gender(b):
    f=len(re.findall(r"\b(she|her|hers|herself)\b",b,re.I)); m=len(re.findall(r"\b(he|his|him|himself)\b",b,re.I))
    if f>=1 and f>=2*m: return 'f'
    if m>=1 and m>=2*f: return 'm'
    return 'u'
CTRY=[('India',r'\b(india|indian|kerala|bengaluru|bangalore|delhi|mumbai|kolkata|chennai|hyderabad|jaipur|pune|kochi|kozhikode|bhopal|odisha|goa|assam|karnataka|tamil nadu)\b'),('United Kingdom',r'\b(british|uk|united kingdom|england|london|scotland|welsh|wales|irish|ireland)\b'),
 ('United States',r'\b(american|united states|usa|new york|california)\b'),('Australia',r'\b(australia|australian)\b'),('Canada',r'\b(canada|canadian)\b'),('Germany',r'\b(german|germany)\b'),('France',r'\b(french|france)\b'),('Pakistan',r'\b(pakistan|pakistani)\b'),('Bangladesh',r'\b(bangladesh|bangladeshi)\b'),('Sri Lanka',r'\b(sri lanka|sri lankan)\b'),('Nepal',r'\b(nepal|nepali)\b')]
def country(b):
    l=b.lower(); h=[(re.search(rx,l).start(),c) for c,rx in CTRY if re.search(rx,l)]
    return (sorted(h)[0][1],'named in bio') if h else ('Unknown','')
ROLES=[('Journalist',r'journalis|editor|anchor|correspondent|columnist'),('Poet',r'\bpoet|poetry'),('Politician',r'\bmla\b|\bmp\b|minister|member of parliament'),('Diplomat',r'diplomat|ambassador'),('Filmmaker',r'film|cinema|director|actor|actress|screenwrit'),('Academic',r'professor|academic|scholar|university|historian|researcher'),('Artist',r'\bartist|painter|sculpt|musician|singer|dancer|theatre'),('Author',r'author|writer|novel|books?\b|story|stories|translator')]
def role(b):
    for r,rx in ROLES:
        if re.search(rx,b,re.I): return r
    return 'Speaker'
_MJ=re.compile(r'[\u00c2-\u00f4][\u0080-\u00bf\u0152\u0153\u0160\u0161\u0178\u017d\u017e\u0192\u02c6\u02dc\u2013\u2014\u2018-\u201e\u2020-\u2022\u2026\u2030\u2039\u203a\u20ac\u2122]{1,3}')
def _mj(m):
    def b(c):
        try: return c.encode('cp1252')
        except Exception: return c.encode('latin-1')
    try: return b''.join(b(c) for c in m.group(0)).decode('utf8')
    except Exception: return m.group(0)
def unmoji(x):
    """Repair text that was UTF-8 read as Windows-1252 ("\u00e2\u20ac\u2122" for the curly apostrophe) in any string inside x."""
    if isinstance(x,str): return _MJ.sub(_mj,x) if re.search(r'[\u00c2\u00c3\u00e2]',x) else x
    if isinstance(x,list): return [unmoji(v) for v in x]
    if isinstance(x,dict): return {k:unmoji(v) for k,v in x.items()}
    return x
def slug(n): return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',n).encode('ascii','ignore').decode().lower()).strip('-') or 'x'
class Past:
    def __init__(self,fid):
        self.fid=fid; self.dir=f'{R}/{fid}'; os.makedirs(self.dir+'/pph',exist_ok=True); self.rows={}
        cur=json.load(open(self.dir+'/data.json',encoding='utf8')); self.cur={norm(o['n']) for o in cur}
    def add(self,name,years,bio='',photo=None,t='Past speakers'):
        name=clean(name); k=norm(name)
        if not name or not k or k in self.cur: return
        r=self.rows.get(k)
        if r:
            r['y']=sorted(set(r['y'])|set(years))
            if len(bio)>len(r['f']): r['f']=bio; r['b']=short(bio)
            if photo and not r['ph']: r['ph']=self._save(r['u'],photo)
            return
        sl=slug(name); u=sl; i=2
        while any(x['u']==u for x in self.rows.values()): u=f'{sl}-{i}'; i+=1
        cc,cb=country(bio) if bio else ('Unknown',''); ro=role(bio) if bio else 'Speaker'
        self.rows[k]={'n':name,'b':short(bio),'f':bio,'y':sorted(set(years)),'pre':[],'first':0,'g':gender(bio) if bio else 'u','t':t,'p':0,'r':0,'a':'','l':'','s':[],'u':u,'bk':[],'lg':[],'le':'','role':ro,'nonauth':0 if ro in('Author','Poet') else 1,'cc':cc,'cb':cb,'dia':0,'city':'','ph':self._save(u,photo) if photo else '','past':1}
    def _save(self,u,raw):
        try:
            im=Image.open(io.BytesIO(raw)).convert('RGB'); w,h=im.size
            if w>280: im=im.resize((280,round(h*280/w)),Image.LANCZOS)
            im.save(f'{self.dir}/pph/{u}.webp','WEBP',quality=66,method=6); return f'pph/{u}.webp'
        except Exception: return ''
    def save(self):
        L=[unmoji(o) for o in sorted(self.rows.values(),key=lambda o:o['n'].lower())]; json.dump(L,open(self.dir+'/past.json','w',encoding='utf8'),ensure_ascii=False)
        print(self.fid,len(L),'past-only people;',sum(1 for o in L if o['ph']),'photos;',sum(1 for o in L if o['f']),'bios')
