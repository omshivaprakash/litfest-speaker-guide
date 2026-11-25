/* Interface labels in Kannada and Hindi (beta). English is the source text; this only swaps fixed labels, never names, bios or data.
   Corrections are welcome through the project's GitHub issues. Choose a language in About or on the home page. */
(function(){
var D={
kn:{'Search':'ಹುಡುಕಿ','Across':'ಹೋಲಿಕೆ','Explore':'ಅನ್ವೇಷಿಸಿ','About':'ಬಗ್ಗೆ','Close':'ಮುಚ್ಚಿ','Official site ↗':'ಅಧಿಕೃತ ತಾಣ ↗',
'Discover':'ಅನ್ವೇಷಣೆ','Who to hear':'ಯಾರನ್ನು ಕೇಳಬೇಕು','All speakers':'ಎಲ್ಲಾ ಭಾಷಣಕಾರರು','Past years':'ಹಿಂದಿನ ವರ್ಷಗಳು','India':'ಭಾರತ','Work in progress':'ಕೆಲಸ ನಡೆಯುತ್ತಿದೆ','International':'ಅಂತರರಾಷ್ಟ್ರೀಯ','The data':'ಅಂಕಿಅಂಶ','Tracker':'ನನ್ನ ಪಟ್ಟಿ','Programme':'ಕಾರ್ಯಕ್ರಮ','People':'ಜನರು','Map':'ನಕ್ಷೆ','Insights':'ಒಳನೋಟ',
'Upcoming':'ಮುಂಬರುವ','Shelf':'ಪುಸ್ತಕ ಕಪಾಟು','Debuts':'ಮೊದಲ ಕೃತಿ','Prizes':'ಪ್ರಶಸ್ತಿಗಳು','Translators':'ಅನುವಾದಕರು','Trails':'ಹಾದಿಗಳು','Languages':'ಭಾಷೆಗಳು','Bookmarks':'ಬುಕ್‌ಮಾರ್ಕ್‌ಗಳು',
'Overlap':'ಸಾಮಾನ್ಯ ಭಾಷಣಕಾರರು','Most travelled':'ಹೆಚ್ಚು ಉತ್ಸವಗಳಲ್ಲಿ','Start here':'ಇಲ್ಲಿಂದ ಆರಂಭಿಸಿ','Back again':'ಮತ್ತೆ ಬಂದವರು','Filters':'ಫಿಲ್ಟರ್‌ಗಳು',
'Add to calendar':'ಕ್ಯಾಲೆಂಡರ್‌ಗೆ ಸೇರಿಸಿ','Remind me':'ನನಗೆ ನೆನಪಿಸಿ','Reminder on ✓':'ನೆನಪು ಆನ್ ✓','Copy list':'ಪಟ್ಟಿ ನಕಲಿಸಿ','Install app':'ಆ್ಯಪ್ ಸ್ಥಾಪಿಸಿ',
'Tomorrow':'ನಾಳೆ','Happening now':'ಈಗ ನಡೆಯುತ್ತಿದೆ','Ended':'ಮುಗಿದಿದೆ','Dates to be announced':'ದಿನಾಂಕ ಇನ್ನೂ ಪ್ರಕಟವಾಗಿಲ್ಲ','‹ Prev':'‹ ಹಿಂದೆ','Next ›':'ಮುಂದೆ ›','All':'ಎಲ್ಲಾ','By prize':'ಪ್ರಶಸ್ತಿ ಪ್ರಕಾರ','Timeline':'ಕಾಲಾನುಕ್ರಮ','‹ All prizes':'‹ ಎಲ್ಲಾ ಪ್ರಶಸ್ತಿಗಳು',
'Who speaks at literature festivals, starting with India':'ಸಾಹಿತ್ಯ ಉತ್ಸವಗಳಲ್ಲಿ ಯಾರು ಮಾತನಾಡುತ್ತಾರೆ: ಭಾರತದಿಂದ ಆರಂಭ','About this portal':'ಈ ಪೋರ್ಟಲ್ ಬಗ್ಗೆ',
pat:[[/^in (\d+) days$/,'$1 ದಿನಗಳಲ್ಲಿ'],[/^About in (\d+) days$/,'ಸುಮಾರು $1 ದಿನಗಳಲ್ಲಿ'],[/^Page (\d+) of (\d+)$/,'ಪುಟ $1 / $2']]},
hi:{'Search':'खोजें','Across':'तुलना','Explore':'खोजबीन','About':'परिचय','Close':'बंद करें','Official site ↗':'आधिकारिक साइट ↗',
'Discover':'खोज','Who to hear':'किसे सुनें','All speakers':'सभी वक्ता','Past years':'पिछले वर्ष','India':'भारत','Work in progress':'काम जारी है','International':'अंतरराष्ट्रीय','The data':'आँकड़े','Tracker':'मेरी सूची','Programme':'कार्यक्रम','People':'लोग','Map':'नक्शा','Insights':'अंतर्दृष्टि',
'Upcoming':'आगामी','Shelf':'किताबों की अलमारी','Debuts':'पहली किताब','Prizes':'पुरस्कार','Translators':'अनुवादक','Trails':'राहें','Languages':'भाषाएँ','Bookmarks':'बुकमार्क',
'Overlap':'साझा वक्ता','Most travelled':'सबसे अधिक उत्सवों में','Start here':'यहाँ से शुरू करें','Back again':'फिर आए','Filters':'फ़िल्टर',
'Add to calendar':'कैलेंडर में जोड़ें','Remind me':'मुझे याद दिलाएँ','Reminder on ✓':'याद दिलाना चालू ✓','Copy list':'सूची कॉपी करें','Install app':'ऐप इंस्टॉल करें',
'Tomorrow':'कल','Happening now':'अभी जारी','Ended':'समाप्त','Dates to be announced':'तारीखें घोषित होना बाकी','‹ Prev':'‹ पिछला','Next ›':'अगला ›','All':'सभी','By prize':'पुरस्कार के अनुसार','Timeline':'समयरेखा','‹ All prizes':'‹ सभी पुरस्कार',
'Who speaks at literature festivals, starting with India':'साहित्य उत्सवों में कौन बोलता है: भारत से शुरुआत','About this portal':'इस पोर्टल के बारे में',
pat:[[/^in (\d+) days$/,'$1 दिन में'],[/^About in (\d+) days$/,'लगभग $1 दिन में'],[/^Page (\d+) of (\d+)$/,'पृष्ठ $1 / $2']]}
};
var lang='en',orig=new WeakMap(),busy=false,queued=false;
try{lang=localStorage.getItem('litfest_lang')||'en'}catch(e){}
function tr(s){var d=D[lang];if(!d)return null;var t=s.trim();if(!t)return null;if(d[t]!==undefined&&t!=='pat')return s.replace(t,d[t]);for(var i=0;i<d.pat.length;i++){var m=d.pat[i][0].exec(t);if(m)return s.replace(t,t.replace(d.pat[i][0],d.pat[i][1]))}return null}
function walk(root){busy=true;var w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{acceptNode:function(n){var p=n.parentNode&&n.parentNode.nodeName;return p==='SCRIPT'||p==='STYLE'?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT}}),n,list=[];while((n=w.nextNode()))list.push(n);
list.forEach(function(n){var o=orig.get(n);if(o===undefined){o=n.nodeValue;var cur=lang==='en'?null:tr(o);if(cur===null&&lang==='en')return;orig.set(n,o)}
var v=lang==='en'?o:(tr(o)||o);if(n.nodeValue!==v)n.nodeValue=v});
document.documentElement.lang=lang==='en'?'en':lang;busy=false}
function mark(){[].forEach.call(document.querySelectorAll('[data-lang]'),function(x){x.classList.toggle('on',x.dataset.lang===lang)})}
function schedule(){if(queued)return;queued=true;requestAnimationFrame(function(){queued=false;walk(document.body);mark()})}
function setLang(l){lang=l;try{localStorage.setItem('litfest_lang',l)}catch(e){}walk(document.body);mark()}
new MutationObserver(function(m){if(busy)return;if(lang!=='en')schedule();else mark()}).observe(document.documentElement,{childList:true,subtree:true,characterData:true});
window.LFI18N={set:setLang,get:function(){return lang},apply:function(){if(lang!=='en')walk(document.body)}};
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('[data-lang]');if(b){setLang(b.dataset.lang)}});
window.addEventListener('load',function(){if(lang!=='en')walk(document.body)});
})();
