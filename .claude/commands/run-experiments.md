# Running Experiments Phase

Execute ML experiments with optimization and performance tracking.

## Syntax
```bash
/run-experiments <topic> [--plan=FILE] [--data=FILE] [--steps=N] [--model=MODEL]
```

## Arguments
- `topic`: Research topic (required)
- `--plan`: Path to research plan file
- `--data`: Path to data preparation code
- `--steps`: Optimization steps (default: 3)
- `--model`: LLM model to use (default: o3-mini)

## Example
```bash
/run-experiments "efficient attention" --steps=5 --model=gpt-4o
```

## What It Does
- ML Engineer Agent generates experiment code
- Executes code safely with timeout protection
- Captures results and metrics
- Iterative optimization using MLESolver
- Performance tracking and logging

## Output
Saves to `{lab_dir}/experiments/` with:
- `experiment_code.py` - Full experiment implementation
- `results.json` - Metrics and scores
- `logs/` - Execution logs
- `models/` - Trained model checkpoints

## Python API
```python
from ai_lab_repo import LaboratoryWorkflow

lab = LaboratoryWorkflow(
    research_topic="topic here",
    openai_api_key="your-key",
    mlesolver_max_steps=5
)
success = lab.running_experiments()
# Returns: False if completed, True if needs retry
```
