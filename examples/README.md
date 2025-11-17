# Example Research Outputs

This directory contains sample outputs from a test run of the Claude Code native research workflow (`--no-api` mode).

## Research Topic
> How to create the best agentic systems with memory organization, CI/CD of failure logs and able to run in claude code web autonomously and create a submodule containing the directory of the agents ready for cloning to their deployment repo

## Generated Artifacts

### 1. Literature Review (`literature_review.md`)
- **Phase:** Literature Review
- **Agent Role:** PhD Student Researcher
- **Tools Used:** WebSearch, WebFetch, Write
- **Content:**
  - 5 papers reviewed (A-MEM, MIRIX, SICA, Darwin Gödel Machine, AgentArch)
  - Key methods in the field
  - Research gaps identified
  - Recommended research direction

### 2. Research Plan (`research_plan.md`)
- **Phase:** Plan Formulation
- **Agent Role:** Postdoc Researcher
- **Tools Used:** Read, Write
- **Content:**
  - 5 research objectives
  - Testable hypotheses
  - 14-week implementation plan
  - Evaluation metrics
  - Potential challenges and mitigations

### 3. Dataset Information (`dataset_info.md`)
- **Phase:** Data Preparation
- **Agent Role:** ML Engineer
- **Tools Used:** WebSearch, WebFetch, Write
- **Content:**
  - Selected datasets (SWE-bench, LiveCodeBench, Multi-SWE-bench)
  - Loading code examples
  - Preprocessing steps
  - Data pipeline architecture

### 4. Workflow State (`workflow_state.json`)
- Tracks workflow progress across sessions
- Records completed phases
- Stores artifact references
- Enables resume functionality

## Workflow Progression

```
[COMPLETED] Literature Review    → literature_review.md
[COMPLETED] Plan Formulation     → research_plan.md
[COMPLETED] Data Preparation     → dataset_info.md
[PENDING]   Experimentation      → experiment_code.py, experiment_results.md
[PENDING]   Paper Writing        → research_paper.tex
```

## How This Was Generated

1. Started workflow:
   ```bash
   python run_claude_research.py --topic "..." --no-api
   ```

2. Claude Code executed each phase using native tools:
   - **WebSearch** - Found relevant papers and datasets
   - **WebFetch** - Retrieved paper details
   - **Write** - Saved outputs to files
   - **Read** - Read previous phase outputs

3. Workflow state automatically advanced after each file was saved.

## Key Findings

### From Literature Review:
- **A-MEM** - Zettelkasten-inspired memory organization (99.9% storage reduction)
- **SICA** - Self-improving coding agents (17-53% performance gains)
- **Darwin Gödel Machine** - Self-rewriting agents (20% → 50% improvement)
- Identified gap: No integration of memory systems with CI/CD failure logs

### From Research Plan:
- Proposed hierarchical memory architecture (Working/Episodic/Semantic)
- Self-improvement loop via git-based version control
- Target: 25% improvement over RAG baseline
- 14-week implementation timeline

### From Dataset Info:
- SWE-bench Verified - Industry standard for code issue resolution
- LiveCodeBench - Holistic code generation evaluation
- Multi-SWE-bench - Multilingual support (7 languages)
- CI/CD logs - Synthetic + real from GitHub Actions API

## Using These Examples

You can reference these outputs when:
- Understanding what each phase produces
- Seeing the expected format and structure
- Testing the workflow with your own topics
- Learning how Claude Code executes research tasks

## Reproducing

To reproduce similar outputs:

```bash
# Reset and start fresh
python run_claude_research.py --topic "your topic" --no-api --reset

# Run workflow
python run_claude_research.py --topic "your topic" --no-api
# Execute the displayed task
# Save output to specified file
# Repeat until complete
```

Your outputs will be saved to `./research_output/results/` (not version controlled).
