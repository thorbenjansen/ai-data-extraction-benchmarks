"""Build the current reader supplement and agent package; preserve source data.

Usage: python build_article_materials.py --source-ai-zip /downloaded/AI.zip
The original OSF package and its expected hash are recorded in materials_sources.
No original manuscript or model evaluation is modified or executed.
"""
from pathlib import Path
from html import escape as E
from collections import Counter
from lxml import html as H
import argparse, csv, hashlib, json, re, shutil, subprocess, tempfile, zipfile

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://thorbenjansen.github.io/ai-data-extraction-benchmarks/'
VERSION = '2026-11-04'
ORDER = ['protocol','documents','retrieve','bind','code','coordinate','derive','verify','collaborate','adjudicate','product','audit']
DATA_FILES = ['article_benchmark_register.csv','article_observations.csv','article_conditions.csv','all_source_values.csv','challenge_mapping.csv','workflow_mapping.csv','workflow_steps.json','challenge_definitions.json','bibliography.json','date_sources.csv','release_date_audit.csv','model_release_registry.json','time_plot_geometry.csv','mean_curve_grid.csv','mean_curve_method.json','time_chart_index.json']
DATA_FILES += ['progress_selection.json','progress_family_decisions.csv','progress_condition_decisions.csv','progress_benchmark_register.csv','progress_observations.csv']
DATA_FILES += ['point_details.json','progress_display_order.json']
DATA_FILES = ['curve_method.json' if name=='mean_curve_method.json' else name for name in DATA_FILES]

