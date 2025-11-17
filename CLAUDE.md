# Agent Laboratory - Project Overview

## 🎯 Project Summary

Agent Laboratory is an end-to-end autonomous research workflow system that uses LLM agents to conduct multi-phase research projects. It automates the entire research pipeline from literature review through paper writing, using specialized agents working together in structured phases.

**Key Features:**
- 🤖 7 specialized agent roles collaborating autonomously
- 📚 Automated literature review from arXiv
- 🔬 Experiment design and execution with ML optimization
- 📝 Automatic research paper generation in LaTeX
- 🎓 Peer review simulation with refinement loop
- 💾 Full checkpoint/recovery system

## 📁 Repository Structure

```
AgentLaboratory_claude/
├── .claude/
│   └── commands/           # Claude Code command specifications (15 commands)
├── agents.py              # Core agent classes (PhD, Postdoc, ML Engineer, etc.)
├── ai_lab_repo.py         # Main LaboratoryWorkflow orchestrator
├── app.py                 # Application layer and server (AgentRxiv)
├── tools.py               # Search tools (ArXiv, HuggingFace, execution)
├── inference.py           # LLM inference wrapper (OpenAI, DeepSeek, etc.)
├── mlesolver.py           # ML experiment optimization solver
├── papersolver.py         # LaTeX paper generation and optimization solver
├── utils.py               # Utility functions
├── common_imports.py      # Shared imports for all modules
├── requirements.txt       # Python dependencies
├── experiment_configs/    # YAML configuration files for experiments
├── README.md              # Project documentation
└── readme/                # Translated READMEs
```

## 🤖 Agent Architecture

### Seven Specialized Agents

1. **PhDStudentAgent**
   - Role: Research director and executor
   - Handles: Literature review, planning, data prep, interpretation
   - Primary thinker in the workflow

2. **PostdocAgent**
   - Role: Mentor and critical reviewer
   - Handles: Plan formulation guidance, results interpretation
   - Provides senior oversight

3. **MLEngineerAgent**
   - Role: Code implementer
   - Handles: Data preparation, experiment coding
   - Creates executable Python code

4. **SWEngineerAgent**
   - Role: Code quality overseer
   - Handles: Code validation and refinement
   - Ensures production-ready code

5. **ProfessorAgent**
   - Role: Report mentor
   - Handles: Paper writing guidance
   - Ensures academic quality

6. **ReviewersAgent** (3 specialized reviewers)
   - Role: Peer reviewers
   - Handles: Report evaluation using NeurIPS criteria
   - Provides accept/reject decisions

7. **BaseAgent** (Parent class)
   - Implements: LLM communication, state management, history tracking
   - Handles: Inference, token tracking, cost calculation

## 📊 Research Workflow Phases

### Phase 1: Literature Review
- Agent queries arXiv for relevant papers
- Collects and summarizes research
- Builds comprehensive review document
- Output: `literature_review.txt`

### Phase 2: Plan Formulation
- PhD Student proposes research plan
- Postdoc provides feedback
- Collaborative dialogue refines approach
- Output: `research_plan.txt`

### Phase 3: Data Preparation
- ML Engineer creates data loading code
- SW Engineer validates code quality
- Handles edge cases and error handling
- Output: `data_preparation.py`

### Phase 4: Running Experiments
- ML Engineer generates experiment code
- MLESolver optimizes approach iteratively
- Executes safely with timeout protection
- Output: `experiment_code.py`, `results.json`

### Phase 5: Results Interpretation
- Postdoc analyzes experiment results
- Extracts key findings and insights
- Discusses implications
- Output: `interpretation.txt`

### Phase 6: Report Writing
- Professor guides paper generation
- PaperSolver optimizes LaTeX iteratively
- Compiles to PDF (if pdflatex available)
- Output: `report.tex`, `report.pdf`, `readme.md`

