"""Build festivals/jsw/data.json (programme type) for JSW Sahitya Habba 2026 (1st edition, 28-29 Nov 2026, Toranagallu) from the festival's
agenda PDF (Canva, 8 pages), transcribed by hand; speaker photos are cropped from page 1 of the PDF.
Usage: pdftoppm -r 70 -f 1 -l 1 -png agenda.pdf pg ; python3 tools/build_jsw.py pg-1.png"""
import sys,json,os
from PIL import Image
OUT=os.path.join(os.path.dirname(__file__),'..','festivals','jsw'); os.makedirs(OUT+'/ph',exist_ok=True)
S=1.28  # coordinates below are from a 1414px-wide view of the 1809px page
ROWS=[(745,960,[(113,340),(350,577),(587,813),(823,1050),(1065,1297)],['Amaresh Nugadoni','Vasudhendra','T. M. Krishna','P. Sheshadri','Ranjani Raghavan']),
 (1015,1197,[(118,300),(311,498),(508,695),(705,892),(903,1090),(1100,1290)],['Chaithanya Pingali','Sri Ramachandra Hadapad','Sumathi Krishnamurthy','M. R. Dattathri','Mallikarjuna Kadakola','Vasundhara Bhupathi']),
 (1250,1402,[(113,274),(285,448),(456,618),(626,788),(797,958),(967,1130),(1138,1300)],['Mallaiah Sandur','Venkatagiri Dalavayi','Manu Baligar','Chidananda Sali','Sampige Nagaraj','Halemane Rajashekar','H. S. Satyanarayana']),
 (1455,1612,[(113,275),(283,446),(453,615),(623,787),(793,957),(963,1127),(1140,1300)],['Sridhar Banavasi','Rashmi S','Srisaila Nagarala','Padmini Nagaraj','Mudiraj Banada','Avineni Bhaskar','Praveen Kumar G']),
 (1662,1812,[(520,683),(697,860)],['Seema Karanth','Chandrakeerti'])]
ROLE={'Ranjani Raghavan':'Indian actress and writer','P. Sheshadri':'Indian film director','Vasundhara Bhupathi':'Renowned author','Amaresh Nugadoni':'Sahitya Akademi Award-winning writer','T. M. Krishna':'Carnatic vocalist (evening concert, 28 Nov)','Seema Karanth':'Children’s session speaker','Chandrakeerti':'Children’s session and theatre workshop speaker'}
GUEST={'E. Tukaram':'Member of Parliament, Ballari','Dr. D. V. Paramashivamurthy':'Vice-Chancellor, Kannada University, Hampi','L. R. Singh':'Chief Operating Officer, JSW Steel Vijayanagar Works','E. Annapoorna':'MLA, Sandur','Dr. Virupakshi Poojarahalli':'Registrar, Kannada University, Hampi','Nagathihalli Chandrashekhar':'Film director (screening of Amerikaa Amerikaa 2)','Paramapada & Team':'Evening music, 29 Nov','B. Sivaramam':'Mridangam','N. Guruprasad':'Ghatam','Sruti Sarathy':'Violin'}
def slug(n): return ''.join(c.lower() if c.isalnum() else '-' for c in n).strip('-').replace('--','-')
bios={}
if len(sys.argv)>1 and os.path.exists(sys.argv[1]):
    im=Image.open(sys.argv[1]).convert('RGB')
    for y0,y1,xs,names in ROWS:
        for (a,b),n in zip(xs,names):
            c=im.crop((int(a*S),int(y0*S),int(b*S),int(y1*S))); c.thumbnail((373,500),Image.LANCZOS); fn=slug(n)+'.webp'; c.save(OUT+'/ph/'+fn,'WEBP',quality=80); bios[n]={'b':ROLE.get(n,''),'ph':'ph/'+fn}
else:
    for _,_,_,names in ROWS:
        for n in names: bios[n]={'b':ROLE.get(n,''),'ph':'ph/'+slug(n)+'.webp'}
