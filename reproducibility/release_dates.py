"""Reviewed primary-source releases; matching never uses free substrings."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parent.parent
REGISTRY=json.loads((ROOT/'data/model_release_registry.json').read_text()) if (ROOT/'data/model_release_registry.json').exists() else []
def candidates(model):
 model=re.sub(r'\((?:max|xhigh|high|medium|low|FC|Prompt|FC Thinking|Prompt Thinking)\)','',model,flags=re.I)
 model=re.sub(r'\s*\[[\d.,/]+B\]','',model,flags=re.I)
 result=[model]+model.split(' / ')
 result+=re.findall(r'(?:text|code)-davinci-00[23]',model,flags=re.I)
 for prefix in ['meta-llama/','microsoft/','Qwen/','CohereForAI/','CohereLabs/','deepseek-ai/','01-ai/']:
  if model.lower().startswith(prefix.lower()):result.append(model[len(prefix):])
 return {re.sub('[^a-z0-9]','',s.lower().replace('+','plus')) for s in result}
def lookup(row):
 ids=candidates(row['model']);found=[]
 for rule in REGISTRY:
  if rule.get('families') and row['family'] not in rule['families']:continue
  if rule.get('observation_ids') and row['observation_id'] not in rule['observation_ids']:continue
  if rule.get('original_dates') and row['date'] not in rule['original_dates']:continue
  if any(re.fullmatch(p,c) for p in rule['patterns'] for c in ids):found.append(rule)
 # Explicit score-cohort or source-identified observations override a generic
 # named-model rule, e.g. August Command R+ must not inherit April's launch.
 if found:
  specificity=lambda x:3*bool(x.get('observation_ids'))+2*bool(x.get('families'))+bool(x.get('original_dates'))
  best=max(map(specificity,found));found=[x for x in found if specificity(x)==best]
 if len({x['release_date'] for x in found})==1 and found:return found[0]
 return None
