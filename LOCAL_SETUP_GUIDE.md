# Local Setup Guide - Agent Laboratory with Claude Code Web

**Goal**: Clone the repository locally and test-run with Claude Code Web integration

---

## Option 1: If Repository is on GitHub (Recommended)

### Step 1: Clone the Repository
```bash
# Clone from GitHub
git clone https://github.com/YOUR_USERNAME/AgentLaboratory_claude.git
cd AgentLaboratory_claude

# Or if you have the specific branch:
git clone -b claude/assess-repo-functionality-01Qhko437nievvP3TVzpYBq5 \
  https://github.com/YOUR_USERNAME/AgentLaboratory_claude.git
cd AgentLaboratory_claude
```

### Step 2: Verify Branch
```bash
git branch
# Should see: * claude/assess-repo-functionality-01Qhko437nievvP3TVzpYBq5

git log --oneline -5
# Should show recent commits
```

### Step 3: Install Dependencies
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install anthropic openai pyyaml arxiv requests PyPDF2 tiktoken feedparser
```

### Step 4: Run Local Test
```bash
# Test without Claude Code Web (manual API key)
export ANTHROPIC_API_KEY="sk-ant-..."
python3 deploy_with_oversight.py --topic "Test topic"

# Or test the demo
python3 deploy_demo.py
```

---

## Option 2: Using Current Claude Code Environment

If you're already in Claude Code Web and want to test here:

### Step 1: Verify You're on the Right Branch
```bash
git branch
git log --oneline -3
```

### Step 2: Test Run (No API Key Needed!)
```bash
# In Claude Code Web, just run:
python3 deploy_with_oversight.py --topic "Your research topic"

# The system will:
# 1. Detect ANTHROPIC_BASE_URL (Claude Code Web environment)
# 2. Use built-in authentication automatically
# 3. Start the deployment with human oversight
```

---

## Option 3: Mirror to Your Own GitHub

If you want to push this to your own GitHub account:

### Step 1: Create Bare Clone
```bash
# On your local machine, create a new GitHub repo first
# Then mirror the repository:

git clone --mirror /path/to/AgentLaboratory_claude/.git AgentLaboratory_claude.git

cd AgentLaboratory_claude.git

git push --mirror https://github.com/YOUR_USERNAME/AgentLaboratory_claude.git

cd ..
rm -rf AgentLaboratory_claude.git

# Now clone normally
git clone https://github.com/YOUR_USERNAME/AgentLaboratory_claude.git
cd AgentLaboratory_claude
```

### Step 2: Verify All Branches
```bash
git branch -a
# Should show:
# * main
#   remotes/origin/main
#   remotes/origin/claude/assess-repo-functionality-01Qhko437nievvP3TVzpYBq5
```

### Step 3: Checkout the Feature Branch
```bash
git checkout claude/assess-repo-functionality-01Qhko437nievvP3TVzpYBq5
```

---

## Running the Deployment Locally

### Without Claude Code Web (Use Explicit API Key)
```bash
# 1. Set your API key
export ANTHROPIC_API_KEY="sk-ant-..."

# 2. Run the deployment
python3 deploy_with_oversight.py --topic "Improving reasoning in LLMs"

# 3. At each phase, you'll be prompted:
#    Are you happy with the presented content? Respond Y or N:
#    - Y = Accept and continue
#    - N = Provide feedback and agent revises
```

### With Claude Code Web (No API Key Needed)
```bash
# 1. Make sure you're in Claude Code Web environment
#    (you should have ANTHROPIC_BASE_URL set automatically)

# 2. Just run:
python3 deploy_with_oversight.py --topic "Your research topic"

# 3. The system automatically detects Claude Code Web
#    and uses built-in authentication
```

---

## Typical Workflow

```bash
# 1. Clone and setup
git clone https://github.com/YOUR_USERNAME/AgentLaboratory_claude.git
cd AgentLaboratory_claude
git checkout claude/assess-repo-functionality-01Qhko437nievvP3TVzpYBq5
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Test locally with API key
export ANTHROPIC_API_KEY="sk-ant-..."
python3 deploy_with_oversight.py --topic "Test topic" --steps 20 --papers 3

