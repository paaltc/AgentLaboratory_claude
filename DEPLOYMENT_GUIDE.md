# Agent Laboratory - Claude Sonnet 4.5 Deployment Guide

**Date**: 2025-11-17
**Status**: Ready for Deployment
**Models**: Claude Sonnet 4.5 (Agent) + Claude Haiku 4.5 (Literature Review)

---

## Quick Start

### Prerequisites
1. Claude API key (via Anthropic)
2. Python 3.10+
3. Dependencies installed: `pip install -r requirements.txt`

### Setup

Set your API key in the environment:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Run with Human Oversight

Start a research workflow with full human oversight (you'll review each phase):

```bash
python3 deploy_with_oversight.py --topic "your research topic"
```

**Example**:
```bash
python3 deploy_with_oversight.py --topic "Novel prompt engineering for mathematical reasoning"
```

### Interactive Mode

If you don't specify a topic, you'll be prompted:
```bash
python3 deploy_with_oversight.py
```

---

## What Happens During Execution

### Phase 1: Literature Review
- Claude Haiku 4.5 searches arXiv for relevant papers
- Summarizes and compiles the research landscape
- **Your role**: Review the literature summary, accept or request changes

### Phase 2: Plan Formulation
- Claude Sonnet 4.5 proposes a research plan
- Specifies experiments and methodology
- **Your role**: Review the plan, accept or provide feedback

### Phase 3: Data Preparation
- Claude Sonnet 4.5 generates code to load and prepare data
- Includes error handling and validation
- **Your role**: Review the code, accept or suggest improvements

### Phase 4: Running Experiments
- Claude Sonnet 4.5 implements the planned experiments
- Executes and collects results
- **Your role**: Review experimental setup and results

### Phase 5: Results Interpretation
- Claude Sonnet 4.5 analyzes what the results mean
- Discusses implications and limitations
- **Your role**: Review the interpretation, accept or clarify

### Phase 6: Report Writing
- Claude Sonnet 4.5 generates a full research paper in LaTeX
- Includes all sections: intro, methods, results, discussion
- **Your role**: Review the paper structure and content

### Phase 7: Report Refinement
- Three reviewer agents evaluate the paper using NeurIPS criteria
- Provide detailed feedback
- **Your role**: Review reviewer comments and decide: improve or accept

---

## For Each Phase

When a phase completes, you'll see:

```
═══════════════════════════════════════════════════════════════
PHASE COMPLETE: [Phase Name]
═══════════════════════════════════════════════════════════════

[Full output of this phase]

═══════════════════════════════════════════════════════════════

Are you happy with the presented content? Respond Y or N:
```

**Options**:
- **Y**: Accept and continue to next phase
- **N**: Reject and provide feedback

If you choose **N**, you'll be prompted:
```
Please provide notes for the agent so that they can try again and improve performance:
```

Type your feedback, and the agent will revise and try again.

---

## Available Options

### Command Line Arguments

```bash
python3 deploy_with_oversight.py [OPTIONS]

Options:
  --topic TOPIC       Research topic (default: prompted)
  --steps STEPS       Max exploration steps (default: 50)
  --papers PAPERS     Number of papers to review (default: 5)
```

**Examples**:

More aggressive exploration:
```bash
python3 deploy_with_oversight.py --topic "..." --steps 100 --papers 10
```

Faster, lighter execution:
```bash
python3 deploy_with_oversight.py --topic "..." --steps 20 --papers 3
```

---

## Model Information

### Claude Sonnet 4.5 (Agent Backbone)
- **Purpose**: Main research orchestrator
- **Strengths**: Advanced reasoning, comprehensive understanding
- **Use**: All core research phases
- **Cost**: ~$0.003 per 1K input tokens

### Claude Haiku 4.5 (Literature Review)
- **Purpose**: Fast paper searching and summarization
- **Strengths**: Quick analysis, efficient processing
- **Use**: Literature review phase
- **Cost**: ~$0.0008 per 1K input tokens

---

## Output Artifacts

After completion, all artifacts are saved in a timestamped directory:

```
MATH_research_dir/
├── literature_review.txt       # Summary of papers found
├── research_plan.txt           # Detailed research plan
├── data_preparation.py         # Data loading code
├── experiments/
│   ├── experiment_code.py      # Main experiment code
│   └── results.json            # Experiment metrics
├── interpretation.txt          # Analysis of results
├── report.tex                  # LaTeX paper source
├── report.pdf                  # Compiled PDF (if enabled)
├── readme.md                   # Markdown summary
├── reviews/
│   ├── review_1.json          # Reviewer 1 feedback
│   ├── review_2.json          # Reviewer 2 feedback
│   └── review_3.json          # Reviewer 3 feedback
└── decision.txt               # Accept/Reject decision
```

---

## Checkpoints and Resumption

**Automatic checkpoints** are saved after each phase:

```
state_saves/
├── literature_review_checkpoint.pkl
├── plan_formulation_checkpoint.pkl
├── data_preparation_checkpoint.pkl
├── running_experiments_checkpoint.pkl
├── results_interpretation_checkpoint.pkl
├── report_writing_checkpoint.pkl
└── report_refinement_checkpoint.pkl
```

**If interrupted** (Ctrl+C or error):
- All progress is saved
- Resume in a new session with the same command
- System automatically detects and loads checkpoints

---

## Cost Estimation

### Per Phase (Approximate)

| Phase | Model | Est. Tokens | Est. Cost |
|-------|-------|------------|-----------|
| Literature Review | Haiku 4.5 | 2,000 | $0.002 |
| Plan Formulation | Sonnet 4.5 | 8,000 | $0.024 |
| Data Preparation | Sonnet 4.5 | 10,000 | $0.030 |
| Running Experiments | Sonnet 4.5 | 30,000 | $0.090 |
| Results Interpretation | Sonnet 4.5 | 15,000 | $0.045 |
| Report Writing | Sonnet 4.5 | 40,000 | $0.120 |
| Report Refinement | Sonnet 4.5 | 15,000 | $0.045 |
| **TOTAL** | **Mixed** | **120,000** | **~$0.36** |

---

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### "Module not found" errors
Install dependencies:
```bash
pip install -r requirements.txt
```

### "Request failed" or timeout
The system includes automatic retry with exponential backoff. If it continues:
- Check your internet connection
- Verify API key is valid
- Try again (progress is saved)

### Want to skip a phase
You can interrupt and resume:
1. Press Ctrl+C
2. Modify the phase or provide feedback
3. Run the same command again

---

## Advanced Usage

### Using Different Research Topics

Each run is completely independent. You can run multiple times with different topics:

```bash
# Topic 1: Prompt engineering
python3 deploy_with_oversight.py --topic "Novel prompt engineering techniques"

# Later... Topic 2: Different area
python3 deploy_with_oversight.py --topic "Transformer architecture improvements"
```

Each creates its own output directory and checkpoints.

### Providing Task Notes

Edit `experiment_configs/deployment_claude_oversight.yaml` to add specific guidance:

```yaml
task-notes:
  plan-formulation:
    - "Focus on this specific aspect"
    - "Use this methodology"
```

Then use that config in the YAML loading path.

### Customizing Agent Behavior

Edit `deploy_with_oversight.py` to change:
- `max_steps`: More = deeper exploration
- `num_papers_lit_review`: More = broader literature review
- `mlesolver_max_steps`: More = more experiment iterations
- `papersolver_max_steps`: More = more paper refinement iterations

---

## Expected Workflow

1. **Start**: Run `deploy_with_oversight.py`
2. **Phase 1 complete**: Review literature summary (2-5 min)
   - Accept or request changes
3. **Phase 2 complete**: Review research plan (5-10 min)
   - Accept or provide feedback
4. **Phase 3 complete**: Review code (5-10 min)
   - Accept or suggest improvements
5. **Phase 4 complete**: Review experiments (10-15 min)
   - Accept or request re-runs
6. **Phase 5 complete**: Review interpretation (5-10 min)
   - Accept or clarify implications
7. **Phase 6 complete**: Review paper (10-20 min)
   - Accept or request revisions
8. **Phase 7 complete**: Review reviewer feedback (10-15 min)
   - Accept or iterate for improvement

**Total time**: 45 min - 90 min depending on feedback cycles

---

## Next Steps After Completion

1. **Review generated report**: `MATH_research_dir/report.pdf`
2. **Check implementation**: `MATH_research_dir/experiments/experiment_code.py`
3. **Read analysis**: `MATH_research_dir/interpretation.txt`
4. **Check reviews**: `MATH_research_dir/reviews/`

---

## Support

For issues or questions:
1. Check `DOCUMENTATION_INDEX.md` for topic navigation
2. Review `FINAL_STATUS_REPORT.md` for system capabilities
3. Check `CLAUDE_PRO_INTEGRATION.md` for token management details

---

**Ready to Deploy?**

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python3 deploy_with_oversight.py --topic "Your research topic here"
```

**Let's accelerate research! 🚀**
