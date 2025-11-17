# Agent Laboratory - System Architecture Analysis

## Research Context: Building Better Agentic Systems

This document analyzes the current Agent Laboratory architecture from the perspective of your research interests:

1. **Memory Organization in Multi-Agent Systems**
2. **CI/CD of Failure Logs and Recovery Mechanisms**
3. **Autonomous Execution in Claude Code Web**
4. **Submodule Architecture for Agent Deployment**

---

## Part 1: Current Architecture Overview

### System Topology

```
┌─────────────────────────────────────────────────────────────┐
│                   LaboratoryWorkflow                        │
│                   (Orchestrator)                            │
└────────┬────────────────────────────────────┬───────────────┘
         │                                    │
         ▼                                    ▼
┌──────────────────────┐         ┌──────────────────────┐
│   7 Agent Roles      │         │  4 Tool Systems      │
├──────────────────────┤         ├──────────────────────┤
│ PhDStudentAgent      │         │ ArxivSearch          │
│ PostdocAgent         │         │ HFDataSearch         │
│ MLEngineerAgent      │         │ execute_code()       │
│ SWEngineerAgent      │         │ query_model()        │
│ ProfessorAgent       │         └──────────────────────┘
│ ReviewersAgent(x3)   │
└──────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│           7-Phase Research Workflow                         │
├─────────────────────────────────────────────────────────────┤
│ 1. Literature Review  → arXiv search & paper analysis       │
│ 2. Plan Formulation   → experimental design dialogue        │
│ 3. Data Preparation   → dataset code generation             │
│ 4. Running Experiments→ ML code execution & optimization    │
│ 5. Results Interp.    → findings analysis                   │
│ 6. Report Writing     → LaTeX paper generation              │
│ 7. Report Refinement  → peer review simulation              │
└─────────────────────────────────────────────────────────────┘
```

---

## Part 2: Memory Organization in Current System

### Current Memory Model

The system uses **conversation history** as its primary memory mechanism:

```python
# In agents.py - BaseAgent class
class BaseAgent:
    def __init__(self):
        self.conversation_history = []  # List of messages
        self.phase_history = {}         # Per-phase state
        self.state = {}                 # Agent-specific state
```

### Information Flow

```
┌─────────────────────────────────────────────────────────────┐
│              PHASE EXECUTION                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Agent receives: research_topic + current_phase         │
│  2. Constructs: prompt = topic + phase_context + history   │
│  3. Queries: LLM with full context                         │
│  4. Parses: LLM response → structured output               │
│  5. Updates: conversation_history.append(response)         │
│  6. Extracts: Next action → ADD_PAPER, SUMMARY, etc.      │
│  7. Validates: SW Engineer checks code quality             │
│  8. Saves: state_saves/{phase}.pkl                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Current State Management

```
state_saves/
├── literature_review.pkl      # Papers collected, LLM state
├── plan_formulation.pkl       # Research plan, dialogue history
├── data_preparation.pkl       # Data code, validation results
├── running_experiments.pkl    # Experiment code, results
├── results_interpretation.pkl # Analysis, key findings
├── report_writing.pkl         # LaTeX draft, optimization state
└── report_refinement.pkl      # Reviews, decision logic
```

### Limitations of Current Memory

| Aspect | Current | Issue |
|--------|---------|-------|
| **Memory Type** | Conversation history | Token-expensive, duplicates context |
| **Locality** | In-memory per phase | Lost between phases without pickle |
| **Accessibility** | Agent class only | Not queryable by other agents |
| **Structure** | Flat conversation list | No semantic indexing |
| **Persistence** | Pickle files | Binary, not debuggable |

---

## Part 3: Autonomous Claude Code Web Architecture

### How It Currently Works

```
USER (Claude Pro Web)
    │
    ├─ Calls: /perform-research "topic" --model=gpt-4o
    │
    ▼
.claude/commands/perform-research.md
    │
    ├─ Parsed as: Python API call
    │
    ▼
