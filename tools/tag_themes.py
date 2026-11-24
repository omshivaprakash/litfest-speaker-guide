"""Tag each programme session with a theme ('th') from its English gloss. Re-run after editing data.json."""
import json,os,re
ROOT=os.path.join(os.path.dirname(__file__),'..','festivals')
RULES=[('Ceremony & performance',r'inaugur|closing|ceremony|cultural programme|book fair|epic performed|singing|talamaddale|singers'),
 ('Technology & AI',r'\bAI\b|artificial'),
 ('Politics & society',r'democracy|politic|nationalism|communal|fascis|social justice|inequality|econom|livelihood|gen z|pro-kannada|ideolog|environment|western ghats|digital politics|conversation with multilingual|special guest'),
 ('Arts, theatre & music',r'dance|stage|theatre|painting|music|film|yakshagana'),
 ('Language, editing & knowledge',r'language|script|grammar|lexicon|manuscript|editing|edited|prosody|translat|knowledge|medical|magazine|research|inscription|folk|prehistoric|literary history'),
 ('Literature & criticism',r'.')]
for fid in ('sjm','jn'):
    p=os.path.join(ROOT,fid,'data.json'); d=json.load(open(p,encoding='utf8')); c={}
    for s in d['sessions']:
        for th,rx in RULES:
            if re.search(rx,s['e'],re.I): s['th']=th; break
        c[s['th']]=c.get(s['th'],0)+1
    json.dump(d,open(p,'w',encoding='utf8'),ensure_ascii=False); print(fid,c)
