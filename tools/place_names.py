"""Add a 'places' map to the programme festivals (sjm, jn) in festivals/<id>/data.json.
A person is placed only when their printed name or listing on the invitation contains a Karnataka
town or village (Kannada names often carry the home place), or the invitation names a place next to them.
This is an inference from names, not a record of where people live. Edit PLACE/MANUAL to correct it."""
import json,os
ROOT=os.path.join(os.path.dirname(__file__),'..','festivals')
# place text in a name -> district (confident matches only)
PLACE={'ಮೈಸೂರು':'Mysuru','ಮಂಡ್ಯ':'Mandya','ಬೆಂಗಳೂರು':'Bengaluru','ಮಂಗಳೂರು':'Dakshina Kannada','ಉಡುಪಿ':'Udupi','ಕೊಪ್ಪಳ':'Koppal','ಹೊಸಪೇಟೆ':'Vijayanagara',
 'ಬಾದಾಮಿ':'Bagalkot','ಹುಳಿಯಾರ್':'Tumakuru','ನಾಗಲಮಡಿಕೆ':'Tumakuru','ಚಳ್ಳಕೆರೆ':'Chitradurga','ಜಾಣಗೆರೆ':'Chitradurga','ಜೋಳದಕೂಡ್ಲಿಗಿ':'Vijayanagara',
 'ಕೊಟ್ಟೂರು':'Vijayanagara','ಮೂಡ್ನಾಕೂಡು':'Chamarajanagar','ವಾಮಂಜೂರು':'Dakshina Kannada','ಹರೇಕಳ':'Dakshina Kannada','ಪದ್ಮುಂಜ':'Dakshina Kannada',
 'ಎಕ್ಕಾರು':'Dakshina Kannada','ಹಿರಿಯಡ್ಕ':'Udupi','ಉಚ್ಚಿಲ':'Udupi','ಅಂಕೋಲ':'Uttara Kannada','ಕಿಗ್ಗ':'Chikkamagaluru','ಕುತ್ತಾರ್':'Dakshina Kannada',
 'ಚೊಕ್ಕಾಡಿ':'Dakshina Kannada','ಹುಲಕೋಡು':'Gadag','ಭೈರಮಂಗಲ':'Ramanagara'}
# places stated on the invitation next to a name or group, or read from the printed listing
MANUAL={'ಗಾಮನಹಳ್ಳಿಸ್ವಾಮಿ ಮತ್ತು ತಂಡ':('Mandya','ಮಂಡ್ಯ'),'ಕರ್ನಾಟಕ ಕಲಾದರ್ಶಿನಿ (ರಿ), ಬೆಂಗಳೂರು':('Bengaluru','ಬೆಂಗಳೂರು'),'ಜಿ. ವಿಷ್ಣು':('Udupi','ಉಡುಪಿ'),
 'ವಸಂತ ಕಲಾಲ್':('Delhi','JNU, ದೆಹಲಿ'),'ಶರಣ್ಯ ವರ್ಮ':('Delhi','ದೆಹಲಿ')}
for fid in ('sjm','jn'):
    p=os.path.join(ROOT,fid,'data.json'); d=json.load(open(p,encoding='utf8')); out={}
    for s in d['sessions']:
        for _,n in s['pp']:
            if n in out: continue
            if n in MANUAL: out[n]={'d':MANUAL[n][0],'w':MANUAL[n][1]}; continue
            for w,dist in PLACE.items():
                if w in n: out[n]={'d':dist,'w':w}; break
    d['places']=out; json.dump(d,open(p,'w',encoding='utf8'),ensure_ascii=False)
    print(fid,len(out),'placed of',len({n for s in d['sessions'] for _,n in s['pp']}))