LaboratoryWorkflow.perform_research()
    │
    ├─ Phase 1: literature_review()
    │   ├─ Creates: ArxivSearch instance
    │   ├─ Queries: arXiv API for papers
    │   ├─ Parses: Paper summaries
    │   └─ Loop: Until papers collected
    │
    ├─ Phase 2: plan_formulation()
    │   ├─ PhD & Postdoc dialogue
    │   ├─ Iterative refinement
    │   └─ Save checkpoint
    │
    ├─ ... (phases 3-7)
    │
    └─ Output: Generated in lab_dir/
```

### Autonomous Execution Flow

```
┌─────────────────────────────────────┐
│ Claude Pro Web Session              │
├─────────────────────────────────────┤
│                                     │
│ /perform-research "topic"           │
│          │                          │
│          ▼                          │
│ LaboratoryWorkflow.perform_research()
│          │                          │
│      ┌───┴───┬───────┬────┬──────┐ │
│      ▼       ▼       ▼    ▼      ▼ │
│    Phase1  Phase2  Phase3 ... Phase7
│      │       │       │    │      │ │
│      └───────┴───────┴────┴──────┘ │
│              │                     │
│              ▼                     │
│        save_state(phase)           │
│              │                     │
│              ▼                     │
│        state_saves/{}.pkl          │
│              │                     │
│              ▼                     │
│        return output               │
│              │                     │
│              ▼                     │
│        User views results          │
│                                     │
│ SESSION TIMEOUT → Checkpoint saved  │
│ RESUME SESSION → Load checkpoint    │
└─────────────────────────────────────┘
```

### Autonomy Level: Current vs. Potential

| Feature | Current | Needed for Full Autonomy |
|---------|---------|--------------------------|
| **Scheduling** | Manual trigger | Cron/scheduler integration |
| **Error Handling** | Basic try/catch | Intelligent retry with backoff |
| **Decision Making** | Predefined phases | Adaptive phase selection |
| **Resource Management** | No monitoring | GPU/CPU/token budget tracking |
| **Self-Healing** | None | Auto-recovery from failures |
| **Monitoring** | Console logs | Structured telemetry |

---

## Part 4: Failure Logging and CI/CD

### Current Logging

```python
# Minimal logging infrastructure
if self.verbose:
    print(f"Beginning phase: {phase}")

# No structured logging
# No error tracking
# No analytics pipeline
```

### What's Missing

```
CURRENT STATE:
├── Logs: Console output only
├── Format: Unstructured print() statements
├── Persistence: Lost after session
├── Analysis: Manual inspection
└── Traceability: No correlation IDs