def load(path): return json.loads(path.read_text())
def dump(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(name):
    with (ROOT/'data'/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def save(path, doc):path.write_text('<!doctype html>'+H.tostring(doc,encoding='unicode',method='html'))
def markdown(text):
    return subprocess.check_output(['pandoc','--from=gfm','--to=html','--wrap=none'],input=text,text=True)
def public_root_links(text):return text.replace('(../','('+BASE)
def page(path,title,body):
    doc=H.parse(str(ROOT/'index.html')).getroot();doc.find('body').set('class','supplement-page article-materials')
    doc.find('head/title').text=title+' | Article materials'
    doc.xpath('//meta[@name="description"]')[0].set('content','Current reader and AI research resources for auditable human–AI data extraction, with literature and benchmark evidence.')
    for el in doc.xpath('//link[@rel="stylesheet"]'):el.set('href','../'+el.get('href'))
    for el in doc.xpath('//script[@src]'):el.set('src','../'+el.get('src'))
    for el in doc.xpath('//header[@class="site-header"]//*[@href]'):el.set('href','../'+el.get('href'))
    main=doc.xpath('//main')[0];main.clear();main.set('id','content')
    for node in H.fragments_fromstring(body):main.append(node)
    footer=doc.find('body/footer')
    if footer is not None:
        footer.clear();footer.text='Reader/agent supplement updated 4 November 2026. Benchmark source cutoff: 31 October 2026. Candidate research workflow; no new model evaluations.'
    save(path,doc)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-ai-zip',type=Path,required=True);args=parser.parse_args()
    content=load(ROOT/'reproducibility/materials_content.json');context=load(ROOT/'reproducibility/materials_sources/context.json')
    source_digest=sha(args.source_ai_zip)
    source_format='corpus'
    if source_digest!=context['source_ai_package']['sha256']:
        expected=load(ROOT/'materials/build_validation.json')['downloads'][f'AI_Research_Package_{VERSION}.zip']
        assert source_digest==expected,'Wrong source package checksum'
        source_format='research-package'
    refs=load(ROOT/'reproducibility/materials_sources/manuscript_references.json');ref={r['id']:r for r in refs}
    steps={s['id']:s for s in load(ROOT/'data/workflow_steps.json')};register=read('article_benchmark_register.csv')
    progress=load(ROOT/'data/progress_selection.json');selected=set(progress['families']);n_selected=len(selected)
    materials=ROOT/'materials';downloads=materials/'downloads';downloads.mkdir(parents=True,exist_ok=True)
    modules=[]
    for i,sid in enumerate(ORDER,1):
        m=dict(content['modules'][sid]);m.update(id=sid,number=i,name=steps[sid]['name'])
        matches=[r for r in register if sid in r['workflow_steps'].split('; ')]
        if sid=='audit':matches=[r for r in register if r['family']in ['ALCE','DTBench','CONSORT diagrams']]
        m['screened_candidate_families']=[r['family']for r in matches]
        m['benchmark_families']=[r['family']for r in matches if r['family']in selected]
        m['benchmark_challenges']=sorted({c.strip()for r in matches if r['family']in selected for c in r['commentary_challenges'].split(';')})
        m['benchmark_role']='partial diagnostic only'if sid=='audit'else'mapped component or extraction task'
        modules.append(m)
    def citation_label(rid):
        r=ref[rid];year=re.search(r'\((\d{4}[a-z]?)\)',r['apa']).group(1)
        name={'R22':'Lu and Wang','R23':'Macnamara','R30':'Pustejovsky and Stubbs'}.get(rid,r['apa'].split(',')[0]+' et al.')
        return name+' ('+year+')'
    def cite(ids):return '; '.join(f'[{citation_label(rid)}](literature.html#{rid})'for rid in ids)
    intro='''# Workflow and literature supplement

This supplement connects a twelve-component research workflow, its supporting literature and eight benchmark families with source-linked time trends. Evidence cutoff: 31 October 2026.

## Why accuracy and auditability belong together

Data extraction turns source evidence into review data through linked decisions. The product must be accurate, while the process must allow its quality to be assessed and steered. The same two criteria apply to human experts, research assistants, LLMs and human–AI teams.

Our original study compared LLM outputs with existing human-extracted data. It measured their agreement and did not independently establish the quality of the human judgments. A disagreement can reflect a human error, an LLM error or different interpretations of a coding rule. It cannot, by itself, show that LLMs are worse than humans. The research question is where each actor performs better, which errors they share and how their abilities can be combined. [R14](literature.html#R14), [R06](literature.html#R06), [R15](literature.html#R15).

Lu and Wang motivate decomposing extraction into challenges and examining context and tools. Macnamara motivates examining how assistance changes human judgment, independence and accuracy. Auditability connects these concerns: consequential decisions, sources, transformations and interventions become observable features of a workflow that can be compared empirically. [R22](literature.html#R22), [R23](literature.html#R23).

These modules are a research blueprint. They do not establish a universally validated sequence, a mandatory allocation to humans or AI, or a default ranking of their accuracy. Protocol reproducibility, interaction and adjudication extend beyond the component capabilities represented by Challenges A–D.

## Reading the evidence

Each module separates its purpose, a proposed research record, possible evaluation targets and an open question. The proposed records and comparisons are authored operationalizations, not validated scales or established cutoffs. Source references indicate their methodological basis; benchmark links indicate related tasks.

The main page now shows eight benchmark families with 650 dated observations in 27 separate conditions. A condition needs at least ten model configurations, six release positions and 180 days of coverage. A selected family must have a qualifying positive trend and no contrary adequately sampled condition. Every adequately sampled condition in each retained family remains visible, including weaker positive associations. [Read all criteria and inclusion decisions](../methods.html#progress-selection).

This selection explicitly depends on observed progress. It illustrates positive trajectories; it cannot estimate how often benchmarks improve or average general progress. The [screening record](../evidence.html) documents all 50 candidate families, including mixed findings and sparse time series. No family is a dedicated test of codebook-based extraction from psychological studies. Challenge assignments overlap; raw scores and curves remain condition-specific. No displayed benchmark tests the complete audit trail.

## Workflow modules

'''
    guide=intro
    for m in modules:
        guide+=f'### {m["number"]:02d}. {m["name"]}\n\n'
        for label,key in [('Purpose','purpose'),('Proposed record','record'),('Evaluation target','evaluate'),('Research question','question'),('Transfer limit','limit')]:guide+=f'**{label}.** {m[key]}\n\n'
        guide+='**Literature.** '+cite(m['sources'])+'.\n\n'
        guide+=f'**Benchmark coverage.** {len(m["benchmark_families"])} families; '+m['benchmark_role']+'. '
        guide+=f'[Explore the corresponding figures]({BASE}index.html?step={m["id"]}).\n\n'
        if m['benchmark_families']:guide+=', '.join(m['benchmark_families'])+'.\n\n'
    guide+='''## Comparing workflows on common terms

Define the eligible documents, variables and extraction units; coder expertise and training; model snapshots, prompts, context and tools; and the information available at each decision. Record which differences are intentional parts of the workflow comparison. Separate held-out evaluation from adaptation of the instructions or codebook. Document the reference procedure, adjudicator independence, denominators and treatment of missing and ambiguous cases.

Assess field and whole-record correctness, unsupported additions and omissions alongside time and cost. Measure agreement separately. For human–AI conditions, report errors corrected, retained and introduced after assistance, while preserving exposure timing and initial judgments when the design calls for independent extraction. Compare possible biases with relevant human-only conditions rather than assuming they originate only from AI. [R07](literature.html#R07), [R09](literature.html#R09), [R23](literature.html#R23), [R45](literature.html#R45).

## Making auditability testable

An audit should determine whether a reader can reconstruct the evidence and the consequential decision path, identify unresolved uncertainty, and see where correction or escalation was possible. The presence of a log is insufficient if source locators do not resolve or the reason for accepting a value cannot be reconstructed. Conversely, a well-documented error remains an inaccurate product. These are separate process and product outcomes. [R07](literature.html#R07), [R08](literature.html#R08), [R38](literature.html#R38).

The companion event schema is an illustrative template for research. It records the actor and condition, codebook and instruction versions, source locator, candidate value, transformation, exposure timing, verification, final disposition and remaining uncertainty. It specifies information to preserve; it does not validate an extraction decision or prescribe one verification policy for all reviews.

## Sources and provenance

Reference strings follow the accompanying manuscript bibliography. The step-to-literature assignments and operational research questions were authored for this supplement. Literature ARAs provide structured routes to source evidence; their quality labels and source-grounding limitations remain visible. Check the cited primary publication before making a citation-grade claim.

[Open the reference collection](literature.html). [Open the AI research package guide](ai.html). [Return to the benchmark atlas](../index.html).
'''
    guide=re.sub(r'\[(R\d{2})\]',lambda m:'['+citation_label(m.group(1))+']',guide)
    (materials/'workflow.md').write_text(guide)
    dump(materials/'workflow_model.json',{'version':VERSION,'status':'candidate research components; not a validated universal workflow','modules':modules,'position':content['position']})
    dump(materials/'references.json',refs);dump(materials/'version.json',context)
    schema={'$schema':'https://json-schema.org/draft/2020-12/schema','title':'Illustrative extraction decision event','description':'Research template, not a validated reporting standard. Null records an unavailable or inapplicable value; it is not evidence of absence.','type':'object','required':['event_id','step','actor','condition_id','instruction_version','source','decision','uncertainty'],'properties':{
      'event_id':{'type':'string'},'step':{'enum':ORDER},'actor':{'type':'object','required':['type','identifier'],'properties':{'type':{'enum':['human expert','research assistant','LLM','human-AI','adjudicator']},'identifier':{'type':'string'},'model_snapshot':{'type':['string','null']},'harness_and_tools':{'type':['string','null']},'training_or_expertise':{'type':['string','null']}}},
      'condition_id':{'type':'string'},'instruction_version':{'type':'string'},'codebook_version':{'type':['string','null']},'source':{'type':'object','required':['document_id','locator'],'properties':{'document_id':{'type':'string'},'locator':{'type':['string','null']},'source_version':{'type':['string','null']}}},
      'decision':{'type':'object','required':['candidate_value','disposition','reason'],'properties':{'candidate_value':{},'disposition':{'enum':['proposed','accepted','rejected','corrected','escalated','unresolved']},'reason':{'type':'string'},'alternatives_considered':{'type':'array'}}},'transformation':{'type':['object','null']},'initial_judgment_before_assistance':{},'assistance_exposure_time':{'type':['string','null']},'verification':{'type':['object','null']},'reference_definition':{'type':['string','null']},'uncertainty':{'type':['string','null']}}}
    dump(materials/'extraction_event.schema.json',schema)
    # A compact current canvas, with the same 12 components as the atlas.
    nodes=[];edges=[]
    for i,m in enumerate(modules):
        nodes.append({'id':m['id'],'type':'text','x':0,'y':i*240,'width':660,'height':200,'text':f'## {i+1:02d} · {m["name"]}\n\n{m["purpose"]}\n\nResearch component; evaluate accuracy and auditability.'})
        if i:edges.append({'id':'e'+str(i),'fromNode':modules[i-1]['id'],'fromSide':'bottom','toNode':m['id'],'toSide':'top'})
    dump(materials/'AI Data Extraction Workflow 2026-11-04.canvas',{'nodes':nodes,'edges':edges})
    jump='<nav class="module-jump" aria-label="Workflow modules">'+''.join(f'<a href="#module-{m["id"]}">{m["number"]:02d} · {E(m["name"])}</a>'for m in modules)+'</nav>'
    body=markdown(guide)
    parsed=H.fragment_fromstring(body,create_parent='div')
    title_node=parsed.xpath('./h1')[0];title_html=H.tostring(title_node,encoding='unicode');title_node.getparent().remove(title_node)
    version_node=parsed.xpath('./p')[0];version_node.set('class','material-version');version_html=H.tostring(version_node,encoding='unicode');version_node.getparent().remove(version_node)
    module_headings=parsed.xpath('.//h3')
    assert len(module_headings)==12
    for heading,m in zip(module_headings,modules):heading.set('id','module-'+m['id'])
    intro_html='<p class="eyebrow">Current reader supplement · 4 November 2026</p><div class="page-links"><a href="downloads/Workflow_Literature_Supplement_2026-11-04.zip" download>Download reader supplement</a><a href="workflow.md" download>Markdown guide</a><a href="AI%20Data%20Extraction%20Workflow%202026-11-04.canvas" download>Workflow canvas</a><a href="ai.html">AI package</a></div>'
    page(materials/'workflow.html','Workflow and literature supplement','<p class="eyebrow">Current reader supplement · 4 November 2026</p>'+title_html+version_html+intro_html.split('</p>',1)[1]+'<details class="material-toc"><summary>Jump to a workflow module</summary>'+jump+'</details>'+H.tostring(parsed,encoding='unicode'))
    used={r for m in modules for r in m['sources']}|{r for c in content['position']for r in c['sources']}
    ref_html='<p class="eyebrow">Current workflow literature</p><h1>References and their workflow roles</h1><p class="lead">APA references from the supplied manuscript, linked to the candidate workflow modules.</p><p>Each link describes the role of a source in this research map. Findings from other domains and decision tasks do not by themselves validate transfer to psychological data extraction. The benchmark-specific references remain with their figures.</p><div class="page-links"><a href="workflow.html">Read the workflow guide</a><a href="references.json" download>References (JSON)</a><a href="../references.html">Benchmark references</a></div>'
    for r in refs:
        links=[m for m in modules if r['id']in m['sources']]
        label='; '.join(m['name']for m in links) or 'Current manuscript reference; no step-specific assignment made in this guide.'
        apa=E(r['apa']);url=r.get('url')
        if url:apa=apa.replace(E(url),f'<a href="{E(url)}">{E(url)}</a>')
        ref_html+=f'<section class="material-reference" id="{r["id"]}"><p class="eyebrow">{r["id"]} · manuscript {r["paragraph_id"]}</p><div class="citation"><p>{apa}</p></div><p><strong>Workflow role:</strong> {E(label)}</p></section>'
    page(materials/'literature.html','References and workflow roles',ref_html)
    # Build a fresh agent entry layer, retaining source ARAs as source evidence.
    with tempfile.TemporaryDirectory(prefix='article-ai-current-') as temp:
        package=Path(temp)/('AI_Data_Extraction_Research_Package_'+VERSION);package.mkdir()
        inventory=[]
        with zipfile.ZipFile(args.source_ai_zip) as z:
            prefix=z.namelist()[0].split('/')[0]+('/agent_native_artifacts/'if source_format=='corpus'else'/literature/artifacts/')
            for item in z.infolist():
                if not item.filename.startswith(prefix) or item.is_dir():continue
                rel=Path(item.filename[len(prefix):]);artifact=rel.parts[0]
                if artifact=='ai-data-extraction-rejoinder-workflow-ara':continue
                assert '..' not in rel.parts and not rel.is_absolute()
                target=package/'literature/artifacts'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(item))
        for path in sorted((package/'literature/artifacts').glob('*/PAPER.md')):
            inventory.append({'artifact_id':path.parent.name,'paper_path':str(path.relative_to(package)),'sha256':sha(path),'role':'retained source evidence; not the current author position'})
        assert len(inventory)==203
        starter='''# Start here: current AI-supported data extraction research package

This package supports literature retrieval, comparison of candidate workflow components and source-bound interpretation of the benchmark data. Evidence cutoff: 31 October 2026. It does not implement or validate an automated extraction workflow.

1. Read `PAPER.md` and `CURRENT_CONTEXT.json` for the current author position.
2. Select a workflow component in `workflow/workflow_model.json` or its Markdown module.
3. Use `logic/claim_routes.json` for the current argument and `literature/references.json` for the manuscript bibliography.
4. Use `literature/source_index.json` to find retained source ARAs. Their existing summaries, evidence labels and provenance are source material, not proof of the current author's position. Follow evidence records and the original publication before making a citation-grade claim.
5. For benchmarks use `benchmarks/`, the original condition identifiers and `data/article_observations.csv`. Preserve reference definitions, metrics, splits, languages, budgets, model versions, release-date evidence and uncertainty. Do not pool heterogeneous scores or invent dates, values or human baselines.

The original study measured agreement with existing human-extracted data; it did not independently assess the quality of those human judgments. Do not infer a general human advantage or LLM disadvantage from discrepancies. Accuracy, agreement and auditability are different quantities.

The research objective is to determine where humans, LLMs and human–AI combinations perform better and how their abilities can be combined. The 50 benchmark families do not validate transfer to psychological codebook extraction or establish one universal workflow. Proposed record templates are not validated scales. No new model runs were conducted for this package.

The progress figures contain eight benchmark families, 650 dated observations and 27 separate conditions. They deliberately select positive time trends and must not be used to estimate the prevalence or average size of progress. Read `data/progress_selection.json` and both progress-decision CSVs. Displayed benchmark cards are in `benchmarks/`; additional screened candidates are in `screening/benchmarks/`. Source observations and mappings cover all 50 candidate families. A benchmark's exclusion from the figures does not establish its irrelevance to the research agenda.

Paths in `source_index.json` are actual paths in this download. Raw-PDF/Markdown paths inside literature ARAs are provenance pointers; raw PDFs and the source manuscript are not included.
'''
        (package/'START_HERE.md').write_text(starter);(package/'AGENT_NAVIGATION.md').write_text(starter)
        (package/'README.md').write_text('# AI-supported data extraction: current research companion\n\n'+starter.split('\n',1)[1])
        paper='# Current research companion: accuracy and auditability\n\n'
        paper+='Source manuscript SHA-256: `'+context['source_manuscript_sha256']+'`. The manuscript is not included or modified.\n\n'
        for c in content['position']:paper+=f'## {c["id"]}\n\n{c["text"]}\n\nManuscript location: {c["anchor"]}. Literature: '+', '.join(c['sources'])+'.\n\n'
        (package/'PAPER.md').write_text(paper.rstrip()+'\n');dump(package/'CURRENT_CONTEXT.json',context)
        dump(package/'logic/claim_routes.json',content['position']);dump(package/'workflow/workflow_model.json',{'version':VERSION,'modules':modules})
        dump(package/'schema/extraction_event.schema.json',schema);dump(package/'literature/references.json',refs);dump(package/'literature/source_index.json',inventory)
        (package/'workflow/READER_SUPPLEMENT.md').write_text(public_root_links(guide).replace('(literature.html','('+BASE+'materials/literature.html').replace('(ai.html)','('+BASE+'materials/ai.html)'))
        shutil.copy2(materials/'AI Data Extraction Workflow 2026-11-04.canvas',package/'workflow/AI Data Extraction Workflow.canvas')
        for m in modules:
            text=f'# {m["number"]:02d} · {m["name"]}\n\n'+ '\n\n'.join(f'## {k.title()}\n\n{m[k]}'for k in ['purpose','record','evaluate','question','limit'])+'\n\nReferences: '+', '.join(m['sources'])+'\n\nRelated benchmark families: '+', '.join(m['benchmark_families'])+'\n'
            (package/'workflow'/f'{m["number"]:02d}_{m["id"]}.md').write_text(text)
        for name in DATA_FILES:
            target=package/'data'/name;target.parent.mkdir(exist_ok=True);shutil.copy2(ROOT/'data'/name,target)
        for r in register:
            target=package/('benchmarks'if r['family']in selected else'screening/benchmarks')/f'{r["figure_id"]}.md';target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(f'# {r["figure_id"]} · {r["family"]}\n\nTask: {r["task"]}\n\nChallenges: {r["commentary_challenges"]}\n\nWorkflow links: {r["workflow_step_names"]}\n\nScope: {r["evidence_scope"]}\n\nTransfer limit: {r["transfer_limits"]}\n\nBenchmark APA: {r["benchmark_apa"]}\n\nCondition-specific values and result references: `data/article_observations.csv`, filtered by family.\n\nPublic figures and source rows: {BASE}{r["html"]}\n')
        dump(package/'provenance/build_inputs.json',context)
        files={str(p.relative_to(package)):sha(p)for p in sorted(package.rglob('*'))if p.is_file()}
        manifest={'version':VERSION,'source_aras_retained':len(inventory),'current_workflow_modules':12,'current_benchmark_families':n_selected,'additional_screened_families':50-n_selected,'current_dated_observations':progress['counts']['displayed_source_observations'],'current_conditions':progress['counts']['displayed_conditions'],'archive_source_observations':4094,'source_cutoff':'2026-10-31','files':files,'scope':'Source-bound progress figures, screened candidate evidence and literature research modules; no raw PDFs, source manuscript or new evaluations'}
        dump(package/'MANIFEST.json',manifest)
        ai_zip=downloads/f'AI_Research_Package_{VERSION}.zip'
        with zipfile.ZipFile(ai_zip,'w',zipfile.ZIP_DEFLATED) as z:
            for path in sorted(package.rglob('*')):
                if path.is_file():z.write(path,str(path.relative_to(package.parent)))
        agent=materials/'agent';agent.mkdir(exist_ok=True)
        for name in ['PAPER.md','START_HERE.md','CURRENT_CONTEXT.json','MANIFEST.json']:
            shutil.copy2(package/name,agent/name)
        dump(agent/'source_index.json',{'download':BASE+'materials/downloads/'+ai_zip.name,'paths_are_inside_download':True,'sources':inventory})
    ai_body='''<p class="eyebrow">Current AI-facing research companion · 4 November 2026</p><h1>AI research package</h1><p class="lead">Use the current argument, workflow modules and source evidence together.</p><div class="page-links"><a class="button" href="downloads/AI_Research_Package_2026-11-04.zip" download>Download current AI package</a><a href="agent/START_HERE.md">Agent starting instructions</a><a href="agent/PAPER.md">Current research context</a><a href="agent/MANIFEST.json">File manifest and checksums</a></div><section class="scope"><h2>What is current</h2><p>The starting documents and argument routes follow the author’s current saved manuscript. They replace the earlier draft’s navigation and make the agreement–accuracy distinction explicit. Human, LLM and human–AI workflows share the same accuracy and auditability criteria.</p></section><h2>Contents</h2><ul><li>12 candidate workflow modules, linked to research questions and literature.</li><li>50 benchmark cards and unchanged source data, reference definitions, release-date evidence and descriptive curve inputs.</li><li>203 retained source ARAs with their existing evidence and quality labels; the earlier rejoinder super-ARA is replaced by the current starting context.</li><li>Current manuscript bibliography, claim routes, proposed extraction-event schema and a source inventory.</li></ul><h2>Use with an agent</h2><ol><li>Download and extract the complete package.</li><li>Read <code>START_HERE.md</code>, <code>PAPER.md</code> and <code>CURRENT_CONTEXT.json</code>.</li><li>Select a workflow module and follow its reference and source-ARA routes.</li><li>For benchmark questions, retain the named test condition and cite the result source for each value.</li><li>Verify citation-grade statements at the primary source. The retained ARAs are retrieval aids, and their source-grounding limits remain visible.</li></ol><p class="scope">The package supports research and source retrieval. It is not a validated extraction pipeline or a new performance evaluation. Raw PDFs and the source manuscript are not included.</p><p><a href="workflow.html">Reader workflow guide</a> · <a href="literature.html">References</a> · <a href="version.json">Source versions and provenance</a></p>'''
    ai_body=ai_body.replace('50 benchmark cards and unchanged source data','8 displayed benchmark cards, 42 additional screened candidates and source data')
    ai_body=ai_body.replace('They replace the earlier draft’s navigation and make the agreement–accuracy distinction explicit.','The agreement–accuracy distinction is explicit.')
    ai_body=ai_body.replace('; the earlier rejoinder super-ARA is replaced by the current starting context','')
    ai_body=ai_body.replace('Current AI-facing research companion','AI-facing research companion').replace('Download current AI package','Download AI research package').replace('What is current','Research context').replace('Source versions and provenance','Source provenance')
    ai_body=ai_body.replace('<h2>Use with an agent</h2>','<p class="progress-selection-note">The current eight-family view deliberately selects well-populated positive time trends. It cannot estimate overall progress. The full 50-family evidence remains in the download. <a href="../methods.html#progress-selection">Selection criteria and decisions</a>.</p><h2>Use with an agent</h2>')
    page(materials/'ai.html','AI research package',ai_body)
    # Reader download: self-contained HTML, Markdown, references, canvas and template.
    human_zip=downloads/f'Workflow_Literature_Supplement_{VERSION}.zip'
    with zipfile.ZipFile(human_zip,'w',zipfile.ZIP_DEFLATED) as z:
        for name in ['workflow_model.json','references.json','version.json','extraction_event.schema.json','AI Data Extraction Workflow 2026-11-04.canvas']:
            z.write(materials/name,name)
        z.writestr('workflow.md',public_root_links(guide))
        for name in ['workflow.html','literature.html']:
            doc=H.parse(str(materials/name)).getroot()
            for el in doc.xpath('//script'):el.getparent().remove(el)
            for el in doc.xpath('//link[@rel="stylesheet"]'):
                style=H.Element('style');style.text=(ROOT/'assets/style.css').read_text();el.getparent().replace(el,style)
            for el in doc.xpath('//*[@href]'):
                href=el.get('href')
                if href.startswith('../'):el.set('href',BASE+href[3:])
                elif href.startswith(('downloads/','ai.html')):el.set('href',BASE+'materials/'+href)
            z.writestr(name,'<!doctype html>'+H.tostring(doc,encoding='unicode'))
        z.writestr('README.md','# Current workflow and literature supplement\n\nOpen workflow.html. This is the 4 November 2026 reader guide. Benchmark figures and the full AI research package are linked to the public article site. The workflow is a research blueprint, not a validated universal procedure.\n')
    fragment='''<section id="article-materials" class="article-materials-hub"><div><p class="eyebrow">All article materials · updated 4 November 2026</p><h2>Workflow, literature and AI research companion</h2><p>Current companions to the benchmark atlas, aligned with the manuscript snapshot read on 4 November 2026.</p></div><div class="materials-grid"><article><h3>Workflow &amp; literature</h3><p>12 candidate components, source-linked research questions and a current literature guide.</p><a href="materials/workflow.html">Read the supplement ↗</a><a href="materials/downloads/Workflow_Literature_Supplement_2026-11-04.zip" download>Download reader package</a></article><article><h3>AI research package</h3><p>Current argument and agent instructions, 203 source ARAs, 50 benchmark cards and the source data.</p><a href="materials/ai.html">Open the agent guide ↗</a><a href="materials/downloads/AI_Research_Package_2026-11-04.zip" download>Download AI package</a></article><article><h3>References &amp; research records</h3><p>APA references, workflow roles, an illustrative event schema and source-version provenance.</p><a href="materials/literature.html">Explore the literature ↗</a><a href="materials/extraction_event.schema.json" download>Download record template</a></article></div></section>'''
    fragment=fragment.replace('50 benchmark cards and the source data','8 displayed benchmark cards, screened candidate evidence and source data')
    fragment=fragment.replace('Current companions to the benchmark atlas, aligned with the manuscript snapshot read on 4 November 2026.','Workflow components, supporting literature and source-linked benchmark evidence for the article.')
    (materials/'home.fragment').write_text(fragment)
    report={'version':VERSION,'source_manuscript_sha256':context['source_manuscript_sha256'],'source_manuscript_not_modified':True,'workflow_modules':12,'current_manuscript_references':len(refs),'source_aras_retained':203,'benchmark_cards':n_selected,'additional_screened_cards':50-n_selected,'source_observations':4094,'current_dated_observations':progress['counts']['displayed_source_observations'],'standalone_navigation':True,'new_model_evaluations':False,'downloads':{ai_zip.name:sha(ai_zip),human_zip.name:sha(human_zip)}}
    dump(materials/'build_validation.json',report);print(json.dumps(report,indent=2))

if __name__=='__main__':main()
