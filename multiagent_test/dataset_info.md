# Dataset Information for IDM-CICDFL Research

**Research Project**: Integrated Dynamic Memory Organization for CI/CD Failure Learning (IDM-CICDFL)

**Created**: November 17, 2025

**Purpose**: Identify, document, and provide loading instructions for datasets suitable for agentic systems research with memory organization and CI/CD failure learning.

---

## Executive Summary

This document outlines **13 primary and secondary datasets** suitable for the IDM-CICDFL research, covering:
- CI/CD-specific failures (build, test, deployment, infrastructure)
- Real-world bug benchmarks
- Failure learning and agent error analysis
- Log anomaly detection
- Code repair and generation tasks

**Recommended Primary Datasets**:
1. **AgentErrorBench** - Failure learning with agent trajectories (HIGHEST PRIORITY)
2. **Defects4J** - Real Java bugs with test cases and fixes
3. **Log Anomaly Detection Datasets** - System-level failures (HDFS, BGL, LO2)
4. **CodeXGLUE** - Code understanding and repair tasks
5. **BART Dataset** - Maven build-specific failures

---

## PRIMARY DATASETS FOR CORE RESEARCH

### 1. AgentErrorBench (PRIORITY: HIGHEST)

**Purpose**: Directly aligned with research objectives - failure learning and agent debugging

**Source**: Paper "Where LLM Agents Fail and How They Can Learn From Failures" (arXiv:2509.25370)
- Authors: Kunlun Zhu et al.
- Date: September 29, 2025
- GitHub: https://github.com/thinkwee/AgentErrorBench

**Dataset Composition**:
- **Size**: Multiple environments with annotated failure trajectories
- **Source Environments**:
  - ALFWorld (embodied reasoning tasks)
  - GAIA (complex reasoning tasks)
  - WebShop (e-commerce interaction tasks)
- **Failure Taxonomy**: AgentErrorTaxonomy covering:
  - Memory failures
  - Reflection failures
  - Planning failures
  - Action/execution failures
  - System-level failures

**Key Features**:
- Systematically annotated failure trajectories
- Root-cause isolation annotations
- Multi-step task failure analysis
- Real agent rollouts (not synthetic)

**Relevance to Research**:
- ✓ Demonstrates failure cascading across agent components
- ✓ Provides failure taxonomy applicable to CI/CD context
- ✓ Tests debugging framework approach
- ✓ Agent learning from failures (core hypothesis)

**Expected Performance on Baseline**:
- AgentDebug achieves 24% higher accuracy than baseline
- 17% improvement in step-level accuracy
- Up to 26% relative improvement after iterative learning

**Loading Code Example**:
```python
# Install dependencies
# pip install -e git+https://github.com/thinkwee/AgentErrorBench#egg=agenterrorbench

from agenterrorbench import load_dataset, AgentErrorTaxonomy

# Load dataset
dataset = load_dataset("agenterrorbench")

# Access failure trajectories with annotations
for example in dataset:
    failure_id = example["trajectory_id"]
    error_type = example["error_type"]  # From AgentErrorTaxonomy
    root_cause = example["root_cause_layer"]  # memory, reflection, planning, action, system
    failure_steps = example["failure_trajectory"]
    corrections = example["corrective_feedback"]
    
# Filter by environment or error type
filtered = dataset.filter(lambda x: x["environment"] == "alfworld")
```

**Preprocessing Steps**:
1. **Trajectory Normalization**: Standardize action/observation formats across environments
2. **Annotation Verification**: Validate root-cause annotations against trajectory execution
3. **Layer Mapping**: Map AgentErrorTaxonomy to CI/CD layers:
   - Memory → Artifact retention failures
   - Reflection → Analysis accuracy failures
   - Planning → Build step sequencing failures
   - Action → Execution/deployment failures
   - System → Infrastructure/dependency failures
4. **Temporal Analysis**: Extract failure propagation timelines
5. **Feature Extraction**: Generate embeddings for failure patterns

**Dataset Split**:
- Train: 70% of trajectories
- Validation: 15%
- Test: 15% (held-out environments)

---

