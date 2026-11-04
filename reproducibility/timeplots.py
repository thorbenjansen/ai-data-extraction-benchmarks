"""Release-date/performance plots. Dates and scores are never jittered or imputed."""
from pathlib import Path
import datetime as dt,calendar,re,math,html,json,csv,collections,textwrap
import hashlib
import release_dates
import mean_trends
E=lambda s:html.escape(str(s),quote=True)
BLUE='#24536e'
ORDER=['protocol','documents','retrieve','bind','code','coordinate','derive','verify','collaborate','adjudicate','product','audit']
W,H=860,565
LEFT,RIGHT,TOP,BOTTOM=100,822,82,434
AUDIT={};VARIANTS={};PLOT_RECORDS=[];GLOBAL_RANGE=None;FAMILY_RANGES={}
CUTOFF_DATE=dt.date(2026,10,31)
DISPLAY_START=None
DISPLAY_END=None
def visible(a):
 return a['status']=='Plotted' and a.get('metric_plot_eligible','True')!='False'
def padded_range(audits):
 """Retain every eligible date, including full release-month intervals."""
 aa=[a for a in audits if visible(a)]
 if not aa:return None
 lo=min(dt.date.fromisoformat(a['date_low']) for a in aa);hi=max(dt.date.fromisoformat(a['date_high']) for a in aa)
 span=(hi-lo).days;pad=30 if span==0 else max(14,min(60,round(span*.06)))
 return lo-dt.timedelta(days=pad),min(CUTOFF_DATE,hi+dt.timedelta(days=pad))
def font_metrics():
 from reportlab.pdfbase import pdfmetrics
 from reportlab.pdfbase.ttfonts import TTFont
 fontroot=Path('/System/Library/Fonts/Supplemental')
 for name,fn in [('Arial','Arial.ttf'),('Arial-Bold','Arial Bold.ttf')]:
  if name not in pdfmetrics.getRegisteredFontNames():pdfmetrics.registerFont(TTFont(name,str(fontroot/fn)))
 return pdfmetrics
def canon(s):
 s=re.sub(r'\((?:FC|Prompt|FC Thinking|Prompt Thinking)\)','',s,flags=re.I)
 s=re.sub(r'^(?:OpenAI|Meta)[- ]+','',s,flags=re.I)
 s=re.sub(r'(?:[- ](?:instruct|chat|hf))+$','',s,flags=re.I)
 return re.sub(r'[^a-z0-9]','',s.lower())
def prohibited(r):return r['reference_type']!='model' or bool(re.search(r'fine.?tun| / (?:n1|n4|n3\+s1)$',r['model'],re.I))
def initial_release(r):
 k=r['date_kind'].lower()
 return bool(r['date']) and not prohibited(r) and ('release' in k) and 'checkpoint' not in k and 'result/submission' not in k
