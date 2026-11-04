'use strict';
if(document.body.classList.contains('workflow-home')&&location.hash==='#article-materials')location.replace(new URL('materials/index.html',location.href).href);
const cards=[...document.querySelectorAll('.benchmark-card')];
const search=document.querySelector('#benchmark-search'),step=document.querySelector('#step-filter');
function filterCards(){const q=(search?.value||'').trim().toLowerCase(),s=step?.value||'';let n=0;for(const c of cards){c.hidden=!(c.dataset.search.includes(q)&&(!s||c.dataset.steps.split(' ').includes(s)));if(!c.hidden)n++;}const el=document.querySelector('#benchmark-count');if(el)el.textContent=n+' benchmark '+(n===1?'family':'families');const empty=document.querySelector('.empty');if(empty)empty.hidden=n>0;}
search?.addEventListener('input',filterCards);step?.addEventListener('change',()=>{filterCards();const u=new URL(location.href);if(step.value)u.searchParams.set('step',step.value);else u.searchParams.delete('step');try{history.replaceState(null,'',u)}catch{}});
if(step){const s=new URL(location.href).searchParams.get('step');if(s)step.value=s;filterCards();}
document.querySelector('.condition-search')?.addEventListener('input',e=>{const q=e.target.value.toLowerCase();for(const d of document.querySelectorAll('.condition'))d.hidden=!d.dataset.search.includes(q);});
document.querySelectorAll('[data-expand]').forEach(b=>b.addEventListener('click',()=>{for(const d of document.querySelectorAll('.condition'))if(!d.hidden)d.open=b.dataset.expand==='true';}));
document.querySelector('.record-search')?.addEventListener('input',e=>{const q=e.target.value.toLowerCase();let n=0;for(const r of document.querySelectorAll('.records tbody tr')){r.hidden=!r.dataset.search.includes(q);if(!r.hidden)n++;}document.querySelector('.record-count').textContent=n+' records';});
function revealRecord(){const id=decodeURIComponent(location.hash.slice(1));const raw=document.querySelector('#records');if(id==='records'){if(raw)raw.open=true;return;}if(!/^V\d+$/.test(id))return;const r=document.getElementById(id);if(!r)return;if(raw)raw.open=true;const s=document.querySelector('.record-search');if(s&&s.value){s.value='';s.dispatchEvent(new Event('input'));}r.hidden=false;setTimeout(()=>r.scrollIntoView({block:'center'}),40);}

window.addEventListener('hashchange',revealRecord);revealRecord();
document.addEventListener('click',async e=>{const b=e.target.closest('[data-copy]');if(!b)return;let ok=false;try{await navigator.clipboard.writeText(b.dataset.copy);ok=true;}catch{const t=document.createElement('textarea');t.value=b.dataset.copy;document.body.append(t);t.select();ok=document.execCommand('copy');t.remove();}const s=document.createElement('div');s.className='copy-status';s.setAttribute('role','status');s.textContent=ok?'APA reference copied':'Select and copy the reference above';document.body.append(s);setTimeout(()=>s.remove(),2200);});
window.addEventListener('beforeprint',()=>document.querySelectorAll('.condition').forEach(d=>{d.dataset.wasOpen=d.open?'1':'0';d.open=true;}));
window.addEventListener('afterprint',()=>document.querySelectorAll('.condition').forEach(d=>d.open=d.dataset.wasOpen==='1'));

