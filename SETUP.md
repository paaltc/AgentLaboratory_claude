# Agent Laboratory - Setup and Installation Guide

## ✅ Quick Start (Claude Pro)

If you're using Claude Code on the web, most setup is automatic. Just:

1. **Set API key:**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run a research workflow:**
   ```bash
   /perform-research "your research topic" --model=gpt-4o --papers=10
   ```

## 🛠️ Full Manual Setup

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Internet connection (for arXiv, HuggingFace APIs)
- API keys for at least one LLM provider

### Step 1: Clone Repository

```bash
git clone https://github.com/paaltc/AgentLaboratory_claude.git
cd AgentLaboratory_claude
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install system dependencies (Linux/Mac only)
# For LaTeX/PDF compilation support:
sudo apt install texlive texlive-latex-extra

# On Mac:
brew install basictex
```

### Step 4: Configure API Keys

Set your API keys as environment variables:

```bash
# For OpenAI (GPT-4o, o1, o3-mini)
export OPENAI_API_KEY="sk-proj-your-key-here"

# For Anthropic Claude (optional, only if using Claude models)
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**To persist environment variables:**

Create a `.env` file (DO NOT COMMIT THIS):
```bash
OPENAI_API_KEY=sk-proj-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Then load it:
```bash
source .env  # On Linux/Mac
set -a; source .env; set +a  # Alternative
```

## 🚀 Running Workflows

### Option A: Full Automated Pipeline

```bash
python ai_lab_repo.py --yaml-location "experiment_configs/MATH_agentlab.yaml"
```

### Option B: Using Claude Code Commands

See `.claude/commands/` for all available commands:

```bash
# Full research workflow
/perform-research "Your research topic" --model=gpt-4o --papers=10

# Individual phases
/lit-review "Your topic" --papers=15
/plan-phase "Your topic"
/data-prep "Your topic"
/run-experiments "Your topic" --steps=5
/results-interp "Your topic"
/write-report "Your topic"
/refine-report "Your topic"

# Utilities
/search-arxiv "attention mechanisms" --count=20
/search-datasets "sentiment analysis"
/execute-code experiment.py
/set-model gpt-4o
/query-model "What is reinforcement learning?"
```

### Option C: Python API

```python
from ai_lab_repo import LaboratoryWorkflow

# Initialize workflow
lab = LaboratoryWorkflow(
    research_topic="Improving transformer efficiency",
    openai_api_key="your-key",
    agent_model_backbone="gpt-4o",
    max_steps=100,
    num_papers_lit_review=10,
    compile_pdf=True
)

# Run full pipeline
lab.perform_research()

# Or run phases individually
lab.literature_review()
lab.plan_formulation()
lab.data_preparation()
lab.running_experiments()
lab.results_interpretation()
lab.report_writing()
lab.report_refinement()
```

## 📋 Configuration Files

### YAML Configuration

Create `experiment_configs/my_experiment.yaml`:

```yaml
# Research topic
research_topic: "Efficient attention mechanisms in transformers"

# Task-specific notes for agents
task_notes_LLM:
  plan-formulation:
    - "Focus on wall-clock time and memory efficiency"
    - "Use gpt-4o for reasoning"
    - "Available resources: 2x A100 GPUs, 256GB RAM"

  data-preparation:
    - "Use datasets from HuggingFace Hub"
    - "Ensure reproducibility with fixed random seeds"

  running-experiments:
    - "Run at least 3 seeds for each experiment"
    - "Track GPU memory usage"
    - "Compare against baseline attention"

# Workflow parameters
max_steps: 100
compile_latex: true
papers_lit_review: 15
mlesolver_max_steps: 5
papersolver_max_steps: 7
language: "English"

# Model selection (optional)
llm_backend: "gpt-4o"  # or "o3-mini", "deepseek-chat"
```

Run with:
```bash
python ai_lab_repo.py --yaml-location experiment_configs/my_experiment.yaml
```

## 📦 Verifying Installation

Check that everything is installed correctly:

```bash
# Check Python version
python --version  # Should be 3.10+

# Check imports
python -c "from agents import PhDStudentAgent; print('✓ Agents loaded')"
python -c "from tools import ArxivSearch; print('✓ Tools loaded')"
python -c "from inference import query_model; print('✓ Inference loaded')"

# Check dependencies
python -m pip list | grep -E "torch|transformers|pandas|openai"

# Test API connectivity (if OPENAI_API_KEY is set)
python -c "
from inference import query_model
response = query_model('Say hello', api_key='test-mode')
print('✓ API wrapper functional')
"
```

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'openai'"

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: "OPENAI_API_KEY not found"