### 2. Defects4J (PRIORITY: HIGH)

**Purpose**: Real-world Java bugs with reproducible failures and test suites

**Source**: Official repository and benchmark
- Paper: "Defects4J: a database of existing faults" (ISSTA 2014)
- GitHub: https://github.com/rjust/defects4j
- Website: http://defects4j.org
- Latest Version: 2.0+ with 854 bugs from 17 open-source projects

**Dataset Composition**:
- **Total Bugs**: 854 real bugs + 10 deprecated
- **Projects**: 17 Java open-source systems
  - Apache Commons (multiple sub-projects)
  - JFreeChart
  - Joda-Time
  - Mockito
  - and others
- **Per-bug Artifacts**:
  - Buggy source code
  - Fixed source code
  - Failing test case(s)
  - Passing test suite
  - Detailed bug description

**Key Features**:
- Real bugs from production systems
- Reproducible (all tested on Java 11)
- Complete test suites for each bug
- Multi-layer failure analysis possible:
  - Compilation failures (if applicable)
  - Test failures (explicit)
  - Propagation through call stack

**Relevance to Research**:
- ✓ Real failures from real systems
- ✓ Root-cause identification can be validated against fixes
- ✓ Test failure analysis (Phase 1 benchmark target)
- ✓ Cross-project transfer evaluation opportunity
- ✓ Hierarchical layer mapping possible (code analysis → test execution)

**Expected Characteristics**:
- Bug types: Logic errors, condition errors, return statement errors, array boundary errors
- Difficulty: Easy to Medium (single-point bugs typically easier than multi-file failures)

**Loading Code Example**:
```python
# Install Defects4J
# Follow: https://github.com/rjust/defects4j#getting-started

import subprocess
import os
import json

class Defects4JLoader:
    def __init__(self, defects4j_root):
        self.d4j_root = defects4j_root
        
    def get_all_bugs(self):
        """Get list of all available bugs"""
        cmd = f"{self.d4j_root}/framework/bin/defects4j list -p all"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip().split('\n')
    
    def load_bug(self, project, bug_id):
        """Load specific bug with metadata"""
        bug_data = {
            "project": project,
            "bug_id": bug_id,
            "buggy_version": None,
            "fixed_version": None,
            "test_cases": [],
            "bug_info": None
        }
        
        # Checkout buggy version
        cmd = f"{self.d4j_root}/framework/bin/defects4j checkout -p {project} -v {bug_id}b -w /tmp/d4j_buggy"
        subprocess.run(cmd, shell=True)
        bug_data["buggy_version"] = "/tmp/d4j_buggy"
        
        # Get failing tests
        cmd = f"{self.d4j_root}/framework/bin/defects4j test -d /tmp/d4j_buggy"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        bug_data["test_cases"] = self._parse_test_output(result.stdout)
        
        return bug_data
    
    def _parse_test_output(self, output):
        """Parse test output to extract failing tests"""
        tests = []
        for line in output.split('\n'):
            if '::' in line:  # JUnit test format
                tests.append(line.strip())
        return tests

# Usage
loader = Defects4JLoader("/path/to/defects4j")
bugs = loader.get_all_bugs()
for bug_info in bugs[:100]:  # Load first 100
    bug_data = loader.load_bug(*bug_info.split('-'))
    # Process bug_data
```

