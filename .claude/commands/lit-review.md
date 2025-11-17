# Literature Review Phase

Conduct an automated literature review by searching arXiv and analyzing relevant papers.

## Syntax
```bash
/lit-review <topic> [--papers=N] [--model=MODEL]
```

## Arguments
- `topic`: Research topic to review (required)
- `--papers`: Number of papers to collect (default: 5)
- `--model`: LLM model to use (default: o3-mini)

## Example
```bash
/lit-review "attention mechanisms in NLP" --papers=15 --model=gpt-4o
```

## What It Does
- Queries arXiv API for relevant papers
- Agent reads and summarizes papers
- Builds formal literature review document
- Extracts key findings and gaps
- Returns structured review summary

## Output
Saves to `{lab_dir}/literature_review.txt` with:
- Paper summaries and citations
- Key research gaps identified
- Relevant methodologies
- Contribution analysis

## Python API
```python
from ai_lab_repo import LaboratoryWorkflow

lab = LaboratoryWorkflow(
    research_topic="topic here",
    openai_api_key="your-key",
    num_papers_lit_review=15
)
success = lab.literature_review()
# Returns: False if completed, True if needs retry
```
