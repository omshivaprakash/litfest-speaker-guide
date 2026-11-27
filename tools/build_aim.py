"""Build festivals/aim for the Author In Me (AIM) Literary Festival, London.
The official site (aimlitfestival.com) is not reachable from our build environment, so this lists only people NAMED in public coverage:
 iGlobal (2023, 2024, 2025 pieces), Round and About (2024), The Bookseller (2023), Nehru Centre London (2022 listing).
2024 is the edition shown as the current roster; 2022 and 2023 are in the history. The 2025 edition (1-5 Oct, StoryGarden at the British Library, theme
'Challenge Your Choices') has no full line-up in any source we could read, so it is described in the note and not in the roster.
Usage: python3 tools/build_aim.py"""
import json,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from pastlib import norm,short,slug,R
OUT=R+'/aim'; os.makedirs(OUT,exist_ok=True); NOW=2024
# name -> (year list, role, one-line description taken from the cited coverage, source)
P={
 'Dr Anamik Saha':([2022],'Academic','Speaker at the 2022 Diversity in Publishing day.','Nehru Centre London'),
 'Kishori Jani':([2022],'Speaker','Speaker at the 2022 Diversity in Publishing day.','Nehru Centre London'),
 'Julia Alden':([2022],'Publisher','Speaker at the 2022 Diversity in Publishing day.','Nehru Centre London'),
 'Isabel Knight':([2022],'Speaker','Speaker at the 2022 Diversity in Publishing day.','Nehru Centre London'),
 'Simon Alexander Ong':([2022],'Speaker','Speaker at the 2022 Diversity in Publishing day.','Nehru Centre London'),
 'Shrabani Basu':([2023],'Author','Author; named among the 2023 line-up.','iGlobal; The Bookseller'),
 'Kavitha Rao':([2023],'Author','Author; named among the 2023 line-up.','iGlobal'),
 'Sarah Mussi':([2023],'Author','Author; named among the 2023 line-up.','iGlobal'),
 'Joseph Coelho':([2023],'Poet','Poet and children’s author; named among the 2023 line-up.','iGlobal; The Bookseller'),
 'Rani Singh':([2023],'Speaker','Literary figure named among the 2023 line-up.','iGlobal'),
 'Sudha Bhuchar':([2023],'Speaker','Literary figure named among the 2023 line-up.','iGlobal'),
 'Lord Meghnad Desai':([2023],'Economist','Padma Bhushan recipient; distinguished guest in 2023.','iGlobal'),
 'Dr M N Nandakumar':([2023],'Scholar','Sanskrit scholar; distinguished guest in 2023.','iGlobal'),
 'Alice Hemming':([2023],'Author','Bestselling author; ran a 2023 workshop.','iGlobal'),
 'Kate Poels':([2023],'Author','Children’s author; ran a 2023 workshop.','iGlobal'),
 'Kelly Weekes':([2023],'Marketer','Marketing mentor; ran a 2023 workshop.','iGlobal'),
 'Aanya Arora':([2023],'Author','Teen author in the 2023 Young Voices segment.','iGlobal'),
 'Deeva Karnani Shah':([2023],'Author','Teen author in the 2023 Young Voices segment.','iGlobal'),
 'Verushka Anand':([2023],'Author','Teen author in the 2023 Young Voices segment.','iGlobal'),
 'Suhana Joshi':([2023],'Author','Teen author in the 2023 Young Voices segment.','iGlobal'),
 'Alan Durant':([2023,2024],'Author','Children’s author; at the 2023 festival and ran The Quill Soup Adventure at the 2024 Young Voices day.','The Bookseller; Round and About'),
 'Lady Kishwar Desai':([2024],'Author','Author and founder of the Arts and Cultural Heritage Trust (the Partition Museum projects in Amritsar and Delhi); 2024 keynote speaker.','iGlobal'),
 'Ekta Bajaj':([2023,2024],'Author','Author and co-founder and co-curator of the festival; on the 2024 ‘Diverse Voices’ panel.','iGlobal'),
 'Monica Sood':([2023,2024],'Publisher','Co-founder and curator of the festival.','iGlobal'),
 'Anila Dhami':([2024],'Broadcaster','Award-winning TV presenter and festival advisory board member; moderated the 2024 panels.','iGlobal; Round and About'),
 'Noel Murphy':([2024],'Publisher','Commercial director of Granta Publishing; 2024 Q&A.','iGlobal'),
 'Bhavya Arora':([2024],'Author','Life coach and debut author (Where the F**k Do I Go From Here), launched in 2024.','iGlobal'),
 'Stephen C. Lawley':([2024],'Author','Debut author (The Catalyst), launched in 2024.','iGlobal'),
 'Priyanka Pandya':([2024],'Author','Debut author; launched her picture book When Mummy Had Cancer at the 2024 opening.','iGlobal'),
 'Ashanti Omkar':([2024],'Journalist','Film journalist; in conversation on books adapted for screen, 2024.','iGlobal'),
 'Sonia Bahl':([2024],'Author','Author; in conversation on books adapted for screen, 2024.','iGlobal'),
 'Debasmita Dasgupta':([2024],'Author','Led a graphic-stories workshop at the 2024 Young Voices day.','Round and About'),
 'Divya Thomas':([2024],'Author','Led ‘Celebrating You: Beyond the Colour of My Skin’ at the 2024 Young Voices day.','Round and About'),
}
HY={}
for n,(ys,*_) in P.items():
    for y in ys: HY.setdefault(str(y),[]).append(n)
S=[]
for n,(ys,ro,d,src) in P.items():
    if NOW not in ys: continue
    ys2=sorted(ys); f=d+' (Source: '+src+'.)'
    S.append({'n':n,'b':short(f),'f':f,'y':ys2,'pre':[y for y in ys2 if y!=NOW],'first':1 if len(ys2)==1 else 0,'g':'u','t':'Speakers','p':0,'r':0,'a':'','l':'','s':[],'u':slug(n),'bk':[],'lg':[],'le':'','role':ro,'nonauth':0 if ro in('Author','Poet') else 1,'cc':'United Kingdom','cb':'London festival','dia':0,'city':'London','ph':''})
S.sort(key=lambda o:o['n'].lower())
json.dump(S,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
hist={y:sorted(v,key=str.lower) for y,v in sorted(HY.items())}
json.dump(hist,open(OUT+'/history.json','w',encoding='utf8'),ensure_ascii=False)
per={}
for y,v in hist.items():
    ks={norm(n) for n in v}; earlier={norm(n) for yy,vv in hist.items() if yy<y for n in vv}; per[y]={'total':len(v),'returning':len(ks&earlier),'inNow':len(ks&{norm(o['n']) for o in S})}
lead=[{'n':o['n'],'y':o['y'],'in26':True} for o in S if len(o['y'])>1]
json.dump({'per':per,'lead':lead,'hist':{str(k):sum(1 for o in S if len(o['y'])==k) for k in sorted({len(o['y']) for o in S})}},open(OUT+'/stats.json','w'))
print(len(S),'speakers in',NOW,';',{y:len(v) for y,v in hist.items()})
