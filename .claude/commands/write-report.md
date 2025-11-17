# Report Writing Phase

Generate a comprehensive research paper in LaTeX format.

## Syntax
```bash
/write-report <topic> [--output=FILE] [--steps=N] [--model=MODEL] [--no-compile]
```

## Arguments
- `topic`: Research topic (required)
- `--output`: Output LaTeX file path
- `--steps`: Optimization steps (default: 5)
- `--model`: LLM model to use (default: o3-mini)
- `--no-compile`: Skip PDF compilation

## Example
```bash
/write-report "efficient attention" --steps=7 --model=gpt-4o
```

## What It Does
- Professor Agent guides report generation
- PaperSolver optimizes LaTeX content
- Iterative refinement of paper structure
- Automatic PDF compilation
- References and citations integration

## Output
Saves to `{lab_dir}/` with:
- `report.tex` - LaTeX source
- `report.pdf` - Compiled PDF (if compilation enabled)
- `readme.md` - Markdown summary
- `report.txt` - Plain text version

## Python API
```python
from ai_lab_repo import LaboratoryWorkflow

lab = LaboratoryWorkflow(
    research_topic="topic here",
    openai_api_key="your-key",
    papersolver_max_steps=7,
    compile_pdf=True
)
success = lab.report_writing()
# Returns: False if completed, True if needs retry
```
