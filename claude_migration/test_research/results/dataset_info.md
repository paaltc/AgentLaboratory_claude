# Dataset Information for Agentic Systems Research

## Selected Datasets

### Primary Dataset: SWE-bench Verified
- **Name:** SWE-bench/SWE-bench_Verified
- **Source:** Hugging Face (https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified)
- **Size:** ~500 verified instances
- **Format:** JSON with problem statements, base commits, test patches
- **Why suitable:** Industry-standard benchmark for code issue resolution; verified by human annotators; directly measures agent performance on real GitHub issues

### Loading Code
```python
from datasets import load_dataset

# Load SWE-bench Verified dataset
swe_bench = load_dataset("SWE-bench/SWE-bench_Verified")

# Structure
# - instance_id: unique identifier
# - problem_statement: GitHub issue text
# - base_commit: commit hash representing pre-fix state
# - repo: repository name
# - test_patch: ground truth test

print(f"Train samples: {len(swe_bench['train'])}")
```

---

### Secondary Dataset: LiveCodeBench
- **Name:** livecodebench/code_generation_lite
- **Source:** Hugging Face (https://huggingface.co/datasets/livecodebench/code_generation_lite)
- **Size:** 500+ problems from LeetCode, AtCoder, Codeforces
- **Format:** Problem descriptions with test cases
- **Why suitable:** Holistic evaluation of code generation, self-repair, and test output prediction; continually updated "live" benchmark

### Loading Code
```python
from datasets import load_dataset

# Load LiveCodeBench
lcb = load_dataset("livecodebench/code_generation_lite")

# Evaluates:
# - Code generation
# - Self-repair capabilities
# - Test output prediction
# - Code execution accuracy
```

---

### Tertiary Dataset: Multi-SWE-bench
- **Name:** ByteDance-Seed/Multi-SWE-bench
- **Source:** Hugging Face (https://huggingface.co/datasets/ByteDance-Seed/Multi-SWE-bench)
- **Size:** 1,632 high-quality instances
- **Languages:** Java, TypeScript, JavaScript, Go, Rust, C, C++
- **Format:** Multilingual code issue resolution tasks
- **Why suitable:** Tests agent generalization across programming languages; curated by 68 expert annotators

### Loading Code
```python
from datasets import load_dataset

# Load Multi-SWE-bench
multi_swe = load_dataset("ByteDance-Seed/Multi-SWE-bench")

# Supports 7 languages beyond Python
# Useful for testing agent's language-agnostic capabilities
```

---

### CI/CD Failure Log Dataset (Synthetic + Real)

Since no public research dataset exists for CI/CD failure logs, we will construct one:

#### Approach 1: GitHub Actions API Mining
```python
import requests
import json

def fetch_workflow_runs(repo, token):
    """Fetch failed workflow runs from GitHub Actions"""
    headers = {"Authorization": f"token {token}"}
    url = f"https://api.github.com/repos/{repo}/actions/runs"
    params = {"status": "failure", "per_page": 100}

    response = requests.get(url, headers=headers, params=params)
    return response.json()

def fetch_run_logs(repo, run_id, token):
    """Download logs for a specific run"""
    headers = {"Authorization": f"token {token}"}
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/logs"

    response = requests.get(url, headers=headers)
    return response.content  # Returns zip file

# Example usage
repos = [
    "microsoft/vscode",
    "facebook/react",
    "tensorflow/tensorflow",
    "pytorch/pytorch"
]

failure_logs = []
for repo in repos:
    runs = fetch_workflow_runs(repo, GITHUB_TOKEN)
    for run in runs.get("workflow_runs", [])[:10]:
        log = fetch_run_logs(repo, run["id"], GITHUB_TOKEN)
        failure_logs.append({
            "repo": repo,
            "run_id": run["id"],
            "conclusion": run["conclusion"],
            "created_at": run["created_at"],
            "logs": log
        })
```

#### Approach 2: Synthetic Failure Generation
```python
import random

# Common CI/CD failure patterns
FAILURE_PATTERNS = {
    "dependency_error": [
        "npm ERR! peer dep missing",
        "ModuleNotFoundError: No module named",
        "Could not find artifact",
    ],
    "test_failure": [
        "FAILED tests/test_main.py::TestCase",
        "AssertionError: Expected X but got Y",
        "Error: Test suite failed to run",
    ],
    "build_error": [
        "error: Cannot find module",
        "SyntaxError: Unexpected token",
        "TypeError: undefined is not a function",
    ],
    "timeout": [
        "Error: Job exceeded maximum execution time",
        "Process timed out after 3600 seconds",
    ],
    "permission_error": [
        "Permission denied (publickey)",
        "Error: EACCES: permission denied",
    ]
}

def generate_synthetic_failure():
    """Generate synthetic CI/CD failure log"""
    error_type = random.choice(list(FAILURE_PATTERNS.keys()))
    error_msg = random.choice(FAILURE_PATTERNS[error_type])

    return {
        "type": error_type,
        "message": error_msg,
        "timestamp": "2025-01-01T00:00:00Z",
        "job": "build_and_test",
        "step": "Run tests",
        "exit_code": 1
    }
```

**Target Dataset Size:** 10,000+ failure logs (mix of real and synthetic)

---

## Data Statistics

### SWE-bench Verified
- Training samples: ~500 instances
- Validation samples: Subset for testing
- Test samples: Held out for final evaluation
- Features: problem_statement, base_commit, repo, test_patch
- Average issue length: ~200-500 tokens
- Repository diversity: 12+ major Python projects

### LiveCodeBench
- Total problems: 500+
- Sources: LeetCode, AtCoder, Codeforces
- Difficulty distribution: Easy (30%), Medium (50%), Hard (20%)
- Features: problem description, test cases, solutions
- Continually updated with new problems

### Multi-SWE-bench
- Total instances: 1,632
- Languages: 7 (Java, TypeScript, JS, Go, Rust, C, C++)
- Annotators: 68 expert reviewers
- Quality: Curated from 2,456 candidates

### CI/CD Failure Logs (Target)
- Total logs: 10,000+
- Error types: 5 major categories
- Sources: Public repos + synthetic
- Format: JSON with structured error information

---

## Preprocessing Steps

### 1. SWE-bench Preprocessing
```python
def preprocess_swe_bench(instance):
    """Preprocess SWE-bench instance for agent training"""
    return {
        "id": instance["instance_id"],
        "issue_text": clean_markdown(instance["problem_statement"]),
        "repo": instance["repo"],
        "commit": instance["base_commit"],
        "test": instance["test_patch"],
        "difficulty": estimate_difficulty(instance)
    }

def estimate_difficulty(instance):
    """Estimate task difficulty based on test complexity"""
    test_lines = instance["test_patch"].count("\n")
    if test_lines < 20:
        return "easy"
    elif test_lines < 50:
        return "medium"
    else:
        return "hard"
```

### 2. Failure Log Preprocessing
```python
def preprocess_failure_log(log):
    """Extract structured information from CI/CD failure log"""
    return {
        "raw_log": log["message"],
        "error_type": classify_error(log["message"]),
        "stack_trace": extract_stack_trace(log),
        "affected_files": extract_file_paths(log),
        "suggested_fixes": generate_fix_suggestions(log["error_type"]),
        "embedding": generate_embedding(log["message"])
    }

def classify_error(message):
    """Classify error type using pattern matching"""
    patterns = {
        "dependency": ["npm ERR!", "ModuleNotFoundError", "pip install"],
        "syntax": ["SyntaxError", "IndentationError", "ParseError"],
        "test": ["AssertionError", "FAILED", "test_"],
        "timeout": ["timeout", "exceeded maximum"],
        "permission": ["Permission denied", "EACCES"]
    }
    for error_type, keywords in patterns.items():
        if any(kw in message for kw in keywords):
            return error_type
    return "unknown"
```

### 3. Data Splitting
```python
from sklearn.model_selection import train_test_split

def split_dataset(dataset, test_size=0.2, val_size=0.1):
    """Split dataset into train/val/test sets"""
    # First split: train+val vs test
    train_val, test = train_test_split(
        dataset, test_size=test_size, random_state=42
    )

    # Second split: train vs val
    val_ratio = val_size / (1 - test_size)
    train, val = train_test_split(
        train_val, test_size=val_ratio, random_state=42
    )

    return train, val, test

# Usage
train_data, val_data, test_data = split_dataset(swe_bench_data)
print(f"Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")
```

---

## Data Quality Assurance

1. **Deduplication:** Remove duplicate entries across datasets
2. **Validation:** Ensure all instances have required fields
3. **Balancing:** Ensure balanced representation of error types
4. **Anonymization:** Remove sensitive information from logs
5. **Versioning:** Track dataset versions with git

---

## Storage Requirements

| Dataset | Raw Size | Processed Size | Format |
|---------|----------|----------------|--------|
| SWE-bench Verified | ~500 MB | ~100 MB | JSON |
| LiveCodeBench | ~200 MB | ~50 MB | JSON |
| Multi-SWE-bench | ~800 MB | ~150 MB | JSON |
| CI/CD Failure Logs | ~1 GB | ~200 MB | JSON |
| **Total** | **~2.5 GB** | **~500 MB** | - |

All datasets will be stored in JSON format for web compatibility and version controlled with git for reproducibility.

---

## Data Pipeline

```
Raw Data Sources → Fetch → Parse → Clean → Categorize → Embed → Store → Index
     ↓                ↓        ↓       ↓         ↓          ↓       ↓       ↓
  GitHub API       JSON    Remove   Validate  Classify   Vector   SQLite  Memory
  HuggingFace      Parse   Noise    Schema    By Type    Embed    DB      Graph
```

This pipeline ensures consistent, high-quality data for training and evaluating our agentic system.
