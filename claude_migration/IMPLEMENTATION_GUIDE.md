# Claude Migration Implementation Guide

## Overview

This implementation maintains **exact compatibility** with the original AgentLaboratory command-based system while using Claude's native capabilities. The migration preserves:

✅ Iterative agent-agent dialogue
✅ Command-based interactions (```COMMAND\ncontent\n```)
✅ Tool execution during dialogue
✅ Human-in-the-loop checkpoints
✅ Phase-based workflow progression
✅ Original prompt structures

## Architecture

### Core Components

```
claude_migration/
├── claude_commands.py              # Command parser & instruction builders
├── claude_agents.py                # Enhanced agents with command support
├── claude_dialogue.py              # Dialogue loop engine
├── claude_research_tools.py        # Tool executors (code, search, etc.)
├── claude_human_loop.py            # Human checkpoint system
├── claude_workflow_orchestrator.py # Main workflow class
└── example_workflow.py             # Usage examples
```

## Key Features

### 1. Command Parser System

Extracts commands from agent responses:

```python
from claude_commands import CommandParser

response = """
Let me search for papers.
```SUMMARY
transformer time series
```
"""

cmd_type, content = CommandParser.extract_command(response)
# cmd_type = "search_papers"
# content = "transformer time series"
```

### 2. Command-Based Agent Inference

Agents respond with structured commands:

```python
agent = PhDStudentAgent(api_key=api_key)

response, cmd_type, cmd_content = agent.inference_with_commands(
    task="Find papers on transformers",
    context=state,
    phase="literature review",
    feedback="",
    step=0
)

if cmd_type == "search_papers":
    # Execute paper search
    papers = search_arxiv(cmd_content)
```

### 3. Dialogue Loop

Agents alternate turns until submission:

```python
from claude_dialogue import DialogueLoop

loop = DialogueLoop(
    agent1=postdoc,
    agent2=phd,
    topic="Create research plan",
    context=state,
    phase="plan formulation",
    max_turns=100
)

result = loop.run_until_submission(
    submission_commands=["submit_plan"],
    agent1_commands=["DIALOGUE", "PLAN"],
    agent2_commands=["DIALOGUE"]
)

plan = result["submission_content"]
```

### 4. Tool-Augmented Dialogue

Agents can execute tools during dialogue:

```python
from claude_dialogue import ToolAugmentedDialogue

tool_executors = {
    "execute_code": ResearchTools.execute_python_code,
    "search_datasets": ResearchTools.search_huggingface_datasets
}

loop = ToolAugmentedDialogue(
    agent1=sw_engineer,
    agent2=ml_engineer,
    topic="Prepare dataset",
    context=state,
    phase="data preparation",
    tool_executors=tool_executors
)

result = loop.run_with_tools(
    submission_commands=["submit_code"],
    agent1_commands=["DIALOGUE", "SUBMIT_CODE"],
    agent2_commands=["DIALOGUE", "python", "SEARCH_HF"]
)
```

### 5. Human-in-Loop Checkpoints

Review and approve phase outputs:

```python
from claude_human_loop import HumanCheckpoint

human_loop = HumanCheckpoint({
    "literature review": True,
    "plan formulation": True,
    "data preparation": False
})

should_retry, feedback = human_loop.check(
    phase="literature review",
    output=lit_review_summary
)

if should_retry:
    # User rejected - retry with feedback
    notes_manager.add_note(["literature review"], feedback)
    run_phase_literature_review()  # Retry
```

## Workflow Phases

### Phase 1: Literature Review

**Agents:** PhD Student (solo)

**Commands:**
- `SUMMARY` → Search papers
- `FULL_TEXT` → Get paper details
- `ADD_PAPER` → Add to review

**Pattern:**
```
PhD → SUMMARY → Tool executes → Feedback
PhD → FULL_TEXT → Tool executes → Feedback
PhD → ADD_PAPER → Store paper
[Repeat until N papers collected]
```

### Phase 2: Plan Formulation

**Agents:** Postdoc ↔ PhD Student

**Commands:**
- `DIALOGUE` → Continue discussion
- `PLAN` → Submit plan (ends phase)

**Pattern:**
```
Postdoc → DIALOGUE → PhD
PhD → DIALOGUE → Postdoc
Postdoc → PLAN → END
```

### Phase 3: Data Preparation

**Agents:** SW Engineer ↔ ML Engineer

**Commands:**
- `DIALOGUE` → Discuss
- `python` → Execute code
- `SEARCH_HF` → Search datasets
- `SUBMIT_CODE` → Submit final code

