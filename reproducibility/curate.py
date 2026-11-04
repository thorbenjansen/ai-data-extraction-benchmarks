"""Curate the frozen 82-family atlas by task fit, without changing scores or plots.

Usage: python curate.py /path/to/original-atlas /new/output-folder
The original atlas is read only. Selection does not depend on performance trends.
"""
from pathlib import Path
from collections import Counter
from copy import deepcopy
from urllib.parse import urlsplit,unquote
import csv,json,hashlib,re,shutil,sys,importlib.util
from lxml import html as H
from html import escape as E

EXCLUDED={
9:'Infographic question answering is less closely matched to scientific reports than the retained document/table tasks.',
16:'School mathematics over tables is a more distant numerical proxy than retained scientific and financial document tasks.',
17:'Mixed visual mathematics is less specific to extraction than the retained chart, table and numerical-processing tasks.',
25:'Synthetic bAbI facts in distractor contexts add less distinct coverage than the retained retrieval and compositional QA tasks.',
27:'Conversational/agent memory is less closely matched to evidence extraction from research reports.',
28:'Conversational memory and temporal QA are outside the selected research-document emphasis.',
29:'Competition mathematics is a distant proxy; retain numerical processing, table reasoning and extraction-specific calculations instead.',
30:'Grade-school mathematics is a distant proxy; retain numerical processing and robustness diagnostics instead.',
32:'The composite reasoning suite has lower task specificity and overlaps narrower retained diagnostics.',
37:'Small open-domain compositional QA set; retain broader or better-targeted multi-hop and scientific QA tasks.',
39:'Scientific claim verification is relevant to verification/auditability, but the existing construct map does not link it directly to A-D.',
42:'Scientific coding and execution are less closely matched to extraction than retained scientific document and coordination tasks.',
43:'Reproducing machine-learning papers is a distant proxy for the requested extraction challenges.',
45:'Kaggle machine-learning engineering is a particularly distant proxy for data extraction.',
48:'API-centric tool use adds less distinct coverage than retained BFCL, GAIA and scientific coordination tasks; API drift complicates comparisons.',
49:'Formal instruction compliance primarily addresses coding-protocol concerns outside A-D; it is not relabelled as complex reasoning.',
50:'Instruction compliance primarily addresses coding-protocol concerns outside A-D.',
52:'Model sycophancy concerns response independence, outside the selected A-D scope.',
53:'Sycophancy under rebuttal is the primary construct; mathematical content alone is insufficient to prioritize this as a numerical benchmark.',
54:'Response to valid/invalid criticism primarily concerns independence and adjudication outside A-D.',
55:'User-pushback and subjective response changes are outside A-D and have limited reference validity.',
56:'Closed-book misconception avoidance is distant from document-grounded extraction and has no direct A-D mapping.',
57:'Hallucination detection primarily concerns source faithfulness rather than A-D.',
58:'Short factual recall is distant from document-grounded extraction and has no direct A-D mapping.',
60:'Unsupported-claim detection primarily addresses source faithfulness rather than A-D.',
61:'Primarily evaluates RAG evaluation systems and overlaps other QA data; retained ALCE and scientific QA provide more distinct task coverage.',
62:'Factual-consistency meta-benchmark primarily concerns verification outside A-D and overlaps other datasets.',
63:'Factual-consistency meta-benchmark primarily concerns verification outside A-D and overlaps other datasets.',
64:'Summary hallucination detection primarily concerns verification outside A-D.',
70:'PICOS title/abstract screening is upstream of full-text extraction; corpus/release limitations reduce its priority here.',
71:'Collaborative software tasks have a different population and task from data extraction; avoid forcing a D mapping.',
72:'Human collaboration on visual puzzles is outside A-D and remote from scientific extraction.'}

