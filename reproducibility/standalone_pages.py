"""Publish self-contained reader pages; source observations and chart assets stay intact."""
from pathlib import Path
from copy import deepcopy
from lxml import html as H
import csv,json,re

ROOT=Path(__file__).resolve().parent.parent

def save(path,doc):path.write_text('<!doctype html>'+H.tostring(doc,encoding='unicode',method='html'))
def text_replace(doc):
    replacements={
      'Previous source audit:':'Source audit:',
      'previous source audit':'recorded source audit',
      'Previously audited source observation':'Source-checked observation',
      'Previously audited date':'Recorded release-date evidence',
      'Previously frozen primary-source text capture:':'Recorded primary-source text:',
      'Prior source status:':'Verification status:',
      'Source archive':'Screened candidate evidence',
      'source archive':'screened candidate evidence',
      'Current reader supplement':'Workflow and literature supplement',
      'Current workflow literature':'Workflow literature',
      'All article materials · updated 4 November 2026':'Article materials',
    }
    for element in doc.iter():
        for attr in ['text','tail']:
            value=getattr(element,attr)
            if value:
                for old,new in replacements.items():value=value.replace(old,new)
                setattr(element,attr,value)
        if element.get('href'):
            href=element.get('href')
            if re.search(r'(^|/)archive\.html',href):element.set('href',href.replace('archive.html','evidence.html'))