**Solution:** Set environment variable:
```bash
export OPENAI_API_KEY="sk-proj-..."
```

Verify it's set:
```bash
echo $OPENAI_API_KEY
```

### Issue: "ImportError: cannot import name 'BeautifulSoup'"

**Solution:** Some dependencies weren't installed. Reinstall:
```bash
pip install --upgrade -r requirements.txt
```

### Issue: "LaTeX compilation failed"

**Solution:** Either install LaTeX or disable compilation:
```bash
# Option 1: Install LaTeX
sudo apt install texlive texlive-latex-extra

# Option 2: Disable in your configuration
python ai_lab_repo.py --yaml-location config.yaml --compile-latex false
```

### Issue: "Timeout during literature review"

**Solution:** arXiv API rate limiting. Increase timeout:
```python
lab = LaboratoryWorkflow(
    research_topic="...",
    openai_api_key="...",
    max_steps=200  # Increase from default 100
)
```

### Issue: "CUDA out of memory"

**Solution:** Use a smaller model or reduce batch sizes:
```python
lab = LaboratoryWorkflow(
    research_topic="...",
    openai_api_key="...",
    agent_model_backbone="gpt-4o-mini"  # Smaller model
)
```

## 📊 Monitoring Execution

### View Progress

During execution, check:
- Console output (verbose mode enabled by default)
- Generated files in `{lab_dir}/`
- State checkpoints in `state_saves/`

### Checkpoints

The system saves state after each phase:
```
state_saves/
├── literature_review.pkl
├── plan_formulation.pkl
├── data_preparation.pkl
├── running_experiments.pkl
├── results_interpretation.pkl
├── report_writing.pkl
└── report_refinement.pkl
```

Resume from a checkpoint:
```bash
python ai_lab_repo.py --yaml-location config.yaml --load-checkpoint
```

### Logs and Artifacts

Output structure:
```
{lab_dir}/
├── literature_review.txt      # Collected papers
├── research_plan.txt          # Experimental design
├── data_preparation.py        # Data loading code
├── experiments/
│   └── experiment_code.py     # ML code
├── interpretation.txt         # Analysis
├── report.tex                # LaTeX source
├── report.pdf                # Compiled PDF
└── reviews/                  # Peer reviews
```

## 💰 Cost Tracking

The system tracks API costs automatically:

```python
lab = LaboratoryWorkflow(...)
lab.perform_research()

# Check costs in logs/console output
# Format: "Total cost: $X.XX"
```

Estimate costs:
- Literature review: $2-5 (arXiv search queries)
- Plan formulation: $5-10 (reasoning-heavy)
- Data prep: $3-7 (code generation)
- Running experiments: $10-30 (longest phase)
- Report writing: $5-15 (LaTeX generation)
- **Total: $25-67** per workflow

Use cheaper models to reduce cost:
```python
agent_model_backbone="gpt-4o-mini"  # Cheaper variant
```

## 🔄 Version Management

Update to latest version:
```bash
git pull origin main
pip install --upgrade -r requirements.txt
```

Revert to previous checkpoint:
```bash
# List available checkpoints
ls -la state_saves/

# The system will automatically use the latest checkpoint
python ai_lab_repo.py --yaml-location config.yaml --load-checkpoint
```

## 🎓 Next Steps

1. **Read CLAUDE.md** - Understand the project architecture
2. **Review .claude/commands/** - See available operations
3. **Create a YAML config** - Define your research topic
4. **Run a test workflow** - Start with a simple topic
5. **Monitor execution** - Watch agents work in the console
6. **Analyze results** - Review generated artifacts

## 📞 Support

- **GitHub Issues:** Report problems at repository
- **Documentation:** See CLAUDE.md for architecture details
- **Command Help:** Check `.claude/commands/` for specific operations
- **Logs:** Check `state_saves/` for error information

## 🔐 Security Best Practices

1. **Never commit API keys** - Use `.env` file (in `.gitignore`)
2. **Use environment variables** - Set them securely
3. **Review agent outputs** - Verify code before execution
4. **Keep dependencies updated** - Run `pip install --upgrade -r requirements.txt`
5. **Monitor costs** - Set up API key alerts if available

---

**Ready to start?** Run your first workflow:
```bash
/perform-research "Your research topic here" --model=gpt-4o --papers=10
```
