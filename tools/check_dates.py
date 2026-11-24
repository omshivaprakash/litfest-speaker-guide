"""List festivals whose dates need attention and check that official sites still answer.
Usage: python3 tools/check_dates.py   (set CHECK_URLS=0 to skip the network checks)"""
import json,os,datetime,urllib.request,re
R=os.path.join(os.path.dirname(__file__),'..'); today=datetime.date.today()
F=json.load(open(R+'/festivals.json',encoding='utf8'))['festivals']
for f in F:
    msg=[]
    if not f.get('start'): msg.append('no start/end dates')
    elif f.get('tbc'): msg.append('dates still to be confirmed')
    elif datetime.date.fromisoformat(f['end'])<today: msg.append('ended %s; add next edition dates'%f['end'])
    elif (datetime.date.fromisoformat(f['start'])-today).days<=14: msg.append('starts soon; refresh the programme')
    if os.environ.get('CHECK_URLS','1')!='0' and f.get('url'):
        try:
            r=urllib.request.urlopen(urllib.request.Request(f['url'],headers={'User-Agent':'Mozilla/5.0'}),timeout=25); html=r.read(200000).decode('utf8','ignore')
            if str(today.year+1) in html and str(f['year'])!=str(today.year+1) and not f.get('start','').startswith(str(today.year+1)): msg.append('site mentions %d: check for a new edition'%(today.year+1))
        except Exception as e: msg.append('site not reachable (%s)'%type(e).__name__)
    if msg: print(f"{f['id']:6} {f['short']:12} "+'; '.join(msg))