NEEDED FOR CI/CD:
├── Logs: Structured JSON/JSONL format
├── Format: Timestamp, level, context, span IDs
├── Persistence: S3/database with indexing
├── Analysis: Automated pattern detection
├── Traceability: Correlated request/session IDs
├── Metrics: Costs, latencies, success rates
├── Alerts: Threshold violations
└── Dashboards: Real-time monitoring
```

### Proposed Failure Tracking Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Agent Execution                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  try:                                                       │
│    Agent.inference(...)                                     │
│  except APIError as e:                                      │
│    Log: {                                                   │
│      "timestamp": "2025-11-17T19:30:00Z",                  │
│      "session_id": "abc123",                                │
│      "phase": "plan_formulation",                           │
│      "agent": "PostdocAgent",                               │
│      "error_type": "APIError",                              │
│      "error_message": "Rate limit exceeded",                │
│      "retry_count": 2,                                      │
│      "recovery_action": "exponential_backoff",              │
│      "tokens_used": 4532,                                   │
│      "estimated_cost": 0.45                                 │
│    }                                                        │
│    Retry with backoff                                       │
│    Or fallback to cheaper model                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Part 5: Submodule Architecture for Deployment

### Current Monolithic Structure

```
AgentLaboratory_claude/
├── agents.py                    # All 7 agents in one file
├── ai_lab_repo.py              # Orchestrator + workflow
├── tools.py                    # All tools mixed
├── inference.py                # LLM interface
├── mlesolver.py                # ML optimization
├── papersolver.py              # Paper generation
└── ...
```

### Proposed Microservice Architecture

```
agent-laboratory/                    # Monorepo root
├── .github/
│   ├── workflows/
│   │   ├── ci-agents.yml           # Test agents
│   │   ├── ci-tools.yml            # Test tools
│   │   ├── ci-inference.yml        # Test LLM interface
│   │   └── cd-deploy.yml           # Deploy services
│   └── actions/
│       ├── test-agent/
│       ├── lint-code/
│       └── build-service/
│
├── agents/                          # SUBMODULE 1
│   ├── git submodule config
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── phd_student_agent.py
│   │   ├── postdoc_agent.py
│   │   ├── ml_engineer_agent.py
│   │   ├── sw_engineer_agent.py
│   │   ├── professor_agent.py
│   │   └── reviewers_agent.py
│   ├── tests/
│   ├── requirements.txt
│   ├── setup.py
│   └── .github/workflows/test.yml
│
├── tools/                           # SUBMODULE 2
│   ├── git submodule config
│   ├── tools/
│   │   ├── arxiv_search.py
│   │   ├── hf_dataset_search.py
│   │   ├── code_executor.py
│   │   └── llm_query.py
│   ├── tests/
│   ├── requirements.txt
│   └── .github/workflows/test.yml
│
├── inference/                       # SUBMODULE 3
│   ├── git submodule config
│   ├── inference/
│   │   ├── llm_interface.py
│   │   ├── openai_backend.py
│   │   ├── anthropic_backend.py
│   │   ├── deepseek_backend.py
│   │   └── cost_tracker.py
│   ├── tests/
│   ├── requirements.txt
│   └── setup.py
│
├── orchestrator/                    # SUBMODULE 4
│   ├── git submodule config
│   ├── orchestrator/
│   │   ├── workflow.py
│   │   ├── phase_manager.py
│   │   ├── state_manager.py
│   │   └── checkpoint.py
│   ├── tests/
│   └── requirements.txt
│
├── solvers/                         # SUBMODULE 5
│   ├── ml_solver/
│   ├── paper_solver/
│   └── tests/
│
├── docker/
│   ├── Dockerfile.agents
│   ├── Dockerfile.orchestrator
│   ├── Dockerfile.api
│   └── docker-compose.yml
│
├── deployment/
│   ├── k8s/
│   │   ├── agents-deployment.yaml
│   │   ├── orchestrator-deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   ├── helm/
│   │   └── agent-lab/
│   └── terraform/
│       └── main.tf
│
├── api/                             # SUBMODULE 6
│   ├── fastapi app
│   ├── endpoints for each phase
│   ├── OpenAPI schema
│   └── tests/
│
├── memory/                          # SUBMODULE 7 (NEW)
│   ├── memory_store.py
│   ├── vector_db_adapter.py
│   ├── cache_layer.py
│   └── persistence.py
│
└── monitoring/                      # SUBMODULE 8 (NEW)
    ├── logging_system.py
    ├── metrics_collector.py
    ├── alert_manager.py
    └── dashboard_config.py
```

### Git Submodule Setup

```bash
# Initialize monorepo with submodules
git submodule add https://github.com/org/agent-agents agents/
git submodule add https://github.com/org/agent-tools tools/
git submodule add https://github.com/org/agent-inference inference/
git submodule add https://github.com/org/agent-orchestrator orchestrator/

# Update submodules
git submodule update --remote

# Deploy agents independently
cd agents/
pip install -e .
python -m agents.agents
```

---

## Part 6: Enhanced Memory System Design

### Proposed Multi-Tier Memory Architecture

```
┌────────────────────────────────────────────────────┐
│           AGENT MEMORY HIERARCHY                  │
├────────────────────────────────────────────────────┤
│                                                   │
│  LAYER 1: Context Window (In-Memory)              │
│  ├─ Last N messages                               │
│  ├─ Current phase context                         │
│  ├─ Relevant papers/data                          │
│  └─ Token budget: ~4000 tokens                     │
│                                                   │
│  LAYER 2: Working Memory (Phase State)             │
│  ├─ Phase-specific findings                       │
│  ├─ Intermediate results                          │
│  ├─ Experiment metrics                            │
│  └─ Persistence: Pickle/JSON during phase         │
│                                                   │
│  LAYER 3: Long-Term Memory (Semantic Index)        │
│  ├─ Vector embeddings of key findings             │
│  ├─ Paper summaries & citations                   │
│  ├─ Code snippets & results                       │
│  └─ Storage: Vector DB (Pinecone/Weaviate)        │
│                                                   │
│  LAYER 4: Archive Memory (Full History)            │
│  ├─ Complete conversation logs                    │
│  ├─ All generated artifacts                       │
│  ├─ Failure logs & recovery info                  │
│  └─ Storage: S3 + PostgreSQL index                │
│                                                   │
│  LAYER 5: Meta-Memory (Learning)                   │
│  ├─ Success patterns                              │
│  ├─ Common failure modes                          │
│  ├─ Optimization strategies                       │
│  └─ Storage: ML model parameters                  │
│                                                   │
└────────────────────────────────────────────────────┘
```

### Memory Query Examples

```python
# Retrieve relevant papers for current research
papers = memory.semantic_search(
    query="attention mechanisms efficiency",
    limit=5,
    similarity_threshold=0.8
)

