# Quick Start Reference - Claude Sonnet 4.5 Deployment

## 30-Second Setup

```bash
# 1. Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# 2. Run deployment with human oversight
python3 deploy_with_oversight.py --topic "Your research topic"

# 3. For each phase, you'll see output and be asked: "Are you happy? (Y/N)"
#    Y = Accept and continue
#    N = Provide feedback and agent revises
```

---

## The 7 Phases at a Glance

| # | Phase | Time | Who Reviews |
|---|-------|------|-------------|
| 1 | 📚 Literature Review | 3-5m | Haiku 4.5 |
| 2 | 📋 Plan Formulation | 5-10m | Sonnet 4.5 |
| 3 | 💾 Data Preparation | 5-10m | Sonnet 4.5 |
| 4 | 🧪 Running Experiments | 10-15m | Sonnet 4.5 |
| 5 | 📊 Results Interpretation | 5-10m | Sonnet 4.5 |
| 6 | 📝 Report Writing | 10-20m | Sonnet 4.5 |
| 7 | ✅ Report Refinement | 10-15m | Sonnet 4.5 |

**Total**: 45-90 minutes | **Cost**: ~$0.031 | **Checkpoints**: 7

---

## Commands

### Run with specific topic
```bash
python3 deploy_with_oversight.py --topic "Efficient transformers"
```

### Run with custom parameters
```bash
python3 deploy_with_oversight.py \
  --topic "Your topic" \
  --steps 30 \
  --papers 3
```

### Run and be prompted for topic
```bash
python3 deploy_with_oversight.py
```

---

## During Execution

### When you see:
```
Are you happy with the presented content? Respond Y or N:
```

### Your options:
- **Y** → Accept output, proceed to next phase
- **N** → Rejected, will ask for feedback

### If you choose N:
```
Please provide notes for the agent so that they can try again and improve performance:
> [Type your feedback here]
```

Agent will revise and show improved version.

---

## Files Created

After each run, you get:

```
MATH_research_dir_[timestamp]/
├── literature_review.txt          # Papers summary
├── research_plan.txt              # Research methodology
├── data_preparation.py            # Data loading code
├── experiments/
│   ├── experiment_code.py         # Experiment code
│   └── results.json               # Results data
├── interpretation.txt             # Analysis
├── report.tex                     # Paper (LaTeX)
├── report.pdf                     # Paper (PDF)
├── readme.md                      # Summary
├── reviews/                       # Peer reviews
│   ├── review_1.json
│   ├── review_2.json
│   └── review_3.json
└── decision.txt                   # Accept/Reject
```

---

## Checkpoints

Auto-saved in `state_saves/`:

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

**If interrupted** (Ctrl+C): Progress saved, resume with same command.

---

## Model Details

### Claude Sonnet 4.5
- **Uses**: Planning, code, analysis, writing, review
- **Capability**: Advanced reasoning
- **Cost**: $0.003 per 1K input tokens

### Claude Haiku 4.5
- **Uses**: Literature review only
- **Capability**: Fast, efficient
- **Cost**: $0.0008 per 1K input tokens

---

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Module not found error
```bash
pip install anthropic openai pyyaml
```

### Want to skip a phase
Press Ctrl+C, then run same command again (checkpoint will resume).

### Want to clear checkpoints
```bash
rm -rf state_saves/
```

---

## Example Topics

- "Efficient attention mechanisms"
- "Few-shot learning strategies"
- "Prompt engineering for code generation"
- "Reasoning in language models"
- "Energy-efficient neural networks"

---

## Key Facts

✓ **Human Oversight**: You approve every major output
✓ **Automatic Checkpoints**: State saved after each phase
✓ **Flexible**: Reject any phase and request improvements
✓ **Cost**: ~$0.031 per complete workflow
✓ **Time**: 45-90 minutes total (with feedback)
✓ **Models**: Sonnet 4.5 (main) + Haiku 4.5 (literature)

---

## Next Steps

1. **Read the full walkthrough**: `DEPLOYMENT_WALKTHROUGH.md`
2. **Get deployment guide**: `DEPLOYMENT_GUIDE.md`
3. **Set API key**: `export ANTHROPIC_API_KEY="..."`
4. **Start research**: `python3 deploy_with_oversight.py --topic "..."`

---

## Questions?

- **Setup**: See `DEPLOYMENT_GUIDE.md`
- **What to expect**: See `DEPLOYMENT_WALKTHROUGH.md`
- **Architecture**: See `README.md`
- **All docs**: See `DOCUMENTATION_INDEX.md`

---

**Ready to start?**

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python3 deploy_with_oversight.py --topic "Your research topic"
```

Let the agents show you what you can accomplish! 🚀
