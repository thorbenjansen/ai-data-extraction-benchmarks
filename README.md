# Benchmarks for AI-supported data extraction

[Open the interactive supplement](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/)

This repository publishes the selected 50-benchmark supplementary atlas for AI-supported data extraction. The frozen scientific snapshot was selected on 2 November 2026, with a source-data cutoff of 31 October 2026.

- [Combined Challenges A-D and workflow homepage](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/): scroll down through the four challenges and across their benchmark figures; filter by extraction step.
- The same page includes the chronological map of all 12 workflow steps and their evidence gaps.
- [Model-release dates and primary sources](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/model-releases.html)
- [Methods](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/methods.html)
- [Complete PDF atlas](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/All_Benchmarks_Article_Atlas.pdf)

## Current article companions (4 November 2026)

- [All article materials](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/index.html#article-materials)
- [Workflow and literature guide](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/materials/workflow.html): 12 candidate research components and 45 manuscript bibliography records.
- [AI research package](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/materials/ai.html): current argument and agent entry points, 203 retained source ARAs, 50 benchmark cards, and unchanged benchmark data.

The current reader and agent resources replace the earlier draft-centered navigation. They are aligned to the saved manuscript snapshot identified in `materials/version.json`; the source manuscript is not published or modified. The original study's agreement comparison is kept distinct from independently assessed accuracy, and no general human-versus-LLM accuracy ordering is assumed. Candidate workflow components and research record templates are not presented as a validated universal workflow.

To rebuild these resources, use Python with lxml and Pandoc, download the original public OSF AI archive listed in `reproducibility/materials_sources/context.json`, and run `python reproducibility/build_article_materials.py --source-ai-zip /path/to/archive.zip`, followed by `python reproducibility/unified_home.py` and `python reproducibility/validate_article_materials.py`. The original archive's checksum is checked before use. The complete source ARA corpus remains inside the downloadable current AI package.

The snapshot contains 4,094 source observations across 391 separately identified test conditions. Forty families supply 1,716 plotted time-series observations; families without supported dated observations remain documented without invented time-series points. Each benchmark has APA references, source-bound scores, and a mapping to workflow steps and commentary challenges. Click a figure to inspect its data.

## Interpretation

These benchmarks measure component skills. None is a dedicated test of codebook-based extraction from psychological studies. Their scores do not establish transfer to that task, a human-versus-LLM ranking, or complete workflow auditability. Distinct test conditions retain separate series and curves.

## Snapshot and reproduction

The scientific snapshot is unchanged: all data files, 882 figure assets, the PDF atlas, source references, release dates, challenge assignments and curve inputs retain their original checksums. Navigation was consolidated on 4 November 2026: the former workflow, challenge and all-benchmark entry points now redirect to one main page. Benchmark detail pages retain their full figures, raw data and sources.

`package_manifest.json` records the current package checksums. The original selected-snapshot manifest is preserved at `reproducibility/inputs/selected50_snapshot_manifest.json`. Historical browser/source-archive checks describe that frozen snapshot. `navigation_validation.json` documents the combined-page checks. To rebuild the combined homepage from the unchanged registers and chart metadata, run `python reproducibility/unified_home.py` (requires lxml).
To download, select **Code > Download ZIP**, extract the complete folder, and open `index.html`. Reproduction instructions are in `README.txt` and `reproducibility/`. The scripts require no model calls.

Benchmark names and third-party source materials retain their respective rights. References and source links are provided in the supplement.

Published through GitHub Pages on 4 November 2026.
