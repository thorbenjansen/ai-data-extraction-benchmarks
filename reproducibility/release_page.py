"""One shared release-date bibliography; benchmark citations stay with the figures."""
from html import escape as E
from collections import defaultdict
import hashlib

def render(audit,registry,retained_sources,root,apa_html):
 body='''<p class="eyebrow">Shared release-date evidence</p><h1>Model release-date sources</h1><p class="lead">The common bibliography for model dates used throughout the supplement.</p><p>These sources establish public model release dates separately from benchmark results. The benchmark reference and each score's result source remain on its benchmark page. Older documented models are included on the chart-specific calendar axes. This bibliography covers release evidence throughout the full retained history.</p><div class="page-links"><a href="#reviewed-releases">Reviewed release and identity references</a><a href="#retained-releases">Retained release-source evidence</a><a href="data/release_date_audit.csv">Every model/date decision (CSV)</a></div><section id="reviewed-releases"><h2>Reviewed release and identity references</h2><p>The [RD…] identifiers link directly from the source-value tables. An identity crosswalk is shown where the benchmark's abbreviated model label required a separate model specification.</p>'''
 for rule in registry:
  rid=rule['release_id'];snap=root/rule['snapshot_file']
  c=dict(apa=rule['apa'],title=rule['title'],url=rule['url'],kind='Release source')
  body+=f'<article class="release-reference" id="release-{rid}"><h3>[{rid}] {E(rule["release_date"])} · {E(rule["title"])}</h3>'+apa_html(c)
  body+='<p>'+E(rule['evidence'])+'</p><small>Exact location: '+E(rule['locator'])+'</small>'
  if rule.get('identity_source'):body+='<p>Evaluated-model identity: '+E(rule['identity_evidence'])+' <a href="'+E(rule['identity_source'])+'">Benchmark model specification</a> ('+E(rule['identity_locator'])+').</p>'
  body+='<details><summary>Release-evidence audit</summary><p>'+E(rule['date_basis'])+'</p><p><a href="'+E(rule['snapshot_file'])+'">Saved release-source audit</a> · reviewed '+E(rule['accessed'])+'</p><code>'+hashlib.sha256(snap.read_bytes()).hexdigest()+'</code>'
  if rule.get('identity_source_sha256'):body+='<p>'+E(rule['identity_hash_target'])+'</p><code>'+rule['identity_source_sha256']+'</code>'
  body+='</details></article>'
 body+='</section><section id="retained-releases"><h2>Retained release-source evidence</h2><p>These [RL…] references carry the release evidence inherited from the preceding figure package, including exact named-model cross-references and source-reported release months. They preserve the prior source status and its limitations; a checkpoint or benchmark result date alone is not treated as a release. Full earlier captures remain in benchmark_figures_paper_style_2026-10-30.</p>'
 groups=defaultdict(list);sources={r['url_or_basis']:r for r in retained_sources}
 for a in audit.values():
  if a['status']=='Plotted' and not a['release_id']:groups[a['release_reference_id']].append(a)
 for rid,rr in sorted(groups.items()):
  url=rr[0]['release_source'];old=sources.get(url,{})
  body+=f'<article class="release-reference" id="release-{rid}"><h3>[{rid}] Retained release source</h3><p><a href="{E(url)}">{E(url)}</a></p>'
  if old:body+='<p>Prior source status: '+E(old['status'])+'; audit date: '+E(old['accessed'])+'.</p>'
  body+='<details><summary>Documented model/date assignments ('+str(len({(a['model'],a['release_date']) for a in rr}))+')</summary><ul>'
  for model,date,basis in sorted({(a['model'],a['release_date'],a['release_basis']) for a in rr}):body+='<li><strong>'+E(model)+'</strong> · '+E(date)+' · '+E(basis)+'</li>'
  body+='</ul>'
  if old.get('sha256'):body+='<p>Prior source-capture SHA-256:</p><code>'+E(old['sha256'])+'</code>'
  body+='</details></article>'
 return body+'</section>'