### Phase 7: Report Refinement
- Three Reviewers evaluate using NeurIPS criteria
- Based on review: Accept or return to Phase 2
- Recursive improvement if needed
- Output: `reviews/*.json`, `decision.txt`

## 🔧 Core Modules

### agents.py (52KB)
**Main Classes:**
- `BaseAgent` - Parent with LLM integration
- `PhDStudentAgent` - Research conductor
- `PostdocAgent` - Guidance provider
- `MLEngineerAgent` - Code generator
- `SWEngineerAgent` - Code validator
- `ProfessorAgent` - Paper mentor
- `ReviewersAgent` - Peer review committee

**Key Methods:**
- `inference()` - Query LLM with context
- `add_review()` - Parse and add papers to literature review
- `format_review()` - Format literature review output

### ai_lab_repo.py (45KB)
**Main Class:**
- `LaboratoryWorkflow` - Orchestrates entire research pipeline

**Key Methods:**
- `perform_research()` - Run full 7-phase workflow
- `literature_review()` - Phase 1
- `plan_formulation()` - Phase 2
- `data_preparation()` - Phase 3
- `running_experiments()` - Phase 4
- `results_interpretation()` - Phase 5
- `report_writing()` - Phase 6
- `report_refinement()` - Phase 7
- `save_state()` - Checkpoint system
- `set_model()` - Change LLM mid-workflow

### tools.py (13KB)
**Search Classes:**
- `ArxivSearch` - Find papers on arXiv
- `HFDataSearch` - Search HuggingFace Hub datasets
- `SemanticScholarSearch` - Search Semantic Scholar

**Execution Functions:**
- `execute_code()` - Safe code execution with timeout

**Key Features:**
- Query length handling (300 char limit for arXiv)
- PDF text extraction
- Retry logic with exponential backoff
- Multiprocessing-based sandboxing

### inference.py (10KB)
**Supported Models:**
- OpenAI: gpt-4o, o1, o1-mini, o3-mini
- Anthropic: claude-3-opus, claude-3-sonnet
- DeepSeek: deepseek-chat
- Google: gemini-pro

**Key Functions:**
- `query_model()` - Send prompt to LLM
- Token counting and cost tracking
- Automatic retry with exponential backoff

### mlesolver.py (33KB)
**ML Experiment Optimization:**
- Iterative code refinement
- Performance metric tracking
- Experimental design optimization
- Reward-based selection

### papersolver.py (33KB)
**LaTeX Paper Optimization:**
- LaTeX document generation
- Iterative refinement based on quality metrics
- PDF compilation integration
- Citation and reference management

## 🚀 How to Use

### Basic Research Execution
```python
from ai_lab_repo import LaboratoryWorkflow

# Initialize workflow
lab = LaboratoryWorkflow(
    research_topic="Your research question here",
    openai_api_key="your-api-key",
    agent_model_backbone="gpt-4o",
    max_steps=100,
    num_papers_lit_review=10
)

# Run full pipeline
lab.perform_research()
```

### Phase-by-Phase Control
```python
# Run individual phases
lab.literature_review()
lab.plan_formulation()
lab.data_preparation()
lab.running_experiments()
lab.results_interpretation()
lab.report_writing()
lab.report_refinement()
```

### Configuration via YAML
```bash
python ai_lab_repo.py --yaml-location "experiment_configs/MATH_agentlab.yaml"
```

### Search for Papers/Datasets
```python
from tools import ArxivSearch, HFDataSearch

# Search arXiv
arxiv = ArxivSearch()
papers = arxiv.find_papers_by_str("attention mechanisms", N=20)
full_text = arxiv.retrieve_full_paper_text("2304.12234")

# Search HuggingFace
hf = HFDataSearch()
datasets = hf.retrieve_ds("sentiment analysis", N=10)
```

## 📋 Claude Code Commands

All workflow phases and utilities are exposed as Claude Code commands in `.claude/commands/`:

