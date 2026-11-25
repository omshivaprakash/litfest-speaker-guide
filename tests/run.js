/* One-screen and error checks for every festival, tab and overlay at three phone/desktop sizes.
   Usage: python3 -m http.server 8765 &   then   BASE=http://localhost:8765 node tests/run.js   (needs: npm i playwright) */
const {chromium}=require('playwright');const BASE=process.env.BASE||'http://localhost:8765';const VPS=[[390,780],[360,640],[1280,720]];
let axeSrc=null;try{axeSrc=require('fs').readFileSync(require.resolve('axe-core/axe.min.js'),'utf8')}catch(e){}
let fails=0;const bad=(m)=>{fails++;console.log('FAIL',m)};
(async()=>{const b=await chromium.launch();const L=await (await fetch(BASE+'/festivals.json')).json();
for(const [w,h] of VPS){const p=await b.newPage({viewport:{width:w,height:h}});const errs=[];
 p.on('pageerror',e=>errs.push('js: '+e.message));p.on('response',r=>{if(r.status()>=400&&!/favicon/.test(r.url()))errs.push(r.status()+' '+r.url().replace(BASE,''))});
 const fit=async(tag)=>{const o=await p.evaluate(()=>({v:document.documentElement.scrollHeight-innerHeight,h:document.documentElement.scrollWidth-innerWidth}));if(o.v>1||o.h>1)bad(`${w}x${h} ${tag} page scrolls (v${o.v} h${o.h})`)};
 await p.goto(BASE+'/');await p.waitForTimeout(900);await fit('landing');
 for(const f of L.festivals){await p.goto(`${BASE}/?f=${f.id}`);await p.waitForTimeout(900);await fit(f.id);
  if(f.status!=='live')continue;
  const n=(await p.$$('.tabs button, .tabs a')).length;
  for(let i=0;i<n;i++){const t=(await p.$$('.tabs button, .tabs a'))[i];if(!t||!(await t.isVisible()))continue;await t.click({timeout:5000});await p.waitForTimeout(350);await fit(`${f.id} tab ${i}`)}}
 await p.goto(BASE+'/?f=blf');await p.waitForTimeout(800);
 if(axeSrc&&w===390){await p.evaluate(axeSrc);const r=await p.evaluate(()=>axe.run(document,{runOnly:['wcag2a','wcag2aa']}));r.violations.forEach(v=>bad('accessibility: '+v.id+' ('+v.nodes.length+') '+v.help))}
 for(const [btn,name] of [['#gsb','search'],['#abb','about']]){await p.click(btn);await p.waitForTimeout(600);await fit(name);await p.keyboard.press('Escape');await p.waitForTimeout(150)}
 await p.click('#axb2');await p.waitForTimeout(3500);await fit('across');await p.click('#axx');
 await p.click('#exb2');await p.waitForTimeout(3500);
 for(const t of ['soon','shelf','debut','prizes','kids','tr','trails','lang','mine']){await p.click(`#ext [data-t=${t}]`);await p.waitForTimeout(350);await fit('explore '+t);if(t==='kids'){await p.click('#exb [data-ks]');await p.waitForTimeout(300);await fit('explore kids strand');await p.click('#exs [data-ks=""]');await p.click('[data-kv=people]');await p.waitForTimeout(300);await fit('explore kids people')}if(t==='prizes'){await p.click('[data-pv=effect]');await p.waitForTimeout(900);await fit('explore prize effect');await p.click('[data-pe=all]');await p.waitForTimeout(300);await fit('explore prize effect all')}}
 if(errs.length)bad(`${w}x${h} errors: ${[...new Set(errs)].slice(0,5).join(' | ')}`);
 await p.close()}
await b.close();console.log(fails?`${fails} failure(s)`:'all checks passed');process.exit(fails?1:0)})()
