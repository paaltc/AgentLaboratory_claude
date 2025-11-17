# Conda Environment Setup - Agent Laboratory

**Goal**: Create and manage a conda environment for Agent Laboratory deployment

---

## 🐍 Conda Setup (Recommended for Python Projects)

### Option 1: Quick Setup (5 minutes)

#### Step 1: Create Conda Environment
```bash
# Create environment with Python 3.11
conda create -n agent-lab python=3.11 -y

# Activate environment
conda activate agent-lab
```

#### Step 2: Clone Repository
```bash
git clone [REPO_URL] AgentLaboratory_claude
cd AgentLaboratory_claude
git checkout claude/assess-repo-functionality-01Qhko437nievvP3TVzpYBq5
```

#### Step 3: Install Dependencies
```bash
# Install core packages via conda (faster and more reliable)
conda install -c conda-forge anthropic openai pyyaml -y

# Install additional packages
pip install arxiv requests PyPDF2 tiktoken feedparser flask
```

#### Step 4: Run Deployment
```bash
# In Claude Code Web (no API key needed):
python3 deploy_with_oversight.py --topic "Your research topic"

# Or locally with explicit API key:
export ANTHROPIC_API_KEY="sk-ant-..."
python3 deploy_with_oversight.py --topic "Your research topic"
```

---

### Option 2: Using environment.yml (Recommended for Sharing)

#### Step 1: Create environment.yml File
```bash
# In your repo root directory
cat > environment.yml << 'EOF'
name: agent-lab
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pip
  - pip:
    - anthropic>=0.39.0
    - openai>=1.55.1
    - pyyaml>=6.0
    - arxiv>=1.4.0
    - requests>=2.31.0
    - PyPDF2>=3.0.0
    - tiktoken>=0.12.0
    - feedparser>=6.0.10
    - flask>=3.0.0
    - tenacity>=8.2.0
    - tqdm>=4.65.0
EOF
```

#### Step 2: Create Environment from File
```bash
# Create environment from environment.yml
conda env create -f environment.yml

# Activate it
conda activate agent-lab
```

#### Step 3: Verify Installation
```bash
python3 -c "import anthropic; import openai; print('✓ All imports working')"
```

---

### Option 3: Step-by-Step Installation (Most Control)

#### Step 1: Create Base Environment
```bash
# Create with minimal Python
conda create -n agent-lab python=3.11 pip -y
conda activate agent-lab
```

#### Step 2: Install Conda Packages
```bash
# Core ML/Data packages via conda (faster compilation)
conda install -c conda-forge \
  numpy \
  pandas \
  pyyaml \
  -y

# Or minimal:
conda install pyyaml -y
```

#### Step 3: Install Python Packages via Pip
```bash
# LLM APIs
pip install anthropic>=0.39.0 openai>=1.55.1

# Data/Search
pip install arxiv requests PyPDF2 feedparser

# Utilities
pip install tiktoken tenacity tqdm flask pydantic

# Optional (for advanced features)
pip install torch transformers datasets
```

#### Step 4: Verify Everything
```bash
python3 << 'EOF'
import sys
packages = ['anthropic', 'openai', 'yaml', 'arxiv', 'requests', 'tiktoken']
missing = []
for pkg in packages:
    try:
        __import__(pkg)
        print(f"✓ {pkg}")
    except ImportError:
        print(f"✗ {pkg}")
        missing.append(pkg)

if missing:
    print(f"\nMissing: {', '.join(missing)}")
    sys.exit(1)
else:
    print("\n✓ All packages installed")
EOF
```

---

## 📋 Common Conda Commands

### Environment Management
```bash
# List all environments
conda env list

# Activate environment
conda activate agent-lab

# Deactivate environment
conda deactivate

# Remove environment
conda remove --name agent-lab --all

# Show environment info
conda info --envs
```

### Package Management
```bash
# List installed packages
conda list

# Search for package
conda search pyyaml

# Install package
conda install pyyaml

# Update package
conda update anthropic

# Uninstall package
conda remove anthropic

# Export environment
conda env export > environment.yml

# Create from export
conda env create -f environment.yml
```

---

## 🚀 Full Workflow with Conda

```bash
# 1. Create environment
conda create -n agent-lab python=3.11 -y
conda activate agent-lab

# 2. Clone repo
git clone [REPO_URL] AgentLaboratory_claude
cd AgentLaboratory_claude
git checkout claude/assess-repo-functionality-01Qhko437nievvP3TVzpYBq5

# 3. Install dependencies
pip install anthropic openai pyyaml arxiv requests PyPDF2 tiktoken

# 4. Run deployment
python3 deploy_with_oversight.py --topic "Your research topic"

# 5. When done
conda deactivate

# 6. Later, reactivate when needed
conda activate agent-lab
```

---

## 🎯 Recommended Approach for This Project

### For Individual Use:
```bash
conda create -n agent-lab python=3.11 -y
conda activate agent-lab
pip install -r requirements.txt
```