# 3. When you're happy, run in Claude Code Web
#    (just use Claude Code Web's native terminal and run the same command)
```

---

## File Structure After Clone

```
AgentLaboratory_claude/
├── deploy_with_oversight.py        # Main deployment script
├── deploy_demo.py                  # Demo/initialization script
├── ai_lab_repo.py                  # Core workflow orchestrator
├── agents.py                       # 7 agent types
├── inference.py                    # LLM interface (Claude 4.5 models)
├── tools.py                        # Search tools (ArXiv, HuggingFace)
├── experiment_configs/
│   └── deployment_claude_oversight.yaml
├── QUICK_START_REFERENCE.md        # 30-second quick start
├── DEPLOYMENT_GUIDE.md             # Complete setup guide
├── DEPLOYMENT_WALKTHROUGH.md       # Phase-by-phase examples
├── DOCUMENTATION_INDEX.md          # Navigation guide
└── requirements.txt                # Dependencies
```

---

## What You'll See When Running

### Phase 1 Output (Example)
```
═══════════════════════════════════════════════════════════════════════════════
PHASE 1: LITERATURE REVIEW
═══════════════════════════════════════════════════════════════════════════════

🔍 Searching arXiv for papers on: "Your topic"

Found 142 relevant papers...
Analyzing top 5 most relevant papers...

═══════════════════════════════════════════════════════════════════════════════
LITERATURE REVIEW SUMMARY
═══════════════════════════════════════════════════════════════════════════════

[100+ lines of literature summary...]

═══════════════════════════════════════════════════════════════════════════════

Are you happy with the presented content? Respond Y or N:
```

### Your Response
```
Y
# → Checkpoint saved, proceeds to Phase 2

# OR

N
# → Asks for feedback:
Please provide notes for the agent so that they can try again and improve performance:
> I'd like you to focus more on recent papers from 2024 and include more
> about prompt engineering specifically

# → Agent revises and shows improved version
```

---

## Troubleshooting

### Module Not Found Errors
```bash
pip install anthropic openai pyyaml arxiv requests PyPDF2 tiktoken feedparser flask
```

### No ANTHROPIC_API_KEY Set
```bash
# Option 1: Set explicitly
export ANTHROPIC_API_KEY="sk-ant-..."

# Option 2: If in Claude Code Web, it's automatic
# (system detects ANTHROPIC_BASE_URL automatically)
```

### Want to Resume After Interruption
```bash
# Just run the same command again
# Checkpoints are automatically detected and loaded
python3 deploy_with_oversight.py --topic "Same topic"
```

### Clear All Checkpoints and Start Fresh
```bash
rm -rf state_saves/
rm -rf MATH_research_dir*/
python3 deploy_with_oversight.py --topic "Your topic"
```

---

## Key Files to Understand

### `deploy_with_oversight.py` (Main Entry Point)
- 150 lines
- Handles argument parsing
- Sets up human oversight system
- Initializes Claude Sonnet 4.5 as agent backbone
- Initializes Claude Haiku 4.5 for literature review

### `ai_lab_repo.py` (Core Orchestrator)
- 1000+ lines
- LaboratoryWorkflow class managing 7 phases
- CheckpointManager for state persistence
- TokenManager for budget tracking
- human_in_loop_flag configuration

### `inference.py` (LLM Interface)
- 200+ lines
- Claude Sonnet 4.5 support (newly added)
- Claude Haiku 4.5 support (newly added)
- Cost estimation
- Token counting

### `agents.py` (Agent Definitions)
- 1400+ lines
- 7 agent classes: PhD, Postdoc, MLEngineer, SWEngineer, Professor, Reviewers
- LLM communication
- State management

---

## Next Steps

1. **Clone the repository**
   ```bash
   git clone [URL] AgentLaboratory_claude
   cd AgentLaboratory_claude
   git checkout claude/assess-repo-functionality-01Qhko437nievvP3TVzpYBq5
   ```

2. **Read the quick start**
   ```bash
   cat QUICK_START_REFERENCE.md
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # or just the essentials:
   pip install anthropic openai pyyaml arxiv
   ```

4. **Test run locally or in Claude Code Web**
   ```bash
   # Local with API key:
   export ANTHROPIC_API_KEY="sk-ant-..."
   python3 deploy_with_oversight.py --topic "Test"

   # Or in Claude Code Web (no API key needed):
   python3 deploy_with_oversight.py --topic "Your topic"
   ```

5. **Follow the interactive prompts**
   - See each phase output
   - Approve (Y) or request changes (N)
   - Agent revises automatically
   - Continue through all 7 phases

---

## Documentation Reference

- **Quick Start**: `QUICK_START_REFERENCE.md` (2 min read)
- **Setup Guide**: `DEPLOYMENT_GUIDE.md` (10 min read)
- **What to Expect**: `DEPLOYMENT_WALKTHROUGH.md` (20 min read)
- **Architecture**: `README.md`
- **All Docs**: `DOCUMENTATION_INDEX.md`

---

**Ready to get started?**

```bash
git clone [YOUR_REPO_URL] AgentLaboratory_claude
cd AgentLaboratory_claude
python3 deploy_with_oversight.py --topic "Your research question"
```

Human oversight enabled on all 7 phases. You control everything! 🚀
