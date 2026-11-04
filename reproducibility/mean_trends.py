"""Descriptive kernel regressions within a single source/metric/task condition.
No extrapolation, cross-benchmark pooling, causal interpretation or invented CI.
"""
import collections,csv,datetime as dt,math,json,re
FITS={};INPUTS=[];GRID=[];SUMMARIES=[]
BANDWIDTH_DAYS=180;SENSITIVITY=[90,180,365]
def predict(points,day,bandwidth):
 weights=[math.exp(-.5*((p['day']-day)/bandwidth)**2) for p in points]
 total=sum(weights)
 if not total:return None,0
 mean=sum(w*p['value'] for w,p in zip(weights,points))/total
 neff=total*total/sum(w*w for w in weights)
 return mean,neff

def prepare(data,audit):
 global FITS,INPUTS,GRID,SUMMARIES
 FITS={};INPUTS=[];GRID=[];SUMMARIES=[]
 groups=collections.OrderedDict()
 for r in data:groups.setdefault(r['series_id'],[]).append(r)
 for sid,rows in groups.items():
  dated=[r for r in rows if audit[r['observation_id']]['status']=='Plotted' and r.get('plot_eligible')!='False']
  exact=[r for r in dated if not r['source_value_text'].startswith('≈')]
  collapsed=collections.OrderedDict()
  for r in exact:
   a=audit[r['observation_id']]
   key=(r.get('canonical_model_identity') or re.sub(r'\s+',' ',r['model']).strip().lower(),a['release_date'])
   collapsed.setdefault(key,[]).append(r)
  pp=[]
  for (model,release),rr in collapsed.items():
   day=dt.date.fromisoformat(audit[rr[0]['observation_id']]['date_position']).toordinal()
   value=sum(float(r['score_native']) for r in rr)/len(rr)
   record=dict(series_id=sid,family=rows[0]['family'],model=rr[0]['model'],release_date=release,date_position=dt.date.fromordinal(day).isoformat(),score_native=value,input_count=len(rr),observation_ids=' '.join(r['observation_id'] for r in rr))
   INPUTS.append(record);pp.append(dict(day=day,value=value,**record))
  dates={p['release_date'] for p in pp};span=max([p['day'] for p in pp],default=0)-min([p['day'] for p in pp],default=0)
  reason=''
  if all(r.get('plot_eligible')=='False' for r in rows):reason='Metric or version definition unresolved; source data retained'
  elif len(pp)<5:reason='Fewer than five dated model configurations'
  elif len(dates)<4:reason='Fewer than four distinct release dates'
  elif span<90:reason='Release-date coverage shorter than 90 days'
  curves={};segments=[]
  if not reason:
   first,last=min(p['day'] for p in pp),max(p['day'] for p in pp)
   days=sorted({round(first+(last-first)*i/100) for i in range(101)})
   for bandwidth in SENSITIVITY:
    curve=[]
    for day in days:
     value,neff=predict(pp,day,bandwidth)
     supported=min(abs(day-p['day']) for p in pp)<=bandwidth and neff>=2
     row=dict(series_id=sid,date_position=dt.date.fromordinal(day).isoformat(),bandwidth_days=bandwidth,mean_native=value,effective_configurations=neff,local_support=supported,n_configurations=len(pp),n_release_dates=len(dates))
     GRID.append(row);curve.append(row)
    curves[bandwidth]=curve
   segment=[]
   for row in curves[BANDWIDTH_DAYS]:
    if row['local_support']:segment.append(row)
    else:
     if len(segment)>=2:segments.append(segment)
     segment=[]
   if len(segment)>=2:segments.append(segment)
   if not segments:reason='Insufficient local support for a mean curve'
  summary=dict(series_id=sid,family=rows[0]['family'],metric=rows[0]['metric'],condition=rows[0]['condition'],n_observations=len(rows),n_dated=len(dated),n_exact_dated=len(exact),n_configurations=len(pp),n_release_dates=len(dates),span_days=span,status='Fitted' if not reason else 'Not fitted',reason=reason,bandwidth_days=BANDWIDTH_DAYS,curve_segments=len(segments),curve_grid_points=sum(len(s) for s in segments),approximate_observations_excluded=len(dated)-len(exact))
  FITS[sid]=dict(summary=summary,segments=segments,curves=curves,points=pp);SUMMARIES.append(summary)
 return FITS

def write_audit(out):
 for name,rows in [('mean_curve_inputs.csv',INPUTS),('mean_curve_grid.csv',GRID),('mean_curve_summary.csv',SUMMARIES)]:
  assert rows,name
  with (out/'data'/name).open('w',encoding='utf-8-sig',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 summary=dict(method='Nadaraya-Watson Gaussian kernel regression',bandwidth_days=BANDWIDTH_DAYS,sensitivity_bandwidth_days=SENSITIVITY,minimum_configurations=5,minimum_release_dates=4,minimum_span_days=90,weighting='One weight per model-configuration/release/condition; repeated results averaged first',uncertainty='No confidence interval: selected reported configurations are not a probability sample',extrapolation=False,conditions=len(SUMMARIES),conditions_with_curve=sum(s['status']=='Fitted' for s in SUMMARIES),families_with_curve=len({s['family'] for s in SUMMARIES if s['status']=='Fitted'}),nonfit_reasons=dict(collections.Counter(s['reason'] for s in SUMMARIES if s['reason'])))
 (out/'data/mean_curve_method.json').write_text(json.dumps(summary,indent=2));return summary
