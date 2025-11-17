# Claude Code Migration Guide

This document describes the migration of AgentLaboratory to a Claude Code-based architecture.

## Overview

The migration replaces the multi-model LLM backend (OpenAI, DeepSeek, Gemini) with a unified Claude-based system that leverages Claude's native tool-calling capabilities for research automation.

## New Architecture

### Core Components

```
claude_inference.py      - Anthropic Claude API client with cost tracking
claude_tools.py          - Tool definitions and executor for research tasks
claude_agents.py         - Agent system using Claude's native capabilities
claude_workflow.py       - Main research workflow orchestrator
claude_config.py         - Configuration management
run_claude_research.py   - CLI entry point
claude_native_runner.py  - Native mode runner (no API key needed)
claude_interactive.py    - Interactive research runner
.claude/commands/        - Slash commands for Claude Code
```

### Migration Mapping

| Original File | New File | Changes |
|--------------|----------|---------|
| `inference.py` | `claude_inference.py` | Single Claude backend instead of multi-model |
| `tools.py` | `claude_tools.py` | Tool definitions for Claude's tool-use API |
| `agents.py` | `claude_agents.py` | Simplified agents using native tool calling |
| `ai_lab_repo.py` | `claude_workflow.py` | Cleaner workflow orchestration |
| YAML configs | `claude_config.py` | Python dataclass configuration |

## Quick Start

### Option 1: Native Mode (Claude Pro - No API Key Required)

Run directly within Claude Code without needing an API key:

```bash
# Start a research workflow
python run_claude_research.py --topic "Few-shot learning in NLP" --no-api

# Check workflow status
python run_claude_research.py --topic "Few-shot learning" --no-api --status

# Reset and start over
python run_claude_research.py --topic "Few-shot learning" --no-api --reset

# Interactive mode
python claude_interactive.py --topic "Few-shot learning" --phase literature
```

Or use the slash command:
```
/research Few-shot learning in NLP
```

### Option 2: API Mode (Requires ANTHROPIC_API_KEY)

```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Basic usage
python run_claude_research.py --topic "Few-shot learning in NLP"

# With custom settings
python run_claude_research.py \
  --topic "Vision transformers for medical imaging" \
  --papers 10 \
  --experiments 5 \
  --output-dir ./medical_research

# Create configuration file
python run_claude_research.py --create-config my_config.json

# Run with human-in-the-loop
python run_claude_research.py --topic "RL for robotics" --human-in-loop
```

### 3. Programmatic usage

```python
from claude_workflow import run_research

result = run_research(
    topic="Novel approaches for few-shot learning",
    output_dir="./research_output",
    num_papers_lit_review=5,
    max_experiment_iterations=3,
    human_in_loop=False
)

print(f"Paper saved to: {result['report']}")
```

## Key Changes

### 1. Unified Model Backend

**Before:**
```python
# inference.py - Multiple models
query_model("o3-mini", prompt, system_prompt)
query_model("gpt-4o", prompt, system_prompt)
query_model("deepseek-chat", prompt, system_prompt)
```

**After:**
```python
# claude_inference.py - Single Claude backend
from claude_inference import query_claude
response = query_claude(prompt, system_prompt, model="claude-sonnet-4-5-20250929")
```

### 2. Native Tool Calling

**Before:**
```python
# Custom command parsing
if "```SUBMIT_CODE" in response:
    code = extract_code(response)
    execute(code)
```

**After:**
```python
# Claude's native tool use
response = client.query_with_tools(
    prompt=prompt,
    system_prompt=system_prompt,
    tools=[execute_python_tool, arxiv_search_tool]
)
# Tools are automatically invoked by Claude
```

### 3. Simplified Agent Architecture

**Before:**
```python
# agents.py - Complex command parsing
class BaseAgent:
    def inference(self, ...):
        # Parse DIALOGUE, PLAN, SUBMIT_CODE commands
        # Handle multi-model selection
        # Custom context management
```

**After:**
```python
# claude_agents.py - Clean tool-based agents
class ClaudeAgent:
    def inference(self, task, context, phase):
        # Direct Claude API with tools
        # Native tool execution
        # Automatic context management
