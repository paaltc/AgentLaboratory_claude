# Save Checkpoint

Save workflow state and progress for recovery.

## Syntax
```bash
/save-checkpoint <phase> [--name=CHECKPOINT_NAME]
```

## Arguments
- `phase`: Current workflow phase (required)
- `--name`: Custom checkpoint name (optional)

## Available Phases
- `literature review`
- `plan formulation`
- `data preparation`
- `running experiments`
- `results interpretation`
- `report writing`
- `report refinement`

## Example
```bash
/save-checkpoint "running experiments"
/save-checkpoint "report writing" --name=before_revision
```

## Checkpoint Contents
Saves automatically:
- Agent state and history
- Generated documents
- Code files
- Experiment results
- Configuration settings
- Progress tracking

## Recovery
Load from checkpoint:
```bash
python ai_lab_repo.py --yaml-location config.yaml --load-checkpoint
```

## Storage
Checkpoints saved to `state_saves/` directory:
- `state_saves/literature_review.pkl`
- `state_saves/plan_formulation.pkl`
- `state_saves/running_experiments.pkl`
- etc.

## Python API
```python
from ai_lab_repo import LaboratoryWorkflow

lab = LaboratoryWorkflow(
    research_topic="topic here",
    openai_api_key="your-key"
)

# Automatic saving on phase completion
lab.save = True

# Manual checkpoint
lab.save_state("running experiments")
```