// Workflow rails and source-condition selectors. No raw observations are loaded on the start page.
for(const button of document.querySelectorAll('[data-rail]'))button.addEventListener('click',()=>{const rail=document.getElementById(button.dataset.rail),card=rail.querySelector('.flow-card:not([hidden])');rail.scrollBy({left:Number(button.dataset.direction)*(card.getBoundingClientRect().width+22),behavior:'smooth'});});
for(const rail of document.querySelectorAll('.benchmark-rail')){const update=()=>{const visible=[...rail.querySelectorAll('.flow-card')].filter(c=>!c.hidden),box=rail.getBoundingClientRect();let nearest=0,dist=Infinity;visible.forEach((c,i)=>{const d=Math.abs(c.getBoundingClientRect().left-box.left);if(d<dist){dist=d;nearest=i;}});rail.closest('.flow-step').querySelector('.rail-position').textContent=(visible.length?nearest+1:0)+' / '+visible.length;};rail.addEventListener('scroll',update,{passive:true});rail.addEventListener('keydown',e=>{if(e.target!==rail||!['ArrowLeft','ArrowRight'].includes(e.key))return;e.preventDefault();const card=rail.querySelector('.flow-card:not([hidden])');if(!card)return;rail.scrollBy({left:(e.key==='ArrowRight'?1:-1)*(card.getBoundingClientRect().width+22),behavior:'smooth'});});update();}
for(const select of document.querySelectorAll('.time-variant'))select.addEventListener('change',()=>{const option=select.selectedOptions[0],card=select.closest('.flow-card');card.querySelector('.time-preview').src=select.value;card.querySelector('.variant-count').textContent=option.dataset.plotted+' shown / '+option.dataset.total+' observations · '+(option.dataset.undated??(Number(option.dataset.total)-Number(option.dataset.dated)))+' undated · '+option.dataset.definitionHeld+' definition-held';card.querySelector('.date-state').textContent=Number(option.dataset.plotted)?'Documented model releases':Number(option.dataset.definitionHeld)===Number(option.dataset.total)?'Metric/version definition unresolved':Number(option.dataset.dated)?'Definition/date unresolved':'Release dates unresolved';const ref=card.querySelector('.benchmark-apa');ref.dataset.benchmarkId=option.dataset.benchmarkId;ref.querySelector('.citation').outerHTML=option.dataset.apaHtml;});
// The homepage unifies commentary challenges and chronological workflow links.
const workflowSearch=document.querySelector('#flow-search');
const workflowStep=document.querySelector('#flow-step-filter');
function filterWorkflow(){
  const count=document.querySelector('#flow-count');if(!count)return;
  const q=(workflowSearch?.value||'').toLowerCase().trim(),step=workflowStep?.value||'',families=new Set();let groups=0;
  for(const row of document.querySelectorAll('.challenge-section')){
    let n=0;
    for(const card of row.querySelectorAll('.flow-card')){
      const steps=(card.dataset.steps+' '+card.dataset.diagnosticSteps).split(' ');
      card.hidden=!(card.dataset.search.includes(q)&&(!step||steps.includes(step)));
      if(!card.hidden){n++;families.add(card.dataset.family);}
    }
    row.hidden=n===0;if(n)groups++;
    row.querySelectorAll('[data-rail]').forEach(button=>button.disabled=n===0);
    row.querySelector('.rail-position').textContent=(n?1:0)+' / '+n;
    row.querySelector('.step-count').textContent=n+' benchmark '+(n===1?'family':'families');
    row.querySelector('.benchmark-rail').scrollLeft=0;
  }
  count.textContent=families.size+' benchmark '+(families.size===1?'family':'families')+' · '+groups+' '+(groups===1?'challenge':'challenges');
  document.querySelector('#flow-empty').hidden=families.size>0;
  const context=document.querySelector('#workflow-context');context.hidden=!step;
  if(step){const option=workflowStep.selectedOptions[0];document.querySelector('#workflow-context-title').textContent=option.dataset.name;document.querySelector('#workflow-context-task').textContent=option.dataset.task;document.querySelector('#workflow-context-gap').textContent=option.dataset.gap;}
  for(const button of document.querySelectorAll('[data-workflow-step]')){
    const active=button.dataset.workflowStep===step;button.setAttribute('aria-pressed',String(active));button.classList.toggle('is-selected',active);
  }
}
function persistWorkflowStep(){
  const url=new URL(location.href);if(workflowStep?.value)url.searchParams.set('step',workflowStep.value);else url.searchParams.delete('step');
  if(url.hash.startsWith('#step-'))url.hash='';try{history.replaceState(null,'',url)}catch{}
}
workflowSearch?.addEventListener('input',filterWorkflow);
workflowStep?.addEventListener('change',()=>{filterWorkflow();persistWorkflowStep();});
document.querySelector('#flow-reset')?.addEventListener('click',()=>{workflowSearch.value='';workflowStep.value='';filterWorkflow();persistWorkflowStep();});
for(const button of document.querySelectorAll('[data-workflow-step]'))button.addEventListener('click',()=>{workflowStep.value=button.dataset.workflowStep;filterWorkflow();persistWorkflowStep();});
for(const link of document.querySelectorAll('.challenge-jump a'))link.addEventListener('click',()=>{const section=document.querySelector(link.getAttribute('href'));if(section?.hidden){workflowSearch.value='';workflowStep.value='';filterWorkflow();persistWorkflowStep();}});
function revealWorkflowAnchor(){
  if(!workflowStep)return;
  const hash=decodeURIComponent(location.hash.slice(1));
  if(hash.startsWith('step-')){
    const sid=hash.slice(5);if([...workflowStep.options].some(o=>o.value===sid)){workflowStep.value=sid;document.querySelector('#workflow-map').open=true;filterWorkflow();}
  }else if(/^F\d{3}$/.test(hash)){
    workflowSearch.value='';workflowStep.value='';filterWorkflow();
  }
}
if(workflowStep){
  const url=new URL(location.href),selected=url.searchParams.get('step');
  if(selected&&[...workflowStep.options].some(o=>o.value===selected))workflowStep.value=selected;
  if(!location.hash&&/^[ABCD]$/.test(url.searchParams.get('challenge')||''))location.hash='challenge-'+url.searchParams.get('challenge');
  filterWorkflow();revealWorkflowAnchor();window.addEventListener('hashchange',revealWorkflowAnchor);
}

