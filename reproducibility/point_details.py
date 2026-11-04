"""Create source-bound point metadata without changing any score or SVG asset."""
from pathlib import Path
import csv,json

ROOT=Path(__file__).resolve().parent.parent

def main():
    with(ROOT/'data/article_benchmark_register.csv').open(encoding='utf-8-sig')as f:
        pages={r['family']:r['html']for r in csv.DictReader(f)}
    fields=['observation_id','model','family','metric','condition','source_value_text','score_native',
            'documented_model_release','release_date_low','release_date_high','release_date_precision',
            'source_ref','source_url','source_locator','source_accessed','result_reference_apa',
            'benchmark_reference_apa','benchmark_reference_url','release_source_url','release_reference_apa']
    points={}
    with(ROOT/'data/article_observations.csv').open(encoding='utf-8-sig')as f:
        for r in csv.DictReader(f):
            if r['displayed_in_time_figure']!='True':continue
            p={k:r[k]for k in fields};p['record_url']=pages[r['family']]+'#'+r['observation_id']
            points[r['observation_id']]=p
    (ROOT/'data/point_details.json').write_text(json.dumps({'points':points},ensure_ascii=False,separators=(',',':'))+'\n')
    print(f'Built exact source metadata for {len(points)} plotted observations.')

if __name__=='__main__':main()
