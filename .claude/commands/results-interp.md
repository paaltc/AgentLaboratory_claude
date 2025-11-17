# Results Interpretation Phase

Analyze experimental results and extract insights.

## Syntax
```bash
/results-interp <topic> [--results=FILE] [--model=MODEL]
```

## Arguments
- `topic`: Research topic (required)
- `--results`: Path to experiment results file
- `--model`: LLM model to use (default: o3-mini)

## Example
```bash
/results-interp "efficient attention" --model=gpt-4o
```

## What It Does
- Postdoc Agent analyzes experimental results
- Extracts key findings and insights
- Discusses implications
- Identifies patterns and anomalies
- Dialogue-based interpretation process

## Output
Saves to `{lab_dir}/interpretation.txt` with:
- Result summary
- Key findings
- Statistical analysis
- Implications for research
- Limitations and caveats
- Suggestions for future work

## Python API
```python
from ai_lab_repo import LaboratoryWorkflow

lab = LaboratoryWorkflow(
    research_topic="topic here",
    openai_api_key="your-key"
)
success = lab.results_interpretation()
# Returns: False if completed, True if needs retry
```
