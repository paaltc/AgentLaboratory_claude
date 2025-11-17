# Full Research Workflow

Execute the complete Agent Laboratory research pipeline from literature review through report refinement.

## Syntax
```bash
/perform-research <topic> [--model=MODEL] [--steps=N] [--papers=N] [--no-compile-pdf]
```

## Arguments
- `topic`: Research topic/question to investigate (required)
- `--model`: LLM model backbone (default: o3-mini)
- `--steps`: Max steps per phase (default: 100)
- `--papers`: Number of papers for literature review (default: 5)
- `--no-compile-pdf`: Skip PDF compilation

## Example
```bash
/perform-research "improving transformer efficiency" --model=gpt-4o --steps=50 --papers=10
```

## What It Does
Runs all 7 research phases:
1. Literature Review - Collects papers from arXiv
2. Plan Formulation - Designs experimental approach
3. Data Preparation - Creates dataset loading code
4. Running Experiments - Executes ML optimizations
5. Results Interpretation - Analyzes findings
6. Report Writing - Generates LaTeX paper
7. Report Refinement - Gets reviews and improves

## Python API
```python
from ai_lab_repo import LaboratoryWorkflow

lab = LaboratoryWorkflow(
    research_topic="topic here",
    openai_api_key="your-key",
    agent_model_backbone="gpt-4o",
    max_steps=50,
    num_papers_lit_review=10,
    compile_pdf=True
)
lab.perform_research()
```
