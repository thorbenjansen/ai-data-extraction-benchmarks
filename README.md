# AI-supported data extraction: supplementary material

Public supplement: https://thorbenjansen.github.io/ai-data-extraction-benchmarks/

Eight benchmark families, 27 separate test conditions and 650 dated observations illustrate time trends in component skills relevant to data extraction. Figures are grouped by Challenges A–D and linked to twelve workflow components. Hover, focus, click or tap a point to inspect its model, original score, test condition, APA result reference and source row.

The figures deliberately select positive trends and cannot estimate the prevalence or average size of general progress. The screening record documents all 50 candidate families and every display decision. Metric versions, prompts, tools and other recorded test conditions remain separate. No benchmark validates a complete psychological data-extraction workflow or its auditability.

Workflow and literature materials include twelve candidate modules, 45 manuscript references and an AI research package with 203 source ARAs. The same accuracy and auditability criteria apply to human experts, research assistants, LLMs and combined workflows. Agreement with human-extracted review data alone does not establish either actor’s accuracy.

## Evidence and reproducibility

Evidence cutoff: 31 October 2026. Source scores, release evidence and fitted curves retain their documented values. No new model evaluation was conducted. Every plotted observation has a source-bound metadata record in `data/point_details.json`; original source fields remain in the data CSVs. `package_manifest.json` records file hashes.

Requirements: Python with lxml and numpy, plus Pandoc for the reader/AI packages. Run `reproducibility/point_details.py`, `reproducibility/build_article_materials.py --source-ai-zip /path/to/source-corpus.zip`, `reproducibility/unified_home.py`, and `reproducibility/standalone_pages.py`. The source corpus is included in the downloadable AI research package, which can itself be passed as the source input; its checksum is checked against `materials/build_validation.json`. A source-corpus input checksum is also recorded in `reproducibility/materials_sources/context.json`. Use the supplied validators to check point metadata, packages and navigation. Chart interactivity is a progressive enhancement of the source SVG figures; the images remain available when scripting or network loading is unavailable.
