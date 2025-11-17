# Plan Formulation Phase

Design the experimental approach and methodology for the research.

## Syntax
```bash
/plan-phase <topic> [--lit-review=FILE] [--model=MODEL]
```

## Arguments
- `topic`: Research topic (required)
- `--lit-review`: Path to literature review file
- `--model`: LLM model to use (default: o3-mini)

## Example
```bash
/plan-phase "efficient attention mechanisms" --model=gpt-4o
```

## What It Does
- PhD Student Agent formulates research plan
- Postdoc provides guidance and feedback
- Collaborative dialogue refines plan
- Defines:
  - Specific hypotheses
  - Experimental setup
  - Baseline comparisons
  - Evaluation metrics
  - Success criteria

## Output
Saves to `{lab_dir}/research_plan.txt` with:
- Detailed experimental design
- Dataset requirements
- Model architectures
- Training procedures
- Evaluation methodology

## Python API
```python
from ai_lab_repo import LaboratoryWorkflow

lab = LaboratoryWorkflow(
    research_topic="topic here",
    openai_api_key="your-key"
)
success = lab.plan_formulation()
# Returns: False if completed, True if needs retry
```
