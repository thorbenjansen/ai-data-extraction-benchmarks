"""Independently recover selection inputs from source observations and audit UI binding."""
from pathlib import Path
from collections import defaultdict, Counter
from datetime import date
import csv, hashlib, json, math, re
import numpy as np
from lxml import html as H

ROOT=Path(__file__).resolve().parent.parent
def read(name):
    with (ROOT/'data'/name).open(encoding='utf-8-sig',newline='')as f:return list(csv.DictReader(f))
selection=json.loads((ROOT/'data/progress_selection.json').read_text())
criteria=selection['criteria'];selected=set(selection['families'])
raw=read('article_observations.csv');audit={r['observation_id']:r for r in read('release_date_audit.csv')}
original=json.loads((ROOT/'reproducibility/inputs/selected50_snapshot_manifest.json').read_text())['files']
checked=0
for path,digest in original.items():
    if path.startswith(('data/','figures/'))or path=='All_Benchmarks_Article_Atlas.pdf':
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
        checked+=1
recovered=defaultdict(lambda:defaultdict(list))
for r in raw:
    a=audit[r['observation_id']]
    if a['status']!='Plotted'or r['plot_eligible']=='False'or r['source_value_text'].startswith('≈'):continue
    model=r.get('canonical_model_identity')or re.sub(r'\s+',' ',r['model']).strip().lower()
    recovered[r['series_id']][(model,a['release_date'])].append((r,a))
decisions={r['series_id']:r for r in read('progress_condition_decisions.csv')}
curve_points=defaultdict(list)
for r in read('mean_curve_grid.csv'):
    if r['local_support']=='True':curve_points[(r['series_id'],int(r['bandwidth_days']))].append(r)
familyflags=defaultdict(list);obsids=set();shown=set();qualified=set()
for sid,decision in decisions.items():
    configs=[];perdate=defaultdict(list)
    for rr in recovered[sid].values():
        day=date.fromisoformat(rr[0][1]['date_position']).toordinal()
        value=float(np.mean([float(r['score_native'])for r,a in rr]))
        configs.append((day,value));perdate[day].append(value)
    xx=np.array(sorted(perdate),dtype=float)
    yy=np.array([np.median(perdate[d])for d in xx],dtype=float)
    n=len(configs);nd=len(xx);span=int(xx[-1]-xx[0])if nd else 0
    assert(n,nd,span)==(int(decision['n_configurations']),int(decision['n_release_dates']),int(decision['span_days'])),sid
    enough=n>=criteria['minimum_configurations']and nd>=criteria['minimum_release_dates']and span>=criteria['minimum_span_days']
    if enough:
        direction=-1 if decision['metric_direction']=='lower'else 1
        dx=xx[None,:]-xx[:,None];dy=direction*(yy[None,:]-yy[:,None])
        upper=np.triu(np.ones((nd,nd),dtype=bool),1)
        slopes=dy[upper]/dx[upper]
        tau=float(np.sign(slopes).sum()/len(slopes));slope=float(np.median(slopes))*365.25
        k=max(2,nd//3);contrast=direction*float(np.median(yy[-k:])-np.median(yy[:k]))
        assert math.isclose(tau,float(decision['date_median_tau_a']),abs_tol=1e-12),sid
        assert math.isclose(slope,float(decision['theil_sen_native_units_per_year']),abs_tol=1e-10),sid
        assert math.isclose(contrast,float(decision['directional_median_change']),abs_tol=1e-10),sid
        changes=[]
        for bw in [90,180,365]:
            grid=sorted(curve_points[(sid,bw)],key=lambda r:r['date_position'])
            means=[]
            for endpoint in [grid[0],grid[-1]]:
                day=date.fromisoformat(endpoint['date_position']).toordinal()
                weights=np.exp(-.5*((np.array([d for d,v in configs])-day)/bw)**2)
                mean=float(np.dot(weights,[v for d,v in configs])/weights.sum())
                assert math.isclose(mean,float(endpoint['mean_native']),abs_tol=1e-9),sid
                means.append(mean)
            change=direction*(means[1]-means[0]);changes.append(change)
            assert math.isclose(change,float(decision[f'directional_curve_change_{bw}d']),abs_tol=1e-9),sid
        qualifies=tau>=criteria['minimum_date_median_tau_a']and slope>0 and contrast>0 and min(changes)>0
        contrary=slope<=0 or contrast<=0 or min(changes)<=0
        assert qualifies==(decision['progress']=='True')and contrary==(decision['contrary']=='True'),sid
        familyflags[decision['family']].append((qualifies,contrary))
        if decision['family']in selected:
            shown.add(sid)
            if qualifies:qualified.add(sid)
            for rr in recovered[sid].values():obsids.update(r['observation_id']for r,a in rr)
    else:assert decision['adequate']=='False',sid
expected={f for f,flags in familyflags.items()if any(q for q,c in flags)and not any(c for q,c in flags)}
assert selected==expected
assert shown==set(selection['displayed_series_ids'])and qualified==set(selection['qualifying_series_ids'])
assert len(obsids)==selection['counts']['displayed_source_observations']==650
assert {r['observation_id']for r in read('progress_observations.csv')}==obsids
for r in read('progress_observations.csv'):
    assert r['benchmark_reference_apa']and r['result_reference_apa']and r['source_url']and r['source_locator']and r['release_source_url'],r['observation_id']
home=H.parse(str(ROOT/'index.html')).getroot()
cards=home.xpath('//article[@data-family]')
assert {c.get('data-family')for c in cards}==selected
variants=set()
index={c['family']:c for c in json.loads((ROOT/'data/time_chart_index.json').read_text())}
for card in cards:
    family=card.get('data-family')
    available={v['path']:v['id']for v in index[family]['time_variants']}
    options=card.xpath('.//select[@class="time-variant"]/option')
    displayed={available[o.get('value')]for o in options}
    assert displayed=={sid for sid in shown if decisions[sid]['family']==family}
    variants.update(displayed)
    default=card.xpath('.//select[@class="time-variant"]/option[@selected]')[0]
    assert available[default.get('value')]in qualified
    assert card.xpath('.//img[@class="time-preview"]/@src')[0]==default.get('value')
assert variants==shown and len(cards)==13
order=json.loads((ROOT/'data/progress_display_order.json').read_text())
for section in home.xpath('//section[@data-challenge]'):
    families=[c.get('data-family')for c in section.xpath('.//article[@data-family]')]
    assert families==order['challenge_order'][section.get('data-challenge')]
    values={r['family']:r for r in order['default_conditions']}
    assert all(values[a]['gain_as_percent_of_axis']>=values[b]['gain_as_percent_of_axis']for a,b in zip(families,families[1:]))
assert {c:fs[0]for c,fs in order['challenge_order'].items()}=={'A':'OmniDocBench','B':'LongBench','C':'GSM-Symbolic','D':'TableBench'}
archive=H.parse(str(ROOT/'evidence.html')).getroot()
assert len(archive.xpath('//tbody/tr'))==50
assert not (ROOT/'claims.html').exists()
report=dict(status='passed',source_scientific_files_byte_identical=checked,independent_input_source='Original source observations plus release audit, without using mean_curve_inputs for model counts or trend calculations',current_families=sorted(selected),current_conditions=len(shown),current_dated_observations=len(obsids),homepage_assignments=len(cards),challenge_family_counts=selection['counts']['challenge_family_counts'],original_values_and_figures_modified=False)
(ROOT/'data/progress_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
