# Execute Code

Safely execute Python code with timeout protection and sandboxing.

## Syntax
```bash
/execute-code <code-file> [--timeout=SECONDS] [--max-output=CHARS]
```

## Arguments
- `code-file`: Path to Python file or inline code (required)
- `--timeout`: Timeout in seconds (default: 600)
- `--max-output`: Max output characters (default: 1000)

## Example
```bash
/execute-code experiment.py --timeout=300
```

## Safety Features
- Automatic timeout protection (prevents infinite loops)
- Output truncation (prevents memory issues)
- Multiprocess sandboxing
- Error capturing and reporting
- Resource monitoring

## Python API
```python
from tools import execute_code

# Execute code string
result = execute_code(
    "print('Hello'); print([1,2,3])",
    timeout=60,
    MAX_LEN=1000
)
print(result)
```

## Returns
- `(return_code, output, error_message)`
- return_code: 0 for success, non-zero for errors
- output: Captured stdout (truncated if needed)
- error_message: Stderr or timeout message
