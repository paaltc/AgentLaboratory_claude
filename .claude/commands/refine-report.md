# Report Refinement Phase

Get peer reviews and optionally improve the research.

## Syntax
```bash
/refine-report <topic> [--report=FILE] [--auto-accept]
```

## Arguments
- `topic`: Research topic (required)
- `--report`: Path to report file
- `--auto-accept`: Auto-accept reviews without improvements

## Example
```bash
/refine-report "efficient attention" --report=report.tex
```

## What It Does
- Three Reviewers Agents evaluate paper
- Reviews based on NeurIPS criteria:
  - Originality, Quality, Clarity
  - Significance, Soundness
  - Presentation, Contribution
- Returns decision: Accept or Reject
- Option to improve based on feedback

## Review Criteria
Each reviewer provides:
- Summary and strengths
- Weaknesses and limitations
- Specific questions
- Ethical concerns check
- Confidence and decision (Accept/Reject)

## Output
Saves to `{lab_dir}/reviews/` with:
- `review_1.json` - First reviewer
- `review_2.json` - Second reviewer
- `review_3.json` - Third reviewer
- `decision.txt` - Final decision

## Python API
```python
from ai_lab_repo import LaboratoryWorkflow

lab = LaboratoryWorkflow(
    research_topic="topic here",
    openai_api_key="your-key"
)
return_to_experiments = lab.report_refinement()
# Returns: False if done, True to go back to experiments
```
