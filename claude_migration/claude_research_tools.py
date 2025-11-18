"""
Extended Research Tools for Claude Migration

Provides tool execution functions that integrate with the command-based
dialogue system. These tools are called when agents use specific commands.
"""
import os
import sys
import subprocess
import tempfile
import json
from typing import Dict, Any, List, Optional
from pathlib import Path


class ResearchTools:
    """
    Tool executors for research workflow.

    These methods are called when agents issue specific commands during
    their dialogue (e.g., ```python, ```SEARCH_HF, etc.)
    """

    @staticmethod
    def execute_python_code(code: str, timeout: int = 60) -> str:
        """
        Execute Python code and return output.

        Equivalent to execute_code from original utils.py

        Args:
            code: Python code to execute
            timeout: Timeout in seconds

        Returns:
            Execution output or error message
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                delete=False
            ) as f:
                f.write(code)
                temp_file = f.name

            try:
                # Execute code
                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False
                )

                # Combine stdout and stderr
                output = result.stdout
                if result.stderr:
                    output += f"\n[STDERR]: {result.stderr}"

                if result.returncode != 0:
                    return f"[CODE EXECUTION ERROR]: Process exited with code {result.returncode}\n{output}"

                return output if output else "[Code executed successfully with no output]"

            finally:
                # Clean up temp file
                if os.path.exists(temp_file):
                    os.remove(temp_file)

        except subprocess.TimeoutExpired:
            return f"[CODE EXECUTION ERROR]: Code execution timed out after {timeout} seconds"

        except Exception as e:
            return f"[CODE EXECUTION ERROR]: {str(e)}"

    @staticmethod
    def search_arxiv_papers(query: str, n: int = 5) -> str:
        """
        Search arXiv for papers.

        Placeholder - needs integration with arXiv API or semantic search.

        Args:
            query: Search query
            n: Number of results

        Returns:
            Formatted search results
        """
        # TODO: Integrate with actual arXiv search
        # For now, return a placeholder that indicates the tool was called
        return f"""
[PLACEHOLDER - ARXIV SEARCH]
Query: {query}
Requested: {n} papers

To implement:
1. Use arxiv Python package: import arxiv
2. Or use WebSearch tool with site:arxiv.org
3. Return formatted list of papers with:
   - Title
   - Authors
   - Abstract
   - arXiv ID
   - Published date

Example implementation:
```python
import arxiv
search = arxiv.Search(query="{query}", max_results={n})
results = []
for paper in search.results():
    results.append(f"Title: {{paper.title}}\\nAuthors: {{paper.authors}}\\nID: {{paper.entry_id}}\\n")
return "\\n".join(results)
```
"""

    @staticmethod
    def get_arxiv_paper_text(arxiv_id: str) -> str:
        """
        Fetch full text of arXiv paper.

        Placeholder - needs integration with arXiv API.

        Args:
            arxiv_id: arXiv paper ID

        Returns:
            Full paper text or abstract
        """
        # TODO: Integrate with actual arXiv text extraction
        return f"""
[PLACEHOLDER - ARXIV FULL TEXT]
Paper ID: {arxiv_id}

To implement:
1. Download PDF from arXiv
2. Extract text using PyPDF2 or similar
3. Or use arXiv API to get abstract + metadata

Example:
```python
import arxiv
paper = next(arxiv.Search(id_list=["{arxiv_id}"]).results())
return f"Title: {{paper.title}}\\n\\nAbstract: {{paper.summary}}\\n\\nFull text: [extract from PDF]"
```
"""

    @staticmethod
    def search_huggingface_datasets(query: str, n: int = 10) -> str:
        """
        Search HuggingFace for datasets.

        Placeholder - needs integration with HuggingFace API.

        Args:
            query: Search query
            n: Number of results

        Returns:
            Formatted dataset results
        """
        # TODO: Integrate with HuggingFace datasets API
        return f"""
[PLACEHOLDER - HUGGINGFACE SEARCH]
Query: {query}
Requested: {n} datasets

To implement:
1. Use HuggingFace datasets library
2. Or use their API: https://huggingface.co/api/datasets

Example implementation:
```python
from huggingface_hub import list_datasets
datasets = list_datasets(search="{query}", limit={n})
results = []
for ds in datasets:
    results.append(f"Name: {{ds.id}}\\nDownloads: {{ds.downloads}}\\nDescription: {{ds.description}}\\n")
return "\\n".join(results)
```
"""


class LiteratureReviewManager:
    """
    Manages literature review collection.

    Mimics the lit_review list management from original PhDStudentAgent.
    """

    def __init__(self):
        self.papers: List[Dict[str, str]] = []

    def add_paper(self, arxiv_id: str, summary: str) -> str:
        """
        Add paper to literature review.

        Args:
            arxiv_id: arXiv paper ID
            summary: Paper summary

        Returns:
            Confirmation message
        """
        self.papers.append({
            "arxiv_id": arxiv_id,
            "summary": summary
        })
        return f"Added paper {arxiv_id} to literature review. Total papers: {len(self.papers)}"

    def format_review(self) -> str:
        """
        Format literature review as string.

        Mimics format_review from original PhDStudentAgent.

        Returns:
            Formatted literature review
        """
        if not self.papers:
            return "No papers in literature review."

        review_text = "Provided here is a literature review on this topic:\n"
        for paper in self.papers:
            review_text += f"arXiv ID: {paper['arxiv_id']}, Summary: {paper['summary']}\n"

        return review_text

    def count(self) -> int:
        """Get number of papers in review."""
        return len(self.papers)

    def clear(self):
        """Clear all papers (used when human rejects review)."""
        self.papers.clear()


def save_to_file(location: str, filename: str, data: str):
    """
    Save data to file.

    Equivalent to save_to_file from original utils.py

    Args:
        location: Directory path
        filename: Filename
        data: Data to write
    """
    filepath = Path(location) / filename

    # Create directory if it doesn't exist
    filepath.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(filepath, 'w') as f:
            f.write(data)
        print(f"Data successfully saved to {filepath}")
    except Exception as e:
        print(f"Error saving file {filename}: {e}")


class ToolExecutorFactory:
    """
    Factory for creating tool executor dictionaries.

    Provides pre-configured tool executor maps for different phases.
    """

    @staticmethod
    def get_literature_review_tools() -> Dict[str, Any]:
        """Get tool executors for literature review phase."""
        tools = ResearchTools()

        return {
            "search_papers": lambda query: tools.search_arxiv_papers(query, n=5),
            "get_paper": tools.get_arxiv_paper_text
        }

    @staticmethod
    def get_data_preparation_tools() -> Dict[str, Any]:
        """Get tool executors for data preparation phase."""
        tools = ResearchTools()

        return {
            "execute_code": tools.execute_python_code,
            "search_datasets": tools.search_huggingface_datasets
        }

    @staticmethod
    def get_experiment_tools() -> Dict[str, Any]:
        """Get tool executors for running experiments."""
        tools = ResearchTools()

        return {
            "execute_code": tools.execute_python_code
        }
