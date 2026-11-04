"""Render a focused A–D/workflow homepage and preserve the 50-family source archive.

Only presentation and navigation are rebuilt. Scores, mappings, sources,
release dates, SVGs, PDFs and curve inputs are read without modification.
"""
from pathlib import Path
from collections import Counter
from html import escape as esc
from urllib.parse import urlsplit, urlunsplit, parse_qs
from lxml import html as H
import csv
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
ORDER = ['protocol', 'documents', 'retrieve', 'bind', 'code', 'coordinate',
         'derive', 'verify', 'collaborate', 'adjudicate', 'product', 'audit']
SHORT = ['Define', 'Prepare', 'Locate', 'Assign', 'Code', 'Coordinate',
         'Calculate', 'Verify', 'Collaborate', 'Adjudicate', 'Evaluate', 'Document']
PARTIAL = {'ALCE', 'DTBench', 'CONSORT diagrams'}
ARCHIVED_FIGURES = set()


def read(name):
    with (ROOT / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def load(name):
    return json.loads((ROOT / name).read_text())


def save(path, doc):
    path.write_text('<!doctype html>' + H.tostring(doc, encoding='unicode', method='html'))


def citation(c):
    text = esc(c['apa'])
    if c.get('url'):
        text = text.replace(esc(c['url']), f'<a href="{esc(c["url"])}">{esc(c["url"])}</a>')
    return (f'<div class="citation"><p>{text}</p><button class="copy" '
            f'data-copy="{esc(c["apa"])}" type="button">Copy APA reference</button></div>')


def redirect_document(name):
    # Preserve previous entry points, query filters and their published anchors.
    base = 'index.html#workflow-map' if name == 'workflow.html' else 'index.html'
    script = '''const u=new URL('index.html',location.href),p=new URLSearchParams(location.search);u.search=p.toString();let h=location.hash;
if(location.pathname.endsWith('/workflow.html'))h=h?'#step-'+h.slice(1):'#workflow-map';
if(!h&&p.get('challenge'))h='#challenge-'+p.get('challenge');u.hash=h;location.replace(u.href);'''
    return H.fromstring(f'''<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Challenges &amp; workflow | Data extraction benchmarks</title><link rel="canonical" href="https://thorbenjansen.github.io/ai-data-extraction-benchmarks/index.html"><script>{script}</script></head><body><main><h1>Challenges and workflow are now on one page</h1><p><a href="{base}">Open the combined benchmark supplement</a></p></main></body></html>''')


def retarget(value, context_path):
    u = urlsplit(value)
    if u.scheme or u.netloc:
        return value
    p = Path(u.path)
    if p.name in {'index.html', 'workflow.html', 'challenges.html', 'all-benchmarks.html'} and u.fragment in ARCHIVED_FIGURES and (context_path.parent/p).resolve().parent == ROOT:
        return urlunsplit(('', '', str(p.with_name('archive.html')), u.query, u.fragment))
    if p.name not in {'workflow.html', 'challenges.html', 'all-benchmarks.html'}:
        return value
    if (context_path.parent/p).resolve().parent!=ROOT:
        return value
    fragment = u.fragment
    if p.name == 'workflow.html':
        fragment = 'step-' + fragment if fragment else 'workflow-map'
    if not fragment and parse_qs(u.query).get('challenge'):
        fragment = 'challenge-' + parse_qs(u.query)['challenge'][0]
    return urlunsplit(('', '', str(p.with_name('index.html')), u.query, fragment))


def build():
    global ARCHIVED_FIGURES
    archive_register = read('data/article_benchmark_register.csv')
    selection = load('data/progress_selection.json')
    family_decisions = {r['family']: r for r in read('data/progress_family_decisions.csv')}
    condition_decisions = {r['series_id']: r for r in read('data/progress_condition_decisions.csv')}
    condition_metadata = {r['series_id']: r for r in read('data/article_conditions.csv')}
    selected = set(selection['families'])
    register = [r for r in archive_register if r['family'] in selected]
    ARCHIVED_FIGURES = {r['figure_id'] for r in archive_register if r['family'] not in selected}
    charts = {f['family']: f for f in load('data/time_chart_index.json')}
    for family in selected:
        f = charts[family]
        f['time_variants'] = [v for v in f['time_variants'] if v['id'] in selection['displayed_series_ids']]
        qualified = [v for v in f['time_variants'] if v['id'] in selection['qualifying_series_ids']]
        previous = f['primary_variant']['id']
        f['primary_variant'] = next((v for v in qualified if v['id'] == previous), max(qualified, key=lambda v: int(condition_decisions[v['id']]['n_configurations'])))
    steps = {s['id']: s for s in load('data/workflow_steps.json')}
    definitions = load('data/challenge_definitions.json')
    defs = definitions['challenges']
    bib = load('data/bibliography.json')['benchmarks']
    mappings = [r for r in read('data/challenge_mapping.csv') if r['family'] in selected]
    counts = Counter(m['challenge'] for m in mappings)
    byfamily = {r['family']: r for r in register}
    stepmap = {r['family']: r['workflow_steps'].split('; ') for r in register}
    chmap = {r['family']: [c.strip() for c in r['commentary_challenges'].split(';')]
             for r in register}
    # Use the existing default condition, never a newly selected favorable subtask.
    # The axis-normalized gain is a display heuristic, not a pooled performance metric.
    display = {}
    for family in selected:
        sid = charts[family]['primary_variant']['id']
        decision = condition_decisions[sid]
        axis_max = float(condition_metadata[sid]['axis_max_native'])
        gain = float(decision['directional_curve_change_180d'])
        display[family] = dict(family=family, series_id=sid, condition=decision['condition'],
                               mean_curve_gain_native=gain, axis_max_native=axis_max,
                               gain_as_percent_of_axis=100*gain/axis_max,
                               date_median_tau_a=float(decision['date_median_tau_a']),
                               n_configurations=int(decision['n_configurations']),
                               span_days=int(decision['span_days']))
    def display_key(family):
        r = display[family]
        return (-r['gain_as_percent_of_axis'], -r['date_median_tau_a'],
                -r['n_configurations'], int(byfamily[family]['figure_id'][1:]))
    ordered = {c: sorted([r['family'] for r in register if c in chmap[r['family']]], key=display_key) for c in defs}
    order_audit = dict(version='2026-11-04', purpose='Illustrative left-to-right ordering within each challenge',
                       primary='Descending first-to-last supported 180-day mean-curve gain in the existing default condition, divided by its native score-axis maximum',
                       ties='Descending date-median tau-a, then configuration count, then figure ID',
                       limits='An editorial display heuristic. Benchmark tasks, difficulty, conditions and observed date spans differ; this is not a comparable effect size or a ranking of benchmark quality. Default conditions, observations and fitted curves are unchanged.',
                       challenge_order=ordered, default_conditions=[display[f] for f in sorted(selected)])
    (ROOT/'data/progress_display_order.json').write_text(json.dumps(order_audit,ensure_ascii=False,indent=2)+'\n')

    doc = H.parse(str(ROOT / 'index.html')).getroot()
    doc.find('body').set('class', 'workflow-home unified-home')
    doc.find('head/title').text = 'Challenges A–D & workflow | Data extraction benchmarks'
    main = doc.xpath('//main')[0]
    main.clear()
    main.set('id', 'content')
    body = f'''<div class="flow-intro"><p class="eyebrow">Data-extraction benchmark supplement · focused progress selection</p>
<h1>Challenges A–D across the extraction workflow</h1>
<p class="lead">Four challenges, one map. Scroll down through A–D and across their benchmark figures. Select a workflow step to explore its evidence.</p>
<p class="integration-note"><strong>{len(register)} benchmark families</strong> · {selection['counts']['displayed_source_observations']:,} dated observations · {selection['counts']['displayed_conditions']} separate test conditions. Each family has a well-populated positive time series; no adequately sampled condition shows a contrary direction.</p>
<p class="progress-selection-note">Selected to illustrate observed progress. This outcome-based selection cannot establish how often benchmarks improve or the average progress across all benchmarks. <a href="methods.html#progress-selection">Criteria and every inclusion decision</a> · <a href="archive.html">Full 50-family source archive</a>.</p>
<div class="challenge-jump" aria-label="Commentary challenges">'''
    for c, d in defs.items():
        body += (f'<a href="#challenge-{c}"><strong>{c}</strong><span>{esc(d["name"])}'
                 f'<small>{counts[c]} benchmark families</small></span></a>')
    body += '''</div><div class="flow-tools"><label>Find a benchmark<input id="flow-search" type="search" placeholder="Name, task or workflow step…"></label><label>Workflow step<select id="flow-step-filter"><option value="">All workflow steps</option>'''
    body += ''.join(f'<option value="{sid}" data-name="{esc(steps[sid]["name"])}" data-task="{esc(steps[sid]["task"])}" data-gap="{esc(steps[sid]["gap"])}">{i:02} · {esc(steps[sid]["name"])}</option>'
                    for i, sid in enumerate(ORDER, 1))
    body += f'''</select></label><button type="button" id="flow-reset">Show all selected benchmarks</button><span id="flow-count" role="status" aria-live="polite">{len(register)} benchmark families · 4 challenges</span></div>
<p class="flow-help">X: documented model release date. Y: the original benchmark metric. Date ranges can differ between figures; compare the calendar labels. Dashed curves describe mean performance within the named test condition. Within each challenge, the larger displayed mean-curve gains come first. <a href="methods.html#figure-order">How the figures are ordered</a>. Click a figure for its raw data and sources.</p>
<div class="supplement-links"><a href="model-releases.html">Model release-date sources</a><a href="methods.html#mean-curves">Mean-curve methods</a><a href="methods.html#progress-selection">Progress selection and limits</a><a href="archive.html">Source archive and PDF</a></div></div>
<details class="unified-workflow" id="workflow-map"><summary>The 12 workflow steps and their links to A–D</summary><p>Challenge badges indicate links through the mapped benchmark tasks. They do not establish that an entire step is validated. Select a step to filter the figures below.</p><div class="workflow-tiles">'''
    for i, sid in enumerate(ORDER, 1):
        families = [f for f in byfamily if sid in stepmap[f]]
        if sid == 'audit':
            families = sorted(PARTIAL & selected)
        related = sorted({c for f in families for c in chmap[f]})
        number = f'{len(families)} partial diagnostics' if sid == 'audit' else f'{len(families)} benchmark families'
        if not families:
            number = 'Evidence gap in this selection'
        badges = ''.join(f'<span class="mini-challenge">{c}</span>' for c in related)
        body += (f'<button id="step-{sid}" type="button" data-workflow-step="{sid}" aria-pressed="false">'
                 f'<span class="workflow-order">{i:02} · {SHORT[i-1]}</span><strong>{esc(steps[sid]["name"])}</strong>'
                 f'<span class="tile-challenges">{badges}</span><small>{number}</small></button>')
    body += '''</div><p class="map-source">The coding-protocol and interaction requirements remain distinct from A–D. Auditability, human–AI collaboration and adjudication have no direct benchmark in this focused progress selection. The source archive retains three partial audit diagnostics; none tests the complete audit trail. <a href="data/challenge_mapping.csv">Download all source challenge/workflow assignments</a>.</p></details>
<aside id="workflow-context" class="workflow-context" hidden aria-live="polite"><h2 id="workflow-context-title"></h2><p id="workflow-context-task"></p><p id="workflow-context-gap"></p></aside>
<p id="flow-empty" class="flow-empty" hidden>No benchmarks match this search and workflow step. Try another step or show all benchmarks.</p>
<div class="flow-sequence challenge-sequence">'''
    used_ids = set()
    for c, d in defs.items():
        families = ordered[c]
        related_steps = [s for s in ORDER if any(s in stepmap[f] for f in families)]
        body += (f'<section class="flow-step challenge-section" id="challenge-{c}" data-challenge="{c}">'
                 f'<div class="step-copy challenge-copy"><div class="step-number">{c}</div>'
                 f'<p class="eyebrow">Commentary challenge {c}</p><h2>{esc(d["name"])}</h2><p>{esc(d["definition"])}</p>'
                 f'<p class="step-count">{len(families)} benchmark families</p>'
                 f'<div class="rail-buttons"><button type="button" data-rail="rail-{c}" data-direction="-1" aria-label="Previous benchmarks for Challenge {c}">←</button>'
                 f'<button type="button" data-rail="rail-{c}" data-direction="1" aria-label="Next benchmarks for Challenge {c}">→</button>'
                 f'<span class="rail-position" aria-live="polite">1 / {len(families)}</span></div>'
                 '<details class="step-limit"><summary>Workflow links and mapping basis</summary><p>')
        body += ', '.join(esc(steps[s]['name']) for s in related_steps)
        body += (f'.</p><p>{esc(definitions["commentary"])} Physical PDF pp. {esc(d["pages"])}. '
                 'These are task-relevance mappings, not evidence that the full extraction workflow succeeds.</p></details></div>'
                 f'<div class="benchmark-rail" id="rail-{c}" tabindex="0" role="region" aria-label="Benchmarks for Challenge {c}">')
        for family in families:
            r, f = byfamily[family], charts[family]
            v = f['primary_variant']
            apa = citation(bib[v['benchmark_id']])
            figure_id = r['figure_id']
            card_id = figure_id if figure_id not in used_ids else figure_id + '-' + c
            used_ids.add(figure_id)
            search = ' '.join([family, r['task'], r['workflow_step_names'], r['challenge_names']]).lower()
            state = ('Documented model releases' if v['plotted'] else
                     'Metric/version definition unresolved' if v.get('definition_held') == v['observations'] else
                     'Definition/date unresolved' if v['dated'] else 'Release dates unresolved')
            body += (f'<article class="flow-card" id="{card_id}" data-family="{esc(family)}" '
                     f'data-challenges="{esc(" ".join(chmap[family]))}" data-steps="{esc(" ".join(stepmap[family]))}" '
                     f'data-diagnostic-steps="{"audit" if family in PARTIAL else ""}" data-search="{esc(search)}">'
                     f'<header><div><p class="eyebrow">{figure_id} · {esc(r["evidence_scope"])}</p>'
                     f'<h3><a href="{r["html"]}#results">{esc(family)}</a></h3></div><span class="date-state">{state}</span></header>'
                     '<div class="card-workflow"><p class="eyebrow">Workflow steps</p><div>')
            for sid in stepmap[family]:
                n = ORDER.index(sid)
                body += f'<button type="button" data-workflow-step="{sid}" title="{esc(steps[sid]["name"])}">{n+1:02} · {SHORT[n]}</button>'
            if family in PARTIAL:
                body += '<button type="button" data-workflow-step="audit" class="partial-tag">12 · Audit: partial diagnostic</button>'
            body += '</div></div>'
            body += (f'<label class="variant-label">Benchmark condition<select class="time-variant" '
                     f'aria-label="Condition for {esc(family)} in Challenge {c}">')
            for vv in f['time_variants']:
                label = vv['heading'] + ' · ' + vv['condition']
                if condition_decisions[vv['id']]['progress'] != 'True':
                    label += ' · weaker positive association'
                body += (f'<option value="{esc(vv["path"])}" data-condition="{esc(vv["condition"])}" '
                         f'data-plotted="{vv["plotted"]}" data-dated="{vv["dated"]}" data-total="{vv["observations"]}" '
                         f'data-definition-held="{vv.get("definition_held",0)}" data-undated="{vv.get("undated",vv["observations"]-vv["dated"])}" '
                         f'data-benchmark-id="{esc(vv["benchmark_id"])}" data-apa-html="{esc(citation(bib[vv["benchmark_id"]]))}"'
                         + (' selected' if vv['id'] == v['id'] else '') + f'>{esc(label)}</option>')
            body += ('</select></label>'
                     f'<a class="figure-link" href="{r["html"]}#records" aria-label="Open the data and references for {esc(family)}">'
                     f'<img class="time-preview" src="{esc(v["path"])}" alt="{esc(family)}: benchmark performance versus model release date" '
                     'width="860" height="565" loading="lazy"><span class="figure-open">Open data and references ↗</span></a>'
                     f'<div class="benchmark-apa" data-benchmark-id="{esc(v["benchmark_id"])}"><p class="eyebrow">Benchmark reference (APA)</p>{apa}</div>'
                     f'<div class="card-foot"><span class="variant-count">{v["plotted"]} shown / {v["observations"]} observations · '
                     f'{v.get("undated",v["observations"]-v["dated"])} undated · {v.get("definition_held",0)} definition-held</span>'
                     '<span>Original metric · separate test conditions</span></div></article>')
        body += '</div></section>'
    body += '''</div><section class="scope unified-scope"><h2>What the selection supports</h2><p>These are illustrative positive trends in component skills. None is a dedicated test of codebook-based extraction from psychological studies, and none validates the complete human–AI workflow or its auditability. The same benchmark can inform several challenges and workflow steps.</p><p>The main page shows every adequately sampled condition in each selected family, including weaker positive associations. Detail pages retain all conditions, APA references, individual result sources and model-release evidence. Original figures, observations and descriptive curves are unchanged.</p><p><a href="data/progress_benchmark_register.csv">Current eight-family register</a> · <a href="data/progress_observations.csv">Current plotted observations</a> · <a href="data/progress_family_decisions.csv">All 50 inclusion decisions</a> · <a href="archive.html">Complete source archive</a></p></section>'''
    fragment=ROOT/'materials/home.fragment'
    if fragment.exists():
        body=body.replace('<details class="unified-workflow"',fragment.read_text()+'<details class="unified-workflow"',1)
    for el in H.fragments_fromstring(body):
        main.append(el)
    save(ROOT / 'index.html', doc)
    # Keep the full source map accessible without presenting it as the current selection.
    archive = H.parse(str(ROOT/'index.html')).getroot()
    archive.find('body').set('class', 'supplement-page')
    archive.find('head/title').text = 'Full source archive | Data extraction benchmarks'
    amain = archive.xpath('//main')[0]; amain.clear(); amain.set('id','content')
    archive_body = '''<p class="eyebrow">Source archive · original 50-family selection</p><h1>Full benchmark source archive</h1><p class="lead">The current main page retains eight families with well-populated, consistently positive release-date trends. All 50 original families and their evidence remain accessible here.</p><p>This archive preserves 4,094 source observations, 391 conditions and the original mappings. A missing or weak time trend is not evidence that a benchmark is unimportant. BFCL, for example, improves on its overall tool-calling score while adequately sampled subtasks show regressions; it is therefore excluded from the focused selection.</p><div class="page-links"><a href="index.html">Current progress figures</a><a href="methods.html#progress-selection">Selection criteria</a><a href="All_Benchmarks_Article_Atlas.pdf">Original 50-family PDF atlas</a><a href="data/article_benchmark_register.csv">Full source register</a><a href="data/progress_family_decisions.csv">All inclusion decisions</a></div><div class="table-scroll"><table><thead><tr><th>Benchmark</th><th>Current status</th><th>Adequately sampled conditions</th><th>Reason</th></tr></thead><tbody>'''
    for r in archive_register:
        decision = family_decisions[r['family']]
        status = 'Current progress selection' if r['family'] in selected else 'Archive only'
        archive_body += f'<tr id="{r["figure_id"]}"><td><a href="{r["html"]}">{esc(r["family"])}</a></td><td>{status}</td><td>{decision["adequate_conditions"]}</td><td>{esc(decision["reason"])}</td></tr>'
    archive_body += '</tbody></table></div>'
    for el in H.fragments_fromstring(archive_body): amain.append(el)
    save(ROOT/'archive.html',archive)
    # The original detail pages remain accessible, with their selection status visible.
    for r in archive_register:
        p=ROOT/r['html']; detail=H.parse(str(p)).getroot()
        for el in detail.xpath('//*[@id="progress-selection-status"]'): el.getparent().remove(el)
        status='Current progress selection' if r['family'] in selected else 'Source archive only'
        note=H.fragment_fromstring(f'<aside id="progress-selection-status" class="progress-selection-note"><strong>{status}.</strong> {esc(family_decisions[r["family"]]["reason"])}. All original conditions and source values are retained below. <a href="../methods.html#progress-selection">Criteria</a> · <a href="../archive.html#{r["figure_id"]}">Archive record</a>.</aside>')
        detail.xpath('//main')[0].insert(0,note); save(p,detail)
    for name in ['workflow.html', 'challenges.html', 'all-benchmarks.html']:
        save(ROOT / name, redirect_document(name))
    for p in list(ROOT.glob('*.html')) + list((ROOT / 'benchmarks').glob('*.html')) + [p for p in (ROOT/'materials').glob('*.html') if p.name!='home.fragment.html']:
        tree = H.parse(str(p)).getroot()
        for el in tree.xpath('//*[@href]'):
            el.set('href', retarget(el.get('href'),p))
        for link in tree.xpath('//footer//a[contains(@href,"all_source_values.csv")]'):
            link.text = 'All 4,094 source archive values (CSV)'
        navs = tree.xpath('//header[@class="site-header"]/nav')
        if navs:
            nav = navs[0]
            for child in list(nav):
                nav.remove(child)
            prefix = '../' if p.parent!=ROOT else ''
            for path, label in [('index.html', 'Challenges & workflow'),
                                ('index.html#article-materials', 'Article materials'),
                                ('references.html', 'References'), ('model-releases.html', 'Model releases'), ('methods.html', 'Methods')]:
                link = H.Element('a', href=prefix + path)
                link.text = label
                if p.name == path:
                    link.set('aria-current', 'page')
                nav.append(link)
        save(p, tree)
    # Cache-bust the shared UI assets on all detail pages as well as the homepage.
    css_hash = hashlib.sha256((ROOT / 'assets/style.css').read_bytes()).hexdigest()[:10]
    js_hash = hashlib.sha256((ROOT / 'assets/app.js').read_bytes()).hexdigest()[:10]
    for p in list(ROOT.glob('*.html')) + list((ROOT / 'benchmarks').glob('*.html')) + [p for p in (ROOT/'materials').glob('*.html') if p.name!='home.fragment.html']:
        tree = H.parse(str(p)).getroot()
        for el in tree.xpath('//link[@rel="stylesheet"]'):
            el.set('href', el.get('href').split('?')[0] + '?v=' + css_hash)
        for el in tree.xpath('//script[@src]'):
            el.set('src', el.get('src').split('?')[0] + '?v=' + js_hash)
        save(p, tree)
    print(f'Built one focused homepage: {len(register)} families, {len(mappings)} A–D assignments, 12 workflow steps; full archive retained.')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ROOT = Path(sys.argv[1]).expanduser().resolve()
    build()
