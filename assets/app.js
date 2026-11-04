'use strict';
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