def prepare(data):
 global AUDIT,PLOT_RECORDS,GLOBAL_RANGE,FAMILY_RANGES,DISPLAY_START,DISPLAY_END
 AUDIT={}
 trusted=collections.defaultdict(list)
 for r in data:
  if initial_release(r):
   # A leaderboard's unqualified Date column alone is not proof of public release.
   if 'longbench2.github.io' in r['date_source'] and 'cross-reference' in r['date_kind']:continue
   # Index complete model identities only. Context sizes or configuration words
   # after a slash must never become release-date lookup keys.
   trusted[canon(r['model'])].append(r)
 def match(candidate,r):
  candidates=trusted.get(canon(candidate),[])
  exact_checkpoint=re.search(r'(20\d{2})-?(0[1-9]|1[012])-?([012]\d|3[01])',candidate)
  if not candidates and exact_checkpoint:
   date='-'.join(exact_checkpoint.groups());base=re.sub(r'(20\d{2})-?(0[1-9]|1[012])-?([012]\d|3[01])','',candidate)
   candidates=[q for q in trusted.get(canon(base),[]) if q['date']==date]
  # Generic rolling API aliases do not identify a release snapshot.
  if canon(candidate) in ['gpt4','gpt4o','gpt4turbo','claude35sonnet','gemini15pro','gemini15flash','gemini25pro','gemini25flash','o1']:return None
  dates={q['date'] for q in candidates}
  if len(dates)==1:return candidates[0]
  return None
 for r in data:
  rule=release_dates.lookup(r)
  a=dict(observation_id=r['observation_id'],family=r['family'],model=r['model'],original_date=r['date'],original_date_kind=r['date_kind'],release_date='',release_source='',release_basis='',release_id='',release_locator='',release_evidence='',release_apa='',release_snapshot='',release_snapshot_sha256='',identity_source='',identity_locator='',identity_evidence='',identity_source_sha256='',identity_hash_target='',date_discrepancy='',status='Not plotted',reason='No documented release date')
  if r['reference_type']!='model':a['reason']='Human/team/other reference has no model release date'
  elif prohibited(r):a['reason']='Fine-tuned configuration has no independently documented release date'
  elif r.get('release_inheritance_only')=='True':
   if r['date']:a.update(release_date=r['date'],release_source=r['date_source'],release_basis=r['date_kind'],status='Plotted',reason='')
   else:a['reason']=r.get('release_omission_reason') or 'No unambiguous prior release audit for the retained checkpoint identity'
  elif rule:
   snapshot=release_dates.ROOT/rule['snapshot_file'];assert snapshot.is_file(),rule
   a.update(release_date=rule['release_date'],release_source=rule['url'],release_basis=rule['date_basis'],release_id=rule['release_id'],release_locator=rule['locator'],release_evidence=rule['evidence'],release_apa=rule['apa'],release_snapshot=rule['snapshot_file'],release_snapshot_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest(),status='Plotted',reason='')
   a.update({k:rule.get(k,'') for k in ['identity_source','identity_locator','identity_evidence','identity_source_sha256','identity_hash_target']})
   if r['date'] and r['date']!=a['release_date']:a['date_discrepancy']='Original recorded date '+r['date']+' differs from developer-documented release '+a['release_date']
  elif initial_release(r) and not ('longbench2.github.io' in r['date_source'] and 'cross-reference' in r['date_kind']):a.update(release_date=r['date'],release_source=r['date_source'],release_basis=r['date_kind'],status='Plotted',reason='')
  else:
   found=next((m for c in [r['model']]+r['model'].split(' / ') if (m:=match(c,r))),None)
   if found:a.update(release_date=found['date'],release_source=found['date_source'],release_basis='Exact named-model match to documented release: '+found['model'],status='Plotted',reason='')
   elif 'checkpoint' in r['date_kind'].lower():a['reason']='Checkpoint date alone does not establish public release date'
   elif 'benchmark-reported' in r['date_kind'].lower():a['reason']='Benchmark Date field not independently established as a model release'
   elif 'result/submission' in r['date_kind'].lower():a['reason']='Result/submission date is not model release date'
  if a['release_date']:
   assert a['release_date']<='2026-10-31'
   if len(a['release_date'])==7:
    year,month=map(int,a['release_date'].split('-'));lo=dt.date(year,month,1);hi=dt.date(year,month,calendar.monthrange(year,month)[1]);mid=lo+(hi-lo)/2
   else:lo=hi=mid=dt.date.fromisoformat(a['release_date'])
   a.update(date_low=lo.isoformat(),date_high=hi.isoformat(),date_position=mid.isoformat(),date_precision='month' if len(a['release_date'])==7 else 'day')
  else:a.update(date_low='',date_high='',date_position='',date_precision='')
  a['metric_plot_eligible']=r.get('plot_eligible','True') or 'True'
  a['definition_status']=r.get('definition_status','Existing audited source condition')
  a['display_status']='Definition unresolved; source data only' if a['metric_plot_eligible']=='False' else 'Shown on data-adaptive time axis' if visible(a) else 'Release date unresolved / not applicable'
  AUDIT[r['observation_id']]=a
 legacy=sorted({a['release_source'] for a in AUDIT.values() if a['status']=='Plotted' and not a['release_id']})
 for a in AUDIT.values():a['release_reference_id']=a['release_id'] or ('RL'+str(legacy.index(a['release_source'])+1).zfill(3) if a['status']=='Plotted' else '')
 GLOBAL_RANGE=padded_range(AUDIT.values());DISPLAY_START,DISPLAY_END=GLOBAL_RANGE
 FAMILY_RANGES={f:padded_range(a for a in AUDIT.values() if a['family']==f) for f in {a['family'] for a in AUDIT.values()}}
 PLOT_RECORDS=[];mean_trends.prepare(data,AUDIT)
 return AUDIT
