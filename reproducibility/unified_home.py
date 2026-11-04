"""Render one A–D/workflow homepage from the frozen selected-50 registers.

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


def retarget(value):
    u = urlsplit(value)
    if u.scheme or u.netloc:
        return value
    p = Path(u.path)
    if p.name not in {'workflow.html', 'challenges.html', 'all-benchmarks.html'}:
        return value
    fragment = u.fragment
    if p.name == 'workflow.html':
        fragment = 'step-' + fragment if fragment else 'workflow-map'
    if not fragment and parse_qs(u.query).get('challenge'):
        fragment = 'challenge-' + parse_qs(u.query)['challenge'][0]
    return urlunsplit(('', '', str(p.with_name('index.html')), u.query, fragment))


def build():
    register = read('data/article_benchmark_register.csv')
    charts = {f['family']: f for f in load('data/time_chart_index.json')}
    steps = {s['id']: s for s in load('data/workflow_steps.json')}
    definitions = load('data/challenge_definitions.json')
    defs = definitions['challenges']
    bib = load('data/bibliography.json')['benchmarks']
    mappings = read('data/challenge_mapping.csv')
    counts = Counter(m['challenge'] for m in mappings)
    byfamily = {r['family']: r for r in register}
    stepmap = {r['family']: r['workflow_steps'].split('; ') for r in register}
    chmap = {r['family']: [c.strip() for c in r['commentary_challenges'].split(';')]
             for r in register}

    doc = H.parse(str(ROOT / 'index.html')).getroot()
    doc.find('body').set('class', 'workflow-home unified-home')
    doc.find('head/title').text = 'Challenges A–D & workflow | Data extraction benchmarks'
    main = doc.xpath('//main')[0]
    main.clear()
    main.set('id', 'content')
    body = '''<div class="flow-intro"><p class="eyebrow">Data-extraction benchmark supplement</p>
<h1>Challenges A–D across the extraction workflow</h1>
<p class="lead">Four challenges, one map. Scroll down through A–D and across their benchmark figures. Select a workflow step to explore its evidence.</p>
<p class="integration-note"><strong>50 benchmark families</strong> · 4,094 source observations · 391 separate test conditions. Challenge assignments overlap; the same benchmark can appear under more than one challenge.</p>
<div class="challenge-jump" aria-label="Commentary challenges">'''
    for c, d in defs.items():
        body += (f'<a href="#challenge-{c}"><strong>{c}</strong><span>{esc(d["name"])}'
                 f'<small>{counts[c]} benchmark families</small></span></a>')
    body += '''</div><div class="flow-tools"><label>Find a benchmark<input id="flow-search" type="search" placeholder="Name, task or workflow step…"></label><label>Workflow step<select id="flow-step-filter"><option value="">All workflow steps</option>'''
    body += ''.join(f'<option value="{sid}" data-name="{esc(steps[sid]["name"])}" data-task="{esc(steps[sid]["task"])}" data-gap="{esc(steps[sid]["gap"])}">{i:02} · {esc(steps[sid]["name"])}</option>'
                    for i, sid in enumerate(ORDER, 1))
    body += '''</select></label><button type="button" id="flow-reset">Show all benchmarks</button><span id="flow-count" role="status" aria-live="polite">50 benchmark families · 4 challenges</span></div>
<p class="flow-help">X: documented model release date. Y: the original benchmark metric. Date ranges can differ between figures; compare the calendar labels. Dashed curves describe mean performance within the named test condition. Click a figure for its raw data and sources.</p>
<div class="supplement-links"><a href="model-releases.html">Model release-date sources</a><a href="methods.html#mean-curves">Mean-curve methods</a><a href="methods.html#selection">Selection and limits</a><a href="All_Benchmarks_Article_Atlas.pdf">Complete PDF atlas</a></div></div>
<details class="unified-workflow" id="workflow-map"><summary>The 12 workflow steps and their links to A–D</summary><p>Challenge badges indicate links through the mapped benchmark tasks. They do not establish that an entire step is validated. Select a step to filter the figures below.</p><div class="workflow-tiles">'''
    for i, sid in enumerate(ORDER, 1):
        families = [f for f in byfamily if sid in stepmap[f]]
        if sid == 'audit':
            families = sorted(PARTIAL)
        related = sorted({c for f in families for c in chmap[f]})
        number = f'{len(families)} partial diagnostics' if sid == 'audit' else f'{len(families)} benchmark families'
        if not families:
            number = 'Evidence gap in this selection'
        badges = ''.join(f'<span class="mini-challenge">{c}</span>' for c in related)
        body += (f'<button id="step-{sid}" type="button" data-workflow-step="{sid}" aria-pressed="false">'
                 f'<span class="workflow-order">{i:02} · {SHORT[i-1]}</span><strong>{esc(steps[sid]["name"])}</strong>'
                 f'<span class="tile-challenges">{badges}</span><small>{number}</small></button>')
    body += '''</div><p class="map-source">The coding-protocol and interaction requirements remain distinct from A–D. The audit step contains partial diagnostics only; no selected benchmark tests the complete audit trail. <a href="data/challenge_mapping.csv">Download the challenge/workflow assignments</a>.</p></details>
<aside id="workflow-context" class="workflow-context" hidden aria-live="polite"><h2 id="workflow-context-title"></h2><p id="workflow-context-task"></p><p id="workflow-context-gap"></p></aside>
<p id="flow-empty" class="flow-empty" hidden>No benchmarks match this search and workflow step. Try another step or show all benchmarks.</p>
<div class="flow-sequence challenge-sequence">'''
    used_ids = set()
    for c, d in defs.items():
        families = [r['family'] for r in register if c in chmap[r['family']]]
        families.sort(key=lambda f: (not bool(charts[f]['primary_variant']['plotted']), int(byfamily[f]['figure_id'][1:])))
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
    body += '''</div><section class="scope unified-scope"><h2>What the collection supports</h2><p>These benchmarks assess component skills and selected extraction tasks. None is a dedicated test of codebook-based extraction from psychological studies, and none validates the complete human–AI workflow or its auditability. The same benchmark can inform several challenges and workflow steps.</p><p>Every benchmark retains its APA references, individual result sources, model-release evidence and separate test conditions. The figures, observations and descriptive curves are unchanged.</p><p><a href="data/article_benchmark_register.csv">50-family register</a> · <a href="data/challenge_mapping.csv">Challenge/workflow mapping</a> · <a href="methods.html">Methods and limits</a></p></section>'''
    for el in H.fragments_fromstring(body):
        main.append(el)
    save(ROOT / 'index.html', doc)
    for name in ['workflow.html', 'challenges.html', 'all-benchmarks.html']:
        save(ROOT / name, redirect_document(name))
    for p in list(ROOT.glob('*.html')) + list((ROOT / 'benchmarks').glob('*.html')):
        tree = H.parse(str(p)).getroot()
        for el in tree.xpath('//*[@href]'):
            el.set('href', retarget(el.get('href')))
        navs = tree.xpath('//header[@class="site-header"]/nav')
        if navs:
            nav = navs[0]
            for child in list(nav):
                nav.remove(child)
            prefix = '../' if p.parent.name == 'benchmarks' else ''
            for path, label in [('index.html', 'Challenges & workflow'),
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
    for p in list(ROOT.glob('*.html')) + list((ROOT / 'benchmarks').glob('*.html')):
        tree = H.parse(str(p)).getroot()
        for el in tree.xpath('//link[@rel="stylesheet"]'):
            el.set('href', el.get('href').split('?')[0] + '?v=' + css_hash)
        for el in tree.xpath('//script[@src]'):
            el.set('src', el.get('src').split('?')[0] + '?v=' + js_hash)
        save(p, tree)
    print('Built one homepage: 50 families, 86 A–D assignments, 12 workflow steps.')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ROOT = Path(sys.argv[1]).expanduser().resolve()
    build()
