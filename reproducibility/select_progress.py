"""Select well-populated, consistently improving series from the frozen atlas.

This is an explicitly outcome-selected illustration, not an estimate of the
prevalence or average size of progress. Original values and curves are read only.
"""
from pathlib import Path
from collections import defaultdict, Counter
from datetime import date
from statistics import median
import csv, hashlib, json

ROOT = Path(__file__).resolve().parent.parent
MIN_CONFIGURATIONS = 10
MIN_DATES = 6
MIN_DAYS = 180
MIN_TAU = 0.30


def read(name):
    with (ROOT / 'data' / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write(name, rows):
    with (ROOT / 'data' / name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    register = read('article_benchmark_register.csv')
    obs = {r['observation_id']: r for r in read('article_observations.csv')}
    inputs, grids = defaultdict(list), defaultdict(list)
    for r in read('mean_curve_inputs.csv'):
        inputs[r['series_id']].append(r)
    for r in read('mean_curve_grid.csv'):
        if r['local_support'] == 'True':
            grids[(r['series_id'], int(r['bandwidth_days']))].append(r)
    decisions = []
    for condition in read('article_conditions.csv'):
        sid = condition['series_id']
        rows = inputs[sid]
        daily = defaultdict(list)
        for r in rows:
            daily[r['date_position']].append(float(r['score_native']))
        points = [(date.fromisoformat(d).toordinal(), median(v))
                  for d, v in sorted(daily.items())]
        span = points[-1][0] - points[0][0] if points else 0
        directions = {obs[r['observation_ids'].split()[0]]['higher_is_better'] for r in rows}
        assert len(directions) <= 1, sid
        sign = -1 if directions == {'False'} else 1
        slopes = [sign * (b[1] - a[1]) / (b[0] - a[0])
                  for i, a in enumerate(points) for b in points[i+1:]]
        tau = sum((v > 0) - (v < 0) for v in slopes) / len(slopes) if slopes else None
        slope = median(slopes) * 365.25 if slopes else None
        k = max(2, len(points) // 3)
        early = median(y for _, y in points[:k]) if points else None
        late = median(y for _, y in points[-k:]) if points else None
        delta = sign * (late - early) if points else None
        increases = {}
        for bw in [90, 180, 365]:
            grid = sorted(grids[(sid, bw)], key=lambda r: r['date_position'])
            increases[bw] = sign * (float(grid[-1]['mean_native']) - float(grid[0]['mean_native'])) if len(grid) >= 2 else None
        enough = len(rows) >= MIN_CONFIGURATIONS and len(daily) >= MIN_DATES and span >= MIN_DAYS and condition['mean_curve_status'] == 'Fitted'
        positive = enough and slope > 0 and delta > 0 and all(v is not None and v > 0 for v in increases.values())
        progress = positive and tau >= MIN_TAU
        contrary = enough and (slope <= 0 or delta <= 0 or any(v is None or v <= 0 for v in increases.values()))
        reason = ('Positive trend meets the descriptive criteria' if progress else
                  'Mixed or nonpositive temporal comparisons' if contrary else
                  'Positive direction, weaker date-level association' if enough else
                  'Insufficient comparable dated configurations, release dates, temporal coverage or curve support')
        decisions.append(dict(figure_id=condition['figure_id'], family=condition['family'], series_id=sid,
                              metric=condition['metric'], condition=condition['condition'], metric_direction=condition['metric_direction'],
                              n_configurations=len(rows), n_release_dates=len(daily), span_days=span,
                              date_median_tau_a=tau, theil_sen_native_units_per_year=slope,
                              early_third_median=early, late_third_median=late, directional_median_change=delta,
                              directional_curve_change_90d=increases[90], directional_curve_change_180d=increases[180], directional_curve_change_365d=increases[365],
                              adequate=bool(enough), progress=bool(progress), contrary=bool(contrary), reason=reason,
                              observation_ids='; '.join(oid for r in rows for oid in r['observation_ids'].split())))
    byfamily = defaultdict(list)
    for r in decisions:
        byfamily[r['family']].append(r)
    families = []
    for r in register:
        rows = byfamily[r['family']]
        enough = [x for x in rows if x['adequate']]
        positive = [x for x in rows if x['progress']]
        contrary = [x for x in rows if x['contrary']]
        included = bool(positive) and not contrary
        reason = ('Included: at least one well-populated positive series and no contrary adequately sampled series' if included else
                  'Mixed evidence: at least one adequately sampled condition has a nonpositive or inconsistent direction' if contrary else
                  'Adequately sampled, but no series meets the positive-trend criteria' if enough else
                  'No condition meets the minimum data and temporal-coverage criteria')
        families.append(dict(figure_id=r['figure_id'], family=r['family'], included=included,
                             adequate_conditions=len(enough), progress_conditions=len(positive), contrary_conditions=len(contrary),
                             commentary_challenges=r['commentary_challenges'], workflow_steps=r['workflow_steps'], reason=reason))
    selected = {r['family'] for r in families if r['included']}
    shown = [r for r in decisions if r['family'] in selected and r['adequate']]
    selected_ids = {oid for r in shown for oid in r['observation_ids'].split('; ')}
    counts = Counter(c.strip() for r in families if r['included'] for c in r['commentary_challenges'].split(';'))
    output = dict(version='2026-11-04',source_cutoff='2026-10-31', purpose='Illustrative selection of well-populated positive release-date trends',
                  inference_limit='Selection explicitly depends on observed progress. It cannot estimate the proportion of benchmarks improving, average general progress, a causal effect of release date, human superiority or transfer to psychological data extraction.',
                  criteria=dict(minimum_configurations=MIN_CONFIGURATIONS,minimum_release_dates=MIN_DATES,minimum_span_days=MIN_DAYS,minimum_date_median_tau_a=MIN_TAU,
                                positive_theil_sen_slope=True,positive_early_late_third_median_difference=True,positive_supported_curve_change_at_bandwidth_days=[90,180,365],
                                family_rule='At least one qualifying condition; no contrary adequately sampled condition. All adequately sampled conditions in an included family are shown, including weaker positive trends.'),
                  trend_unit='Median native score at each distinct documented release position; tied values contribute zero to tau-a. Month-only dates retain their documented interval and midpoint positioning.',
                  configurations='Existing exact, plotted model-configuration/release/condition inputs, with repeated results averaged first. No count of benchmark questions is used as the model sample size.',
                  native_change='Higher-is-better direction; native units are never pooled across benchmarks. Annualized slopes describe the observed interval and are not forecasts.',
                  counts=dict(archive_families=len(register),selected_families=len(selected),archived_families=len(register)-len(selected),displayed_conditions=len(shown),displayed_source_observations=len(selected_ids),displayed_configurations=sum(r['n_configurations'] for r in shown),challenge_family_counts=dict(sorted(counts.items()))),
                  families=[r['family'] for r in families if r['included']],
                  displayed_series_ids=[r['series_id'] for r in shown],
                  qualifying_series_ids=[r['series_id'] for r in shown if r['progress']],
                  input_sha256={name:hashlib.sha256((ROOT/'data'/name).read_bytes()).hexdigest() for name in ['article_observations.csv','article_conditions.csv','mean_curve_inputs.csv','mean_curve_grid.csv']})
    write('progress_condition_decisions.csv',decisions)
    write('progress_family_decisions.csv',families)
    write('progress_benchmark_register.csv',[r for r in register if r['family'] in selected])
    write('progress_observations.csv',[r for r in obs.values() if r['observation_id'] in selected_ids])
    (ROOT/'data/progress_selection.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(output['counts'],indent=2))
    print('Selected:', ', '.join(output['families']))


if __name__ == '__main__':
    main()