DEFS={
'A':dict(name='Parsing and understanding semi-structured data',pages='15–17',definition='Preserve and interpret document layouts, reading order, text, digits, formulas, tables and figures.'),
'B':dict(name='Understanding long contexts',pages='18–21',definition='Locate and combine relevant evidence across long or dispersed contexts, including distractors and non-literal retrieval.'),
'C':dict(name='Arithmetic and symbolic induction',pages='21–23',definition='Process numbers and symbols, apply numerical operations and derive requested values from reported inputs.'),
'D':dict(name='Complex reasoning',pages='23–25',definition='Coordinate multiple intermediate steps, including retrieval, tool use, planning, computation and checking.')}
KEEP_WHY={
1:'Broad full-page parsing with task-specific layout, text, table and formula annotations.',2:'Whole-document PDF-to-structure extraction complements component OCR scores.',3:'Explicit unit tests localize document-parsing failures.',4:'Visual text recognition/localization provides a distinct OCR diagnostic; versions remain separate.',5:'Language and photographed-document variation tests robustness of source preparation.',6:'Clean/degraded matched documents isolate parsing robustness.',7:'Difficult long expert documents complement average-case parsing tests; failure-based sampling remains explicit.',8:'A clear document-grounded QA baseline, with its page-level scope retained.',10:'Chart lookup and numerical reasoning test visual evidence use.',11:'Harder chart reasoning complements ChartQA; the scores are not merged.',12:'Hierarchical headers and quantity/entity alignment closely match table interpretation needs.',13:'Combines hierarchical tables, text and multi-step numerical evidence.',14:'Hybrid table/text arithmetic provides interpretable document-grounded numerical tasks.',15:'Executable numerical programs separate reasoning operations from final answers.',18:'Short/long numerical document tasks bridge retrieval, tables and derivation.',19:'Long multimodal documents add cross-page and unanswerable-evidence cases.',20:'Realistic long-context task diversity; benchmark versions and inherited subtasks stay distinct.',21:'Controlled synthetic retrieval/tracking complements natural-document tests.',22:'Diverse long-context tasks and citation evaluation; component overlap is disclosed.',23:'Non-literal retrieval tests semantic evidence location beyond lexical matching.',24:'Very-long-context tasks provide a distinct length diagnostic.',26:'Repeated similar requests test long-context disambiguation.',31:'Matched symbolic/numerical perturbations diagnose arithmetic robustness.',33:'Discrete operations on textual evidence link retrieval to arithmetic.',34:'Retrieval plus multi-hop factual reasoning tests dependent evidence use.',35:'Connected multi-hop evidence tests compositional reasoning.',36:'Supporting-sentence annotations make multi-hop evidence retrieval inspectable.',38:'Questions and supporting evidence are anchored in complete scientific papers.',40:'Scientific literature comprehension/extraction provides closer domain fit than generic reasoning.',41:'Literature, supplements, tables and figures are evaluated in scientific research tasks.',44:'Scientific code/data reproduction provides a labelled adjacent task for multi-step execution.',46:'Multi-step tool-assisted tasks complement isolated tool-call syntax.',47:'Explicit tool/argument and multi-turn scoring supplies a focused coordination diagnostic.',51:'Dependencies between constraints test composition beyond isolated instruction compliance.',59:'Citation-supported answers link retrieval to inspectable evidence support.',65:'Biomedical risk-of-bias evidence retrieval is a concrete synthesis task; domain transfer remains limited.',66:'Clinical search, screening and result extraction provide a direct evidence-synthesis task.',67:'Scientific numerical extraction spans text, tables/images and calculation-dependent values.',68:'Schema-based document-to-table extraction tests structured outputs and numerical relationships.',69:'Schema-constrained key information extraction tests document-to-field assignment.',73:'Table-based fact checking, numerical reasoning and analysis distinguish operations over tabular evidence.',74:'Basic table lookup/manipulation directly targets a table-understanding concern in the commentary.',75:'Elementary numerical understanding/processing is closer to extraction operations than competition mathematics.',76:'Controlled copying and symbolic transformations isolate elementary numerical/symbolic failures.',77:'Localizing the first incorrect reasoning step provides an interpretable intermediate-step diagnostic.',78:'Literal retrieval is retained as a baseline explicitly discussed in the commentary, not as sufficient evidence of comprehension.',79:'Long-dependency comprehension complements literal retrieval and short-context tasks.',80:'Long multimodal retrieval/counting combines document modalities with dispersed evidence.',81:'Normalized document-level evidence extraction in systematic reviews provides a close task analogue.',82:'Participant-count and group-flow extraction targets structural binding in scientific diagrams.'}

def read(p):
    with p.open(encoding='utf-8-sig',newline='')as f:return list(csv.DictReader(f))
def write(p,rows,fields=None):
    if not rows and not fields:return
    with p.open('w',encoding='utf-8-sig',newline='')as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hasclass(node,c):return c in (node.get('class')or'').split()
def parse(p):return H.fromstring(p.read_text())
def save(p,d):p.write_text('<!doctype html>'+H.tostring(d,encoding='unicode',method='html'))
def frag(s):return H.fragments_fromstring(s)
def replace_main(doc,s):
    m=doc.xpath('//main')[0];m.clear();m.set('id','content')
    for el in frag(s):m.append(el)
def insert_html(parent,s,index=None):
    for n in frag(s):
        if index is None:parent.append(n)
        else:parent.insert(index,n);index+=1
def apa(c):return '<div class="citation"><p>'+E(c['apa']).replace(E(c['url']),'<a href="'+E(c['url'])+'">'+E(c['url'])+'</a>')+'</p><button class="copy" data-copy="'+E(c['apa'])+'" type="button">Copy APA reference</button></div>'

def finalize(out):
    """Reconcile visible labels and retain prior full-archive checks as history."""
    summary=json.loads((out/'data/article_overview_summary.json').read_text())
    reg=read(out/'data/article_benchmark_register.csv');sd={s['id']:s for s in json.loads((out/'data/workflow_steps.json').read_text())}
    vax_caution='Related to B through distributed evidence aggregation; its abstract-level baselines do not test long-context-length robustness. Medical review domain; transfer to psychological coding remains untested.'
    for r in reg:
        if r['family']=='VaxScope':r['transfer_limits']=vax_caution
    write(out/'data/article_benchmark_register.csv',reg)
    fi=read(out/'data/figure_index.csv')
    for r in fi:r['steps']=';'.join(next(x['workflow_steps']for x in reg if x['family']==r['family']).split('; '))
    write(out/'data/figure_index.csv',fi)
    cm=read(out/'data/challenge_mapping.csv')
    for r in cm:
        if r['family']=='VaxScope':r['transfer_limit']=vax_caution;r['mapping_basis']='Distributed review-level evidence aggregation is related to B; this is not a direct test of long-context length. Primary source: Ilgen et al. (2026), abstract and methods.'
    write(out/'data/challenge_mapping.csv',cm)
    for p in list(out.glob('*.html'))+list((out/'benchmarks').glob('*.html')):
        doc=parse(p)
        for a in doc.xpath('//footer//a'):
            if 'source values'in a.text_content():a.text=f'All {summary["source_observations"]:,} selected source values (CSV)'
        if p.name=='all-benchmarks.html':
            for el in doc.xpath('//div[contains(@class,"atlas-method")]//p'):
                if '125 observations remain'in el.text_content():
                    el.text=f'{summary["definition_held_observations"]} observations remain raw-only because a required definition is unresolved. Missing release dates are a separate issue; no eligible release is excluded by a fixed calendar window.'
            for card in doc.xpath('//article[@data-family]'):
                row=next(r for r in reg if r['family']==card.get('data-family'));steps=card.xpath('./p[@class="atlas-steps"]')[0];steps.clear();steps.set('class','atlas-steps')
                insert_html(steps,' · '.join(f'<a href="index.html#step-{s}">{E(sd[s]["name"])}</a>'for s in row['workflow_steps'].split('; ')))
        if p.name=='F067_Manalyzer.html':
            box=doc.xpath('//div[@class="mapping-list"]')[0]
            if not box.xpath('.//a[contains(@href,"#derive")]'):
                insert_html(box,'<article><h3><a href="../workflow.html#derive">Transform and calculate values</a></h3><p><span class="badge">Direct extraction task</span></p><p>Table 4, Level 3 explicitly requires calculation from reported research data. Atmospheric, agricultural and environmental domains; transfer to psychology remains untested.</p></article>',3)
        if p.name=='F081_VaxScope.html':
            box=doc.xpath('//*[@id="challenge-mapping"]')[0]
            if not box.xpath('./p[@class="vax-caution"]'):insert_html(box,'<p class="vax-caution">'+E(vax_caution)+'</p>')
        if p.name=='challenges.html':
            for row in doc.xpath('//tr'):
                if row.xpath('.//a[contains(@href,"F081_VaxScope.html")]'):
                    small=row.xpath('.//small')
                    if small:small[0].text=vax_caution
        save(p,doc)
    previous=out/'reproducibility/source_archive_validation';previous.mkdir(exist_ok=True)
    for name in ['article_browser_check.json','article_overview_validation.json','browser_check.json','reproduction_check.json']:
        p=out/name
        if p.exists():shutil.move(p,previous/name)
    (previous/'README.txt').write_text('These are historical checks copied from the original 82-family source archive. They do not describe the selected 50. Current checks are in /validation.json and /data/selection_validation.json.\n')

