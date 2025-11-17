# Set Model

Change the LLM model backbone for agents.

## Syntax
```bash
/set-model <model-name> [--phase=PHASE]
```

## Arguments
- `model-name`: Model identifier (required)
- `--phase`: Apply to specific phase (optional)

## Supported Models
### OpenAI
- `gpt-4o` - GPT-4 Omni
- `o3-mini` - O3 Mini reasoning model
- `o1-mini` - O1 Mini reasoning
- `o1-preview` - O1 Preview reasoning
- `o1` - O1 full reasoning

### DeepSeek
- `deepseek-chat` - DeepSeek V3

### Anthropic
- `claude-3-opus` - Claude 3 Opus
- `claude-3-sonnet` - Claude 3 Sonnet

### Google
- `gemini-pro` - Gemini Pro

## Example
```bash
/set-model gpt-4o
/set-model o3-mini --phase=report writing
```

## Phase-Specific Models
Set different models for each phase:
```bash
/set-model o1-mini --phase=plan formulation
/set-model gpt-4o --phase=report writing
/set-model deepseek-chat --phase=running experiments
```

## Python API
```python
from ai_lab_repo import LaboratoryWorkflow

lab = LaboratoryWorkflow(
    research_topic="topic here",
    openai_api_key="your-key",
    agent_model_backbone="gpt-4o"
)

# Change model mid-workflow
lab.set_model("o3-mini")

# Phase-specific models
lab.model_backbone = {
    "literature review": "gpt-4o",
    "plan formulation": "o1-mini",
    "report writing": "gpt-4o"
}
```