```

### 4. Configuration

**Before (YAML):**
```yaml
research-topic: "..."
llm-backend: "o3-mini"
mlesolver-max-steps: 3
copilot-mode: True
```

**After (Python/JSON):**
```python
from claude_config import ResearchConfig

config = ResearchConfig(
    research_topic="...",
    model="claude-sonnet-4-5-20250929",
    max_experiment_iterations=3,
    human_in_loop=True
)
```

## Available Tools

The new system provides Claude with these tools:

| Tool | Description | Used By |
|------|-------------|---------|
| `arxiv_search` | Search arXiv for papers | PhD Student, ML Engineer, Postdoc |
| `arxiv_get_paper` | Get full paper text | PhD Student, ML Engineer, Postdoc |
| `huggingface_dataset_search` | Find datasets | ML Engineer |
| `execute_python` | Run Python code | ML Engineer, SW Engineer |
| `read_file` | Read file contents | All agents |
| `write_file` | Write files | Most agents |
| `edit_file` | Edit existing files | ML Engineer, SW Engineer, Professor |
| `bash_command` | Execute shell commands | ML Engineer, SW Engineer |
| `web_search` | Search the web | PhD Student, Postdoc |

## Cost Tracking

The new system automatically tracks API costs:

```python
from claude_inference import get_current_cost, get_token_stats

# Get current cost
cost = get_current_cost()
print(f"Total cost: ${cost:.6f}")

# Get detailed stats
stats = get_token_stats()
print(f"Input tokens: {stats['claude-sonnet-4-5-20250929']['input_tokens']}")
```

## Workflow Phases

The research workflow remains similar but uses Claude tools:

1. **Literature Review** - Claude uses `arxiv_search` and `arxiv_get_paper`
2. **Plan Formulation** - Multi-agent dialogue (no tools, pure reasoning)
3. **Experimentation** - Claude uses `execute_python`, `huggingface_dataset_search`
4. **Results & Writing** - Claude uses `write_file`, `edit_file` for LaTeX

## Checkpointing

State is automatically saved as JSON (not pickle):

```bash
research_output/
├── checkpoints/
│   ├── literature_review.json
│   ├── plan_formulation.json
│   ├── experimentation.json
│   └── final_paper.json
└── research_paper.tex
```

Resume from checkpoint:

```bash
python run_claude_research.py --resume ./research_output/checkpoints/experimentation.json
```

## Benefits of Migration

1. **Unified Backend** - Single API, simpler management
2. **Native Tool Use** - No custom parsing, Claude handles tool calls
3. **Better Context** - Claude maintains conversation context naturally
4. **Cost Visibility** - Real-time cost tracking from Anthropic API
5. **Cleaner Code** - Less boilerplate, more maintainable
6. **Sandboxed Execution** - Safer code execution via tool abstraction
7. **JSON State** - Human-readable checkpoints (no pickle)

## Migration Checklist

- [x] Replace inference.py with Claude API client
- [x] Create tool definitions for Claude
- [x] Redesign agent system for native tool use
- [x] Migrate workflow orchestration
- [x] Add configuration management
- [x] Create CLI entry point
- [ ] Port all experiments from old system
- [ ] Benchmark against original performance
- [ ] Add comprehensive tests
- [ ] Document all APIs

## Future Work

1. **MCP Integration** - Use Model Context Protocol for external tools
2. **Parallel Agents** - Run multiple agents concurrently
3. **Streaming** - Real-time output streaming
4. **Web UI** - Interactive dashboard for monitoring
5. **Git Integration** - Version control for research artifacts

## Backwards Compatibility

The new system includes a compatibility layer:

```python
# Old code still works
from claude_inference import query_model

# Routes to Claude automatically
response = query_model(
    model_str="o3-mini",  # Maps to claude-sonnet-4-5
    prompt=prompt,
    system_prompt=system_prompt
)
```

## Support

For issues with the migration:
1. Check ANTHROPIC_API_KEY is set correctly
2. Ensure Python 3.9+ is installed
3. Install dependencies: `pip install anthropic`
4. Review checkpoints for debugging

## License

Same as original AgentLaboratory (MIT License).