# Find similar experiments from history
similar = memory.find_similar_experiments(
    current_plan=plan,
    limit=3
)

# Get recovery strategy for common errors
strategy = memory.lookup_recovery_pattern(
    error_type="APIError",
    model="gpt-4o",
    phase="running_experiments"
)
```

---

## Part 7: Autonomous Claude Code Web Execution

### Phase 1: Session Setup (Automatic)

```python
# .claude/hooks/session-start.sh (Optional)
#!/bin/bash

# 1. Verify environment
echo "Checking environment..."
test -n "$OPENAI_API_KEY" || echo "ERROR: OPENAI_API_KEY not set"

# 2. Load previous checkpoint if exists
if [ -f "state_saves/session.pkl" ]; then
    echo "Resuming from checkpoint..."
    export RESUME_SESSION=true
fi

# 3. Initialize logging
mkdir -p logs
export LOG_FILE="logs/session_$(date +%s).log"

# 4. Start monitoring
python monitoring/health_check.py &
```

### Phase 2: Autonomous Execution (Claude Code)

```
Session 1 (User starts):
├─ /perform-research "topic"
├─ Runs through Phase 1-2
├─ Session timeout → Auto-saves state
└─ Returns: Partial results to user

Session 2 (User resumes):
├─ Claude reads checkpoint
├─ Resumes at Phase 3
├─ Continues autonomously
└─ Returns: Complete results

Background (No user interaction):
├─ Monitoring checks phase status
├─ Retries on transient failures
├─ Escalates to fallback models on errors
├─ Updates metrics/logs continuously
└─ Notifies on completion or blockers
```

### Phase 3: Failure Recovery (Intelligent)

```python
class AutonomousExecutor:
    def execute_phase_with_recovery(self, phase):
        for attempt in range(max_retries):
            try:
                return self.execute_phase(phase)
            except RateLimitError:
                # Strategy 1: Backoff
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            except ContextWindowError:
                # Strategy 2: Compression
                self.compress_context()
                continue
            except TokenBudgetExceeded:
                # Strategy 3: Model switch
                self.switch_to_cheaper_model()
                continue
            except PermanentError as e:
                # Strategy 4: Checkpoint & escalate
                self.save_checkpoint()
                self.notify_user_intervention_needed(e)
                break
```

---

## Part 8: CI/CD Pipeline for Failure Logs

### Proposed GitHub Actions Workflow

```yaml
# .github/workflows/monitor-experiments.yml
name: Monitor Experiments

on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check experiment status
        run: |
          python monitoring/check_status.py \
            --since 5min \
            --output logs/status.json

      - name: Analyze failures
        run: |
          python monitoring/analyze_failures.py \
            --input logs/status.json \
            --output logs/analysis.json

      - name: Generate report
        run: |
          python monitoring/generate_report.py \
            --input logs/analysis.json \
            --output reports/latest.md

      - name: Upload metrics
        run: |
          aws s3 cp logs/status.json \
            s3://agent-lab-logs/$(date +%Y%m%d)/status.json

      - name: Create issues for critical failures
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const failures = JSON.parse(fs.readFileSync('logs/analysis.json'));

            for (const failure of failures.critical) {
              await github.rest.issues.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                title: `Critical Failure: ${failure.error_type}`,
                body: failure.summary,
                labels: ['critical', 'auto-generated']
              });
            }