**Pattern:**
```
SW Engineer → DIALOGUE → ML Engineer
ML Engineer → python → Tool executes → Feedback
ML Engineer → SEARCH_HF → Tool executes → Feedback
ML Engineer → DIALOGUE → SW Engineer
SW Engineer → SUBMIT_CODE → END
```

### Phase 4: Running Experiments

**Tool:** MLESolver (existing system)

Uses original implementation for experiment optimization.

### Phase 5: Results Interpretation

**Agents:** Postdoc ↔ PhD Student

**Commands:**
- `DIALOGUE` → Discuss results
- `INTERPRETATION` → Submit interpretation

### Phase 6: Report Writing

**Tool:** PaperSolver (existing system)

Uses original implementation for LaTeX paper generation.

## Usage Examples

### Basic Usage

```python
from claude_workflow_orchestrator import AgentLabWorkflow

workflow = AgentLabWorkflow(
    research_topic="Using transformers for time series",
    output_dir="./output",
    api_key=your_api_key,
    max_steps=100,
    num_papers_lit_review=5
)

workflow.run_all_phases()
```

### With Human Checkpoints

```python
from claude_human_loop import HumanCheckpoint

human_config = HumanCheckpoint.get_default_config(human_mode=True)

workflow = AgentLabWorkflow(
    research_topic="Self-supervised learning",
    human_checkpoints=human_config,
    api_key=your_api_key
)

workflow.run_all_phases()
```

### With Agent Notes

```python
notes = [
    {
        "phases": ["literature review"],
        "note": "Focus on papers from 2023-2024"
    }
]

workflow = AgentLabWorkflow(
    research_topic="Graph neural networks",
    notes=notes,
    api_key=your_api_key
)

workflow.run_all_phases()
```

### Run Single Phase

```python
workflow = AgentLabWorkflow(
    research_topic="Molecular property prediction",
    api_key=your_api_key
)

# Run only literature review
workflow.run_phase_literature_review()

print(workflow.state["lit_review_sum"])
```

## Command Instructions

All command instructions are defined in `claude_commands.py` using the exact strings from the original `agents.py`. This ensures agents receive identical instructions to the original system.

### Example: Plan Formulation Instructions

**Postdoc:**
```
You can produce dialogue using: ```DIALOGUE
dialogue here
```

When you believe a good plan has been reached, submit: ```PLAN
plan here
```

Use ONE command per turn.
```

**PhD Student:**
```
You can produce dialogue using: ```DIALOGUE
dialogue here
```

Use ONE command per turn.
```

## Differences from Original

### Maintained:
- ✅ Exact command format
- ✅ Dialogue patterns
- ✅ Tool execution
- ✅ Human checkpoints
- ✅ Phase progression
- ✅ Original prompts

### Changed:
- 🔄 Uses Claude API instead of OpenAI
- 🔄 Tool integration via executors (not direct bash)
- 🔄 State stored in dict (not agent attributes)
- 🔄 Cleaner separation of concerns

### Not Yet Implemented:
- ⏳ Running experiments (MLESolver integration)
- ⏳ Report writing (PaperSolver integration)
- ⏳ Report refinement (reviewer feedback loop)
- ⏳ Full arXiv/HuggingFace tool integration

## Testing

Run example workflows:

```bash
# Basic automated workflow
python example_workflow.py basic

# With human oversight
python example_workflow.py human

# With agent notes
python example_workflow.py notes

# Single phase only
python example_workflow.py single
```

## Next Steps

To complete the migration:

1. **Integrate MLESolver** for running experiments phase
2. **Integrate PaperSolver** for report writing phase
3. **Add ReviewersAgent** for report refinement
4. **Implement real arXiv/HF tools** (currently placeholders)
5. **Add state persistence** (save/load workflow state)
6. **Add cost tracking** (from original system)

## API Key Setup

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

Or pass directly:
```python
workflow = AgentLabWorkflow(
    research_topic="...",
    api_key="your-key-here"
)
```

## Troubleshooting

**"Max turns reached"**: Increase `max_steps` parameter

**"Command not recognized"**: Check command format has exactly three backticks

**"Tool execution failed"**: Check tool executor implementation

**Human checkpoint not triggering**: Verify phase name in `human_checkpoints` dict

## File Outputs

```
output_dir/
├── src/
│   ├── load_data.py          # Data preparation code
│   ├── run_experiments.py    # Experiment code
│   └── experiment_output.log # Results
├── readme.md                  # Generated README
└── report.txt                 # Final report
```

## Contributing

When adding new phases:

1. Define command instructions in `CommandInstructionBuilder`
2. Create dialogue loop or tool-augmented dialogue
3. Add human checkpoint
4. Integrate into `AgentLabWorkflow`
5. Test with example script

## License

Same as original AgentLaboratory.
