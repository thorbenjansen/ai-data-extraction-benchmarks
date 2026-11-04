"""Authored construct mapping; it is not an empirical validation result."""
STEPS=[
 dict(id='protocol',name='Define variables and coding rules',codes=['E'],question='Can the system apply an explicit extraction schema and its constraints?',task='Specify variables, eligible evidence, missing-value rules and decision criteria before extraction.',gap='Formal instruction compliance does not validate the construct meaning of a codebook, pilot adequacy or preregistration.',anchor='Preparation and reporting, manuscript paragraph 33'),
 dict(id='documents',name='Prepare and read source documents',codes=['A'],question='Are text, digits, formulae, tables and reading order preserved?',task='Read the available article, tables, figures and supplements without losing source information.',gap='Parsing a page is not a demonstration that an entire article and all supplements were acquired or processed correctly.',anchor='Lu and Wang, Challenges A–B; manuscript paragraphs 15–18'),
 dict(id='retrieve',name='Locate relevant evidence',codes=['B'],question='Can the relevant information be found in long or dispersed source material?',task='Retrieve candidate passages and retain information needed for a specific extraction question.',gap='A retrieval score does not establish that all eligible evidence was inspected or that omissions were eliminated.',anchor='Source-based step comparisons, manuscript paragraph 31'),
 dict(id='bind',name='Bind values to the correct unit',codes=['R','A2'],question='Does a value refer to the intended study, sample, group, outcome and time point?',task='Select the correct row, header, group, sample and analytical unit rather than matching an isolated number.',gap='Table/diagram binding transfers only partly to heterogeneous psychological studies with overlapping samples and outcomes.',anchor='Wrong-subgroup example, manuscript paragraph 29'),
 dict(id='code',name='Interpret evidence and apply coding rules',codes=['E','Q'],question='Can source evidence be translated into the category required by the codebook?',task='Apply semantic coding and methodological criteria, distinguishing ambiguous and unsupported interpretations.',gap='Generic instruction following and biomedical risk-of-bias coding do not establish validity for a psychological review codebook.',anchor='Lu and Wang, Challenge E; manuscript paragraphs 20 and 31'),
 dict(id='derive',name='Transform and calculate values',codes=['C'],question='Are numerical inputs, units and deterministic transformations correct?',task='Derive a requested value from reported inputs, preserving the calculation and its inputs.',gap='Arithmetic and program execution are not direct validation of effect-size formula selection or study-specific eligibility rules.',anchor='Lu and Wang, Challenge C; manuscript paragraphs 15, 17–18 and 33'),
 dict(id='coordinate',name='Coordinate retrieval, tools and intermediate steps',codes=['D'],question='Can a system select tools and carry a task through several dependent operations?',task='Combine evidence, choose executable operations and check intermediate outputs.',gap='Research-agent and machine-learning tasks are particularly indirect proxies for data extraction; tools and budgets can differ.',anchor='Lu and Wang, Challenge D; manuscript paragraphs 9, 15–18 and 31'),
 dict(id='verify',name='Verify source support and detect errors',codes=['F'],question='Is the accepted value or statement supported by the specified source?',task='Check support, contradictions, missing evidence and intermediate errors against source material.',gap='Detection and citation metrics differ from generation accuracy and do not independently validate the benchmark reference labels.',anchor='Product accuracy and auditability, manuscript paragraphs 28–29'),
 dict(id='adjudicate',name='Resolve disagreements without yielding to pressure',codes=['S'],question='Does a system accept valid corrections while resisting unsupported pressure?',task='Reconsider competing values using the source and coding rule, retaining the reason for the final decision.',gap='Sycophancy tasks test model responses. They do not validate source-based adjudication of human–LLM extraction disagreements.',anchor='Discrepancies and adjudication records, manuscript paragraphs 29, 31 and 33'),
 dict(id='collaborate',name='Combine human and LLM contributions',codes=['H'],question='How do human, model and joint performance change with the interaction?',task='Record initial judgments, timing of AI exposure, corrections, introduced errors, time and coder expertise.',gap='The two interaction benchmarks concern coding or puzzles. No matched comparison of psychological extraction by experts, research assistants and LLMs is established by this register.',anchor='Human–AI comparisons, manuscript paragraphs 23 and 31–33'),
 dict(id='audit',name='Retain an auditable extraction record',codes=[],question='Can an independent reader reconstruct evidence, decisions and transformations?',task='Preserve source locators, rejected alternatives, transformations, exposure timing, adjudication and uncertainty records.',gap='No benchmark in this collection validates complete process auditability for the proposed extraction workflow. Citation and structured-output tests assess only components.',anchor='Auditability definition and reporting, manuscript paragraphs 11, 28–29 and 33'),
 dict(id='product',name='Assess the complete extraction product',codes=[],question='Are fields and their relationships correct, and is the entire record complete?',task='Evaluate field, tuple and whole-record correctness, omissions and unsupported additions alongside time.',gap='Direct extraction tasks cover particular documents or domains; none establishes a universal human–AI workflow for psychological evidence synthesis.',anchor='Comparative evaluation agenda, manuscript paragraph 31'),
]
DIRECT_PRODUCT={'TRIAL','MANALYZER','DTBENCH','VAX','CONSORT','UNIKIE'}
DIRECT_BIND={'CONSORT','DTBENCH'}
def mappings(c):
 result=[];codes=set(c['constructs'].split(';'));bid=c['benchmark_id']
 for s in STEPS:
  if s['id']=='audit':continue
  if s['id']=='product':
   if bid not in DIRECT_PRODUCT:continue
   level='Direct extraction task';why='The benchmark evaluates extraction outputs in its stated document/domain setting; '+c['transfer_limit']
  elif not codes.intersection(s['codes']):continue
  elif s['id']=='collaborate':level='Direct interaction task';why='Human–AI interaction is manipulated or observed in the source task; '+c['transfer_limit']
  elif s['id']=='bind' and bid in DIRECT_BIND:level='Direct extraction task';why='Structured output requires preserving field/group relationships in the source task; '+c['transfer_limit']
  elif c['evidence_scope']=='distant proxy' or s['id']=='adjudicate':level='Indirect proxy';why='The measured task is related to the requirement but does not directly test it in an extraction workflow; '+c['transfer_limit']
  else:level='Component task';why=c['task']+'. '+c['transfer_limit']
  result.append(dict(step=s['id'],level=level,rationale=why,benchmark_id=bid))
 return result