def bounds(rows,axis_mode='focused'):
 return GLOBAL_RANGE if axis_mode=='shared' else padded_range(AUDIT[r['observation_id']] for r in rows)
def primary_series(rows):
 groups=collections.OrderedDict()
 for r in rows:groups.setdefault(r['series_id'],[]).append(r)
 def rank(item):
  sid,rr=item;nn=[r for r in rr if visible(AUDIT[r['observation_id']])];dates={AUDIT[r['observation_id']]['release_date'] for r in nn};overall=bool(re.search(r'overall|original main setup|original test|answer f1',rr[0]['condition']+' '+rr[0]['metric'],re.I))
  documented=[r for r in rr if AUDIT[r['observation_id']]['status']=='Plotted']
  return (len(dates)>=2,bool(nn),bool(documented),overall,len(nn),len(documented),-list(groups).index(sid))
 return max(groups.items(),key=rank)[0]
def draw_series(rows,heading,condition,filename,download=False,preview=False,variant_id='',axis_mode='focused'):
 documented=[r for r in rows if AUDIT[r['observation_id']]['status']=='Plotted'];eligible=[r for r in documented if visible(AUDIT[r['observation_id']])];bb=bounds(rows,axis_mode);scale=float(rows[0]['axis_max_native']);yy=lambda v:BOTTOM-float(v)/scale*(BOTTOM-TOP)
 shown_curve=False
 parts=[]
 def text(x,y,t,size=17,**attrs):
  at=' '.join(f'{k.replace("_","-")}="{E(v)}"' for k,v in attrs.items());return f'<text x="{x}" y="{y}" font-size="{size}" {at}>{E(t)}</text>'
 parts.append(f'<rect width="860" height="{H}" fill="white"/>')
 title=heading if len(heading)<85 else heading[:82]+'…'
 parts.append(text(LEFT,28,title,18,font_weight='700'))
 for i,line in enumerate(textwrap.wrap(condition,98)[:2]):parts.append(text(LEFT,49+i*17,line,14,fill='#526670'))
 for q in ([] if all(r.get('plot_eligible')=='False' for r in rows) else [0,.25,.5,.75,1]):
  y=yy(scale*q);parts.append(f'<line x1="{LEFT}" x2="{RIGHT}" y1="{y}" y2="{y}" stroke="#e2e8eb"/>');parts.append(text(LEFT-14,y+6,format(scale*q,'.4g'),16,text_anchor='end',fill='#526670'))
 parts.append(f'<path d="M{LEFT},{TOP} L{LEFT},{BOTTOM} L{RIGHT},{BOTTOM}" fill="none" stroke="#728894" stroke-width="1.2"/>')
 parts.append(text((LEFT+RIGHT)/2,490,'Model release date'+(' · common range' if axis_mode=='shared' else ' · chart-specific range'),18,text_anchor='middle',fill='#294a5e'))
 parts.append(f'<text transform="translate(25,{(TOP+BOTTOM)/2}) rotate(-90)" font-size="18" fill="#294a5e" text-anchor="middle">Benchmark performance</text>')
 if bb:
  d0,d1=bb;xx=lambda d:LEFT+(dt.date.fromisoformat(d)-d0).days/(d1-d0).days*(RIGHT-LEFT)
  # Calendar spacing on a real date axis; endpoints remain visible.
  t0,t1=d0,d1;span=(t1-t0).days
  if span>700:step=6
  elif span>300:step=3
  elif span>120:step=2
  else:step=1
  tickset={t0,t1};cur=dt.date(t0.year,t0.month,1)
  if span<=120:
   daystep=14 if span<=60 else 28
   cur=t0+dt.timedelta(days=daystep)
   while cur<t1:tickset.add(cur);cur+=dt.timedelta(days=daystep)
  else:
   while cur<=t1:
    if cur>=t0 and (cur.year*12+cur.month)%step==0:tickset.add(cur)
    m=cur.month+1;cur=dt.date(cur.year+(m>12),(m-1)%12+1,1)
  ticks=sorted(tickset);selected=[]
  for d in ticks:
   if not selected or xx(d.isoformat())-xx(selected[-1].isoformat())>88:selected.append(d)
  if selected and selected[-1]!=t1:
   if len(selected)>1 and xx(t1.isoformat())-xx(selected[-1].isoformat())<88:selected.pop()
   selected.append(t1)
  for d in selected:
   x=xx(d.isoformat());parts.append(f'<line x1="{x}" x2="{x}" y1="{TOP}" y2="{BOTTOM}" stroke="#edf0f2"/>');parts.append(text(x,BOTTOM+27,d.strftime('%d %b %y' if span<=120 else '%Y-%m'),15,text_anchor='middle',fill='#526670'))
  fit=mean_trends.FITS[variant_id]
  for segment in fit['segments']:
   segment=[row for row in segment if d0.isoformat()<=row['date_position']<=d1.isoformat()]
   if len(segment)<2:continue
   shown_curve=True
   path=' '.join(('M' if i==0 else 'L')+str(xx(row['date_position']))+','+str(yy(row['mean_native'])) for i,row in enumerate(segment))
   parts.append(f'<path class="mean-trend" data-series-id="{E(variant_id)}" d="{path}" fill="none" stroke="#a16e2f" stroke-width="2.5" stroke-dasharray="8 5"><title>Smoothed mean of reported model configurations; 180-day Gaussian kernel; descriptive, not a causal trend.</title></path>')
  # Identical date/value pairs coincide; no artificial date or score displacement.
  grouped=collections.OrderedDict()
  for r in eligible:
   a=AUDIT[r['observation_id']];grouped.setdefault((a['date_position'],r['score_native']),[]).append(r)
  label_boxes=[];label_candidates=[]
  for (date,value),group in grouped.items():
   r=group[0];a=AUDIT[r['observation_id']];x=xx(date);y=yy(value);radius=5.3+min(3,math.log2(len(group))*1.2);ids=' '.join(q['observation_id'] for q in group);target=('../benchmarks/'+filename+'.html' if download else '')+'#'+r['observation_id']
   tip=' | '.join(q['model']+': '+q['source_value_text']+'; release '+AUDIT[q['observation_id']]['release_date']+'; '+q['source_ref']+'; '+q['source_locator'] for q in group)
   parts.append(f'<a href="{target}" class="time-point" data-observation-ids="{ids}" data-date="{date}" data-score="{value}" aria-label="{E(tip)}"><title>{E(tip)}</title>')
   months=[AUDIT[q['observation_id']] for q in group if AUDIT[q['observation_id']]['date_precision']=='month']
   if months:parts.append(f'<line x1="{xx(min(m["date_low"] for m in months))}" x2="{xx(max(m["date_high"] for m in months))}" y1="{y}" y2="{y}" stroke="#869fac" stroke-width="2"/>')
   for q in group:
    lo=q['source_lower'];hi=q['source_upper']
    if not lo and q['uncertainty'] and q.get('uncertainty_kind')!='unspecified':
     m=re.search(r'±\s*([\d.]+)',q['source_value_text']) or re.search(r'SEM:\s*([\d.]+)',q['uncertainty'])
     if m:lo=float(value)-float(m[1]);hi=float(value)+float(m[1])
    if lo!='' and hi!='':parts.append(f'<line x1="{x}" x2="{x}" y1="{yy(lo)}" y2="{yy(hi)}" stroke="{BLUE}" stroke-width="1.6"/>')
   approximate=any(q['source_value_text'].startswith('≈') for q in group)
   parts.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="white" stroke="{BLUE if not approximate else "#8095a0"}" stroke-width="2"/>')
   if len(group)>1:parts.append(text(x,y+3,str(len(group)),10,text_anchor='middle',fill=BLUE))
   if approximate:parts.append(text(x+9,y-6,'≈',15,fill='#526670'))
   parts.append('</a>')
   label_candidates.append((x,y,r['model'],len(group)))
   if not preview:
    for q in group:PLOT_RECORDS.append(dict(variant_id=variant_id,observation_id=q['observation_id'],x=x,y=y,date_position=date,score_native=q['score_native'],axis_max_native=scale,date_min=d0.isoformat(),date_max=d1.isoformat(),source_ref=q['source_ref']))
  # Keep sparse labels clear of both other labels and every observed mark.
  metrics=font_metrics();point_boxes=[(x-9,y-9,x+9,y+9) for x,y,_,_ in label_candidates]
  for x,y,name,n in sorted(label_candidates,key=lambda t:(t[1],t[0])):
   if len(label_boxes)>=5:break
   # Keep source markers in raw model names/tooltips; the paper font lacks these glyphs.
   name=name.replace('★','').replace('🤔','').strip()
   label=name if len(name)<29 else name[:26]+'…';width=metrics.stringWidth(label,'Arial',14)
   for dx,dy in [(12,-14),(-width-12,-14),(12,26),(-width-12,26),(12,-34),(-width-12,-34),(12,46),(-width-12,46)]:
    bx,by=x+dx,y+dy;box=(bx-3,by-16,bx+width+3,by+5)
    if box[0]<LEFT+2 or box[2]>RIGHT-2 or box[1]<TOP+4 or box[3]>BOTTOM-3:continue
    if any(not(box[2]<b[0] or box[0]>b[2] or box[3]<b[1] or box[1]>b[3]) for b in label_boxes+point_boxes):continue
    label_boxes.append(box);parts.append(text(bx,by,label,14,fill='#294a5e',stroke='white',stroke_width='3',paint_order='stroke'));break
 if not eligible:
  message='Metric definition unresolved: source data only' if all(r.get('plot_eligible')=='False' for r in rows) else 'Release dates not documented'
  parts.append(text((LEFT+RIGHT)/2,235,message,23,text_anchor='middle',fill='#647b88'))
  parts.append(text((LEFT+RIGHT)/2,268,'Click the figure for the available results and sources.',16,text_anchor='middle',fill='#647b88'))
 undated=len(rows)-len(documented);held=sum(r.get('plot_eligible')=='False' for r in rows);refs=', '.join(dict.fromkeys(r['source_ref'] for r in rows))
 parts.append(text(LEFT,516,f'{len(eligible)} shown · {undated} undated · {held} definition-held · sources: {refs}'[:117],13,fill='#526670'))
 fit=mean_trends.FITS[variant_id]['summary']
 if shown_curve:
  parts.append('<line x1="100" x2="134" y1="539" y2="539" stroke="#a16e2f" stroke-width="2.5" stroke-dasharray="8 5"/>')
  note=f'Smoothed mean · {fit["n_configurations"]} configurations · {fit["n_release_dates"]} release dates · 180-day kernel'
  parts.append(text(145,544,note,13,fill='#7d5628'))
 elif fit['status']=='Fitted':parts.append(text(LEFT,544,'Mean curve has no supported segment in this date range.',13,fill='#647b88'))
 else:parts.append(text(LEFT,544,'No mean curve: '+fit['reason']+'.',13,fill='#647b88'))
 return f'<svg xmlns="http://www.w3.org/2000/svg" width="860" height="{H}" viewBox="0 0 860 {H}" class="release-plot" data-series-id="{E(variant_id)}" data-axis-policy="{"common" if axis_mode=="shared" else "data-adaptive"}" data-date-min="{bb[0].isoformat() if bb else ""}" data-date-max="{bb[1].isoformat() if bb else ""}" role="img" aria-label="{E(heading+" versus model release date")}" style="font-family:Arial,sans-serif">'+''.join(parts)+'</svg>',H
