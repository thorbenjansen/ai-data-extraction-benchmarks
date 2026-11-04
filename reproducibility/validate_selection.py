"""Validate the selected atlas, its two mappings, provenance and local navigation."""
from pathlib import Path
from collections import Counter
from urllib.parse import urlsplit,unquote
from lxml import html as H,etree as E
from pypdf import PdfReader
import csv,json,hashlib,sys

ROOT=Path(sys.argv[1]).expanduser().resolve()if len(sys.argv)>1 else Path(__file__).resolve().parent.parent
def read(name):
    with(ROOT/name).open(encoding='utf-8-sig',newline='')as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
reg=read('data/article_benchmark_register.csv');raw=read('data/all_source_values.csv');obs=read('data/article_observations.csv');cond=read('data/article_conditions.csv');maps=read('data/challenge_mapping.csv');workflow=read('data/workflow_mapping.csv');decisions=read('data/selection_decisions.csv')
families={r['family']for r in reg};ids={r['observation_id']for r in raw};series={r['series_id']for r in raw}
assert len(reg)==len(families)==50
assert len(decisions)==82 and Counter(r['decision']for r in decisions)=={'included':50,'excluded':32}
assert all(r['selection_rationale']and r['commentary_challenges']and r['workflow_steps']for r in reg)
assert len(raw)==len(ids)==len(obs)==4094
assert len(cond)==len(series)==391
assert{r['family']for r in maps}=={r['family']for r in workflow}==families
counts=Counter(r['challenge']for r in maps);assert dict(counts)=={'A':24,'B':25,'C':17,'D':20}
assert len({(r['family'],r['challenge'])for r in maps})==len(maps)==86
for r in reg:
    assigned={c.strip()for c in r['commentary_challenges'].split(';')}
    assert assigned=={m['challenge']for m in maps if m['family']==r['family']}
    assert set(r['workflow_steps'].split('; '))=={m['step']for m in workflow if m['family']==r['family']}
assert any(r['family']=='Manalyzer'and r['challenge']=='C'for r in maps)
bib=json.loads((ROOT/'data/bibliography.json').read_text());old={r['observation_id']:r for r in raw};dates={r['observation_id']:r for r in read('data/release_date_audit.csv')};visible={r['observation_id']for r in read('data/time_plot_geometry.csv')}
assert len(visible)==1716
for r in obs:
    assert all(r[k]==v for k,v in old[r['observation_id']].items()),r['observation_id']
    assert r['benchmark_reference_apa']==bib['benchmarks'][r['benchmark_id']]['apa']
    assert r['result_reference_apa']==bib['result_sources'][r['source_ref']]['citation']['apa']
    assert r['documented_model_release']==dates[r['observation_id']]['release_date']
    assert(r['displayed_in_time_figure']=='True')==(r['observation_id']in visible)
archive=json.loads((ROOT/'reproducibility/source_archive_manifest.json').read_text())['source_sha256']
assets=list((ROOT/'figures').glob('*'));assert assets
for p in assets:
    if p.is_file():assert sha(p)==archive[str(p.relative_to(ROOT))],p.name
benchmark_pages=list((ROOT/'benchmarks').glob('*.html'));assert len(benchmark_pages)==50
for p in benchmark_pages:
    doc=H.fromstring(p.read_bytes());assert doc.xpath('//*[@id="challenge-mapping"]')
    assert doc.xpath('//*[@id="benchmark-reference"]')
    assert len(doc.xpath('//*[@class="records"]//tbody/tr'))==sum(r['family']==next(x['family']for x in reg if Path(x['html']).name==p.name)for r in raw)
    assert not doc.xpath('//*[@id="records"]/@open'),'Raw values must remain collapsed until requested'