### For Team/Sharing:
```bash
# 1. Create environment
conda env create -f environment.yml

# 2. Make changes, then export
conda env export > environment.yml

# 3. Team members can recreate
conda env create -f environment.yml
```

---

## 📝 Creating environment.yml for This Project

Let me create a proper one for Agent Laboratory:

**File: `environment.yml`**
```yaml
name: agent-lab
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pip
  - yaml
  - pip:
    # LLM APIs
    - anthropic>=0.39.0
    - openai>=1.55.1
    - google-generativeai>=0.3.0

    # Paper and Data Handling
    - arxiv>=1.4.0
    - PyPDF2>=3.0.0
    - pypdf>=5.1.0
    - feedparser>=6.0.10

    # Web Framework (optional, for app.py)
    - flask>=3.0.0
    - werkzeug>=2.0.0

    # Text/Token Processing
    - tiktoken>=0.12.0
    - requests>=2.31.0

    # Utilities
    - tenacity>=8.2.0
    - pydantic>=2.0.0
    - tqdm>=4.65.0
    - python-dateutil>=2.8.2

    # Optional for advanced features
    # - torch>=2.0.0
    # - transformers>=4.30.0
    # - pandas>=2.0.0
    # - numpy>=1.24.0
```

---

## ⚡ Quick Start with Conda

```bash
# 1. Install conda if needed (miniconda is lightweight)
# From: https://docs.conda.io/projects/miniconda/en/latest/

# 2. Create environment
conda create -n agent-lab python=3.11 pip -y

# 3. Activate
conda activate agent-lab

# 4. Clone repo
git clone [URL] && cd AgentLaboratory_claude
git checkout claude/assess-repo-functionality-01Qhko437nievvP3TVzpYBq5

# 5. Install from environment file (if it exists)
conda env create -f environment.yml

# Or install manually
pip install anthropic openai pyyaml arxiv requests PyPDF2

# 6. Run
python3 deploy_with_oversight.py --topic "Your topic"
```

---

## 🔧 Troubleshooting Conda

### Issue: Conda command not found
```bash
# Add conda to PATH (Linux/Mac)
export PATH="/path/to/miniconda3/bin:$PATH"

# Or reinstall miniconda from:
# https://docs.conda.io/projects/miniconda/en/latest/
```

### Issue: Package conflict
```bash
# Solve conflicts with conda solver
conda install --strict-channel-priority

# Or try mamba (faster)
conda install -c conda-forge mamba -y
mamba create -n agent-lab python=3.11 -y
```

### Issue: Environment doesn't activate
```bash
# Initialize conda
conda init bash  # or zsh, fish, powershell, etc.

# Then open new terminal
conda activate agent-lab
```

### Issue: Pip packages not installing in conda env
```bash
# Make sure pip is from conda env
which pip  # Should show path to agent-lab environment

# If not, reinstall pip in conda env
conda install pip -y
```

---

## 🐋 Docker Alternative (If Conda Issues)

If conda doesn't work, here's a Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone repo
RUN git clone [REPO_URL] . && \
    git checkout claude/assess-repo-functionality-01Qhko437nievvP3TVzpYBq5

# Install Python dependencies
RUN pip install --no-cache-dir \
    anthropic \
    openai \
    pyyaml \
    arxiv \
    requests \
    PyPDF2 \
    tiktoken \
    feedparser \
    flask

# Default command
CMD ["python3", "deploy_with_oversight.py"]
```

Build and run:
```bash
docker build -t agent-lab .
docker run -it agent-lab --topic "Your topic"
```

---

## ✅ Verification Checklist

After setting up conda environment, verify:

```bash
conda activate agent-lab

# Check Python version
python --version  # Should be 3.11+

# Check key packages
python -c "import anthropic; print('✓ anthropic')"
python -c "import openai; print('✓ openai')"
python -c "import yaml; print('✓ yaml')"
python -c "import arxiv; print('✓ arxiv')"

# Check deployment script exists
ls deploy_with_oversight.py

# Try running help
python deploy_with_oversight.py --help
```

---

## 📚 Resources

- **Conda Documentation**: https://docs.conda.io/
- **Miniconda (lightweight)**: https://docs.conda.io/projects/miniconda/en/latest/
- **Environment Management**: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html
- **Pip + Conda**: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#using-pip-in-an-environment

---

## 🚀 Next Steps

1. **Install Miniconda** (if not already installed)
   ```bash
   # Check if conda exists
   conda --version
   ```

2. **Create Agent Lab environment**
   ```bash
   conda create -n agent-lab python=3.11 -y
   conda activate agent-lab
   ```

3. **Clone and setup**
   ```bash
   git clone [REPO_URL] AgentLaboratory_claude
   cd AgentLaboratory_claude
   git checkout claude/assess-repo-functionality-01Qhko437nievvP3TVzpYBq5
   pip install anthropic openai pyyaml arxiv requests PyPDF2
   ```

4. **Run deployment**
   ```bash
   python3 deploy_with_oversight.py --topic "Your research topic"
   ```

---

**Conda environment ready for Agent Laboratory deployment! 🐍**
