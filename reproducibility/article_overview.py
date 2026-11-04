"""Article-facing register and PDF atlas from the frozen supplement; no new scores."""
from pathlib import Path
from collections import defaultdict
import csv, json, html, hashlib, re, io, sys
from lxml import html as LH

E=lambda x:html.escape(str(x),quote=True)
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(p,rows):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def unique(values):return list(dict.fromkeys(values))
def citation(c):
    text=E(c['apa']).replace(E(c['url']),'<a href="'+E(c['url'])+'">'+E(c['url'])+'</a>')
    return '<div class="citation"><p>'+text+'</p><button class="copy" data-copy="'+E(c['apa'])+'" type="button">Copy APA reference</button></div>'

def build(root):
    root=Path(root);d=root/'data'
    figures=json.loads((d/'time_chart_index.json').read_text())
    bib=json.loads((d/'bibliography.json').read_text())
    from timeplots import ORDER
    steps=sorted(json.loads((d/'workflow_steps.json').read_text()),key=lambda s:ORDER.index(s['id']));sd={s['id']:s for s in steps}
    claims=json.loads((d/'commentary_requirements.json').read_text())
    data=read(d/'all_source_values.csv');release={r['observation_id']:r for r in read(d/'release_date_audit.csv')}
    visible={r['observation_id'] for r in read(d/'time_plot_geometry.csv')}
    maps=read(d/'workflow_mapping.csv');cat=read(root/'reproducibility/inputs/benchmark_catalogue.csv')
    byfamily=defaultdict(list);byseries=defaultdict(list)
    for r in data:byfamily[r['family']].append(r);byseries[r['series_id']].append(r)
    fitvisible=set()
    for f in figures:
        for v in f['time_variants']:
            if 'class="mean-trend"' in (root/v['path']).read_text():fitvisible.add(v['id'])
    # Curves use their published condition identity; counts never sum overlapping workflow mappings.
    conditions=[];register=[];cards=[]
    for f in figures:
        family=f['family'];rr=byfamily[family];cc=[c for c in cat if c['record_type']=='benchmark' and c['family']==family]
        mm=[m for m in maps if m['family']==family];stepids=[s['id'] for s in steps if any(m['step']==s['id'] for m in mm)]
        bids=unique(r['benchmark_id'] for r in rr);refs=unique(r['source_ref'] for r in rr)
        cr=[c for c in claims if family in c['benchmark_families']]
        added=sum(bool(r.get('integration_candidate_id')) for r in rr);held=sum(r.get('plot_eligible')=='False' for r in rr)
        nvisible=sum(r['observation_id'] in visible for r in rr)
        curveids={v['id'] for v in f['time_variants'] if v['id'] in fitvisible}
        row=dict(figure_id=f['figure_id'],family=family,benchmark_ids='; '.join(bids),task='; '.join(unique(c['task'] for c in cc)),workflow_steps='; '.join(stepids),workflow_step_names='; '.join(sd[s]['name'] for s in stepids),manuscript_anchors='; '.join(sd[s]['anchor'] for s in stepids),evidence_scope='; '.join(unique(c['evidence_scope'] for c in cc)),transfer_limits='; '.join(unique(c['transfer_limit'] for c in cc)),source_observations=len(rr),added_model_card_observations=added,separate_conditions=len(f['time_variants']),dated_observations=sum(release[r['observation_id']]['status']=='Plotted' for r in rr),visible_observations=nvisible,definition_held_observations=held,visible_mean_curves=len(curveids),source_refs='; '.join(refs),commentary_requirement_rows='; '.join(str(c['workbook_row']) for c in cr),benchmark_apa='\n'.join(b+' | '+bib['benchmarks'][b]['apa'] for b in bids),html='benchmarks/'+f['filename']+'.html',vector_pdf=f['vector_pdf'],source_csv=f['source_values_csv'])
        register.append(row)
        for v in f['time_variants']:
            ss=byseries[v['id']];r=ss[0];c=v['mean_curve']
            conditions.append(dict(figure_id=f['figure_id'],family=family,series_id=v['id'],benchmark_id=r['benchmark_id'],benchmark_version=r.get('benchmark_version') or r['benchmark'],metric=r['metric'],axis_max_native=r['axis_max_native'],metric_direction=r['metric_direction'],condition=r['condition'],source_observations=len(ss),added_model_card_observations=sum(bool(x.get('integration_candidate_id')) for x in ss),dated_observations=v['dated'],visible_observations=v['plotted'],definition_held_observations=v['definition_held'],mean_curve_status=c['status'],mean_curve_reason=c['reason'],mean_curve_visible=v['id'] in fitvisible,figure_date_start=v['date_min'],figure_date_end=v['date_max'],source_refs='; '.join(unique(x['source_ref'] for x in ss)),observation_ids='; '.join(x['observation_id'] for x in ss),benchmark_apa=bib['benchmarks'][r['benchmark_id']]['apa'],figure_svg=v['path'],raw_data=row['html']+'#records'))
        v=f['primary_variant'];path=row['html']
        search=' '.join([family,row['task'],row['workflow_step_names'],*refs,*[r['metric']+' '+r['condition'] for r in rr]]).lower()
        flag='timeline' if nvisible else 'no-timeline'
        if added:flag+=' updated'
        if held:flag+=' held'
        if curveids:flag+=' mean'
        card=f'<article class="flow-card atlas-card" id="{f["figure_id"]}" data-family="{E(family)}" data-search="{E(search)}" data-steps="{" ".join(stepids)}" data-flags="{flag}"><header><div><p class="eyebrow">{f["figure_id"]} · {E(row["evidence_scope"])}</p><h2><a href="{path}">{E(family)}</a></h2></div><span class="date-state">'+('Documented model releases' if v['plotted'] else 'Definition/date unresolved' if v['dated'] else 'Release dates unresolved')+'</span></header>'
        card+='<p class="atlas-task">'+E(row['task'])+'.</p><p class="atlas-steps">'+' · '.join(f'<a href="index.html#step-{s}">{steps.index(sd[s])+1:02} {E(sd[s]["name"])}</a>' for s in stepids)+'</p>'
        card+='<div class="atlas-counts">'+''.join(f'<span><strong>{n:,}</strong>{label}</span>' for n,label in [(len(rr),'source values'),(added,'new values'),(len(f['time_variants']),'conditions'),(nvisible,'time points'),(len(curveids),'visible curves')])+'</div>'
        card+=f'<label class="variant-label">Benchmark condition<select class="time-variant" aria-label="Condition for {E(family)} in all benchmarks">'
        for vv in f['time_variants']:
            label=vv['heading']+' · '+vv['condition']
            card+=f'<option value="{E(vv["path"])}" data-plotted="{vv["plotted"]}" data-dated="{vv["dated"]}" data-total="{vv["observations"]}" data-definition-held="{vv["definition_held"]}" data-undated="{vv["undated"]}" data-range-start="{vv["date_min"]}" data-range-end="{vv["date_max"]}" data-benchmark-id="{E(vv["benchmark_id"])}" data-apa-html="{E(citation(bib["benchmarks"][vv["benchmark_id"]]))}"'+(' selected' if vv['id']==v['id'] else '')+'>'+E(label)+'</option>'
        card+='</select></label>'
        card+=f'<a class="figure-link" href="{path}#records" aria-label="Open source values for {E(family)}"><img class="time-preview" src="{v["path"]}" alt="{E(family)}: model release date and native benchmark performance" width="860" height="565" loading="lazy"><span class="figure-open">Open data and exact result references ↗</span></a>'
        card+='<div class="benchmark-apa" data-benchmark-id="'+v['benchmark_id']+'"><p class="eyebrow">Selected benchmark reference (APA)</p>'+citation(bib['benchmarks'][v['benchmark_id']])+'</div>'
        card+=f'<div class="card-foot"><span class="variant-count">{v["plotted"]} shown / {v["observations"]} observations · {v["undated"]} undated · {v["definition_held"]} definition-held</span><a href="{f["vector_pdf"]}">Vector PDF</a></div>'
        card+='<details class="atlas-scope"><summary>Article use, coverage and interpretation</summary><p>'+E(row['transfer_limits'])+'</p>'
        card+=f'<p>{held} source values have unresolved metric/version definitions and remain raw-only.</p><p>Results: '+', '.join(f'<a href="references.html#ref-{s}">[{s}]</a>' for s in refs)+'.</p>'
        card+='<p>Manuscript mapping: '+E(row['manuscript_anchors'])+'.</p>'
        if cr:card+='<p>Related commentary requirements: '+', '.join(f'<a href="claims.html#claim-{c["workbook_row"]}">{E(c["source"])} · row {c["workbook_row"]}</a>' for c in cr)+'.</p>'
        card+='<p><a href="'+path+'#benchmark-reference">All benchmark-version APA references</a> · <a href="'+row['source_csv']+'" download>All family source values</a></p></details></article>'
        cards.append(card)
    # Observation-level article table joins dates and citations exactly once per original row.
    obs=[]
    for r in data:
        a=release[r['observation_id']];br=bib['benchmarks'][r['benchmark_id']];sr=bib['result_sources'][r['source_ref']]
        obs.append({**r,'documented_model_release':a['release_date'],'release_date_low':a['date_low'],'release_date_high':a['date_high'],'release_date_precision':a['date_precision'],'release_source_url':a['release_source'],'release_source_locator':a['release_locator'],'release_reference_apa':a['release_apa'],'release_status':a['status'],'release_omission_or_caution':a['reason'],'displayed_in_time_figure':r['observation_id'] in visible,'benchmark_reference_apa':br['apa'],'benchmark_reference_url':br['url'],'result_reference_apa':sr['citation']['apa']})
    write(d/'article_benchmark_register.csv',register);write(d/'article_conditions.csv',conditions);write(d/'article_observations.csv',obs)
    summary=dict(benchmark_families=len(register),benchmark_versions=len(unique(r['benchmark_id'] for r in data)),source_observations=len(obs),added_model_card_observations=sum(bool(r.get('integration_candidate_id')) for r in data),separate_conditions=len(conditions),visible_observations=len(visible),definition_held_observations=sum(r.get('plot_eligible')=='False' for r in data),visible_mean_curves=len(fitvisible),axis_policy='data-adaptive per condition; every eligible release shown',display_start=min(v['date_min'] for f in figures for v in f['time_variants'] if v['date_min']),display_end=max(v['date_max'] for f in figures for v in f['time_variants'] if v['date_max']),source_values_sha256=hashlib.sha256((d/'all_source_values.csv').read_bytes()).hexdigest())
    dump(d/'article_overview_summary.json',summary)
    body='<p class="eyebrow">Article evidence register · updated 31 October 2026</p><h1>All benchmarks</h1><p class="lead">All 82 benchmark families in one place, linked to the extraction workflow, their task conditions and original evidence.</p>'
    body+='<p>4,940 source observations, including 1,085 additional model-card values. The figures show all 2,036 eligible observations from 65 families with documented model releases. Each condition uses its full available date range with a small margin; time spans differ between figures. Versions, metrics, scales, languages and test conditions remain separate.</p>'
    body+='<div class="page-links"><a href="All_Benchmarks_Article_Atlas.pdf">Complete article atlas (PDF)</a><a href="data/article_benchmark_register.csv" download>Benchmark register (82 rows)</a><a href="data/article_conditions.csv" download>Condition register (581 rows)</a><a href="data/article_observations.csv" download>All observations with APA references and releases (4,940 rows)</a></div>'
    body+='<div class="scope atlas-method"><p><strong>How to use this evidence.</strong> The curves describe selected reported configurations within their own conditions. They are not a common accuracy scale or an independent replication. A component result does not establish end-to-end extraction quality. Human agreement alone does not establish correctness or a general human–LLM ranking.</p><p>125 observations remain raw-only because a required definition is unresolved. Missing release dates are a separate issue; no eligible release is excluded by a fixed calendar window. <a href="methods.html">Methods and definition decisions</a> · <a href="model-releases.html">Central model-release bibliography</a>.</p></div>'
    body+='<div class="controls atlas-controls"><label>Find a benchmark or condition<input id="atlas-search" type="search" placeholder="Benchmark, metric, model-card source…"></label><label>Workflow step<select id="atlas-step"><option value="">All workflow steps</option>'+''.join(f'<option value="{s["id"]}">{i:02} {E(s["name"])}</option>' for i,s in enumerate(steps,1))+'</select></label><label>Evidence availability<select id="atlas-status"><option value="">All benchmark families</option><option value="updated">With new model-card values</option><option value="timeline">With documented time points</option><option value="mean">With supported mean curves</option><option value="held">With unresolved definitions</option><option value="no-timeline">Without documented time points</option></select></label><span id="atlas-count" aria-live="polite">82 benchmark families</span></div><p class="atlas-empty" hidden>No benchmark families match these filters.</p><div class="atlas-grid">'+''.join(cards)+'</div>'
    doc=LH.fromstring((root/'index.html').read_text());main=doc.xpath('//main')[0];main.clear();main.set('id','content')
    for child in LH.fragments_fromstring(body):main.append(child)
    doc.xpath('//title')[0].text='All benchmarks | Data extraction benchmarks';doc.xpath('//body')[0].set('class','supplement-page atlas-home')
    (root/'all-benchmarks.html').write_text('<!doctype html>'+LH.tostring(doc,encoding='unicode',method='html'))
    # Keep the workflow start page and all existing deep links; add the overview to every navigation.
    csshash=hashlib.sha256((root/'assets/style.css').read_bytes()).hexdigest()[:10];jshash=hashlib.sha256((root/'assets/app.js').read_bytes()).hexdigest()[:10]
    for p in root.rglob('*.html'):
        text=p.read_text();prefix='../' if p.parent.name=='benchmarks' else ''
        text=text.replace(f'<a href="{prefix}index.html">All benchmarks</a>',f'<a href="{prefix}index.html">Workflow</a><a href="{prefix}all-benchmarks.html">All benchmarks</a>')
        text=re.sub(r'assets/style.css\?v=[a-f0-9]+','assets/style.css?v='+csshash,text);text=re.sub(r'assets/app.js\?v=[a-f0-9]+','assets/app.js?v='+jshash,text)
        p.write_text(text)
    build_pdf(root,figures,register,conditions,bib,steps,claims)
    return summary