home=H.fromstring((ROOT/'index.html').read_bytes());cards=home.xpath('//article[@data-family]')
progress=json.loads((ROOT/'data/progress_selection.json').read_text());selected=set(progress['families'])
current_maps=[m for m in maps if m['family']in selected]
assert len(cards)==len(current_maps) and{c.get('data-family')for c in cards}==selected
sections=home.xpath('//section[@data-challenge]')
assert [s.get('data-challenge')for s in sections]==list('ABCD')
for section in sections:
    challenge=section.get('data-challenge')
    expected={m['family']for m in current_maps if m['challenge']==challenge}
    assert {c.get('data-family')for c in section.xpath('.//article[@data-family]')}==expected
for card in cards:
    family=card.get('data-family')
    assert set(card.get('data-challenges').split())=={m['challenge']for m in maps if m['family']==family}
    assert set(card.get('data-steps').split())=={m['step']for m in workflow if m['family']==family}
    assert bool(card.get('data-diagnostic-steps'))==(family in {'ALCE','DTBench','CONSORT diagrams'})
assert len(home.xpath('//*[@id="workflow-map"]//button[@data-workflow-step]'))==12
assert home.xpath('//*[@id="flow-step-filter"]')
assert not home.xpath('//*[@class="records"]'),'Raw observations must not appear on the main page'
for name in ['workflow.html','challenges.html','all-benchmarks.html']:
    legacy=H.fromstring((ROOT/name).read_bytes())
    assert legacy.xpath('//link[@rel="canonical" and contains(@href,"/index.html")]')
    assert 'location.replace'in ''.join(legacy.xpath('//script/text()'))
    assert not legacy.xpath('//article[@data-family]'),'Former overviews must route to the single main page'
broken=[];links_checked=0;anchors_checked=0
cache={}
for p in list(ROOT.glob('*.html'))+benchmark_pages+list((ROOT/'figures').glob('*.svg')):
    doc=H.fromstring(p.read_bytes())if p.suffix=='.html'else E.parse(str(p))
    if p.suffix=='.html':
        ids_in_page=doc.xpath('//@id');assert len(ids_in_page)==len(set(ids_in_page)),p.name
    attrs=doc.xpath('//@href|//@src')
    for value in attrs:
        u=urlsplit(str(value))
        if u.scheme or u.netloc or not u.path and not u.fragment:continue
        target=(p.parent/unquote(u.path)).resolve()if u.path else p
        if not target.is_relative_to(ROOT):continue # documented source-archive locators are provenance, not selected navigation
        links_checked+=1
        if not target.is_file():broken.append((str(p.relative_to(ROOT)),str(value),'file'));continue
        if u.fragment and target.suffix=='.html':
            if target not in cache:cache[target]=set(H.fromstring(target.read_bytes()).xpath('//@id'))
            anchors_checked+=1
            if unquote(u.fragment)not in cache[target]:broken.append((str(p.relative_to(ROOT)),str(value),'anchor'))
assert not broken,broken[:25]
pdf=PdfReader(ROOT/'All_Benchmarks_Article_Atlas.pdf');ix=read('data/article_pdf_index.csv');assert len(ix)==50
assert'50 benchmark families'in pdf.pages[0].extract_text()
cover=pdf.pages[0].extract_text();assert'1,716 eligible points from 40 families'in cover and'50 family rows'in cover
assert'2,036 eligible points'not in cover and'125 definition-held'not in cover
for r in ix:
    page=pdf.pages[int(r['first_page'])-1];text=page.extract_text();assert r['figure_id']in text and'Challenges:'in text
    if r['family']=='VaxScope':assert'no visible mean curve:'in text
result=dict(status='passed',current_benchmark_families=len(selected),current_homepage_assignments=len(cards),current_dated_observations=progress['counts']['displayed_source_observations'],candidate_benchmark_families=50,source_observations=4094,candidate_conditions=391,candidate_challenge_assignments=86,candidate_challenge_family_counts=dict(counts),candidate_dated_observations=1716,unchanged_figure_assets=len(assets),local_links_checked=links_checked,local_anchors_checked=anchors_checked,pdf_pages=len(pdf.pages),pdf_family_chapters=50,all_source_rows_have_result_and_benchmark_references=True)
(ROOT/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