**Workflow Commands:**
- `/perform-research` - Full pipeline
- `/lit-review` - Literature review
- `/plan-phase` - Plan formulation
- `/data-prep` - Data preparation
- `/run-experiments` - Experiment execution
- `/results-interp` - Results interpretation
- `/write-report` - Report writing
- `/refine-report` - Report refinement

**Utility Commands:**
- `/search-arxiv` - Search papers
- `/search-datasets` - Search datasets
- `/execute-code` - Run code safely
- `/set-model` - Change LLM model
- `/save-checkpoint` - Save state
- `/query-model` - Query LLM directly
- `/configure-workflow` - Set parameters

## ⚙️ Configuration

### Environment Variables Required
```bash
export OPENAI_API_KEY="sk-..."        # For OpenAI models
export ANTHROPIC_API_KEY="sk-ant-..."  # For Anthropic models (optional)
```

### YAML Configuration Example
```yaml
research_topic: "Your research topic"
task_notes_LLM:
  plan-formulation:
    - "Use gpt-4o for this phase"
    - "Focus on efficiency"
  running-experiments:
    - "Available: 2x A100 GPUs"
    - "Max 4 hours per experiment"

max_steps: 100
compile_latex: true
papers_lit_review: 10
mlesolver_max_steps: 5
papersolver_max_steps: 7
language: "English"
```

## 🔄 Checkpoint and Recovery

The system automatically saves state after each phase:
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

Resume from checkpoint:
```bash
python ai_lab_repo.py --yaml-location config.yaml --load-checkpoint
```

## 📦 Dependencies

### Core Dependencies
- **LLM APIs:** openai, anthropic, google-generativeai
- **Paper Search:** arxiv, feedparser
- **Data:** pandas, numpy, datasets, pyarrow
- **ML/DL:** torch, transformers, huggingface-hub
- **Code Execution:** requests, pydantic, tenacity

### Optional System Dependencies
- **LaTeX Compilation:** `apt install texlive texlive-latex-extra`

## 🔐 Security Notes

- Code execution sandboxed via multiprocessing with timeout
- All LLM calls logged for cost tracking
- State saved locally (no cloud dependencies except API calls)
- API keys only stored in environment variables

## 🎓 Research Best Practices

1. **Write extensive notes** - Tell agents your constraints and preferences
2. **Use powerful models** - Better models = better research (consider o1/o3)
3. **Set realistic steps** - max_steps limits exploration, reasonable is 20-100
4. **Leverage checkpoints** - Save frequently and resume on failures
5. **Monitor costs** - Track token usage and API costs in logs

## 📚 Output Artifacts

Each research run generates:
```
{lab_dir}/
├── literature_review.txt    # Summary of papers
├── research_plan.txt        # Detailed experimental plan
├── data_preparation.py      # Data loading code
├── experiments/
│   ├── experiment_code.py   # Main experiment code
│   └── results.json         # Performance metrics
├── interpretation.txt       # Analysis of results
├── report.tex              # LaTeX source
├── report.pdf              # Compiled PDF
├── readme.md               # Markdown summary
├── reviews/
│   ├── review_1.json       # Reviewer 1
│   ├── review_2.json       # Reviewer 2
│   └── review_3.json       # Reviewer 3
└── decision.txt            # Accept/Reject
```

## 🤝 Integration with Claude Code

This project is optimized for Claude Code Web:
- All commands documented in `.claude/commands/`
- Settings configured in `claude-settings.json`
- Automatic dependency management via requirements.txt
- State checkpoints enable resumable sessions

## 📞 Support

For issues:
1. Check existing logs in `state_saves/`
2. Review agent outputs in `{lab_dir}/`
3. Verify API keys are set correctly
4. Check Python version is 3.10+

## 📄 Citation

```bibtex
@misc{schmidgall2025agentlaboratoryusingllm,
      title={Agent Laboratory: Using LLM Agents as Research Assistants},
      author={Samuel Schmidgall and others},
      year={2025},
      eprint={2501.04227},
      archivePrefix={arXiv},
      primaryClass={cs.HC}
}
```
