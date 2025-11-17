# Configure Workflow

Set up workflow parameters and agent configurations.

## Syntax
```bash
/configure-workflow [--max-steps=N] [--compile-pdf=BOOL] [--verbose=BOOL]
```

## Arguments
- `--max-steps`: Max steps per phase (default: 100)
- `--compile-pdf`: Enable PDF compilation (default: true)
- `--verbose`: Verbose output (default: true)
- `--papers`: Papers for lit review (default: 5)
- `--mle-steps`: ML optimization steps (default: 3)
- `--paper-steps`: Paper optimization steps (default: 5)
- `--human-in-loop`: Enable human feedback (default: false)

## Example
```bash
/configure-workflow --max-steps=50 --compile-pdf=true --verbose=true
```

## Configuration File
Create `experiment_configs/custom.yaml`:
```yaml
research_topic: "Your research topic"
task_notes_LLM:
  plan-formulation:
    - "Focus on efficiency improvements"
    - "Use gpt-4o model"
max_steps: 100
compile_latex: true
papers_lit_review: 10
mlesolver_max_steps: 5
papersolver_max_steps: 7
language: "English"
```

## Python API
```python
from ai_lab_repo import LaboratoryWorkflow

lab = LaboratoryWorkflow(
    research_topic="Your topic",
    openai_api_key="your-key",
    max_steps=50,
    num_papers_lit_review=10,
    compile_pdf=True,
    mlesolver_max_steps=5,
    papersolver_max_steps=7
)
```

## Notes System
Add task-specific notes for agents:
```yaml
task_notes_LLM:
  plan-formulation:
    - "Use this prompt technique"
    - "Available GPUs: 2x A100"
  data-preparation:
    - "Use datasets from HuggingFace"
```
