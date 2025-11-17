"""
Claude Code Migration - Tool Integration Layer
Provides Claude-native tool definitions for research workflows
"""
import os
import json
import subprocess
import tempfile
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path


# Tool definitions for Claude's tool-use API
RESEARCH_TOOLS = [
    {
        "name": "arxiv_search",
        "description": "Search arXiv for academic papers on a given topic. Returns paper titles, abstracts, and IDs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for arXiv papers (max 300 chars)"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of papers to return (default: 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "arxiv_get_paper",
        "description": "Retrieve full text content of an arXiv paper by its ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "paper_id": {
                    "type": "string",
                    "description": "arXiv paper ID (e.g., '2301.00123')"
                }
            },
            "required": ["paper_id"]
        }
    },
    {
        "name": "huggingface_dataset_search",
        "description": "Search Hugging Face for datasets relevant to a machine learning task.",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "Description of the desired dataset"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of datasets to return (default: 5)",
                    "default": 5
                }
            },
            "required": ["description"]
        }
    },
    {
        "name": "execute_python",
        "description": "Execute Python code in a sandboxed environment. Returns stdout, stderr, and exit code.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 120, max: 600)",
                    "default": 120
                },
                "working_dir": {
                    "type": "string",
                    "description": "Working directory for code execution (optional)"
                }
            },
            "required": ["code"]
        }
    },
    {
        "name": "read_file",
        "description": "Read contents of a file from the filesystem.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute path to the file to read"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file, creating or overwriting as needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute path to the file to write"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                }
            },
            "required": ["file_path", "content"]
        }
    },
    {
        "name": "edit_file",
        "description": "Edit a file by replacing a specific string with new content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute path to the file to edit"
                },
                "old_string": {
                    "type": "string",
                    "description": "The text to replace"
                },
                "new_string": {
                    "type": "string",
                    "description": "The replacement text"
                }
            },
            "required": ["file_path", "old_string", "new_string"]
        }
    },
    {
        "name": "web_search",
        "description": "Search the web for information on a topic. Returns relevant results.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "bash_command",
        "description": "Execute a bash command in the shell.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 120)",
                    "default": 120
                }
            },
            "required": ["command"]
        }
    }
]


class ToolExecutor:
    """Executes tools on behalf of Claude agents."""

    def __init__(self, working_dir: Optional[str] = None):
        """Initialize tool executor with optional working directory."""
        self.working_dir = working_dir or os.getcwd()

    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Execute a tool and return results.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            String result from tool execution
        """
        tool_map = {
            "arxiv_search": self._arxiv_search,
            "arxiv_get_paper": self._arxiv_get_paper,
            "huggingface_dataset_search": self._hf_dataset_search,
            "execute_python": self._execute_python,
            "read_file": self._read_file,
            "write_file": self._write_file,
            "edit_file": self._edit_file,
            "web_search": self._web_search,
            "bash_command": self._bash_command,
        }

        if tool_name not in tool_map:
            return f"Error: Unknown tool '{tool_name}'"

        try:
            return tool_map[tool_name](**tool_input)
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"

    def _arxiv_search(self, query: str, max_results: int = 5) -> str:
        """Search arXiv for papers."""
        import arxiv

        # Truncate query if too long
        if len(query) > 300:
            query = query[:300]

        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )

            results = []
            for paper in search.results():
                results.append({
                    "id": paper.entry_id.split("/")[-1],
                    "title": paper.title,
                    "abstract": paper.summary[:500] + "..." if len(paper.summary) > 500 else paper.summary,
                    "authors": [str(a) for a in paper.authors[:5]],
                    "published": str(paper.published.date()),
                    "pdf_url": paper.pdf_url
                })

            return json.dumps(results, indent=2)
        except Exception as e:
            return f"ArXiv search error: {str(e)}"

    def _arxiv_get_paper(self, paper_id: str) -> str:
        """Get full text of an arXiv paper."""
        import arxiv
        from PyPDF2 import PdfReader
        import io

        try:
            # Search for the specific paper
            search = arxiv.Search(id_list=[paper_id])
            paper = next(search.results())

            # Download PDF
            pdf_url = paper.pdf_url
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()

            # Extract text from PDF
            pdf_file = io.BytesIO(response.content)
            reader = PdfReader(pdf_file)

            text_parts = []
            for page_num, page in enumerate(reader.pages[:20]):  # Limit to first 20 pages
                text = page.extract_text()
                if text:
                    text_parts.append(f"--- Page {page_num + 1} ---\n{text}")

            full_text = "\n\n".join(text_parts)

            # Truncate if too long
            if len(full_text) > 50000:
                full_text = full_text[:50000] + "\n\n[Text truncated at 50000 characters]"

            return json.dumps({
                "paper_id": paper_id,
                "title": paper.title,
                "text": full_text
            }, indent=2)
        except Exception as e:
            return f"Error retrieving paper {paper_id}: {str(e)}"

    def _hf_dataset_search(self, description: str, max_results: int = 5) -> str:
        """Search Hugging Face for datasets."""
        from huggingface_hub import HfApi

        try:
            api = HfApi()

            # Search datasets
            datasets = api.list_datasets(
                search=description,
                sort="downloads",
                direction=-1,
                limit=max_results
            )

            results = []
            for ds in datasets:
                results.append({
                    "id": ds.id,
                    "downloads": getattr(ds, "downloads", 0),
                    "likes": getattr(ds, "likes", 0),
                    "tags": getattr(ds, "tags", [])[:10],
                })

            return json.dumps(results, indent=2)
        except Exception as e:
            return f"HuggingFace search error: {str(e)}"

    def _execute_python(
        self,
        code: str,
        timeout: int = 120,
        working_dir: Optional[str] = None
    ) -> str:
        """Execute Python code in a subprocess."""
        if timeout > 600:
            timeout = 600

        work_dir = working_dir or self.working_dir

        # Create temporary file for the code
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            dir=work_dir,
            delete=False
        ) as f:
            f.write(code)
            temp_file = f.name

        try:
            result = subprocess.run(
                ["python", temp_file],
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return json.dumps({
                "exit_code": result.returncode,
                "stdout": result.stdout[:10000] if len(result.stdout) > 10000 else result.stdout,
                "stderr": result.stderr[:5000] if len(result.stderr) > 5000 else result.stderr
            }, indent=2)
        except subprocess.TimeoutExpired:
            return json.dumps({
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout} seconds"
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e)
            }, indent=2)
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except Exception:
                pass

    def _read_file(self, file_path: str) -> str:
        """Read contents of a file."""
        try:
            path = Path(file_path)
            if not path.exists():
                return f"Error: File not found: {file_path}"

            if not path.is_file():
                return f"Error: Path is not a file: {file_path}"

            # Check file size
            if path.stat().st_size > 10_000_000:  # 10MB limit
                return f"Error: File too large (>10MB): {file_path}"

            content = path.read_text(encoding="utf-8", errors="ignore")

            # Truncate if too long
            if len(content) > 100000:
                content = content[:100000] + "\n\n[Content truncated at 100000 characters]"

            return content
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def _write_file(self, file_path: str, content: str) -> str:
        """Write content to a file."""
        try:
            path = Path(file_path)

            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)

            path.write_text(content, encoding="utf-8")
            return f"Successfully wrote {len(content)} characters to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    def _edit_file(self, file_path: str, old_string: str, new_string: str) -> str:
        """Edit a file by replacing a string."""
        try:
            path = Path(file_path)
            if not path.exists():
                return f"Error: File not found: {file_path}"

            content = path.read_text(encoding="utf-8")

            if old_string not in content:
                return f"Error: String not found in file: {old_string[:100]}..."

            # Count occurrences
            count = content.count(old_string)
            if count > 1:
                return f"Error: String found {count} times. Make it unique or use replace_all."

            new_content = content.replace(old_string, new_string, 1)
            path.write_text(new_content, encoding="utf-8")

            return f"Successfully replaced string in {file_path}"
        except Exception as e:
            return f"Error editing file: {str(e)}"

    def _web_search(self, query: str) -> str:
        """
        Perform a web search (placeholder - would integrate with actual search API).
        In a full implementation, this would call a search API.
        """
        # This is a placeholder. In production, integrate with:
        # - DuckDuckGo API
        # - Serper API
        # - Google Custom Search API
        return json.dumps({
            "note": "Web search integration pending. Use arxiv_search for academic papers.",
            "query": query,
            "results": []
        }, indent=2)

    def _bash_command(self, command: str, timeout: int = 120) -> str:
        """Execute a bash command."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return json.dumps({
                "exit_code": result.returncode,
                "stdout": result.stdout[:10000] if len(result.stdout) > 10000 else result.stdout,
                "stderr": result.stderr[:5000] if len(result.stderr) > 5000 else result.stderr
            }, indent=2)
        except subprocess.TimeoutExpired:
            return json.dumps({
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds"
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e)
            }, indent=2)


