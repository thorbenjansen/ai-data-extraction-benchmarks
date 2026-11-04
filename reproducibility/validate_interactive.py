"""Verify point-to-source bindings and self-contained reader navigation."""
from pathlib import Path
from collections import Counter
from lxml import html as H,etree as E
import csv,json,re,hashlib

ROOT=Path(__file__).resolve().parent.parent
points=json.loads((ROOT/'data/point_details.json').read_text())['points']
with(ROOT/'data/article_observations.csv').open(encoding='utf-8-sig')as f:rows={r['observation_id']:r for r in csv.DictReader(f)}
assert set(points)=={oid for oid,r in rows.items()if r['displayed_in_time_figure']=='True'}
for oid,p in points.items():
    for key,value in p.items():
        if key!='record_url':assert value==rows[oid][key],(oid,key)
    path,anchor=p['record_url'].split('#')
    assert anchor==oid and H.parse(str(ROOT/path)).xpath(f'//*[@id="{oid}"]')
    assert p['result_reference_apa']and p['source_locator']and p['source_url']and p['model']
home=H.parse(str(ROOT/'index.html')).getroot()
assert home.xpath('//main/*[1][@id="workflow-map" and @open]')
assert not home.xpath('//*[@class="flow-intro"]|//*[@id="article-materials"]')
cards=home.xpath('//article[@data-family]');assert len(cards)==13
svgs={o.get('value')for o in home.xpath('//select[@class="time-variant"]/option')}
assert len(svgs)==27
point_bindings=0;source_ids=set()
for path in svgs:
    doc=E.parse(str(ROOT/path))
    for a in doc.xpath('//*[local-name()="a" and @class="time-point"]'):
        ids=a.get('data-observation-ids').split()
        for oid in ids:
            assert oid in points,(path,oid)
            assert float(a.get('data-score'))==float(points[oid]['score_native']),(path,oid)
            source_ids.add(oid)
        point_bindings+=1
assert len(source_ids)==650
assert len(home.xpath('//div[contains(concat(" ",@class," ")," interactive-figure ")]'))==13
assert not home.xpath('//a[@class="figure-link"]')
assert not home.xpath('//section[contains(@class,"unified-scope")]')
history=re.compile(r'earlier (?:reader|draft|supplement|OSF corpus)|previous (?:version|supplement)|preceding figure package|original 50.family|full source archive|replaces the earlier|superseded|82.family|source archive|archived cards',re.I)
pages=list(ROOT.glob('*.html'))+list((ROOT/'materials').glob('*.html'))+list((ROOT/'benchmarks').glob('*.html'))
for path in pages:
    doc=H.parse(str(path))
    text=' '.join(doc.xpath('//main//text()'))
    assert not history.search(text),(path.name,history.search(text).group())
    assert not any('archive.html'in href for href in doc.xpath('//a/@href')),path.name
    assert not any('All_Benchmarks_Article_Atlas.pdf'in href for href in doc.xpath('//a/@href')),path.name
    assert doc.xpath('//script[contains(@src,"assets/app.js")]')or doc.xpath('//link[@rel="canonical"]'),path.name
original=json.loads((ROOT/'reproducibility/inputs/selected50_snapshot_manifest.json').read_text())['files'];unchanged=0
for path,digest in original.items():
    if path.startswith(('data/','figures/'))or path=='All_Benchmarks_Article_Atlas.pdf':
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
        unchanged+=1
report=dict(status='passed',point_metadata_records=len(points),main_page_distinct_point_ids=len(source_ids),main_page_conditions=len(svgs),point_bindings_checked=point_bindings,reader_pages_checked=len(pages),source_scientific_files_unchanged=unchanged,all_metadata_fields_match_source_rows=True,prior_supplement_navigation_absent=True)
(ROOT/'interactive_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
