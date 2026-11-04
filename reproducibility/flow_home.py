from html import escape as E
from timeplots import ORDER

def render(figures,steps,maps,catalogue,bibliography,apa_html):
 bystep={s['id']:s for s in steps};ff={f['family']:f for f in figures}
 body='''<div class="flow-intro"><p class="eyebrow">Data-extraction workflow · benchmark supplement</p><h1>From source documents to an auditable extraction</h1><p class="lead">Scroll down through the workflow. Scroll right within a step to compare its benchmarks.</p><p class="flow-help">X: documented model release date, with each condition focused on its full available release-date range. The time span can differ between figures. Y: performance in the benchmark’s original metric. The dashed line estimates the mean of reported model configurations where temporal coverage is sufficient. All eligible documented dates are shown, including older models. Compare the calendar labels across figures. Click a figure to open the data and references.</p><p class="integration-note">Updated 31 October 2026: 1,085 additional model-card values, with separate source/task conditions. 125 values with unreported metric/version details remain available as source data. <a href="methods.html#model-cards">Definition decisions</a>.</p><div class="flow-tools"><label>Find a benchmark<input id="flow-search" type="search" placeholder="Name, task or workflow step…"></label><span id="flow-count" aria-live="polite">82 benchmark families · 12 workflow steps</span><a href="model-releases.html">Model release-date sources</a><a href="methods.html#mean-curves">How mean curves are fitted</a></div></div>'''
 shortnames=['Define','Prepare','Locate','Assign','Code','Coordinate','Calculate','Verify','Collaborate','Adjudicate','Evaluate','Document']
 body+='<nav class="step-jump" aria-label="Workflow steps">'+''.join(f'<a href="#step-{s}"><span>{i:02}</span> {shortnames[i-1]}</a>' for i,s in enumerate(ORDER,1))+'</nav><div class="flow-sequence">'
 for num,sid in enumerate(ORDER,1):
  step=bystep[sid];matches=[m for arr in maps.values() for m in arr if m['step']==sid]
  families=list(dict.fromkeys(m['family'] for m in matches))
  partial=sid=='audit'
  if partial:families=['ALCE','DTBench','CONSORT diagrams']
  def key(fam):
   f=ff[fam];levels=[m['level'] for m in matches if m['family']==fam]
   return (bool(f['primary_variant']['plotted']),any(x.startswith('Direct') for x in levels),f['primary_variant']['plotted'],-int(f['figure_id'][1:]))
  families.sort(key=key,reverse=True)
  body+=f'<section class="flow-step" id="step-{sid}" data-step-id="{sid}"><div class="step-copy"><div class="step-number">{num:02}</div><p class="eyebrow">Extraction step</p><h2>{E(step["name"])}</h2><p>{E(step["task"])}</p>'
  if partial:body+='<p class="step-gap">No benchmark here tests the complete audit trail. The adjacent figures show partial diagnostics.</p>'
  else:body+=f'<p class="step-count">{len(families)} benchmark families</p>'
  body+=f'<div class="rail-buttons"><button type="button" data-rail="rail-{sid}" data-direction="-1" aria-label="Previous benchmarks for {E(step["name"])}">←</button><button type="button" data-rail="rail-{sid}" data-direction="1" aria-label="Next benchmarks for {E(step["name"])}">→</button><span class="rail-position" aria-live="polite">1 / {len(families)}</span></div><details class="step-limit"><summary>What still needs testing</summary><p>{E(step["gap"])}</p></details></div>'
  body+=f'<div class="benchmark-rail" id="rail-{sid}" tabindex="0" role="region" aria-label="Benchmarks for {E(step["name"])}">'
  for fam in families:
   f=ff[fam];v=f['primary_variant'];variants=f['time_variants'];path='benchmarks/'+f['filename']+'.html';cc=next(c for c in catalogue if c['family']==fam)
   levels=list(dict.fromkeys(m['level'] for m in matches if m['family']==fam));level='Partial diagnostic' if partial else next((l for l in levels if l.startswith('Direct')),levels[0])
   search=' '.join([fam,step['name'],cc['task']]).lower()
   body+=f'<article class="flow-card" data-family="{E(fam)}" data-search="{E(search)}"><header><div><p class="eyebrow">{f["figure_id"]} · {E(level)}</p><h3><a href="{path}#results">{E(fam)}</a></h3></div><span class="date-state">'+('Documented model releases' if v['plotted'] else 'Metric/version definition unresolved' if v.get('definition_held')==v['observations'] else 'Definition/date unresolved' if v['dated'] else 'Release dates unresolved')+'</span></header>'
   body+=f'<label class="variant-label">Benchmark condition<select class="time-variant" aria-label="Condition for {E(fam)} at step {num}">'
   for vv in variants:
    label=vv['heading']+' · '+vv['condition'];short=label if len(label)<115 else label[:112]+'…'
    body+=f'<option value="{E(vv["path"])}" data-condition="{E(vv["condition"])}" data-plotted="{vv["plotted"]}" data-dated="{vv["dated"]}" data-total="{vv["observations"]}" data-definition-held="{vv.get("definition_held",0)}" data-undated="{vv.get("undated",vv["observations"]-vv["dated"])}" data-range-start="{vv["date_min"]}" data-range-end="{vv["date_max"]}" data-benchmark-id="{E(vv["benchmark_id"])}" data-apa-html="{E(apa_html(bibliography[vv["benchmark_id"]]))}"'+(' selected' if vv['id']==v['id'] else '')+f'>{E(short)}</option>'
   body+='</select></label>'
   body+=f'<a class="figure-link" href="{path}#records" aria-label="Open the data and references for {E(fam)}"><img class="time-preview" src="{E(v["path"])}" alt="{E(fam)}: benchmark performance versus model release date, with a descriptive mean curve where supported" width="860" height="565" loading="lazy"><span class="figure-open">Open data and references ↗</span></a>'
   body+=f'<div class="benchmark-apa" data-benchmark-id="{E(v["benchmark_id"])}"><p class="eyebrow">Benchmark reference (APA)</p>'+apa_html(bibliography[v['benchmark_id']])+'</div>'
   body+=f'<div class="card-foot"><span class="variant-count">{v["plotted"]} shown / {v["observations"]} observations · {v.get("undated",v["observations"]-v["dated"])} undated · {v.get("definition_held",0)} definition-held</span><span>Original metric · separate task conditions</span></div></article>'
  body+='</div></section>'
 body+='</div><p class="flow-bottom">Dates describe the named model’s public release, including source-reported release months. Checkpoint and result dates alone are not treated as release dates. Missing dates remain visible as gaps; all source values remain on the benchmark pages.</p>'
 return body