def get_tools_for_role(role: str) -> List[Dict[str, Any]]:
    """
    Get the appropriate tool definitions for a given agent role.

    Args:
        role: Agent role (phd_student, ml_engineer, sw_engineer, postdoc, professor, reviewer)

    Returns:
        List of tool definitions appropriate for that role
    """
    all_tools = {t["name"]: t for t in RESEARCH_TOOLS}

    role_tools = {
        "phd_student": [
            "arxiv_search",
            "arxiv_get_paper",
            "read_file",
            "write_file",
            "web_search"
        ],
        "ml_engineer": [
            "arxiv_search",
            "arxiv_get_paper",
            "huggingface_dataset_search",
            "execute_python",
            "read_file",
            "write_file",
            "edit_file",
            "bash_command"
        ],
        "sw_engineer": [
            "execute_python",
            "read_file",
            "write_file",
            "edit_file",
            "bash_command"
        ],
        "postdoc": [
            "arxiv_search",
            "arxiv_get_paper",
            "read_file",
            "web_search"
        ],
        "professor": [
            "read_file",
            "write_file",
            "edit_file"
        ],
        "reviewer": [
            "read_file"
        ]
    }

    tool_names = role_tools.get(role, [])
    return [all_tools[name] for name in tool_names if name in all_tools]


if __name__ == "__main__":
    print("Claude Code Tools - Testing")
    print("=" * 50)

    # Test tool executor
    executor = ToolExecutor()

    # Test file operations
    print("\nTesting file write...")
    result = executor.execute_tool("write_file", {
        "file_path": "/tmp/test_claude_tools.txt",
        "content": "Hello from Claude Tools!"
    })
    print(result)

    print("\nTesting file read...")
    result = executor.execute_tool("read_file", {
        "file_path": "/tmp/test_claude_tools.txt"
    })
    print(result)

    # Test bash command
    print("\nTesting bash command...")
    result = executor.execute_tool("bash_command", {
        "command": "echo 'Hello from bash'"
    })
    print(result)

    # Test Python execution
    print("\nTesting Python execution...")
    result = executor.execute_tool("execute_python", {
        "code": "print('Hello from Python!')\nprint(2 + 2)"
    })
    print(result)

    print("\nAll tests completed!")