def run(source,out):
    assert source.resolve()!=out.resolve() and not out.exists(),'Choose a new output folder.'
    source_hashes={str(p.relative_to(source)):sha(p)for p in source.rglob('*')if p.is_file()and'__pycache__'not in p.parts and not p.name.startswith('.')}
    register=read(source/'data/article_benchmark_register.csv');cat=read(source/'reproducibility/inputs/benchmark_catalogue.csv')
    selected=[r for r in register if int(r['figure_id'][1:])not in EXCLUDED]
    assert len(register)==82 and len(selected)==50 and len(EXCLUDED)==32
    families={r['family']for r in selected};fids={r['figure_id']for r in selected};selectedcat=[r for r in cat if r['record_type']=='benchmark'and r['family']in families]
    # Manalyzer's calculation-dependent extraction is explicit in Table 4 of the primary paper.
    for r in selectedcat:
        if r['family']=='Manalyzer':r['constructs']=';'.join(dict.fromkeys(r['constructs'].split(';')+['C']))
    bids={r['benchmark_id']for r in selectedcat}
    codes={f:{s.strip()for r in selectedcat if r['family']==f for s in r['constructs'].split(';')}for f in families}
    challenges={f:sorted((codes[f]&set('ABCD'))|({'A'}if'A2'in codes[f]else set()))for f in families}
    assert all(challenges.values())
    shutil.copytree(source,out,ignore=shutil.ignore_patterns('__pycache__','*.pyc','package_manifest.json'))
    # All pruning is confined to the newly created selected version; the 82-family archive stays intact.
    for p in(out/'benchmarks').glob('*.html'):
        if p.name[:4]not in fids:p.unlink()
    for folder,pattern in [('figures','F*'),('data','F*')]:
        for p in(out/folder).glob(pattern):
            if p.is_file()and p.name[:4]not in fids:p.unlink()
    raw=read(source/'data/all_source_values.csv');values=[r for r in raw if r['family']in families]
    ids={r['observation_id']for r in values};series={r['series_id']for r in values};refs={r['source_ref']for r in values}
    def keep(r):
        if 'family'in r:return r['family']in families
        if 'figure_id'in r:return r['figure_id']in fids
        if 'observation_id'in r:return r['observation_id']in ids
        if 'series_id'in r:return r['series_id']in series
        if 'benchmark_id'in r:return r['benchmark_id']in bids
        return True
    for folder in ['data','reproducibility/inputs']:
        for p in(out/folder).glob('*.csv'):
            if re.match(r'F\d{3}_',p.name):continue
            rows=read(p)
            if rows:write(p,[r for r in rows if keep(r)],list(rows[0]))
    write(out/'reproducibility/inputs/benchmark_catalogue.csv',selectedcat)
    figures=[f for f in json.loads((source/'data/time_chart_index.json').read_text())if f['family']in families]
    steps=json.loads((source/'data/workflow_steps.json').read_text());sd={s['id']:s for s in steps}
    order=['protocol','documents','retrieve','bind','code','coordinate','derive','verify','collaborate','adjudicate','product','audit']
    maps=[r for r in read(source/'data/workflow_mapping.csv')if r['family']in families]
    for r in selectedcat:
        if r['family']=='Manalyzer'and not any(m['family']=='Manalyzer'and m['step']=='derive'for m in maps):
            maps.append(dict(step='derive',level='Direct extraction task',rationale='Level 3 explicitly requires calculating values from research reports; Table 4 distinguishes these from text and table/image copying. Source: Xu et al., Manalyzer, arXiv:2505.20310v2, Table 4. Domain transfer to psychology remains untested.',benchmark_id=r['benchmark_id'],family='Manalyzer',figure_id='F067'))
    for f in figures:f['steps']=[s for s in order if any(m['family']==f['family']and m['step']==s for m in maps)];f['commentary_challenges']=challenges[f['family']]
    fm={f['family']:f for f in figures}
    stepmap={f:fm[f]['steps']for f in families}
    bib=json.loads((source/'data/bibliography.json').read_text());bib['benchmarks']={k:v for k,v in bib['benchmarks'].items()if k in bids};bib['result_sources']={k:v for k,v in bib['result_sources'].items()if k in refs}
    dump(out/'data/bibliography.json',bib);dump(out/'data/time_chart_index.json',figures);write(out/'data/workflow_mapping.csv',maps)
    # Preserve every source number, definition and release assignment; only membership/mapping fields change.
    for r in selected:
        f=r['family'];r.update(workflow_steps='; '.join(stepmap[f]),workflow_step_names='; '.join(sd[s]['name']for s in stepmap[f]),commentary_challenges='; '.join(challenges[f]),challenge_names='; '.join(DEFS[c]['name']for c in challenges[f]),selection_rationale=KEEP_WHY[int(r['figure_id'][1:])])
    write(out/'data/article_benchmark_register.csv',selected)
    for name in ['article_conditions.csv','article_observations.csv','figure_index.csv']:
        rows=read(out/'data'/name)
        for r in rows:r['commentary_challenges']='; '.join(challenges[r['family']])
        write(out/'data'/name,rows)
    claims=json.loads((source/'data/commentary_requirements.json').read_text())
    for c in claims:c['benchmark_families']=[f for f in c['benchmark_families']if f in families]
    dump(out/'data/commentary_requirements.json',claims)
    conditions=read(out/'data/article_conditions.csv');observations=read(out/'data/article_observations.csv')
    visible={r['observation_id']for r in read(out/'data/time_plot_geometry.csv')}
    counts=Counter(c for f in families for c in challenges[f])
    summary=dict(benchmark_families=50,benchmark_versions=len(bids),source_observations=len(values),added_model_card_observations=sum(bool(r.get('integration_candidate_id'))for r in values),separate_conditions=len(conditions),visible_observations=len(visible),families_with_time_points=len({r['family']for r in values if r['observation_id']in visible}),definition_held_observations=sum(r.get('plot_eligible')=='False'for r in values),visible_mean_curves=sum(c['mean_curve_visible']=='True'for c in conditions),challenge_family_counts=dict(sorted(counts.items())),source_cutoff='2026-10-31',selection_date='2026-11-02',source_archive_families=82,axis_policy='Retained condition-specific full supported release histories; native metrics; unchanged curves')
    dump(out/'data/article_overview_summary.json',summary)
    decisions=[]
    for r in register:
        n=int(r['figure_id'][1:]);yes=r['family']in families
        decisions.append(dict(figure_id=r['figure_id'],family=r['family'],decision='included'if yes else'excluded',rationale=KEEP_WHY[n]if yes else EXCLUDED[n],commentary_challenges='; '.join(challenges.get(r['family'],[])),source_observations=r['source_observations']))
    write(out/'data/selection_decisions.csv',decisions)
    definition=dict(commentary='Lu, J., & Wang, X. T. Tackling challenges in large language model-based data extraction: A commentary on Jansen et al. (2025). Supplied manuscript BUL-2025-2112R3.',source_file='Commentary.pdf',source_sha256='4f59cf13d7e3327c59e99f899c88157d3cac4ed262a9e3c9686cd9d13e74fdf0',pagination='One-based physical PDF pages in the supplied review file; section headings disambiguate the duplicated manuscript copy.',challenges=DEFS,mapping_status='Authored task/construct interpretation, not empirical evidence of transfer or task success.',A2_rule='Tables and figures (legacy A2) are part of Challenge A, not an additional commentary challenge.',additional_mapping_evidence={'Manalyzer_C':'https://arxiv.org/html/2505.20310v2#S5.T4; Table 4, Level 3 requires calculation.'})
    dump(out/'data/challenge_definitions.json',definition)
    mappingrows=[]
    for r in selected:
        for c in challenges[r['family']]:mappingrows.append(dict(figure_id=r['figure_id'],family=r['family'],challenge=c,challenge_name=DEFS[c]['name'],commentary_pdf_pages=DEFS[c]['pages'],task=r['task'],mapping_basis=r['selection_rationale']if c!='C'or r['family']!='Manalyzer'else'Calculation-dependent numerical extraction is explicitly evaluated in Manalyzer Table 4, Level 3.',workflow_steps=r['workflow_steps'],evidence_scope=r['evidence_scope'],transfer_limit=r['transfer_limits'],benchmark_apa=r['benchmark_apa'],benchmark_page=r['html']))
    write(out/'data/challenge_mapping.csv',mappingrows)
    source_summary=json.loads((source/'data/article_overview_summary.json').read_text())
    selected_note=f'{len(values):,} source observations; {len(visible):,} plotted observations from {summary["families_with_time_points"]} families; {len(conditions)} separate conditions. Scores, model dates and descriptive curves are unchanged.'
    def badges(f,p=''):
        return '<div class="challenge-badges" aria-label="Commentary challenges">'+''.join(f'<a class="challenge-badge" href="{p}challenges.html#challenge-{c}" title="{E(DEFS[c]["name"])}">{c} · {E(DEFS[c]["name"])}</a>'for c in challenges[f])+'</div>'
    # Shared navigation and the per-benchmark two-axis mapping.
    for p in out.glob('*.html'):
        if p.name not in ['index.html','all-benchmarks.html','workflow.html','claims.html','references.html','model-releases.html','methods.html']:p.unlink()
    for p in list(out.glob('*.html'))+list((out/'benchmarks').glob('*.html')):
        doc=parse(p);prefix='../'if p.parent.name=='benchmarks'else''
        nav=doc.xpath('//header/nav')[0]
        insert_html(nav,f'<a href="{prefix}challenges.html">Challenges A–D</a>',2)
        if p.parent.name=='benchmarks':
            f=next(f for f in figures if p.stem==f['filename']);family=f['family'];main=doc.xpath('//main')[0]
            block='<section class="challenge-map" id="challenge-mapping"><h2>Commentary challenges and extraction workflow</h2>'+badges(family,'../')+'<p>'+E(KEEP_WHY[int(f['figure_id'][1:])])+'</p><p><strong>Workflow steps:</strong> '+', '.join(f'<a href="../index.html#step-{s}">{E(sd[s]["name"])}</a>'for s in stepmap[family])+'</p><details><summary>Mapping basis and transfer limits</summary><p>'+E(next(r['transfer_limits']for r in selected if r['family']==family))+'</p><p>These links describe the task content. They do not establish successful transfer to psychological evidence synthesis or validate a complete workflow.</p><ul>'+''.join(f'<li><strong>{c}:</strong> {E(DEFS[c]["definition"])} Commentary PDF pp. {DEFS[c]["pages"]}.</li>'for c in challenges[family])+'</ul></details></section>'
            insert_html(main,block,5)
        save(p,doc)
    # Keep the workflow's vertical steps and horizontal benchmark rails.
    p=out/'index.html';doc=parse(p)
    for card in doc.xpath('//article[@data-family]'):
        if card.get('data-family')not in families:card.getparent().remove(card)
    derive_rail=doc.get_element_by_id('rail-derive')
    man=doc.xpath('//article[@data-family="Manalyzer"]')[0]
    if not derive_rail.xpath('./article[@data-family="Manalyzer"]'):derive_rail.append(deepcopy(man))
    for row in doc.xpath('//section[@data-step-id]'):
        sid=row.get('data-step-id');cards=row.xpath('.//article[@data-family]');copy=row.xpath('./div[contains(@class,"step-copy")]')[0]
        count=copy.xpath('.//*[contains(@class,"step-count")]')
        if count:count[0].text=f'{len(cards)} benchmark families'
        pos=row.xpath('.//*[contains(@class,"rail-position")]')
        if pos:pos[0].text=f'{1 if cards else 0} / {len(cards)}'
        if not cards:
            rail=row.xpath('.//div[contains(@class,"benchmark-rail")]')[0]
            insert_html(rail,'<p class="selection-gap">No benchmark in this A–D selection directly evaluates this workflow step. '+E(sd[sid]['gap'])+'</p>')
            for button in copy.xpath('.//button[@data-rail]'):button.set('disabled','disabled')
        for card in cards:
            family=card.get('data-family');card.set('data-challenges',' '.join(challenges[family]));card.set('data-search',(card.get('data-search')or'')+' '+' '.join(DEFS[c]['name']for c in challenges[family]).lower());insert_html(card,badges(family),1)
    intro=doc.xpath('//*[@class="flow-intro"]')[0]
    note=intro.xpath('.//p[@class="integration-note"]')[0];note.clear();note.set('class','integration-note');insert_html(note,'<strong>Selected 50 benchmarks · Challenges A–D.</strong> '+E(selected_note)+' <a href="methods.html#selection">Selection and limits</a>.')
    doc.get_element_by_id('flow-count').text='50 benchmark families · 12 workflow steps'
    tools=doc.xpath('//*[@class="flow-tools"]')[0]
    challenge_select='<label>Commentary challenge<select id="flow-challenge"><option value="">All challenges A–D</option>'+''.join(f'<option value="{c}">{c} · {E(d["name"])}</option>'for c,d in DEFS.items())+'</select></label>'
    insert_html(tools,challenge_select,1);save(p,doc)
    # The complete selected register is still one card per family.
    p=out/'all-benchmarks.html';doc=parse(p)
    for card in doc.xpath('//article[@data-family]'):
        family=card.get('data-family')
        if family not in families:card.getparent().remove(card);continue
        card.set('data-challenges',' '.join(challenges[family]));card.set('data-steps',' '.join(stepmap[family]));insert_html(card,badges(family),1)
    doc.xpath('//h1')[0].text='The selected 50 benchmarks'
    doc.xpath('//main/p[@class="lead"]')[0].text='Fifty benchmark families mapped to extraction workflow steps and the commentary’s Challenges A–D.'
    doc.xpath('//main/p[not(@class)]')[0].text=selected_note+' Versions, metrics, scales, languages and test conditions remain separate.'
    links=doc.xpath('//*[@class="page-links"]')[0];links.clear();links.set('class','page-links')
    insert_html(links,'<a href="All_Benchmarks_Article_Atlas.pdf">Selected benchmark atlas (PDF)</a><a href="data/article_benchmark_register.csv" download>Benchmark register (50 rows)</a><a href="data/challenge_mapping.csv" download>Challenge and workflow mapping</a><a href="data/article_observations.csv" download>Source observations and references</a>')
    controls=doc.xpath('//*[contains(@class,"atlas-controls")]')[0];insert_html(controls,challenge_select.replace('flow-challenge','atlas-challenge'),2)
    doc.get_element_by_id('atlas-count').text='50 benchmark families';save(p,doc)
    # New commentary view: 50 unique rows, plus non-exclusive counts by challenge.
    template=parse(out/'all-benchmarks.html')
    defs_html=''.join(f'<section class="challenge-definition" id="challenge-{c}"><h2>{c} · {E(d["name"])}</h2><p>{E(d["definition"])}</p><p><strong>{counts[c]} benchmark families</strong> · commentary PDF pp. {d["pages"]}.</p><p>'+', '.join(f'<a href="{r["html"]}#challenge-mapping">{E(r["family"])}</a>'for r in selected if c in challenges[r['family']])+'</p><a href="all-benchmarks.html?challenge='+c+'">Explore these figures</a></section>'for c,d in DEFS.items())
    body='<p class="eyebrow">Commentary × extraction workflow</p><h1>Challenges A–D across the selected 50 benchmarks</h1><p class="lead">Each benchmark has at least one challenge assignment and at least one workflow assignment.</p><p>Assignments can overlap: a document task may require parsing, retrieval and calculation. Counts across A–D therefore do not sum to 50. A mapping describes task relevance; it does not demonstrate transfer to psychological studies.</p>'+defs_html+'<h2>All 50 benchmarks: both mappings</h2><div class="table-scroll"><table class="mapping-table"><thead><tr><th>Benchmark</th><th>Challenges</th><th>Workflow steps</th><th>Task fit and limit</th></tr></thead><tbody>'
    for r in selected:
        f=r['family'];body+='<tr><th><a href="'+r['html']+'#challenge-mapping">'+E(f)+'</a></th><td>'+badges(f)+'</td><td>'+', '.join(f'<a href="index.html#step-{s}">{E(sd[s]["name"])}</a>'for s in stepmap[f])+'</td><td>'+E(r['selection_rationale'])+'<small>'+E(r['transfer_limits'])+'</small></td></tr>'
    body+='</tbody></table></div><details><summary>Source and interpretation</summary><p>'+E(definition['commentary'])+'</p><p>Section headings and physical PDF pages are recorded in data/challenge_definitions.json. Tables and figures (legacy A2) are grouped under A. Coding-protocol reproducibility remains Challenge E and is not silently relabelled as D.</p><p>The Manalyzer C assignment additionally follows its calculation-dependent extraction level (Table 4).</p><a href="data/challenge_mapping.csv">Download every assignment and its basis</a></details>'
    replace_main(template,body);template.xpath('//title')[0].text='Challenges A–D | Selected 50 benchmarks';save(out/'challenges.html',template)
    # Rebuild the workflow table rather than leaving links to excluded families.
    p=out/'workflow.html';doc=parse(p);body='<p class="eyebrow">Workflow requirements and benchmark coverage</p><h1>From extraction steps to observable tasks</h1><p class="lead">The selected 50 benchmarks cover tasks related to Challenges A–D. Later workflow requirements can remain evidence gaps.</p><div class="table-scroll"><table class="mapping-table"><thead><tr><th>Workflow step</th><th>Question</th><th>Selected benchmarks</th><th>Limit</th></tr></thead><tbody>'
    for sid in order:
        s=sd[sid];matched=[f for f in fm if sid in stepmap[f]]
        if sid=='audit':matched=['ALCE','DTBench','CONSORT diagrams']
        names=', '.join(f'<a href="benchmarks/{fm[f]["filename"]}.html#challenge-mapping">{E(f)}</a>'for f in matched)or'No selected benchmark directly evaluates this step.'
        if sid=='audit':names='Partial diagnostics only: '+names
        body+=f'<tr id="{sid}"><th>{E(s["name"])}</th><td>{E(s["question"])}</td><td>{names}</td><td>{E(s["gap"])}</td></tr>'
    body+='</tbody></table></div><p>The mapping is an authored interpretation of task content. No benchmark in this collection validates the full proposed workflow or complete process auditability.</p>';replace_main(doc,body);save(p,doc)
    p=out/'claims.html';doc=parse(p)
    for row in doc.xpath('//tr[starts-with(@id,"claim-")]'):
        for a in row.xpath('.//a[contains(@href,"benchmarks/")]'):
            if not any(f['filename']+'.html'in a.get('href')for f in figures):a.drop_tree()
        for detail in row.xpath('.//details'):
            aa=detail.xpath('.//a[contains(@href,"benchmarks/")]')
            if aa:detail.xpath('./summary')[0].text=f'Related selected tasks ({len(aa)} families)'
            else:detail.getparent().remove(detail)
    insert_html(doc.xpath('//main')[0],'<p class="scope">This page retains the commentary requirements as context. Only the selected A–D benchmark families are linked; absent links indicate a gap in this selection.</p>',3);save(p,doc)
    p=out/'references.html';doc=parse(p);body='<h1>References for the selected 50 benchmarks</h1><h2>Benchmark definitions</h2>'
    for bid,c in bib['benchmarks'].items():body+='<h3 id="benchmark-'+E(bid)+'">'+E(next(r['benchmark']for r in selectedcat if r['benchmark_id']==bid))+'</h3>'+apa(c)
    body+='<h2>Sources for the reported results</h2>'
    for ref,s in bib['result_sources'].items():body+='<h3 id="ref-'+ref+'">['+ref+'] '+E(s['source_id'])+'</h3>'+apa(s['citation'])
    replace_main(doc,body);save(p,doc)
    # Retain the shared date bibliography: the sources are model-level evidence, not extra benchmarks.
    p=out/'methods.html';doc=parse(p);main=doc.xpath('//main')[0]
    for el in main.xpath('./p'):
        if 'covers all 82 families'in el.text_content():el.text=f'The article selection contains 50 benchmark families and {len(bids)} benchmark-version entries from the original 82-family archive. It is a curated evidence map, not an exhaustive systematic review. Versions, subtasks and shared component datasets are not independent studies.'
    selection='<section id="selection"><h2>How the 50 benchmarks were selected</h2><p>Selection prioritizes task fit to A–D, source traceability, distinct diagnostic coverage and relevance to research documents. Scores, model rankings and apparent improvement were not selection criteria. Closely related variants remain within their existing family.</p><p>The full 82-family atlas is preserved separately as the source archive. The 32 exclusions include remote mathematics/engineering tasks, conversation/puzzle tasks, screening-only work, and benchmarks primarily about instruction compliance, sycophancy or factuality outside A–D. This selection is a reasoned editorial choice, not an objective or exhaustive ranking of benchmark quality.</p><p>Each included family has a task-specific rationale, at least one A–D link and at least one extraction-workflow link. Existing mappings are retained; Manalyzer additionally maps to C because its Table 4 explicitly evaluates calculation-dependent extraction. Tables and figures (legacy A2) map to A.</p><p>'+E(selected_note)+'</p><p>Curve estimates remain descriptive within each original condition. This selection does not establish overall model progress, comparative human accuracy, or successful transfer to psychology.</p><p><a href="data/selection_decisions.csv">All 82 selection decisions and reasons</a> · <a href="data/challenge_mapping.csv">Every selected challenge assignment</a></p></section>'
    insert_html(main,selection,2)
    # Historical integration totals are provenance of the original archive, not current selection totals.
    insert_html(main,'<p class="archive-note">The retained release/model-card audit sections below document the original 82-family source archive. Their historical audit totals are not counts for the selected 50. Current selected totals are in the selection section and article register.</p>',3);save(p,doc)
    css='''\n/* Selected-50 commentary mapping; chart styles are unchanged. */
.challenge-badges{display:flex;flex-wrap:wrap;gap:7px;margin:10px 0 14px}.challenge-badge{display:inline-block;font-size:12px;line-height:1.45;padding:5px 9px;border:1px solid #b8cbd4;border-radius:6px;color:#173f56;background:#f2f7fa;text-decoration:none}.challenge-badge:hover{background:#e5eff4}.challenge-map{margin:25px 0;padding:18px 20px;border-left:4px solid #24536e;background:#f6f9fb}.challenge-definition{margin:32px 0}.flow-tools label{max-width:440px}.flow-tools select{max-width:100%}.selection-gap{padding:30px;font-size:16px;max-width:680px}.mapping-table small{display:block;margin-top:10px;color:#516974}.archive-note{color:#516974}.mapping-table td{vertical-align:top}.mapping-table .challenge-badge{font-size:11px}
'''
    with(out/'assets/style.css').open('a')as fp:fp.write(css)
    js=(out/'assets/app.js').read_text()
    js=js.replace("const card=rail.querySelector('.flow-card:not([hidden])');rail.scrollBy", "const card=rail.querySelector('.flow-card:not([hidden])');if(!card)return;rail.scrollBy")
    start=js.index("document.querySelector('#flow-search')?.addEventListener('input'")
    end=js.index('\n',start)
    js=js[:start]+'''function filterWorkflow(){const q=(document.querySelector('#flow-search')?.value||'').toLowerCase().trim(),ch=document.querySelector('#flow-challenge')?.value||'',families=new Set();let steps=0;for(const row of document.querySelectorAll('.flow-step')){let n=0;for(const c of row.querySelectorAll('.flow-card')){c.hidden=!(c.dataset.search.includes(q)&&(!ch||c.dataset.challenges.split(' ').includes(ch)));if(!c.hidden){n++;families.add(c.dataset.family);}}const gap=row.querySelector('.selection-gap');row.hidden=n===0&&!(gap&&!q&&!ch);if(!row.hidden)steps++;row.querySelectorAll('[data-rail]').forEach(b=>b.disabled=n===0);const pos=row.querySelector('.rail-position');if(pos)pos.textContent=(n?1:0)+' / '+n;}document.querySelector('#flow-count').textContent=families.size+' benchmark families · '+steps+' workflow steps';}
document.querySelector('#flow-search')?.addEventListener('input',filterWorkflow);document.querySelector('#flow-challenge')?.addEventListener('change',filterWorkflow);if(document.querySelector('#flow-count'))filterWorkflow();'''+js[end:]
    js=js.replace("t=document.querySelector('#atlas-status')?.value||'';let n=0;", "t=document.querySelector('#atlas-status')?.value||'',ch=document.querySelector('#atlas-challenge')?.value||'';let n=0;")
    js=js.replace("&&(!t||card.dataset.flags.split(' ').includes(t)));", "&&(!t||card.dataset.flags.split(' ').includes(t))&&(!ch||card.dataset.challenges.split(' ').includes(ch)));")
    js=js.replace("['atlas-search','atlas-step','atlas-status']", "['atlas-search','atlas-step','atlas-status','atlas-challenge']")
    js=js.replace('if(atlasCards.length)filterAtlas();',"if(atlasCards.length){const ch=new URL(location.href).searchParams.get('challenge');if(ch&&document.querySelector('#atlas-challenge'))document.querySelector('#atlas-challenge').value=ch;filterAtlas();}")
    (out/'assets/app.js').write_text(js)
    for p in list(out.glob('*.html'))+list((out/'benchmarks').glob('*.html')):
        t=p.read_text();t=re.sub(r'assets/style.css\?v=[a-f0-9]+','assets/style.css?v='+sha(out/'assets/style.css')[:10],t);t=re.sub(r'assets/app.js\?v=[a-f0-9]+','assets/app.js?v='+sha(out/'assets/app.js')[:10],t);p.write_text(t)
    finalize(out)
    selected=read(out/'data/article_benchmark_register.csv')
    # Reuse the established vector-PDF layout, with current scope and mappings.
    pdf_code=(source/'reproducibility/article_overview.py').read_text()
    pdf_code=pdf_code.replace('All benchmarks: Article evidence atlas','Selected 50 benchmarks: Article evidence atlas').replace("P('All benchmarks','Heading')","P('Selected 50 benchmarks','Heading')")
    pdf_code=pdf_code.replace('All 2,036 eligible points from 65 families are visible',f'All {len(visible):,} eligible points from {summary["families_with_time_points"]} families are visible').replace('The 125 definition-held values',f'The {summary["definition_held_observations"]} definition-held values').replace('82 family rows','50 family rows').replace('all 581 conditions',f'all {len(conditions)} conditions').replace('all 4,940 source observations',f'all {len(values):,} source observations')
    pdf_code=pdf_code.replace("if c['mean_curve_visible'] else", "if c['mean_curve_visible'] in (True,'True') else")
    pdf_code=pdf_code.replace("'Updated 31 October 2026. All 82 benchmark families; 90 benchmark-version entries; 4,940 source observations; 581 separate conditions.'",repr(f'Selected 2 November 2026. 50 benchmark families; {len(bids)} benchmark-version entries; {len(values):,} source observations; {len(conditions)} separate conditions. Source cutoff: 31 October 2026.'))
    pdf_code=pdf_code.replace("P(E(r['workflow_step_names']))", "P('Challenges: '+E(r['commentary_challenges'])),P(E(r['workflow_step_names']))")
    pdf_code=pdf_code.replace("'82 families; 4940 source observations; separate conditions; reviewed 2026-10-31'",repr(f'50 families; {len(values)} source observations; mapped to Challenges A-D; selected 2026-11-02'))
    (out/'reproducibility/article_overview.py').write_text(pdf_code)
    sys.path.insert(0,str(out/'reproducibility'))
    spec=importlib.util.spec_from_file_location('curated_article_pdf',out/'reproducibility/article_overview.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    mod.build_pdf(out,figures,selected,conditions,bib,steps,claims)
    # Replace the old full-scope runner/checks with a snapshot reproduction contract.
    for name in ['render_supplement.py','validate_supplement.py','validate_article_overview.py']:
        p=out/'reproducibility'/name
        if p.exists():p.unlink()
    shutil.copy2(Path(__file__),out/'reproducibility/curate.py')
    dump(out/'reproducibility/source_archive_manifest.json',dict(source_archive_name=source.name,source_sha256=source_hashes,selection_decisions='data/selection_decisions.csv'))
    (out/'reproducibility/reproduce.py').write_text('''from pathlib import Path
import sys,shutil,subprocess
here=Path(__file__).resolve().parent.parent
if len(sys.argv)!=2:raise SystemExit('Usage: python reproduce.py /new/output/folder')
out=Path(sys.argv[1]).expanduser().resolve()
if out.exists():raise SystemExit('Choose a new output folder.')
shutil.copytree(here,out,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
subprocess.run([sys.executable,str(out/'reproducibility/validate_selection.py')],check=True)
print('Reproduced the frozen selected-50 snapshot:',out)
''')
    (out/'README.txt').write_text(f'''SELECTED 50 BENCHMARKS FOR DATA EXTRACTION
Selection: 2 November 2026. Source-data cutoff: 31 October 2026.

Open index.html after extracting the complete folder. Scroll down through
the 12 workflow steps and right through each step's benchmarks. Filter by
commentary Challenge A, B, C or D. challenges.html maps all 50 families to
both challenges and workflow steps; all-benchmarks.html has one card per family.

CURRENT SCOPE
{json.dumps(summary,indent=2)}

COUNTS AND INTERPRETATION
There are exactly 50 selected families. Versions are not extra independent
benchmarks, and challenge assignments overlap. The selection prioritizes task
fit, source traceability and distinct coverage, not high scores or improvement.
The source 82-family atlas is unchanged and remains the broader archive.
All 82 inclusion/exclusion decisions are in data/selection_decisions.csv.
Every selected family has a rationale and an A-D/workflow assignment.
No collection member is a dedicated test of codebook-based extraction for
psychological evidence synthesis. Component scores do not validate transfer,
human-versus-LLM rankings, or complete process auditability.

SOURCE PRESERVATION
Every included observation, condition, release-date assignment, SVG plot,
vector figure, mean-curve input and fitted grid value is retained unchanged.
The added mapping fields describe task relevance, not new empirical results.
Raw data open on a benchmark page when its figure is clicked; each value
retains benchmark APA, result APA and release-source evidence. Release sources
remain on one shared page. Historical model-card audit sections describe the
original source archive and are labelled separately from current totals.

REPRODUCTION
python reproducibility/reproduce.py /new/output/folder clones and validates
this frozen selected snapshot, without model calls. To re-derive the selection
from the original 82-family archive, run:
python reproducibility/curate.py /path/to/original-82-atlas /new/output/folder
The source archive manifest records all input checksums. The complete selection
script and validation are included. No upload or journal submission was made.
''')
    finalize(out)
    validator=Path(__file__).with_name('validate_selection.py')
    if validator.exists():shutil.copy2(validator,out/'reproducibility/validate_selection.py')
    # Check scores, definitions, dates, geometry and curve grids against the actual source archive.
    rawold={r['observation_id']:r for r in raw}
    assert all(r==rawold[r['observation_id']]for r in read(out/'data/all_source_values.csv'))
    unchanged_assets=[]
    for folder in ['figures']:
        for p in(out/folder).iterdir():
            if p.is_file():assert sha(p)==sha(source/p.relative_to(out));unchanged_assets.append(str(p.relative_to(out)))
    for name,key in [('release_date_audit.csv','observation_id'),('time_plot_geometry.csv','observation_id'),('mean_curve_inputs.csv',None),('mean_curve_grid.csv',None)]:
        original=read(source/'data'/name);retained=[r for r in original if keep(r)];assert read(out/'data'/name)==retained,name
    assert all(sha(source/p)==digest for p,digest in source_hashes.items()),'Source archive changed'
    dump(out/'data/selection_validation.json',dict(status='passed',families=50,all_have_challenge_and_workflow_mapping=True,source_observations=len(values),source_observations_unchanged=True,source_archive_unchanged=True,retained_figure_assets_unchanged=len(unchanged_assets),retained_date_geometry_curve_rows_unchanged=True,challenge_counts=dict(sorted(counts.items()))))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('Usage: python curate.py /original-82-atlas /new/output-folder')
    run(Path(sys.argv[1]).expanduser().resolve(),Path(sys.argv[2]).expanduser().resolve())
