# Query Model

Query the LLM directly for custom requests.

## Syntax
```bash
/query-model <prompt> [--model=MODEL] [--temperature=TEMP] [--max-tokens=N]
```

## Arguments
- `prompt`: Question or prompt (required)
- `model`: Model to use (default: o3-mini)
- `temperature`: Creativity level 0-2 (default: 0.7)
- `max-tokens`: Max response tokens (default: 2048)

## Example
```bash
/query-model "What are the best practices for transformers?" --model=gpt-4o --temperature=0.5
```

## Available Models
See `/set-model` for full list of supported models.

## Temperature Guide
- `0.0` - Deterministic, best for factual questions
- `0.5` - Balanced, good for most tasks
- `0.7` - Default, creative but consistent
- `1.0` - More random variations
- `2.0` - Maximum creativity (may be incoherent)

## Python API
```python
from inference import query_model

response = query_model(
    prompt="Your question here",
    model="gpt-4o",
    temperature=0.5,
    max_tokens=2048,
    api_key="your-key"
)
print(response)
```