**Preprocessing Steps**:
1. **Failure Type Classification**: Categorize by:
   - Compilation failure (if code won't compile)
   - Test failure type (assertion, exception, timeout)
   - Failure layer (unit test, integration test, etc.)
2. **Code Diff Analysis**: Extract modifications needed for fix
3. **Dependency Tracing**: Map affected modules and dependencies
4. **Complexity Scoring**: Rate bug complexity (lines changed, scope, etc.)
5. **Test Coverage**: Analyze which tests detect the bug
6. **Fix Pattern Extraction**: Identify common fix patterns

**Expected Dataset Statistics**:
- Compilation failures: ~5-10%
- Test failures: 85%+
- Multi-file bugs: ~40%
- Average lines changed: 5-15

**Cross-Project Opportunities**:
- Train on N-1 projects for transfer learning evaluation
- Identify common patterns across projects
- Test meta-learning capabilities

---

### 3. Log Anomaly Detection Datasets (PRIORITY: HIGH)

**Purpose**: System-level and infrastructure failure detection - addresses infrastructure layer of CI/CD

**Primary Datasets**: HDFS, BGL, LO2 (from Loghub and AIT-AECID)

#### 3a. HDFS Log Dataset
- **Size**: 11.2 million log messages
- **Source**: Map-reduce tasks on 200+ Amazon EC2 nodes
- **Processed**: 575,061 log sequences (16,838 anomalous)
- **Format**: Structured log entries with timestamps
- **Application**: Distributed system failure detection

#### 3b. BGL (Blue Gene/L) Dataset
- **Size**: 4.7 million log messages
- **Source**: Supercomputer at Lawrence Livermore National Labs
- **Failure Labels**: 348,460 messages labeled as failures
- **Format**: Supercomputer system logs
- **Application**: Hardware/infrastructure failure patterns

#### 3c. LO2 Dataset (2025 - Most Recent)
- **Size**: Production-scale microservice logs
- **Components**: Logs, metrics, and distributed traces
- **Source**: Real microservice system
- **Features**:
  - Log sequences with context
  - Performance metrics
  - Trace spans
  - Failure annotations
- **Application**: Modern CI/CD infrastructure analysis

**Relevance to Research**:
- ✓ Infrastructure layer failure detection (5-10% of benchmark)
- ✓ Hierarchical layer analysis: infrastructure → deployment → test
- ✓ Real system logs for pretraining failure patterns
- ✓ Multi-modal failure signals (logs + metrics + traces)

**Loading Code Example**:
```python
# Using anomaly-detection-log-datasets tools
# GitHub: https://github.com/ait-aecid/anomaly-detection-log-datasets

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

class LogDatasetLoader:
    def __init__(self, dataset_type="hdfs"):
        self.dataset_type = dataset_type
        
    def load_hdfs(self, filepath):
        """Load HDFS log dataset"""
        logs = pd.read_csv(filepath, sep='^')
        logs['timestamp'] = pd.to_datetime(logs['timestamp'])
        return logs
    
    def load_bgl(self, filepath):
        """Load BGL supercomputer logs"""
        logs = pd.read_csv(filepath, sep='^')
        return logs
    
    def load_lo2(self, filepath):
        """Load LO2 microservice logs"""
        logs = pd.read_json(filepath, lines=True)
        logs['timestamp'] = pd.to_datetime(logs['timestamp'])
        return logs
    
    def extract_sequences(self, logs, window_size=100):
        """Extract log sequences for anomaly detection"""
        sequences = []
        labels = []
        
        for session_id in logs['session_id'].unique():
            session_logs = logs[logs['session_id'] == session_id].sort_values('timestamp')
            session_sequence = session_logs['event_template'].values
            session_label = 1 if session_logs['failure'].any() else 0
            
            # Create sliding windows
            for i in range(len(session_sequence) - window_size + 1):
                seq = session_sequence[i:i+window_size]
                sequences.append(seq)
                labels.append(session_label)
        
        return np.array(sequences), np.array(labels)
    
    def extract_features(self, logs):
        """Extract ML-ready features from logs"""
        features = {
            "message_count": logs.groupby("session_id").size(),
            "unique_events": logs.groupby("session_id")["event_id"].nunique(),
            "time_span": logs.groupby("session_id")["timestamp"].apply(
                lambda x: (x.max() - x.min()).total_seconds()
            ),
            "error_rate": logs.groupby("session_id")["level"].apply(
                lambda x: (x == "ERROR").sum() / len(x)
            )
        }
        return pd.DataFrame(features)

# Usage
loader = LogDatasetLoader()
hdfs_logs = loader.load_hdfs("hdfs_log.csv")
sequences, labels = loader.extract_sequences(hdfs_logs)
features = loader.extract_features(hdfs_logs)
```

**Preprocessing Steps**:
1. **Log Parsing**: Extract structured fields from raw logs
   - Timestamp normalization
   - Event template extraction
   - Parameter extraction
2. **Session Identification**: Group logs by execution context
3. **Sequence Creation**: Build time-series from log events
4. **Anomaly Labeling**: Apply failure annotations
5. **Feature Engineering**:
   - Event frequency patterns
   - Temporal characteristics
   - Severity distributions
6. **Normalization**: Scale features for model input

**Mapping to CI/CD Layers**:
- Infrastructure failures: Container issues, resource constraints
- Deployment failures: Network problems, configuration errors
- Test failures: Resource timeouts in test environment

---

### 4. CodeXGLUE (PRIORITY: MEDIUM)

**Purpose**: Code understanding, generation, and repair benchmarks

**Source**: Microsoft Research
- Paper: "CodeXGLUE: A Machine Learning Benchmark Dataset for Code" (arXiv:2102.04664)
- GitHub: https://github.com/microsoft/CodeXGLUE
- Hugging Face: https://huggingface.co/datasets/microsoft/codeXGLUE

**Dataset Composition**:
- **14 Datasets** across 10 tasks
- **Languages**: Java, Python, C#, JavaScript, PHP, Go, Ruby, Rust
- **Tasks Relevant to Research**:
  - **Code Repair (Bugs2Fix)**: Buggy code → fixed code
  - **Defect Detection**: Identify if code has defects
  - **Code Completion**: Predict missing tokens
  - **Clone Detection**: Find similar code snippets

**Key Features**:
- Code-to-code alignment
- Bug-fix pair annotations
- Multi-language coverage
- Large-scale: 1M+ examples across tasks

**Relevance to Research**:
- ✓ Code repair task directly applicable
- ✓ Compilation error detection
- ✓ Test failure patterns in code
- ✓ Multi-language generalization testing

**Loading Code Example**:
```python
from datasets import load_dataset

# Load Code Repair task (Bugs2Fix)
repair_dataset = load_dataset("microsoft/codeXGLUE", "code_repair")

# Example structure
for example in repair_dataset['train']:
    buggy_code = example['buggy_code']
    fixed_code = example['fixed_code']
    repo = example['repo']  # Project source
    
# Load Defect Detection task
defect_dataset = load_dataset("microsoft/codeXGLUE", "defect_detection")

for example in defect_dataset['train']:
    code = example['code']
    label = example['label']  # 0: no defect, 1: has defect
    
# Custom preprocessing
def preprocess_repair(batch):
    """Tokenize and prepare for fine-tuning"""
    return {
        "buggy_ids": tokenizer(batch['buggy_code'], truncation=True),
        "fixed_ids": tokenizer(batch['fixed_code'], truncation=True)
    }

processed = repair_dataset.map(preprocess_repair, batched=True)
```

**Preprocessing Steps**:
1. **Code Tokenization**: Parse and tokenize code
2. **AST Extraction**: Build Abstract Syntax Trees
3. **Diff Computation**: Calculate changes between buggy/fixed
4. **Context Expansion**: Include surrounding code/imports
5. **Error Type Annotation**: Classify bug types (if not provided)

---

### 5. BART Dataset (Maven Build Failures) (PRIORITY: MEDIUM)

**Purpose**: Maven build-specific failures - compilation and dependency errors

**Source**: Research on "Every build you break"
- Authors: Carmine Vassallo et al.
- Publication: Empirical Software Engineering journal
- Replication Package: https://zenodo.org/record/3346615
- Paper: https://link.springer.com/article/10.1007/s10664-019-09765-y

**Dataset Composition**:
- **Build Logs**: From real Maven projects
- **Failure Categories** (exact research taxonomy):
  - Compilation failures (syntax, symbol errors)
  - Testing failures (assertion failures, test errors)
  - Dependency failures (missing/conflicting dependencies)
  - Plugin failures (Maven plugin configuration errors)
  - Code analysis failures (Checkstyle, PMD violations)

**Key Features**:
- Raw ~40,000-line Maven logs per failure
- Processed summaries (~14 lines per failure)
- Root cause annotations
- Suggested fixes from StackOverflow integration
- Build error patterns and hints

**Relevance to Research**:
- ✓ Build layer specificity (Phase 1 benchmark: 20-25% compilation errors)
- ✓ Real-world build systems
- ✓ Failure summarization (memory organization challenge)
- ✓ Cross-project build patterns

**Expected Impact from Paper**:
- Build-fix time reduction: 41% average
- Clarity ratings: 88-100% for different failure categories

**Loading Code Example**:
```python
import json
import pandas as pd
from pathlib import Path

class MavenBuildFailureLoader:
    def __init__(self, data_path):
        self.data_path = Path(data_path)
    
    def load_failures(self):
        """Load Maven build failure dataset"""
        failures = []
        
        for failure_file in self.data_path.glob("**/failure_*.json"):
            with open(failure_file) as f:
                failure_data = json.load(f)
                failures.append(failure_data)
        
        return pd.DataFrame(failures)
    
    def parse_maven_log(self, raw_log):
        """Parse Maven build log into structured format"""
        parsed = {
            "timestamp": self._extract_timestamp(raw_log),
            "project": self._extract_project(raw_log),
            "phase": self._extract_phase(raw_log),  # compile, test, package
            "error_type": self._classify_error(raw_log),
            "error_message": self._extract_error(raw_log),
            "stack_trace": self._extract_stack_trace(raw_log),
            "root_cause": None,  # To be annotated
            "suggested_fix": None  # To be filled
        }
        return parsed
    
    def extract_failure_summary(self, raw_log, max_lines=14):
        """Extract concise summary from verbose log"""
        # Filtering strategy: Keep only error lines and context
        error_lines = [
            line for line in raw_log.split('\n')
            if '[ERROR]' in line or 'FAILURE' in line or 'Exception' in line
        ]
        return '\n'.join(error_lines[:max_lines])
    
    def _extract_timestamp(self, log): pass
    def _extract_project(self, log): pass
    def _extract_phase(self, log): pass
    def _classify_error(self, log): pass
    def _extract_error(self, log): pass
    def _extract_stack_trace(self, log): pass

# Usage
loader = MavenBuildFailureLoader("./maven_failures")
failures_df = loader.load_failures()

# Access failure summaries
for idx, failure in failures_df.iterrows():
    raw_log = failure['raw_log']
    summary = loader.extract_failure_summary(raw_log)
    error_type = failure['error_type']
```

**Preprocessing Steps**:
1. **Log Parsing**: Extract structured fields from raw Maven output
2. **Error Classification**: Map to categories (compilation, test, dependency, etc.)
3. **Stack Trace Processing**: Parse Java exceptions
4. **Dependency Resolution**: Extract Maven dependency information
5. **Plugin Analysis**: Identify failing Maven plugins
6. **Failure Summarization**: Create concise summaries from verbose logs
7. **Solution Linking**: Connect to StackOverflow solutions

---

## SECONDARY DATASETS FOR EVALUATION AND BASELINES

### 6. LiveCodeBench (Code Generation and Self-Repair)

**Purpose**: Code generation with test-based feedback - relevant for test layer learning

**Source**: Competition programming benchmark
- GitHub: https://github.com/livebench/livebench
- Hugging Face: https://huggingface.co/datasets/livecodebench/code_generation_lite
- Paper: Focus on holistic code evaluation

**Dataset Characteristics**:
- **Size**: 400+ problems (v1), 511+ (v2), 612+ (v3, latest)
- **Languages**: Python, Java, C++
- **Format**: Problem description → code generation → test evaluation
- **Test Cases**: Multiple test cases per problem with clear pass/fail signals
- **Difficulty Range**: Easy to Hard difficulty levels

**Relevance**:
- ✓ Test failure signal analysis
- ✓ Code generation error patterns
- ✓ Failure feedback learning
- ✓ Self-repair capabilities

**Loading Code Example**:
```python
from datasets import load_dataset

# Load LiveCodeBench
livecodebench = load_dataset("livecodebench/code_generation_lite", "python")

# Access problem and test information
for example in livecodebench['test']:
    problem_id = example['problem_id']
    problem_statement = example['problem_statement']
    starter_code = example['starter_code']
    test_cases = example['test_cases']  # List of (input, expected_output)
    difficulty = example['difficulty']
    
    # Run generated code against tests
    for test_input, expected_output in test_cases:
        # This would be execution sandbox
        pass
```

---

### 7. HumanEval and MBPP (Code Generation Benchmarks)

**Purpose**: Established code generation tasks with clear failure signals

**Source**: 
- HumanEval: OpenAI (arXiv:2107.03374)
- MBPP: Google (arXiv:2108.07732)

**Dataset Characteristics**:
- **HumanEval**: 164 hand-written Python programming problems
- **MBPP**: 1,000 Python programming problems from crowd-sourcing
- **Test Cases**: 2-8 test cases per problem
- **Difficulty**: Easy to Medium difficulty

**Relevance**:
- ✓ Test failure scenarios with clear success criteria
- ✓ Code generation error types
- ✓ Baseline comparison for learning efficiency (H3)

**Loading Code Example**:
```python
# HumanEval
from datasets import load_dataset

humaneval = load_dataset("openai_humaneval")
for example in humaneval['test']:
    task_id = example['task_id']
    prompt = example['prompt']
    test = example['test']
    entry_point = example['entry_point']
    
# MBPP
mbpp = load_dataset("google-research-datasets/mbpp")
```

---

### 8. StaQC Stack Overflow Dataset

**Purpose**: Real failure patterns from Stack Overflow Q&A

**Source**: Researchers at UC Davis
- Paper: "StaQC: A Systematically Mined Question-Code Dataset from Stack Overflow"
- GitHub: https://github.com/LittleYUYU/StackOverflow-Question-Code-Dataset
- Size: ~148K Python, ~120K SQL question-code pairs

**Relevance**:
- ✓ Real error descriptions and solutions
- ✓ Knowledge extraction for memory organization
- ✓ Failure pattern diversity
- ✓ Developer-facing explanations

---

### 9. Reflexion Benchmarks

**Purpose**: Evaluation of linguistic feedback and agent learning

**Source**: NeurIPS 2023 paper "Reflexion: Language Agents with Verbal Reinforcement Learning"
- GitHub: https://github.com/noahshinn/reflexion
- Paper: arXiv:2303.11366

**Benchmarks Used**:
- **HotPotQA**: 100 question samples for reasoning evaluation
- **LeetcodeHardGym**: 40 hard-level Leetcode problems across 19 languages
- **MBPP/HumanEval**: Code generation (mentioned above)

**Key Innovation**: Agents learn through linguistic feedback + memory reflection

**Relevance**:
- ✓ Linguistic feedback mechanisms (H4)
- ✓ Episodic memory for failure patterns
- ✓ Learning from explanations rather than weights
- ✓ Cross-domain evaluation

---

### 10. Deep-Bench (Deep Learning Code Generation Failures)

**Purpose**: Failure analysis specific to deep learning code

**Source**: arXiv:2502.18726

**Failure Types Catalogued**:
- Tensor shape mismatches
- Type mismatches (int vs float)
- Import errors
- API compatibility issues
- Logic errors in learning procedures

**Relevance**:
- ✓ Code generation error taxonomy
- ✓ ML-specific failure patterns
- ✓ Deep learning framework specificity

---

## RECOMMENDED DATA PREPARATION WORKFLOW

### Phase 1: Dataset Selection and Integration (Weeks 1-2)

```python
# Priority selection
primary_datasets = [
    ("AgentErrorBench", "Highest", "Core failure learning"),
    ("Defects4J", "High", "Real bugs with test suites"),
    ("Log Datasets (HDFS/BGL/LO2)", "High", "Infrastructure failures"),
    ("CodeXGLUE", "Medium", "Code repair benchmarks"),
    ("BART Maven", "Medium", "Build-specific failures")
]

# Obtain datasets
for name, priority, description in primary_datasets:
    # Download and document
    # Verify integrity (checksums)
    # Extract metadata
    pass
```

### Phase 2: Unified Dataset Creation (Weeks 3-4)

Create a unified CI/CD failure dataset combining:
1. **Defects4J Test Failures** → Test layer
2. **CodeXGLUE Code Repair** → Compilation layer
3. **BART Maven Logs** → Build layer
4. **Log Anomalies** → Infrastructure layer
5. **AgentErrorBench Trajectories** → Multi-layer propagation

**Target**: 500+ annotated failures with consistent schema

### Phase 3: Annotation Framework

**Unified Schema**:
```python
{
    "failure_id": str,
    "timestamp": datetime,
    "project": str,
    "failure_type": str,  # compilation, test, integration, deployment, infrastructure
    "primary_layer": str,  # application, build, test, deployment, infrastructure
    "affected_layers": List[str],  # layers impacted by failure propagation
    "root_cause": str,
    "error_message": str,
    "stack_trace": str,
    "reproduction_steps": List[str],
    "resolution": str,
    "resolution_steps": List[str],
    "prevention_strategy": str,
    "complexity_score": float,  # 0-10
    "frequency_pattern": str,  # rare, occasional, frequent, recurring
    "learning_difficulty": str,  # easy, medium, hard
    "source_dataset": str,
    "raw_data": dict  # Original format from source dataset
}
```

---

## DATASET STATISTICS SUMMARY

| Dataset | Size | Primary Use | Failure Types | Annotations |
|---------|------|------------|---------------|-------------|
| AgentErrorBench | ~1k trajectories | Agent failure learning | Multi-module | Full |
| Defects4J | 854 bugs | Test failures | Logic errors | Comprehensive |
| HDFS Logs | 575k sequences | Infrastructure anomalies | System-level | Labels |
| BGL Logs | 4.7M messages | Infrastructure patterns | Hardware faults | Partial |
| CodeXGLUE | 1M+ examples | Code repair | Syntax, logic | Some |
| BART Maven | Variable | Build failures | Compilation, deps | Full |
| LiveCodeBench | 612 problems | Test feedback | Code generation | Test cases |
| HumanEval | 164 problems | Code generation | Syntax, logic | Test cases |
| StaQC | 268k pairs | Knowledge patterns | Diverse | Natural |
| LO2 | Production scale | Microservice logs | System faults | Labels |

---

## IMPLEMENTATION ROADMAP

### Month 1: Dataset Preparation
- [ ] Download and verify all datasets
- [ ] Create unified annotation framework
- [ ] Implement loading utilities for each dataset
- [ ] Establish quality assurance metrics

### Month 2: Benchmark Creation
- [ ] Merge datasets into unified 500+ failure benchmark
- [ ] Perform cross-validation annotations
- [ ] Create hierarchical layer mappings
- [ ] Generate statistics and coverage analysis

### Month 3: Validation
- [ ] Verify annotation consistency (inter-rater reliability)
- [ ] Test baseline systems on unified dataset
- [ ] Document failure patterns and edge cases
- [ ] Generate Phase 1 evaluation report

---

## REFERENCES

1. Zhu, K., et al. (2025). "Where LLM Agents Fail and How They Can Learn From Failures." arXiv:2509.25370

2. Just, R., et al. (2014). "Defects4J: a database of existing faults..." ISSTA 2014

3. Deng, Y., et al. (2021). "CodeXGLUE: A Machine Learning Benchmark Dataset for Code." arXiv:2102.04664

4. Vasallo, C., et al. (2019). "Every build you break: developer-oriented assistance..." Empirical Software Engineering

5. Shinn, N., et al. (2023). "Reflexion: Language Agents with Verbal Reinforcement Learning." NeurIPS 2023

6. OpenAI. "HumanEval: A human-evaluated dataset for code generation tasks"

7. Austin, J., et al. (2021). "Program Synthesis with Large Language Models." arXiv:2108.07732

8. He, S., et al. "Loghub: A large collection of system log datasets for AI-driven log analytics"

---

**Document Status**: Draft - Requires advisor review and dataset access validation

**Next Steps**:
1. Confirm dataset access and licensing
2. Verify infrastructure capacity for storage (500GB-1TB estimated)
3. Schedule dataset download and extraction
4. Assign annotation team for consistency verification