for n,b in GUEST.items(): bios[n]={'b':b}
CH=[{'id':1,'k':'Chavadi (OPJ Museum)','e':'Chavadi (OPJ Museum)'},{'id':2,'k':'Chinnarangala (J-Max)','e':'Chinnarangala (J-Max)'},{'id':3,'k':'Evening programme','e':'Evening programme'}]
def P(*a): return [list(x) for x in a]
def sp(*n): return [['p',x] for x in n]
def mod(n): return [['c',n]]
SS=[
 {'d':28,'f':0,'t':'10:00–10:50','k':'Inauguration Ceremony','e':'Inauguration Ceremony','th':'Ceremony','pp':P(['g','E. Tukaram'],['g','Dr. D. V. Paramashivamurthy'],['g','P. Sheshadri'],['g','Vasundhara Bhupathi'],['g','L. R. Singh'])},
 {'d':28,'f':1,'t':'11:00–11:50','k':'ತುಂಗಭದ್ರೆಯ ಒಡಲು- ಕೃಷ್ಣೆಯ ಮಡಿಲು: ನೆಲದ ಕಥನ, ನುಡಿಯ ವೈಭವ','e':'In the womb of the Tungabhadra, the lap of the Krishna: tales of the land, the glory of the language','th':'Panel','pp':sp('Amaresh Nugadoni','Vasudhendra','Chidananda Sali')+mod('Halemane Rajashekar')},
 {'d':28,'f':1,'t':'12:00–12:50','k':'Hampi to Hyderabad: Exploring the Richness of Literature','e':'Hampi to Hyderabad: Exploring the Richness of Literature','th':'Panel','pp':sp('M. R. Dattathri','Avineni Bhaskar','Chaithanya Pingali')+mod('Sumathi Krishnamurthy')},
 {'d':28,'f':1,'t':'2:00–2:50','k':'ರಂಗ, ರಾಗ, ರಂಗವಲ್ಲಿ: ಕಲ್ಯಾಣ ಕರ್ನಾಟಕದ ಸಾಂಸ್ಕೃತಿಕ ಸಂಗಮ','e':'Stage, raga, rangoli: the cultural confluence of Kalyana Karnataka','th':'Panel','pp':sp('Mallikarjuna Kadakola','Vasundhara Bhupathi','Sumathi Krishnamurthy','Mallaiah Sandur')+mod('Rashmi S')},
 {'d':28,'f':1,'t':'3:00–3:50','k':'ಬಯಲಿನ ಬದುಕು, ಜನಪದದ ಬೆರಗು: ಮಣ್ಣಿನ ಹಾಡು, ಜನರ ಕಥೆ','e':'Life of the plains, wonder of folklore: songs of the soil, stories of the people','th':'Panel','pp':sp('Amaresh Nugadoni','P. Sheshadri','Sampige Nagaraj')+mod('Venkatagiri Dalavayi')},
 {'d':28,'f':2,'t':'11:00–12:00','k':'Children Fur-tastic Tales! The Hornless Fox & Animal Adventures','e':'Children Fur-tastic Tales! The Hornless Fox & Animal Adventures (primary school storytelling)','th':'Children’s session','pp':[['p','Chandrakeerti']]},
 {'d':28,'f':2,'t':'12:00–1:00','k':'Of Books, Adventures and an Asura','e':'Of Books, Adventures and an Asura (primary school)','th':'Children’s session','pp':[['p','Seema Karanth']]},
 {'d':28,'f':2,'t':'2:00–4:00','k':'Express It Out! A Theatre Exploration Workshop','e':'Express It Out! A Theatre Exploration Workshop (grades 8 to 10)','th':'Workshop','pp':[['p','Chandrakeerti']]},
 {'d':28,'f':3,'t':'6:30 PM–8:00 PM','k':'T. M. Krishna’s Carnatic vocal concert','e':'T. M. Krishna’s Carnatic vocal concert, with B. Sivaramam (mridangam), N. Guruprasad (ghatam) and Sruti Sarathy (violin)','th':'Performance','pp':P(['s','T. M. Krishna'],['s','B. Sivaramam'],['s','N. Guruprasad'],['s','Sruti Sarathy'])},
 {'d':28,'f':3,'t':'8:00 PM–10:00 PM','k':'Screening: Ruby Cube (ರೂಬಿಕ್ಯೂಬ್)','e':'Screening of P. Sheshadri’s Kannada film Ruby Cube','th':'Screening','pp':[['g','P. Sheshadri']]},
 {'d':29,'f':1,'t':'10:00–10:50','k':'ಕಥೆ ಕಟ್ಟಿದ ನೆಲ, ಕಾದಂಬರಿ ಕಟ್ಟಿದ ಕಾಲ: ಕನ್ನಡ ಸಾಹಿತ್ಯದ ಉತ್ತರದ ದನಿಗಳು','e':'The land that built stories, the era that built novels: northern voices of Kannada literature','th':'Panel','pp':sp('Praveen Kumar G','Mudiraj Banada','Ranjani Raghavan')+mod('Sridhar Banavasi')},
 {'d':29,'f':1,'t':'11:00–11:50','k':'ವಚನದಿಂದ ಬಂಡಾಯದವರೆಗೆ: ಉತ್ತರದ ನೆಲ, ಪ್ರತಿರೋಧದ ನುಡಿ','e':'From vachana to protest: the northern land, the language of resistance','th':'Panel','pp':sp('Manu Baligar','Chidananda Sali','Srisaila Nagarala')+mod('Padmini Nagaraj')},
 {'d':29,'f':1,'t':'12:00–12:50','k':'ವಿಮರ್ಶೆಯ ಕಣ್ಣು, ಸಾಹಿತ್ಯದ ಪಯಣ: ಉತ್ತರದ ಸಾಹಿತ್ಯಕ ಹೆಜ್ಜೆಗಳು','e':'The eye of criticism, the journey of literature: literary footprints of the north','th':'Panel','pp':sp('Amaresh Nugadoni','H. S. Satyanarayana','Venkatagiri Dalavayi')+mod('Halemane Rajashekar')},
 {'d':29,'f':1,'t':'2:00–2:50','k':'Rooted in the Land, Dreaming Beyond Borders: The Future of Literature and Culture','e':'Rooted in the Land, Dreaming Beyond Borders: The Future of Literature and Culture','th':'Panel','pp':sp('Vasudhendra','M. R. Dattathri','Chaithanya Pingali')+mod('Avineni Bhaskar')},
 {'d':29,'f':0,'t':'3:00–3:50','k':'Valedictory Ceremony','e':'Valedictory Ceremony','th':'Ceremony','pp':P(['g','E. Annapoorna'],['g','Dr. Virupakshi Poojarahalli'],['g','Ranjani Raghavan'],['g','Amaresh Nugadoni'],['g','L. R. Singh'])},
 {'d':29,'f':2,'t':'11:00–12:00','k':'Tale-a-licious! Magical Tales from the Land of Japan','e':'Two Japanese folktales, Issun-bōshi and The Rolling Rice Ball (primary school storytelling)','th':'Children’s session','pp':[['p','Chandrakeerti']]},
 {'d':29,'f':2,'t':'12:00–1:00','k':'Up, Up and Away! An Afternoon with the Librarian on the Roof','e':'Up, Up and Away! An Afternoon with the Librarian on the Roof (primary school)','th':'Children’s session','pp':[['p','Seema Karanth']]},
 {'d':29,'f':2,'t':'2:00–4:00','k':'Act It Out! From Imagination to Performance','e':'Act It Out! From Imagination to Performance (grades 8 to 10 theatre workshop, day 2)','th':'Workshop','pp':[['p','Chandrakeerti']]},
 {'d':29,'f':3,'t':'6:30 PM–8:00 PM','k':'Sangeetha Sanje: Paramapada & Team','e':'Sangeetha Sanje, an evening of music by Paramapada & Team','th':'Performance','pp':[['s','Paramapada & Team']]},
 {'d':29,'f':3,'t':'8:00 PM–10:00 PM','k':'Screening: Amerikaa Amerikaa 2','e':'Screening of Nagathihalli Chandrashekhar’s Amerikaa Amerikaa 2','th':'Screening','pp':[['g','Nagathihalli Chandrashekhar']]}]
def _t(x):
    h,m=map(int,x.split('–')[0].lower().replace('pm','').replace('am','').split(':')); return (h+12 if ('pm' in x.lower() or h<8) and h<12 else h)*60+m
SS.sort(key=lambda s:(s['d'],_t(s['t'])))
data={'sessions':SS,'en':{},'forums':CH,'days':[{'d':28,'l':'Sat 28 Nov'},{'d':29,'l':'Sun 29 Nov'}],'bios':bios,'forumLabel':'venue','themeLabel':'format'}
json.dump(data,open(OUT+'/data.json','w',encoding='utf8'),ensure_ascii=False)
print(len(SS),'sessions;',len(bios),'photos')