def main():
    method=json.loads((ROOT/'data/mean_curve_method.json').read_text())
    for key in ['conditions','conditions_with_curve','families_with_curve','nonfit_reasons']:method.pop(key,None)
    method.update(scope='Descriptive within-condition smoothing for the benchmark supplement',displayed_conditions=27,displayed_families=8,displayed_dated_observations=650)
    (ROOT/'data/curve_method.json').write_text(json.dumps(method,indent=2)+'\n')
    path=ROOT/'methods.html';doc=H.parse(str(path)).getroot()
    progress=deepcopy(doc.xpath('//*[@id="progress-selection"]')[0])
    for el in progress.xpath('.//p'):
        if 'complete source archive' in ''.join(el.itertext()):
            el.text='These thresholds are transparent editorial choices for selecting illustrative time trends. They are not preregistered or established standards. Model composition, task difficulty and observed periods differ. The figures cannot estimate general progress, establish a causal effect of release date, or validate transfer to psychological data extraction. All candidate screening decisions are documented.'
    for a in progress.xpath('.//a'):
        if a.get('href')=='archive.html':a.set('href','evidence.html');a.text='Benchmark screening record'
    mean=[deepcopy(doc.xpath('//*[@id="mean-curves"]')[0])]
    node=doc.xpath('//*[@id="mean-curves"]')[0].getnext()
    while node is not None and node.tag not in {'h2','section'}:
        if not ''.join(node.itertext()).startswith('Current coverage:'):mean.append(deepcopy(node))
        node=node.getnext()
    main_node=doc.xpath('//main')[0];main_node.clear();main_node.set('id','content')
    intro='''<p class="eyebrow">Scope, sources and interpretation</p><h1>Methods for the benchmark supplement</h1><p class="lead">Eight benchmark families, 27 separate test conditions and 650 dated observations provide illustrative time trends for skills relevant to data extraction.</p><section id="interactive-points"><h2>Interactive data points</h2><p>Hover over or focus a point to see its model name, original score, metric, test condition, release evidence and APA result reference. Click, tap or press Enter to keep the details open. The source-row link opens the exact observation and its full provenance. Overlapping observations can be selected individually within the panel. Escape or the close button dismisses the panel.</p><p>The published values and point positions are source-bound. Adding interactivity does not alter the scores, dates, conditions or fitted curves. <a href="data/point_details.json">Point metadata</a> · <a href="data/progress_observations.csv">Displayed dated observations</a>.</p></section>'''
    for el in H.fragments_fromstring(intro):main_node.append(el)
    main_node.append(progress)
    dates='''<section id="release-dates"><h2>Model release dates and comparable conditions</h2><p>X positions use documented public model releases or source-reported release months. Model aliases must identify the evaluated release cohort; a benchmark publication, checkpoint filename or result date is not substituted for a release date. Month-only dates retain their full interval and use its midpoint for positioning. Missing or unresolved dates are not invented.</p><p>Each figure spans the documented eligible release history of its own source, metric, benchmark version and test condition. Calendar ranges can differ between figures. Prompts, tools, reasoning modes, splits, context lengths and budgets remain separate whenever recorded as different evaluation conditions. Scores retain their native units; no pooled cross-benchmark accuracy is calculated.</p><p><a href="model-releases.html">Release-date sources and verification status</a> · <a href="data/release_date_audit.csv">Release-date decisions</a> · <a href="data/article_conditions.csv">Candidate condition register</a>.</p></section>'''
    for el in H.fragments_fromstring(dates):main_node.append(el)
    for el in mean:main_node.append(el)
    end='''<section id="selection"><h2>Scope of the evidence</h2><p>The figures illustrate component capabilities. No displayed benchmark is a dedicated test of codebook-based extraction from psychological studies or a validation of a complete human–AI workflow. The workflow links and A–D assignments indicate task relevance. Shared datasets, subtasks and benchmark versions are not independent studies.</p><p>Agreement with human-extracted review data does not by itself establish either actor’s accuracy. Human-only, LLM and joint workflows require independent source verification and comparable product-accuracy and process-auditability criteria.</p><p>The screening record covers 50 candidate families and documents why a family is included in or excluded from the displayed progress examples. Mixed findings and insufficient dated observations remain documented. <a href="evidence.html">Screening record</a> · <a href="data/progress_family_decisions.csv">Family decisions</a> · <a href="data/progress_condition_decisions.csv">Condition decisions</a>.</p></section><section id="sources"><h2>Sources and reproducibility</h2><p>Each score retains its primary result reference, URL, locator, access date, metric and condition. Model release sources are recorded separately. Where source access or model identity remains uncertain, the recorded status is retained. Benchmark citations describe the evaluation task; result citations identify the evidence for a numerical value.</p><p>The evidence cutoff is 31 October 2026. Curves summarize reported model configurations; no new model evaluation was conducted. Reproducibility materials document the data, date decisions, calculation inputs, chart geometry and descriptive smoothing method.</p><p><a href="references.html">Benchmark and result references</a> · <a href="data/progress_selection.json">Selection specification</a> · <a href="data/progress_display_order.json">Figure ordering</a> · <a href="package_manifest.json">File checksums</a> · <a href="materials/workflow.html">Workflow and literature guide</a>.</p></section>'''
    for el in H.fragments_fromstring(end):main_node.append(el)
    text_replace(doc);save(path,doc)
    bib=json.loads((ROOT/'data/bibliography.json').read_text())
    pages=list(ROOT.glob('*.html'))+list((ROOT/'benchmarks').glob('*.html'))+list((ROOT/'materials').glob('*.html'))
    for path in pages:
        doc=H.parse(str(path)).getroot();text_replace(doc)
        for a in doc.xpath('//a[contains(@href,"mean_curve_method.json")]'):a.set('href',a.get('href').replace('mean_curve_method.json','curve_method.json'))
        if path.name=='references.html':
            doc.xpath('//h1')[0].text='Benchmark and result references'
            for h in doc.xpath('//h3'):
                t=''.join(h.itertext())
                if 'legacy_figure'in t:
                    match=re.search(r'\[(S\d+)\]',t)
                    if match:h.text='['+match.group(1)+'] '+bib['result_sources'][match.group(1)]['citation']['title']
        if path.name=='model-releases.html':
            for p in doc.xpath('//p'):
                if 'preceding figure package'in ''.join(p.itertext()):
                    p.clear();p.text='These references document model release evidence, including exact named-model identity checks and source-reported release months. Each record retains its verification status. A checkpoint or benchmark result date alone is not treated as a public release. Where a cited page could not be rechecked, that limitation is recorded.'
        save(path,doc)
    print('Built self-contained methods, reader language and screening navigation.')

if __name__=='__main__':main()
