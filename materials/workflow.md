# Workflow and literature supplement

Updated 4 November 2026. This resource accompanies the author's saved manuscript snapshot read on that date and the selected 50-benchmark atlas. It replaces the earlier reader guide and its draft-centered agent navigation.

## Why accuracy and auditability belong together

Data extraction turns source evidence into review data through linked decisions. The product must be accurate, while the process must allow its quality to be assessed and steered. The same two criteria apply to human experts, research assistants, LLMs and human–AI teams.

Our original study compared LLM outputs with existing human-extracted data. It measured their agreement and did not independently establish the quality of the human judgments. A disagreement can reflect a human error, an LLM error or different interpretations of a coding rule. It cannot, by itself, show that LLMs are worse than humans. The research question is where each actor performs better, which errors they share and how their abilities can be combined. [Jansen et al. (2025)](literature.html#R14), [Courvoisier et al. (2025)](literature.html#R06), [Jansen et al. (2026)](literature.html#R15).

Lu and Wang motivate decomposing extraction into challenges and examining context and tools. Macnamara motivates examining how assistance changes human judgment, independence and accuracy. Auditability connects these concerns: consequential decisions, sources, transformations and interventions become observable features of a workflow that can be compared empirically. [Lu and Wang (2026)](literature.html#R22), [Macnamara (2026)](literature.html#R23).

These modules are a research blueprint. They do not establish a universally validated sequence, a mandatory allocation to humans or AI, or a default ranking of their accuracy. Protocol reproducibility, interaction and adjudication extend beyond the component capabilities represented by Challenges A–D.

## Reading the evidence

Each module separates its purpose, a proposed research record, possible evaluation targets and an open question. The proposed records and comparisons are authored operationalizations, not validated scales or established cutoffs. Source references indicate their methodological basis; benchmark links indicate related tasks.

The atlas retains 50 benchmark families, 4,094 source observations and 391 separate conditions. Forty families supply 1,716 plotted observations. No included family is a dedicated test of codebook-based extraction from psychological studies. Challenge assignments overlap; raw scores and fitted curves remain condition-specific. The audit module offers partial diagnostics, not a benchmark of the complete audit trail.

## Workflow modules

### 01. Define variables and coding rules

**Purpose.** Define the variables, eligible evidence, extraction units, missingness conventions and decision rules before comparing extractors.

**Proposed record.** Version the codebook, instructions and prompts; retain training and pilot decisions, held-out evaluation rules and any subsequent amendments.

**Evaluation target.** Test whether independent humans, LLMs and supported raters apply the same operational definitions. Separate misunderstanding of a rule from failure to follow a sufficiently specified rule.

**Research question.** Which examples, training procedures and rule representations improve extraction without concealing unresolved construct ambiguity?

**Transfer limit.** Instruction compliance and schema completion do not establish that a psychological construct has been operationalized validly.

**Literature.** [Farotimi et al. (2026)](literature.html#R07); [Pustejovsky and Stubbs (2013)](literature.html#R30); [Thomas et al. (2025a)](literature.html#R35); [Villiger et al. (2022)](literature.html#R38).

**Benchmark coverage.** 9 families; mapped component or extraction task. [Explore the corresponding figures](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/index.html?step=protocol).

GSM-Symbolic, BFCL, ComplexBench, DTBench, UNIKIE-BENCH, SUC, Symbolic manipulation, VaxScope, CONSORT diagrams.

### 02. Prepare and read source documents

**Purpose.** Establish which article versions, appendices and other eligible materials enter the extraction, and preserve the information needed downstream.

**Proposed record.** Retain the document inventory, versions and identifiers; the parsing or OCR route; page and table locators; and checks of missing or degraded material.

**Evaluation target.** Distinguish document coverage and preservation of layout, digits and reading order from the correctness of later extraction judgments.

**Research question.** Where do source acquisition, OCR and representation choices produce omissions or distortions that humans or LLMs can detect or repair?

**Transfer limit.** Document-parsing scores do not establish that all materials for a review were obtained or that review variables were extracted correctly.

**Literature.** [Farotimi et al. (2026)](literature.html#R07); [Lu and Wang (2026)](literature.html#R22); [Ouyang et al. (2025)](literature.html#R28); [Villiger et al. (2022)](literature.html#R38).

**Benchmark coverage.** 11 families; mapped component or extraction task. [Explore the corresponding figures](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/index.html?step=documents).

OmniDocBench, READoc, olmOCR-bench, OCRBench, MDPBench, PureDocBench, Dr. DocBench, DocVQA, MMLongBench-Doc, UNIKIE-BENCH, CONSORT diagrams.

### 03. Locate relevant evidence

**Purpose.** Find the evidence relevant to a variable across text, tables, figures, appendices and dispersed passages.

**Proposed record.** Store the question or query, materials searched, candidate evidence and exact source locations, including relevant information that could not be located.

**Evaluation target.** Measure source-evidence recall and precision separately from answer accuracy, using a reference procedure whose coverage is itself documented.

**Research question.** Which retrieval strategies reduce missed evidence, and when do additional searches correct errors or introduce distracting candidates?

**Transfer limit.** Long-context and question-answering tasks assess related capabilities; their scores do not establish exhaustive search in psychological studies.

**Literature.** [Butcher et al. (2024)](literature.html#R04); [Farotimi et al. (2026)](literature.html#R07); [Lu and Wang (2026)](literature.html#R22).

**Benchmark coverage.** 25 families; mapped component or extraction task. [Explore the corresponding figures](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/index.html?step=retrieve).

MultiHiertt, DocMath-Eval, MMLongBench-Doc, LongBench, RULER, HELMET, NoLiMa, InfiniteBench, MRCR, DROP, FRAMES, MuSiQue, HotpotQA, QASPER, SciAssess, LAB-Bench, GAIA, ALCE, RoBBR, TrialReviewBench, Manalyzer, NIAH, LooGLE, MM-NIAH, VaxScope.

### 04. Bind values to the correct unit

**Purpose.** Associate a candidate value with the correct study, sample, group, outcome, time point and analytical unit.

**Proposed record.** Preserve row and column headers, units, footnotes, relevant sample identifiers and the relationship between each candidate value and its source context.

**Evaluation target.** Score correct value–unit assignments and complete records, rather than counting an isolated number as correct when it belongs to the wrong subgroup.

**Research question.** Which structured representations and checks help humans and LLMs distinguish overlapping samples, outcomes and repeated measurements?

**Transfer limit.** Table and diagram tasks provide component evidence; transfer to heterogeneous psychological study designs remains to be tested.

**Literature.** [Farotimi et al. (2026)](literature.html#R07); [Jones et al. (2005)](literature.html#R16); [Mathes et al. (2017)](literature.html#R25); [Villiger et al. (2022)](literature.html#R38).

**Benchmark coverage.** 30 families; mapped component or extraction task. [Explore the corresponding figures](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/index.html?step=bind).

OmniDocBench, READoc, olmOCR-bench, OCRBench, MDPBench, PureDocBench, Dr. DocBench, DocVQA, ChartQA, ChartQAPro, HiTab, MultiHiertt, TAT-QA, FinQA, DocMath-Eval, MMLongBench-Doc, LongBench, DROP, QASPER, SciAssess, LAB-Bench, TrialReviewBench, Manalyzer, DTBench, UNIKIE-BENCH, TableBench, SUC, MM-NIAH, VaxScope, CONSORT diagrams.

### 05. Interpret evidence and apply coding rules

**Purpose.** Translate evidence into the category or value specified by the codebook, retaining defensible alternatives when the source is ambiguous.

**Proposed record.** Link the interpretation to the applicable rule and supporting evidence; record missingness decisions, competing interpretations and confidence or uncertainty separately.

**Evaluation target.** Use source-based reference judgments and describe how ambiguity was adjudicated. Report agreement without treating agreement alone as proof of correctness.

**Research question.** When do human expertise, LLM interpretation and joint review improve semantic coding, and where do they share the same errors?

**Transfer limit.** Generic annotation and biomedical appraisal studies do not validate the meaning of a psychological review's codebook.

**Literature.** [Courvoisier et al. (2025)](literature.html#R06); [Horton et al. (2010)](literature.html#R13); [Mathes et al. (2017)](literature.html#R25); [Pustejovsky and Stubbs (2013)](literature.html#R30); [Villiger et al. (2022)](literature.html#R38).

**Benchmark coverage.** 10 families; mapped component or extraction task. [Explore the corresponding figures](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/index.html?step=code).

GSM-Symbolic, BFCL, ComplexBench, RoBBR, DTBench, UNIKIE-BENCH, SUC, Symbolic manipulation, VaxScope, CONSORT diagrams.

### 06. Coordinate retrieval, tools and intermediate steps

**Purpose.** Coordinate retrieval, tool use and dependent operations so intermediate decisions can be inspected and reconsidered.

**Proposed record.** Identify the model snapshot, harness, tools, prompt and instruction versions, available context, budgets and consequential intermediate inputs and outputs.

**Evaluation target.** Compare model and harness contributions under matched or explicitly different conditions. Preserve failed and corrected steps as well as the accepted result.

**Research question.** Which tool and context arrangements improve extraction, and which apparent gains arise from changes in models, inputs, budgets or supervision?

**Transfer limit.** An agent's success on a research or tool-use task does not establish success on the target extraction workflow.

**Literature.** [Farotimi et al. (2026)](literature.html#R07); [Lu and Wang (2026)](literature.html#R22); [Raj et al. (2026)](literature.html#R31).

**Benchmark coverage.** 20 families; mapped component or extraction task. [Explore the corresponding figures](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/index.html?step=coordinate).

FinQA, LongBench, RULER, HELMET, NoLiMa, InfiniteBench, FRAMES, MuSiQue, HotpotQA, SciAssess, LAB-Bench, CORE-Bench, GAIA, BFCL, ComplexBench, TrialReviewBench, Manalyzer, TableBench, ProcessBench, LooGLE.

### 07. Transform and calculate values

**Purpose.** Transform reported inputs into the requested value using explicit formulas, units and executable operations where appropriate.

**Proposed record.** Store input values and locators, the formula and its assumptions, code or tool calls, rounding rules and intermediate and final outputs.

**Evaluation target.** Separate retrieval and formula-selection errors from arithmetic or execution errors. Independently check important transformations against the source inputs.

**Research question.** Which transformations benefit from deterministic tools, and where do humans or LLMs select an inappropriate formula or set of inputs?

**Transfer limit.** Arithmetic benchmark performance does not validate effect-size formula selection, eligibility decisions or study-specific assumptions.

**Literature.** [Farotimi et al. (2026)](literature.html#R07); [Lu and Wang (2026)](literature.html#R22); [Mathes et al. (2017)](literature.html#R25); [Villiger et al. (2022)](literature.html#R38).

**Benchmark coverage.** 17 families; mapped component or extraction task. [Explore the corresponding figures](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/index.html?step=derive).

ChartQA, ChartQAPro, HiTab, MultiHiertt, TAT-QA, FinQA, DocMath-Eval, InfiniteBench, GSM-Symbolic, DROP, Manalyzer, DTBench, TableBench, NUPA, Symbolic manipulation, ProcessBench, LooGLE.

### 08. Verify source support and detect errors

**Purpose.** Check whether a candidate value and its interpretation are supported by the recorded source and extraction rule.

**Proposed record.** Document what was checked, the verifier and information available to that verifier, detected omissions or unsupported additions, and corrections or newly introduced errors.

**Evaluation target.** Assess error detection and correction separately, including false reassurance and harmful corrections. Apply comparable reference definitions to human and LLM outputs.

**Research question.** When do independent verification, targeted checks or combinations of human and AI verification improve the final extraction?

**Transfer limit.** A complete verification log does not establish that the verifier's judgment is correct or that the reference labels are error-free.

**Literature.** [Buscemi et al. (2006)](literature.html#R03); [Courvoisier et al. (2025)](literature.html#R06); [Farotimi et al. (2026)](literature.html#R07); [Gartlehner et al. (2025)](literature.html#R09); [Villiger et al. (2022)](literature.html#R38).

**Benchmark coverage.** 11 families; mapped component or extraction task. [Explore the corresponding figures](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/index.html?step=verify).

HELMET, FRAMES, HotpotQA, QASPER, LAB-Bench, CORE-Bench, ALCE, RoBBR, DTBench, ProcessBench, LooGLE.

### 09. Combine human and LLM contributions

**Purpose.** Specify how human experts, research assistants and LLMs contribute, and when each sees another actor's output.

**Proposed record.** Retain initial judgments when the design includes independent extraction; otherwise document the timing of AI exposure, revisions, coder expertise and training, time and workload.

**Evaluation target.** Compare human-only, LLM-only and human–AI conditions without assuming an accuracy ordering. Measure corrected, retained and introduced errors as well as efficiency and independence.

**Research question.** Which allocation and exposure designs combine complementary abilities, and when do deference, fatigue or incomplete search impair each type of workflow?

**Transfer limit.** Human–AI studies in adjacent tasks inform the design of comparisons but do not establish their effects in psychological data extraction.

**Literature.** [Beck et al. (2025)](literature.html#R01); [Gartlehner et al. (2025)](literature.html#R09); [Jansen et al. (2026)](literature.html#R15); [Macnamara (2026)](literature.html#R23); [Wang et al. (2025)](literature.html#R40); [Xavier et al. (2026)](literature.html#R41); [Zhang et al. (2020)](literature.html#R45).

**Benchmark coverage.** 0 families; mapped component or extraction task. [Explore the corresponding figures](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/index.html?step=collaborate).

### 10. Resolve disagreements without yielding to pressure

**Purpose.** Resolve discrepancies through source evidence and coding rules, while retaining uncertainty when the available information does not support one defensible answer.

**Proposed record.** Preserve competing values, actor identities or roles, evidence and rules considered, the reason for acceptance or escalation, and unresolved cases.

**Evaluation target.** Distinguish agreement, consensus and correctness. Record how the reference was constructed and whether adjudicators were independent of the compared extraction conditions.

**Research question.** Which adjudication arrangements identify human and LLM errors rather than merely privileging one actor's initial judgment?

**Transfer limit.** Consensus is not an automatically error-free gold standard, and generic resistance-to-pressure tests do not validate extraction adjudication.

**Literature.** [Buscemi et al. (2006)](literature.html#R03); [Courvoisier et al. (2025)](literature.html#R06); [Jansen et al. (2026)](literature.html#R15); [Macnamara (2026)](literature.html#R23); [Villiger et al. (2022)](literature.html#R38).

**Benchmark coverage.** 0 families; mapped component or extraction task. [Explore the corresponding figures](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/index.html?step=adjudicate).

### 11. Assess the complete extraction product

**Purpose.** Evaluate the resulting review data at the field, relationship and whole-record levels, with omissions and unsupported additions made explicit.

**Proposed record.** Define the eligible denominator, missing-value treatment, reference construction and ambiguity rules, and report accuracy alongside time, cost and actor expertise.

**Evaluation target.** Use the same scoring rules and reference definitions across compared conditions; report important subgroups and error types rather than relying solely on a pooled agreement index.

**Research question.** Which workflow components improve final data quality, for which variables and source conditions, and at what cost?

**Transfer limit.** The 50 benchmark families do not provide a single common metric or a matched human–LLM comparison for psychology-specific extraction.

**Literature.** [Courvoisier et al. (2025)](literature.html#R06); [Farotimi et al. (2026)](literature.html#R07); [Gartlehner et al. (2025)](literature.html#R09); [Jansen et al. (2025)](literature.html#R14); [Mathes et al. (2017)](literature.html#R25).

**Benchmark coverage.** 6 families; mapped component or extraction task. [Explore the corresponding figures](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/index.html?step=product).

TrialReviewBench, Manalyzer, DTBench, UNIKIE-BENCH, VaxScope, CONSORT diagrams.

### 12. Retain an auditable extraction record

**Purpose.** Enable another researcher to reconstruct consequential decisions and assess where the process could be checked, corrected or redirected.

**Proposed record.** Link final values to source locations, actors, transformations and accepted or rejected alternatives; preserve versioned instructions, exposure timing, adjudication and uncertainty records.

**Evaluation target.** Examine whether sources and decision paths can actually be reconstructed, whether uncertainties remain visible and whether correction or escalation was possible. Evaluate final accuracy separately.

**Research question.** What records and interfaces enable useful assessment and steering of the process, and which omissions prevent an independent audit?

**Transfer limit.** No benchmark in the selected collection validates complete workflow auditability. Citation and structured-extraction tasks supply partial diagnostics only.

**Literature.** [Farotimi et al. (2026)](literature.html#R07); [Flemyng et al. (2025)](literature.html#R08); [Thomas et al. (2025a)](literature.html#R35); [Thomas et al. (2025b)](literature.html#R36); [Thomas et al. (2025c)](literature.html#R37); [Villiger et al. (2022)](literature.html#R38).

**Benchmark coverage.** 3 families; partial diagnostic only. [Explore the corresponding figures](https://thorbenjansen.github.io/ai-data-extraction-benchmarks/index.html?step=audit).

ALCE, DTBench, CONSORT diagrams.

## Comparing workflows on common terms

Define the eligible documents, variables and extraction units; coder expertise and training; model snapshots, prompts, context and tools; and the information available at each decision. Record which differences are intentional parts of the workflow comparison. Separate held-out evaluation from adaptation of the instructions or codebook. Document the reference procedure, adjudicator independence, denominators and treatment of missing and ambiguous cases.

Assess field and whole-record correctness, unsupported additions and omissions alongside time and cost. Measure agreement separately. For human–AI conditions, report errors corrected, retained and introduced after assistance, while preserving exposure timing and initial judgments when the design calls for independent extraction. Compare possible biases with relevant human-only conditions rather than assuming they originate only from AI. [Farotimi et al. (2026)](literature.html#R07), [Gartlehner et al. (2025)](literature.html#R09), [Macnamara (2026)](literature.html#R23), [Zhang et al. (2020)](literature.html#R45).

## Making auditability testable

An audit should determine whether a reader can reconstruct the evidence and the consequential decision path, identify unresolved uncertainty, and see where correction or escalation was possible. The presence of a log is insufficient if source locators do not resolve or the reason for accepting a value cannot be reconstructed. Conversely, a well-documented error remains an inaccurate product. These are separate process and product outcomes. [Farotimi et al. (2026)](literature.html#R07), [Flemyng et al. (2025)](literature.html#R08), [Villiger et al. (2022)](literature.html#R38).

The companion event schema is an illustrative template for research. It records the actor and condition, codebook and instruction versions, source locator, candidate value, transformation, exposure timing, verification, final disposition and remaining uncertainty. It specifies information to preserve; it does not validate an extraction decision or prescribe one verification policy for all reviews.

## Sources and version

The current manuscript remains unchanged. Reference strings are preserved from its bibliography. The step-to-literature assignments and operational research questions were authored for this supplement. The earlier OSF corpus remains the source of the retained literature ARAs; their quality labels and source-grounding limitations remain visible. The earlier draft's framing and routes are superseded by the current starting documents.

[Open the reference collection](literature.html). [Open the AI research package guide](ai.html). [Return to the benchmark atlas](../index.html).