```

---

## Part 9: Implementation Roadmap

### Phase 1: Structured Logging (1-2 weeks)

```
Goals:
  ✓ Replace print() with structured logging
  ✓ Add correlation IDs for tracing
  ✓ Implement retry logic with telemetry

Files to modify:
  - agents.py: Add logging to BaseAgent
  - ai_lab_repo.py: Log phase transitions
  - inference.py: Log API calls and costs
  - tools.py: Log search queries and results

New files:
  - logging_config.py
  - metrics.py
```

### Phase 2: Enhanced Memory System (2-3 weeks)

```
Goals:
  ✓ Implement semantic memory with embeddings
  ✓ Add vector DB integration
  ✓ Create memory query API

New modules:
  - memory/
    ├── semantic_memory.py
    ├── vector_store.py (Pinecone adapter)
    ├── cache.py
    └── persistence.py
```

### Phase 3: Submodule Architecture (3-4 weeks)

```
Goals:
  ✓ Extract agents into separate package
  ✓ Create tools package
  ✓ Package inference layer
  ✓ Set up CI/CD for each

New structure:
  agent-agents/ (submodule)
  agent-tools/ (submodule)
  agent-inference/ (submodule)
```

### Phase 4: Autonomous Execution (2-3 weeks)

```
Goals:
  ✓ Implement health checks
  ✓ Add failure detection
  ✓ Create recovery strategies

New files:
  - monitoring/health_check.py
  - orchestrator/resilience.py
  - .claude/hooks/
```

---

## Part 10: Key Learnings for Research

### Research Questions to Explore

1. **Memory Organization**
   - How much context window is optimal for agents?
   - What semantic chunking strategy works best?
   - How to prevent memory bloat in long-running agents?
   - What's the token cost of different memory architectures?

2. **Failure Resilience**
   - What are common failure modes in agentic systems?
   - How to detect failures automatically?
   - What recovery strategies are most effective?
   - How to prevent error cascades?

3. **Autonomous Operation**
   - How to make agents truly autonomous?
   - What monitoring is necessary?
   - How to handle long-running phases (>24 hours)?
   - How to optimize token budgets?

4. **Scalability**
   - How to run multiple agents in parallel?
   - What coordination mechanisms work best?
   - How to manage shared resources (API quotas)?
   - How to scale to thousands of concurrent workflows?

5. **Observability**
   - What metrics matter most?
   - How to detect agent "confusion"?
   - How to correlate failures across agents?
   - How to provide explainability for decisions?

### Metrics to Track

```python
# Key metrics for analysis
agent_metrics = {
    # Performance
    'phase_duration_seconds': [...],
    'tokens_per_phase': [...],
    'api_calls_per_phase': [...],
    'cost_per_phase': [...],

    # Quality
    'success_rate_by_phase': {...},
    'error_types': {...},
    'retry_attempts': [...],

    # Resource
    'context_window_utilization': [...],
    'memory_peak_mb': [...],
    'api_rate_limit_hits': [...],

    # Autonomy
    'human_interventions': [...],
    'auto_recovery_successes': [...],
    'fallback_model_switches': [...],
}
```

---

## Conclusion

The Agent Laboratory provides a solid foundation for researching agentic systems. The current architecture demonstrates:

✅ **What Works:**
- Multi-agent coordination through sequential phases
- Modular design with clear separation of concerns
- Checkpoint-based recovery mechanism
- Claude Code integration for automation

⚠️ **Areas for Research:**
- Memory organization at scale
- Intelligent failure detection and recovery
- True autonomous operation without human oversight
- Cost optimization for LLM calls
- Explainability of agent decisions

This analysis provides the blueprint for implementing these enhancements while maintaining backward compatibility with the existing system.

---

## References

- **Current Code**: See `agents.py`, `ai_lab_repo.py`, `tools.py`
- **Configuration**: See `CLAUDE.md` for system overview
- **Deployment**: See `SETUP.md` for running instructions
- **Commands**: See `.claude/commands/` for available operations