# Existing claim table: row numbers refer to the authored English workbook's Claims sheet.
# Historical descriptions and normative requirements are not turned into new performance evidence.
CLAIMS={
 2:('retrieve coordinate collaborate','Component evidence; integrated context-engineering workflow remains unvalidated.'),
 3:('documents','Component evidence for preservation of source information.'),
 4:('retrieve','Component evidence; not proof that retrieval improves every extraction workflow.'),
 5:('documents product','Parsing and extraction are measurable separately; their causal error propagation requires a linked study.'),
 6:('derive coordinate','Component evidence for numerical programs and tool calls; effect-size rule selection remains task-specific.'),
 7:('coordinate retrieve','Component and indirect agent evidence; no claim that chain-of-thought alone solves extraction.'),
 8:('collaborate code adjudicate','Several requirements, with substantial gaps for human attention, complacency and methodology.'),
 9:('collaborate','Human interaction is only indirectly covered; source-based extraction reliance needs a direct experiment.'),
 10:('retrieve collaborate','Retrieval tests and interaction tests do not measure the proposed illusion of exhaustive coverage.'),
 11:('adjudicate','Sycophancy tests are relevant to model response changes; iterative prompt-optimization bias in extraction is not directly tested.'),
 12:('adjudicate','Valid-versus-invalid criticism is tested in component tasks; AI-judge independence under extraction disagreement remains open.'),
 13:('','Normative priority; benchmark scores cannot establish the appropriate ethical balance between rigor and efficiency.'),
 14:('retrieve','Long-context component tasks directly operationalize uneven retrieval/retention, with task-specific conditions.'),
 15:('','Status of the commentary examples; later component benchmarks do not retroactively validate those examples.'),
 16:('','Legal and ethical requirements; no empirical capability benchmark can establish permission or compliance.'),
 17:('code retrieve verify','RoBBR separates methodological evidence and judgments in biomedical reports; transfer to other domains is limited.'),
 18:('collaborate','No benchmark here isolates occasional-coder experience or accumulated review-specific expertise.'),
 19:('','Historical characterization of the original study; it must be checked against that study, not a new general-purpose benchmark.'),
 20:('derive product','Related numerical tasks motivate tests; the original agreement design cannot identify whether a human or LLM was wrong.'),
 21:('bind derive','Component tasks distinguish numerical reasoning and binding, but do not independently explain the original variable-level discrepancies.'),
 22:('protocol code','Instruction/schema tasks assess explicit constraints; reconstruction of missing codebooks and construct validity remain unresolved.'),
 23:('','The original study measured agreement, not independently established human/model accuracy or a manipulated speed–accuracy trade-off.'),
 24:('collaborate','Existing interaction tasks are indirect for assistant/second-coder/judge roles in evidence extraction.'),
 25:('verify collaborate audit','Error-detection tasks cover components; meaningful human control over the target workflow is not established.'),
 26:('','A historical ensemble finding needs replication under a matched reference and model-set design; this register does not supply it.'),
 27:('','Component evidence does not validate the original workflow recommendations as an integrated intervention.'),
 28:('adjudicate collaborate','Disagreement-only human review has not been validated by these component tasks; shared errors also require auditing.'),
 29:('','A second human provides another judgment, not an infallible ceiling. No general human–LLM ranking follows from agreement.'),
 30:('code','RoBBR is a directly relevant study-quality task, distinct from the variables in the original agreement study.'),
}
