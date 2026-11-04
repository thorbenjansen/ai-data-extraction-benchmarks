# Start here: current AI-supported data extraction research package

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