// Article-wide family filtering does not modify the frozen observations.
const atlasCards=[...document.querySelectorAll('.atlas-card')];
function filterAtlas(){const q=(document.querySelector('#atlas-search')?.value||'').trim().toLowerCase(),s=document.querySelector('#atlas-step')?.value||'',t=document.querySelector('#atlas-status')?.value||'',ch=document.querySelector('#atlas-challenge')?.value||'';let n=0;for(const card of atlasCards){card.hidden=!(card.dataset.search.includes(q)&&(!s||card.dataset.steps.split(' ').includes(s))&&(!t||card.dataset.flags.split(' ').includes(t))&&(!ch||card.dataset.challenges.split(' ').includes(ch)));if(!card.hidden)n++;}const count=document.querySelector('#atlas-count');if(count)count.textContent=n+' benchmark '+(n===1?'family':'families');const empty=document.querySelector('.atlas-empty');if(empty)empty.hidden=n>0;}
for(const id of ['atlas-search','atlas-step','atlas-status','atlas-challenge'])document.getElementById(id)?.addEventListener(id==='atlas-search'?'input':'change',filterAtlas);
if(atlasCards.length){const ch=new URL(location.href).searchParams.get('challenge');if(ch&&document.querySelector('#atlas-challenge'))document.querySelector('#atlas-challenge').value=ch;filterAtlas();}