def write_audit(out):
 vals=list(AUDIT.values())
 for name,rows in [('release_date_audit.csv',vals),('time_plot_geometry.csv',PLOT_RECORDS)]:
  with (out/'data'/name).open('w',encoding='utf-8-sig',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 summary=dict(observations=len(vals),plotted=sum(r['status']=='Plotted' for r in vals),families_with_plotted_values=len({r['family'] for r in vals if r['status']=='Plotted'}),reasons=dict(collections.Counter(r['reason'] for r in vals if r['status']!='Plotted')))
 summary.update(axis_policy='Per-condition full eligible release-date range, with 14–60 days padding (30 days for a single exact date), capped at evidence cutoff',display_start=DISPLAY_START.isoformat(),display_end=DISPLAY_END.isoformat(),visible_observations=sum(visible(r) for r in vals),dated_outside_window=0,definition_held_within_window=sum(r['status']=='Plotted' and r.get('metric_plot_eligible')=='False' for r in vals),families_with_visible_values=len({r['family'] for r in vals if visible(r)}))
 (out/'data/release_plot_summary.json').write_text(json.dumps(summary,indent=2));mean_trends.write_audit(out);return summary

def export_pdf(path,svgs):
 """Export our simple, explicit SVG geometry to a vector PDF without new dependencies."""
 from reportlab.pdfgen import canvas
 import xml.etree.ElementTree as ET
 font_metrics()
 scale=.72;c=canvas.Canvas(str(path),pagesize=(W*scale,H*scale),invariant=1)
 def color(s):return s if s and s!='none' else '#ffffff'
 for svg in svgs:
  c.saveState();c.scale(scale,scale);root=ET.fromstring(svg)
  for e in root.iter():
   tag=e.tag.rsplit('}',1)[-1]
   if tag in ['svg','a','title']:continue
   stroke=e.get('stroke');fill=e.get('fill','#1d2b32')
   if stroke:c.setStrokeColor(color(stroke))
   c.setFillColor(color(fill));c.setLineWidth(float(e.get('stroke-width','1')))
   c.setDash([float(x) for x in e.get('stroke-dasharray','').split()] or [])
   if tag=='rect':c.rect(float(e.get('x','0')),H-float(e.get('y','0'))-float(e.get('height','0')),float(e.get('width','0')),float(e.get('height','0')),stroke=bool(stroke),fill=fill!='none')
   elif tag=='line':c.line(float(e.get('x1')),H-float(e.get('y1')),float(e.get('x2')),H-float(e.get('y2')))
   elif tag=='circle':c.circle(float(e.get('cx')),H-float(e.get('cy')),float(e.get('r')),stroke=1,fill=1)
   elif tag=='path':
    p=c.beginPath()
    for command,x,y in re.findall(r'([ML])([\d.]+),([\d.]+)',e.get('d','')):
     (p.moveTo if command=='M' else p.lineTo)(float(x),H-float(y))
    c.drawPath(p,stroke=bool(stroke),fill=fill!='none')
   elif tag=='text':
    c.saveState();font='Arial-Bold' if e.get('font-weight')=='700' else 'Arial';c.setFont(font,float(e.get('font-size','16')))
    trans=e.get('transform','');x=float(e.get('x','0'));y=H-float(e.get('y','0'))
    if trans:
     x0,y0=map(float,re.search(r'translate\(([\d.]+),([\d.]+)\)',trans).groups());c.translate(x0,H-y0);c.rotate(90);x=y=0
    text=''.join(e.itertext());fn=c.drawCentredString if e.get('text-anchor')=='middle' else c.drawRightString if e.get('text-anchor')=='end' else c.drawString;fn(x,y,text);c.restoreState()
  c.restoreState();c.showPage()
 c.save()
