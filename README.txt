SELECTED 50 BENCHMARKS FOR DATA EXTRACTION
Selection: 2 November 2026. Source-data cutoff: 31 October 2026.

Open index.html after extracting the complete folder. The main page combines
Challenges A-D with the extraction workflow. Scroll down through the four
challenges and right through each challenge's benchmark figures. Search or
select a workflow step to filter the figures. Expand the workflow map for all
12 chronological steps, their challenge links and evidence gaps. The former
workflow, challenge and all-benchmark URLs redirect to this one main page.
The 4 November 2026 navigation update changes no observations or figures.

CURRENT SCOPE
{
  "benchmark_families": 50,
  "benchmark_versions": 54,
  "source_observations": 4094,
  "added_model_card_observations": 683,
  "separate_conditions": 391,
  "visible_observations": 1716,
  "families_with_time_points": 40,
  "definition_held_observations": 29,
  "visible_mean_curves": 81,
  "challenge_family_counts": {
    "A": 24,
    "B": 25,
    "C": 17,
    "D": 20
  },
  "source_cutoff": "2026-10-31",
  "selection_date": "2026-11-02",
  "source_archive_families": 82,
  "axis_policy": "Retained condition-specific full supported release histories; native metrics; unchanged curves"
}

COUNTS AND INTERPRETATION
There are exactly 50 selected families. Versions are not extra independent
benchmarks, and challenge assignments overlap. The selection prioritizes task
fit, source traceability and distinct coverage, not high scores or improvement.
The source 82-family atlas is unchanged and remains the broader archive.
All 82 inclusion/exclusion decisions are in data/selection_decisions.csv.
Every selected family has a rationale and an A-D/workflow assignment.
No collection member is a dedicated test of codebook-based extraction for
psychological evidence synthesis. Component scores do not validate transfer,
human-versus-LLM rankings, or complete process auditability.

SOURCE PRESERVATION
Every included observation, condition, release-date assignment, SVG plot,
vector figure, mean-curve input and fitted grid value is retained unchanged.
The added mapping fields describe task relevance, not new empirical results.
Raw data open on a benchmark page when its figure is clicked; each value
retains benchmark APA, result APA and release-source evidence. Release sources
remain on one shared page. Historical model-card audit sections describe the
original source archive and are labelled separately from current totals.

REPRODUCTION
python reproducibility/reproduce.py /new/output/folder clones and validates
this frozen selected snapshot, without model calls. To re-derive the selection
from the original 82-family archive, run:
python reproducibility/curate.py /path/to/original-82-atlas /new/output/folder
The source archive manifest records all input checksums. The complete selection
script and validation are included. The frozen snapshot predates GitHub publication. The supplement is now public
at https://thorbenjansen.github.io/ai-data-extraction-benchmarks/ .
No journal submission was made by this publication workflow.
