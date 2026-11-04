# Benchmarks for AI-supported data extraction

[Open the interactive supplement](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/)

This repository publishes a focused eight-benchmark progress selection for AI-supported data extraction, together with the complete 50-family source archive. The source archive was selected on 2 November 2026, with a source-data cutoff of 31 October 2026. The progress display was curated on 4 November 2026.

- [Combined Challenges A-D and workflow homepage](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/): scroll down through the four challenges and across their benchmark figures; filter by extraction step.
- The same page includes the chronological map of all 12 workflow steps and their evidence gaps.
- [Model-release dates and primary sources](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/model-releases.html)
- [Methods](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/methods.html)
- [Original 50-family PDF atlas (source archive)](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/All_Benchmarks_Article_Atlas.pdf)

## Current article companions (4 November 2026)

- [All article materials](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/index.html#article-materials)
- [Workflow and literature guide](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/materials/workflow.html): 12 candidate research components and 45 manuscript bibliography records.
- [AI research package](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/materials/ai.html): current argument and agent entry points, 203 retained source ARAs, 8 current benchmark cards, 42 archived cards, and unchanged complete source data.

The current reader and agent resources replace the earlier draft-centered navigation. They are aligned to the saved manuscript snapshot identified in `materials/version.json`; the source manuscript is not published or modified. The original study's agreement comparison is kept distinct from independently assessed accuracy, and no general human-versus-LLM accuracy ordering is assumed. Candidate workflow components and research record templates are not presented as a validated universal workflow.

To rebuild these resources, use Python with lxml and Pandoc, download the original public OSF AI archive listed in `reproducibility/materials_sources/context.json`, and run `python reproducibility/build_article_materials.py --source-ai-zip /path/to/archive.zip`, followed by `python reproducibility/unified_home.py` and `python reproducibility/validate_article_materials.py`. The original archive's checksum is checked before use. The complete source ARA corpus remains inside the downloadable current AI package.

The snapshot contains 4,094 source observations across 391 separately identified test conditions. Forty families supply 1,716 plotted time-series observations; families without supported dated observations remain documented without invented time-series points. Each benchmark has APA references, source-bound scores, and a mapping to workflow steps and commentary challenges. Click a figure to inspect its data.

## Interpretation

These benchmarks measure component skills. None is a dedicated test of codebook-based extraction from psychological studies. Their scores do not establish transfer to that task, a human-versus-LLM ranking, or complete workflow auditability. Distinct test conditions retain separate series and curves.

## Snapshot and reproduction

The original scientific snapshot is unchanged: existing source data files, 882 figure assets, the PDF atlas, source references, release dates, challenge assignments and curve inputs retain their original checksums. Navigation was consolidated on 4 November 2026: the former workflow, challenge and all-benchmark entry points now redirect to one main page. Benchmark detail pages retain their full figures, raw data and sources.

`package_manifest.json` records the current package checksums. The original selected-snapshot manifest is preserved at `reproducibility/inputs/selected50_snapshot_manifest.json`. Historical browser/source-archive checks describe that frozen snapshot. `navigation_validation.json` documents the combined-page checks. To rebuild the combined homepage from the unchanged registers and chart metadata, run `python reproducibility/unified_home.py` (requires lxml).
To download, select **Code > Download ZIP**, extract the complete folder, and open `index.html`. Reproduction instructions are in `README.txt` and `reproducibility/`. The scripts require no model calls.

Benchmark names and third-party source materials retain their respective rights. References and source links are provided in the supplement.

Published through GitHub Pages on 4 November 2026.

## Focused progress selection (4 November 2026)

The main page shows OmniDocBench, olmOCR-bench, PureDocBench, LongBench, RULER, GSM-Symbolic, TableBench and ProcessBench: 650 dated observations in 27 separate conditions. Each family has at least one qualifying positive series and no contrary adequately sampled series. Conditions need ten model configurations, six release positions and 180 days; positive trends must also pass the stated robust slope, date-median association, early–late contrast and three-bandwidth checks. All adequately sampled conditions in retained families remain visible.

This outcome-selected illustration cannot estimate how often benchmarks improve, average general progress, causal effects, human comparisons or transfer to psychology. The full 50-family source register, raw observations, existing figures and curves remain unchanged. `archive.html` retains access to all original benchmark pages and the original PDF. `data/progress_family_decisions.csv` and `data/progress_condition_decisions.csv` document every decision.

Rebuild the selection with `python reproducibility/select_progress.py`, then rebuild article materials and run `python reproducibility/unified_home.py`. Validate with `python reproducibility/validate_progress.py`, `python reproducibility/validate_selection.py` and `python reproducibility/validate_article_materials.py`. No new model evaluation is performed.

Within each challenge, figures are ordered by the displayed mean-curve gain in their unchanged default condition. The order is illustrative; tasks and observed time spans differ. Exact condition identifiers and ordering values are recorded in `data/progress_display_order.json`.