def build_pdf(root,figures,register,conditions,bib,steps,claims):
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4,landscape
    from reportlab.pdfgen import canvas
    from pypdf import PdfReader,PdfWriter,Transformation
    from timeplots import font_metrics
    font_metrics();W,H=landscape(A4);styles=getSampleStyleSheet()
    for name,size,leading in [('Body',10,14),('Small',8,11),('Heading',21,26),('Subhead',12,16)]:
        styles.add(ParagraphStyle(name,fontName='Arial-Bold' if name in ['Heading','Subhead'] else 'Arial',fontSize=size,leading=leading,textColor=colors.HexColor('#17364a'),spaceAfter=8))
    P=lambda t,style='Body':Paragraph(t,styles[style])
    def note(c,doc):
        c.setFont('Arial',8);c.setFillColor(colors.HexColor('#607985'));c.drawString(38,22,'DATA EXTRACTION | ALL BENCHMARKS | 31 OCTOBER 2026')
    def pdf_story(story):
        buf=io.BytesIO();doc=SimpleDocTemplate(buf,pagesize=(W,H),rightMargin=38,leftMargin=38,topMargin=35,bottomMargin=38,title='Selected 50 benchmarks: Article evidence atlas',author='Benchmark supplement',invariant=1)
        doc.build(story,onFirstPage=note,onLaterPages=note);return PdfReader(io.BytesIO(buf.getvalue()))
    writer=PdfWriter();page_register=[];condition_map=defaultdict(list)
    for c in conditions:condition_map[c['family']].append(c)
    story=[P('Selected 50 benchmarks','Heading'),P('Article evidence atlas','Subhead'),P('Selected 2 November 2026. 50 benchmark families; 54 benchmark-version entries; 4,094 source observations; 391 separate conditions. Source cutoff: 31 October 2026.'),Spacer(1,12),P('Reading this supplement','Subhead'),P('Each family chapter gives its benchmark APA references, workflow mapping, scope limits and complete condition inventory. The following vector figures retain the reviewed native scores and release dates. Every figure carries its benchmark-version APA reference; result-source IDs resolve in the final bibliography and the HTML observation table.'),P('Each figure uses the full eligible release-date range of its own condition, with a small margin. All 1,716 eligible points from 40 families are visible, including older models. Time spans differ; compare the calendar labels rather than apparent slopes across figures. Undated observations remain in the linked tables. Families without eligible points have an explicit gap panel.'),P('Versions, metrics, scales, languages, tool settings, reasoning modes, context lengths and frozen source cohorts are separate. The 29 definition-held values are retained as raw data without time points or mean curves.'),P('A component benchmark does not demonstrate complete extraction quality. The original study measured agreement and did not independently establish human accuracy. Disagreement alone therefore does not establish that LLMs performed worse than humans.'),P('Machine-readable article tables','Subhead'),P('data/article_benchmark_register.csv: 50 family rows. data/article_conditions.csv: all 391 conditions and their inclusion/curve status. data/article_observations.csv: all 4,094 source observations, joined once to their release evidence, benchmark APA and result-source APA. The accompanying HTML supplement gives every exact table/cell/page locator and preserves the original values.'),PageBreak(),P('Trend method and interpretation','Heading'),P('The dashed gold line is Nadaraya-Watson Gaussian-kernel regression, fitted separately within a source, metric and test condition, using a 180-day bandwidth. Repeated values for the same configuration and release are averaged first. At least five configurations, four release dates and 90 days of coverage are required. Approximate readings, human references, undated and definition-held values do not enter the fit. No extrapolation or unsupported temporal gaps. Sensitivity grids at 90 and 365 days remain in the CSV data.'),P('94 source-condition series meet the full fitting criteria and have supported segments on their chart-specific time axes. These are descriptive means of selected reported configurations, without a confidence interval. They do not estimate a representative model population, causal progress, a pooled cross-benchmark ability, or end-to-end extraction success.'),P('Source status','Subhead'),P('The 1,085 appended observations are exact published model-card/report numbers, including provider-reported baseline comparisons. These are not new evaluations or independent replications. Unknown release snapshots are not dated from another benchmark crosswalk. Native units are retained; OCRBench scores are not rescaled without a source basis. Unspecified uncertainty terms remain in source text without invented error bars.'),P('Coverage and overlap','Subhead'),P('A family may support several workflow steps and commentary requirements. Those mappings overlap and must not be summed as independent evidence. The collection is a source-bound landscape assembled for this article, not an exhaustive systematic review of every available benchmark.'),PageBreak(),P('Benchmark index','Heading')]
    for r in register:
        story.append(P(f'<b>{r["figure_id"]} {E(r["family"])}</b> | {r["source_observations"]} source values | {r["visible_observations"]} time points | {r["separate_conditions"]} conditions | {r["visible_mean_curves"]} visible mean curves','Small'))
    intro=pdf_story(story);writer.append(intro)
    for f,r in zip(figures,register):
        first=len(writer.pages);cc=condition_map[f['family']]
        story=[P(f'{f["figure_id"]} {E(f["family"])}','Heading'),P(E(r['task'])),P(f'{r["source_observations"]} source values; {r["added_model_card_observations"]} new; {r["separate_conditions"]} separate conditions; {r["visible_observations"]} visible time points; {r["definition_held_observations"]} definition-held values; {r["visible_mean_curves"]} visible mean curves.','Small'),P('Benchmark references (APA)','Subhead')]
        for bid in r['benchmark_ids'].split('; '):story.append(P(E(bib['benchmarks'][bid]['apa']),'Small'))
        story+=[P('Workflow and article scope','Subhead'),P('Challenges: '+E(r['commentary_challenges'])),P(E(r['workflow_step_names'])),P(E(r['transfer_limits']),'Small'),P('Manuscript anchors: '+E(r['manuscript_anchors']),'Small'),P('Result-source references: '+E(r['source_refs'])+'. Full references appear in the final bibliography.','Small'),P('Complete condition inventory','Subhead')]
        for i,c in enumerate(cc,1):
            state='visible mean curve' if c['mean_curve_visible'] in (True,'True') else 'no visible mean curve: '+(c['mean_curve_reason'] or 'no supported segment in display window')
            if c['definition_held_observations']==c['source_observations']:state='definition unresolved; raw data only'
            story.append(P(f'<b>{i:02}. {E(c["metric"])}</b> | {E(c["condition"])}<br/>{c["source_observations"]} values; {c["visible_observations"]} time points; {E(state)}. Sources: {E(c["source_refs"])}.','Small'))
        writer.append(pdf_story(story));writer.add_outline_item(f'{f["figure_id"]} {f["family"]}',first)
        used=[v for v in f['time_variants'] if v['plotted']] or [f['time_variants'][0]]
        reader=PdfReader(root/f['vector_pdf']);assert len(reader.pages)==len(used)
        for panel,v in zip(reader.pages,used):
            buf=io.BytesIO();cv=canvas.Canvas(buf,pagesize=(W,H),invariant=1)
            cv.setFont('Arial-Bold',10);cv.setFillColor(colors.HexColor('#24536e'));cv.drawString(38,H-25,f'{f["figure_id"]} | {f["family"]}')
            apa=P('Benchmark reference (APA): '+E(bib['benchmarks'][v['benchmark_id']]['apa']),'Small');_,rh=apa.wrap(W-76,160)
            apa.drawOn(cv,38,43);floor=43+rh+8
            footer=P('Result-source references: '+E('; '.join(unique(x['source_ref'] for x in read(root/f['source_values_csv']) if x['series_id']==v['id'])))+'. Exact point locators and raw values: '+E(f['source_values_csv'])+'.','Small');_,fh=footer.wrap(W-76,100);footer.drawOn(cv,38,floor);floor+=fh+6
            scale=min((W-76)/float(panel.mediabox.width),(H-46-floor)/float(panel.mediabox.height))
            cv.save();overlay=PdfReader(io.BytesIO(buf.getvalue())).pages[0];out=writer.add_blank_page(W,H)
            out.merge_transformed_page(panel,Transformation().scale(scale).translate(38+(W-76-float(panel.mediabox.width)*scale)/2,floor),expand=False)
            out.merge_page(overlay)
        page_register.append(dict(figure_id=f['figure_id'],family=f['family'],first_page=first+1,last_page=len(writer.pages),condition_inventory=len(cc),figure_panels=len(used)))
    refstart=len(writer.pages);story=[P('Result-source bibliography','Heading'),P('These references identify where scores were reported. They can differ from the paper introducing a benchmark. Every observation retains its own source URL and exact locator in the article observation table and the HTML benchmark page.')]
    for ref,s in bib['result_sources'].items():story.append(P('['+ref+'] '+E(s['citation']['apa']),'Small'))
    story+=[PageBreak(),P('Model-release evidence','Heading'),P('Model-release dates are documented separately in model-releases.html and data/release_date_audit.csv. The article observation table includes the release APA reference, URL, locator, precision and available interval for each point. Release months are intervals; checkpoint and result dates alone are insufficient.'),P('Reproducibility','Subhead'),P('Use reproducibility/reproduce.py with a new output directory. Reproduction reads frozen data and makes no model or network calls. Original source observations are retained unchanged. The HTML supplement, vector figures, source locators, decisions, full kernel grids and article registers accompany this PDF.')]
    writer.append(pdf_story(story));writer.add_outline_item('Result-source bibliography',refstart)
    writer.add_metadata({'/Title':'Selected 50 benchmarks: Article evidence atlas','/Author':'Benchmark supplement','/Subject':'50 families; 4094 source observations; mapped to Challenges A-D; selected 2026-11-02'})
    # Page numbers are an overlay; the chart vector geometry is unchanged.
    for i,page in enumerate(writer.pages,1):
        buf=io.BytesIO();cv=canvas.Canvas(buf,pagesize=(W,H),invariant=1);cv.setFont('Arial',8);cv.setFillColor(colors.HexColor('#607985'));cv.drawRightString(W-38,22,f'{i} / {len(writer.pages)}');cv.save();page.merge_page(PdfReader(io.BytesIO(buf.getvalue())).pages[0])
    out=root/'All_Benchmarks_Article_Atlas.pdf'
    writer.compress_identical_objects(remove_duplicates=True,remove_unreferenced=True)
    with out.open('wb') as fp:writer.write(fp)
    write(root/'data/article_pdf_index.csv',page_register)

if __name__=='__main__':print(json.dumps(build(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent.parent),indent=2))
