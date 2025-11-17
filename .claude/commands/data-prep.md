# Data Preparation Phase

Create and validate dataset loading code and data processing pipeline.

## Syntax
```bash
/data-prep <topic> [--plan=FILE] [--model=MODEL]
```

## Arguments
- `topic`: Research topic (required)
- `--plan`: Path to research plan file
- `--model`: LLM model to use (default: o3-mini)

## Example
```bash
/data-prep "efficient attention" --model=gpt-4o
```

## What It Does
- ML Engineer Agent generates dataset code
- SW Engineer validates code quality
- Collaborative refinement of data pipeline
- Handles:
  - Dataset downloading/loading
  - Preprocessing steps
  - Train/test splits
  - Data validation
  - Error handling

## Output
Saves to `{lab_dir}/data_preparation.py` with:
- Fully functional data loading code
- Preprocessing functions
- Validation checks
- Usage examples
- Comments and documentation

## Python API
```python
from ai_lab_repo import LaboratoryWorkflow

lab = LaboratoryWorkflow(
    research_topic="topic here",
    openai_api_key="your-key"
)
success = lab.data_preparation()
# Returns: False if completed, True if needs retry
```