// Source-bound interactive points, shared by homepage and benchmark detail figures.
const pointBase=new URL('../',document.querySelector('script[src*="assets/app.js"]').src);
let pointDataPromise;
function pointData(){return pointDataPromise??=fetch(new URL('data/point_details.json',pointBase)).then(r=>{if(!r.ok)throw Error('Point metadata unavailable');return r.json();}).then(r=>r.points);}
const svgRequests=new Map();
function sourceSvg(url){if(!svgRequests.has(url))svgRequests.set(url,fetch(url).then(r=>{if(!r.ok)throw Error('Figure unavailable');return r.text();}));return svgRequests.get(url);}
function preparePointSvg(svg){
  if(svg.dataset.pointReady)return;svg.dataset.pointReady='true';svg.setAttribute('role','group');
  const groups=new Map();
  for(const a of svg.querySelectorAll('.time-point')){
    const circle=a.querySelector('circle');if(!circle)continue;
    const key=Number(circle.getAttribute('cx')).toFixed(3)+'|'+Number(circle.getAttribute('cy')).toFixed(3);
    if(!groups.has(key))groups.set(key,[]);groups.get(key).push(a);
    a.setAttribute('role','button');a.setAttribute('tabindex','0');a.setAttribute('aria-haspopup','dialog');a.setAttribute('aria-expanded','false');
    for(const title of a.querySelectorAll('title'))title.remove();
    const hit=document.createElementNS('http://www.w3.org/2000/svg','circle');
    for(const k of ['cx','cy'])hit.setAttribute(k,circle.getAttribute(k));hit.setAttribute('r','9');hit.setAttribute('fill','transparent');hit.classList.add('point-hit');a.append(hit);
  }
  for(const anchors of groups.values()){
    const ids=[...new Set(anchors.flatMap(a=>(a.dataset.observationIds||'').split(/\s+/).filter(Boolean)))];
    for(const a of anchors)a.dataset.pointIds=ids.join(' ');
  }
}
async function loadPointChart(img){
  const url=new URL(img.getAttribute('src'),document.baseURI).href;
  if(img.dataset.interactiveSource===url)return;img.dataset.interactiveSource=url;
  const parent=img.parentElement;if(activePoint&&parent.contains(activePoint))hidePointPanel();parent.querySelector('svg[data-inline-chart]')?.remove();img.hidden=false;
  try{
    const xml=new DOMParser().parseFromString(await sourceSvg(url),'image/svg+xml');
    if(img.dataset.interactiveSource!==url)return;
    const source=xml.documentElement;if(source.localName!=='svg')throw Error('Invalid figure');
    for(const el of source.querySelectorAll('script,foreignObject'))el.remove();
    for(const el of [source,...source.querySelectorAll('*')])for(const attr of [...el.attributes])if(attr.name.toLowerCase().startsWith('on'))el.removeAttribute(attr.name);
    for(const a of source.querySelectorAll('a[href]'))a.setAttribute('href',new URL(a.getAttribute('href'),url).href);
    const svg=document.importNode(source,true);svg.dataset.inlineChart='true';preparePointSvg(svg);img.after(svg);img.hidden=true;
  }catch{img.hidden=false;}
}
const pointObserver=new IntersectionObserver(entries=>{for(const e of entries)if(e.isIntersecting){loadPointChart(e.target);pointObserver.unobserve(e.target);}},{rootMargin:'250px'});
for(const img of document.querySelectorAll('img.time-preview')){
  pointObserver.observe(img);
  new MutationObserver(()=>loadPointChart(img)).observe(img,{attributes:true,attributeFilter:['src']});
}
for(const svg of document.querySelectorAll('svg.release-plot'))preparePointSvg(svg);
const pointPanel=document.createElement('aside');pointPanel.className='point-detail';pointPanel.id='point-detail';pointPanel.hidden=true;
pointPanel.setAttribute('role','dialog');pointPanel.setAttribute('aria-label','Data point details');document.body.append(pointPanel);
let activePoint=null,pointPinned=false,pointHideTimer,pointRequest=0;
function pointEl(tag,text,className){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(className)e.className=className;return e;}
function pointLink(text,url){const a=pointEl('a',text);const resolved=new URL(url,pointBase);if(!['https:','http:'].includes(resolved.protocol))return pointEl('span',text);a.href=resolved.href;return a;}
function positionPointPanel(){
  if(pointPanel.hidden||!activePoint)return;
  const r=activePoint.getBoundingClientRect(),w=pointPanel.offsetWidth,h=pointPanel.offsetHeight;
  let left=r.right+14;if(left+w>innerWidth-12)left=r.left-w-14;
  pointPanel.style.left=Math.max(12,Math.min(left,innerWidth-w-12))+'px';
  pointPanel.style.top=Math.max(12,Math.min(r.top,innerHeight-h-12))+'px';
}
function hidePointPanel(){clearTimeout(pointHideTimer);pointRequest++;if(activePoint){activePoint.classList.remove('point-selected');activePoint.setAttribute('aria-expanded','false');}pointPanel.hidden=true;activePoint=null;pointPinned=false;}
function deferPointHide(){clearTimeout(pointHideTimer);if(!pointPinned)pointHideTimer=setTimeout(hidePointPanel,220);}
function renderPoint(row,rows){
  pointPanel.replaceChildren();
  const head=pointEl('div',undefined,'point-detail-head'),title=pointEl('h3',row.model),close=pointEl('button','×','point-close');
  close.type='button';close.setAttribute('aria-label','Close data point details');close.addEventListener('click',hidePointPanel);head.append(title,close);pointPanel.append(head);
  pointPanel.append(pointEl('p',row.family+' · '+row.metric,'point-metric'));
  pointPanel.append(pointEl('p',row.source_value_text,'point-score'));
  const release=row.release_date_low&&row.release_date_high&&row.release_date_low!==row.release_date_high?row.release_date_low+' – '+row.release_date_high:row.documented_model_release;
  pointPanel.append(pointEl('p','Model release: '+release,'point-release'));
  pointPanel.append(pointEl('p',row.condition,'point-condition'));
  if(rows.length>1){const label=pointEl('label','Reported results at this position'),select=document.createElement('select');select.setAttribute('aria-label','Reported results at this position');for(const r of rows){const o=pointEl('option',r.model+' · '+r.source_value_text);o.value=r.observation_id;o.selected=r.observation_id===row.observation_id;select.append(o);}select.addEventListener('change',()=>{renderPoint(rows.find(r=>r.observation_id===select.value),rows);positionPointPanel();});label.append(select);pointPanel.append(label);}
  const source=pointEl('section',undefined,'point-source');source.append(pointEl('h4','Result reference (APA)'));source.append(pointEl('p',row.result_reference_apa,'point-reference'));source.append(pointEl('p',row.source_locator,'point-locator'));
  const links=pointEl('div',undefined,'point-links'),external=pointLink('Open result source ↗',row.source_url);external.target='_blank';external.rel='noopener noreferrer';links.append(external);
  const copy=pointEl('button','Copy reference','copy');copy.type='button';copy.dataset.copy=row.result_reference_apa;links.append(copy);source.append(links);pointPanel.append(source);
  const ref=document.createElement('details');ref.append(pointEl('summary','Benchmark and release references'));ref.append(pointEl('p',row.benchmark_reference_apa,'point-reference'));
  if(row.benchmark_reference_url)ref.append(pointLink('Benchmark source ↗',row.benchmark_reference_url));
  if(row.release_reference_apa)ref.append(pointEl('p',row.release_reference_apa,'point-reference'));
  if(row.release_source_url)ref.append(pointLink('Model release source ↗',row.release_source_url));pointPanel.append(ref);
  const foot=pointEl('div',undefined,'point-detail-foot');foot.append(pointLink('Open source row '+row.observation_id,row.record_url));foot.append(pointEl('span',pointPinned?'Pinned · Esc to close':'Click point to keep open'));pointPanel.append(foot);
  positionPointPanel();
}
async function showPointPanel(a,pin=false){
  clearTimeout(pointHideTimer);if(pointPinned&&a!==activePoint&&!pin)return;
  if(activePoint&&activePoint!==a){activePoint.classList.remove('point-selected');activePoint.setAttribute('aria-expanded','false');}
  activePoint=a;pointPinned=pin||pointPinned;a.classList.add('point-selected');a.setAttribute('aria-expanded','true');pointPanel.hidden=false;pointPanel.textContent='Loading source details…';positionPointPanel();const request=++pointRequest;
  try{const data=await pointData();if(request!==pointRequest||a!==activePoint)return;const rows=(a.dataset.pointIds||a.dataset.observationIds||'').split(/\s+/).map(id=>data[id]).filter(Boolean);if(!rows.length)throw Error('No source record');renderPoint(rows[0],rows);}
  catch{if(request!==pointRequest)return;pointPanel.replaceChildren(pointEl('p',a.getAttribute('aria-label')||'Data point'),pointLink('Open source row',a.getAttribute('href')));positionPointPanel();}
}
function chartPoint(target){return target instanceof Element?target.closest('a.time-point'):null;}
document.addEventListener('pointerover',e=>{const a=chartPoint(e.target);if(a){clearTimeout(pointHideTimer);if(a!==activePoint)showPointPanel(a);}});
document.addEventListener('pointerout',e=>{const a=chartPoint(e.target);if(a&&chartPoint(e.relatedTarget)!==a&&!pointPanel.contains(e.relatedTarget))deferPointHide();});
document.addEventListener('focusin',e=>{const a=chartPoint(e.target);if(a)showPointPanel(a);});
document.addEventListener('click',e=>{const a=chartPoint(e.target);if(a){e.preventDefault();showPointPanel(a,true);}else if(!pointPanel.contains(e.target))hidePointPanel();});
document.addEventListener('keydown',e=>{if(e.key==='Escape')hidePointPanel();const a=chartPoint(e.target);if(a&&['Enter',' '].includes(e.key)){e.preventDefault();showPointPanel(a,true);}});
pointPanel.addEventListener('pointerenter',()=>clearTimeout(pointHideTimer));pointPanel.addEventListener('pointerleave',deferPointHide);
window.addEventListener('resize',positionPointPanel);document.addEventListener('scroll',e=>{if(pointPanel.contains(e.target))return;if(pointPinned)positionPointPanel();else hidePointPanel();},true);
