"""Check current reader/agent resources, frozen data and local navigation."""
from pathlib import Path
from urllib.parse import urlsplit,unquote
from lxml import html as H
import csv,hashlib,io,json,zipfile

ROOT=Path(__file__).resolve().parent.parent
M=ROOT/'materials'
load=lambda p:json.loads(p.read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
version=load(M/'version.json');context=load(ROOT/'reproducibility/materials_sources/context.json')
assert version==context
refs=load(M/'references.json');assert refs==load(ROOT/'reproducibility/materials_sources/manuscript_references.json')
assert len(refs)==45 and len({r['id']for r in refs})==45
model=load(M/'workflow_model.json');modules=model['modules'];ids={m['id']for m in modules}
assert len(modules)==len(ids)==12
assert all(set(m['sources'])<={r['id']for r in refs}for m in modules)
assert all(m['purpose']and m['record']and m['evaluate']and m['question']and m['limit']for m in modules)
assert len(load(M/'AI Data Extraction Workflow 2026-11-04.canvas')['nodes'])==12
assert set(load(M/'extraction_event.schema.json')['properties']['step']['enum'])==ids
with(ROOT/'data/article_benchmark_register.csv').open(encoding='utf-8-sig')as f:reg=list(csv.DictReader(f))
families={r['family']for r in reg};assert len(families)==50
for m in modules:assert set(m['benchmark_families'])<=families
assert next(m for m in modules if m['id']=='audit')['benchmark_role']=='partial diagnostic only'
assert not next(m for m in modules if m['id']=='collaborate')['benchmark_families']
assert not next(m for m in modules if m['id']=='adjudicate')['benchmark_families']
with zipfile.ZipFile(M/'downloads/AI_Research_Package_2026-11-04.zip')as z:
    assert z.testzip()is None
    names=z.namelist();prefix=names[0].split('/')[0]+'/'
    assert not any('..'in Path(n).parts or n.startswith('/')for n in names)
    assert not any(Path(n).suffix.lower()in ['.pdf','.docx','.xlsx']for n in names)
    manifest=json.loads(z.read(prefix+'MANIFEST.json'))
    for path,digest in manifest['files'].items():assert sha(z.read(prefix+path))==digest,path
    source_index=json.loads(z.read(prefix+'literature/source_index.json'));assert len(source_index)==203
    assert all(prefix+r['paper_path']in names for r in source_index)
    assert sum(n.startswith(prefix+'benchmarks/')and n.endswith('.md')for n in names)==50
    assert sum(n.startswith(prefix+'workflow/')and Path(n).name[:2].isdigit()and n.endswith('.md')for n in names)==12
    assert json.loads(z.read(prefix+'CURRENT_CONTEXT.json'))==context
    assert 'REJOINDER_CONTEXT.md'not in [n[len(prefix):]for n in names]
    assert not any('/ai-data-extraction-rejoinder-workflow-ara/'in n for n in names)
    core=z.read(prefix+'START_HERE.md').decode()
    assert 'did not independently assess the quality'in core and 'Do not infer a general human advantage'in core
    data_files=[n for n in names if n.startswith(prefix+'data/')]
    for n in data_files:assert z.read(n)==(ROOT/n[len(prefix):]).read_bytes(),n
    observations=list(csv.DictReader(io.StringIO(z.read(prefix+'data/article_observations.csv').decode('utf-8-sig'))))
    assert len(observations)==4094
with zipfile.ZipFile(M/'downloads/Workflow_Literature_Supplement_2026-11-04.zip')as z:
    assert z.testzip()is None
    for name in ['workflow.html','literature.html']:
        doc=H.fromstring(z.read(name))
        assert not doc.xpath('//script|//link[@rel="stylesheet"]')
        for link in doc.xpath('//@href'):
            u=urlsplit(link)
            if u.scheme or u.netloc:continue
            target=unquote(u.path)or name
            assert target in z.namelist(),(name,link)
            if u.fragment and target.endswith('.html'):
                assert unquote(u.fragment)in H.fromstring(z.read(target)).xpath('//@id'),(name,link)
pages=list(ROOT.glob('*.html'))+list((ROOT/'benchmarks').glob('*.html'))+list(M.glob('*.html'))
cache={p.resolve():H.fromstring(p.read_bytes())for p in pages};links=0
for path,doc in cache.items():
    html_ids=doc.xpath('//@id');assert len(html_ids)==len(set(html_ids)),path.name
    assert not doc.xpath('//a[contains(@href,"claims.html")]'),path.name
    for link in doc.xpath('//@href|//@src'):
        u=urlsplit(str(link))
        if u.scheme or u.netloc:continue
        target=(path.parent/unquote(u.path)).resolve()if u.path else path
        assert target.is_relative_to(ROOT)
        assert target.is_file(),(str(path.relative_to(ROOT)),link)
        links+=1
        if u.fragment and target.suffix=='.html':assert unquote(u.fragment)in cache[target].xpath('//@id'),(path.name,link)
home=cache[(ROOT/'index.html').resolve()]
assert home.xpath('//*[@id="article-materials"]')
assert len(home.xpath('//article[@data-family]'))==86
assert not (ROOT/'claims.html').exists()
assert len(cache[(M/'workflow.html').resolve()].xpath('//h3[starts-with(@id,"module-")]'))==12
report={'status':'passed','version':'2026-11-04','reader_and_ai_packages_reopened':True,'source_ara_paths_checked':203,'benchmark_cards':50,'workflow_modules':12,'reference_entries':45,'source_observations':4094,'copied_benchmark_data_files_byte_identical':len(data_files),'active_html_pages_checked':len(pages),'local_links_checked':links,'obsolete_commentary_page_absent':True,'source_manuscript_not_published':True,'old_draft_navigation_not_reused':True}
(M/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
