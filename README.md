# Benchmarks for AI-supported data extraction

[Open the interactive supplement](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/)

This repository publishes the selected 50-benchmark supplementary atlas for AI-supported data extraction. The frozen scientific snapshot was selected on 2 November 2026, with a source-data cutoff of 31 October 2026.

- [Workflow view](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/): scroll down through the 12 extraction steps and across their benchmarks.
- [All 50 benchmark families](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/all-benchmarks.html)
- [Challenges A-D and workflow mappings](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/challenges.html)
- [Model-release dates and primary sources](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/model-releases.html)
- [Methods](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/methods.html)
- [Complete PDF atlas](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/All_Benchmarks_Article_Atlas.pdf)

The snapshot contains 4,094 source observations across 391 separately identified test conditions. Forty families supply 1,716 plotted time-series observations; families without supported dated observations remain documented without invented time-series points. Each benchmark has APA references, source-bound scores, and a mapping to workflow steps and commentary challenges. Click a figure to inspect its data.

## Interpretation

These benchmarks measure component skills. None is a dedicated test of codebook-based extraction from psychological studies. Their scores do not establish transfer to that task, a human-versus-LLM ranking, or complete workflow auditability. Distinct test conditions retain separate series and curves.

## Snapshot and reproduction

All 1,101 files listed in `package_manifest.json` are preserved byte for byte from the selected supplement. The manifest itself is included. GitHub publication adds this README, `.gitignore`, and `.nojekyll`; generated Python cache files are omitted. The original local snapshot remains unchanged. `README.txt` and historical validation files describe the frozen snapshot before its GitHub publication.

To download, select **Code > Download ZIP**, extract the complete folder, and open `index.html`. Reproduction instructions are in `README.txt` and `reproducibility/`. The scripts require no model calls.

Benchmark names and third-party source materials retain their respective rights. References and source links are provided in the supplement.

Published through GitHub Pages on 4 November 2026.
