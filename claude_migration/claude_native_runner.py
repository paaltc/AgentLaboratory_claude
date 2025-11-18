#!/usr/bin/env python3
"""
Claude Code Native Runner
Runs research workflow directly within Claude Code (Claude Pro) without API access.

This module generates structured prompts for Claude Code to execute using its
native tools (WebFetch, WebSearch, Bash, Read, Write, Edit) instead of API calls.
"""
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from claude_config import ResearchConfig


class ClaudeNativeWorkflow:
    """
    Research workflow that runs natively within Claude Code.

    Instead of making API calls, this outputs structured task files that
    Claude Code (the AI) executes using its native tools.
    """

    def __init__(
        self,
        research_topic: str,
        output_dir: str = "./research_output",
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize native workflow."""
        self.research_topic = research_topic
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Default configuration
        self.config = {
            "num_papers_lit_review": 5,
            "max_experiment_iterations": 3,
            "max_paper_iterations": 2,
        }
        if config:
            self.config.update(config)

        # Task directory for Claude Code to process
        self.task_dir = self.output_dir / "tasks"
        self.task_dir.mkdir(exist_ok=True)

        # Results directory
        self.results_dir = self.output_dir / "results"
        self.results_dir.mkdir(exist_ok=True)

        # State file
        self.state_file = self.output_dir / "workflow_state.json"
        self.state = self._load_or_create_state()

    def _load_or_create_state(self) -> Dict[str, Any]:
        """Load existing state or create new one."""
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)

        return {
            "current_phase": "not_started",
            "current_task": None,
            "completed_phases": [],
            "research_topic": self.research_topic,
            "config": self.config,
            "created_at": datetime.now().isoformat(),
            "artifacts": {
                "literature": "",
                "plan": "",
                "dataset_info": "",
                "code": "",
                "results": "",
                "paper": ""
            }
        }

    def _save_state(self):
        """Save current state to file."""
        self.state["updated_at"] = datetime.now().isoformat()
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def generate_next_task(self) -> Dict[str, Any]:
        """
        Generate the next task for Claude Code to execute.

        Returns a dictionary with:
        - task_id: Unique task identifier
        - phase: Current research phase
        - prompt: Instructions for Claude Code
        - tools_to_use: Suggested Claude Code tools
        - output_file: Where to save results
        """
        phase = self.state["current_phase"]

        if phase == "not_started":
            return self._generate_literature_review_task()
        elif phase == "literature_review":
            # Check if literature review is done
            lit_file = self.results_dir / "literature_review.md"
            if lit_file.exists():
                self.state["artifacts"]["literature"] = lit_file.read_text()
                self.state["completed_phases"].append("literature_review")
                self.state["current_phase"] = "plan_formulation"
                self._save_state()
                return self._generate_plan_formulation_task()
            else:
                return self._generate_literature_review_task()
        elif phase == "plan_formulation":
            plan_file = self.results_dir / "research_plan.md"
            if plan_file.exists():
                self.state["artifacts"]["plan"] = plan_file.read_text()
                self.state["completed_phases"].append("plan_formulation")
                self.state["current_phase"] = "data_preparation"
                self._save_state()
                return self._generate_data_preparation_task()
            else:
                return self._generate_plan_formulation_task()
        elif phase == "data_preparation":
            data_file = self.results_dir / "dataset_info.md"
            if data_file.exists():
                self.state["artifacts"]["dataset_info"] = data_file.read_text()
                self.state["completed_phases"].append("data_preparation")
                self.state["current_phase"] = "experimentation"
                self._save_state()
                return self._generate_experimentation_task()
            else:
                return self._generate_data_preparation_task()
        elif phase == "experimentation":
            code_file = self.results_dir / "experiment_code.py"
            results_file = self.results_dir / "experiment_results.md"
            if code_file.exists() and results_file.exists():
                self.state["artifacts"]["code"] = code_file.read_text()
                self.state["artifacts"]["results"] = results_file.read_text()
                self.state["completed_phases"].append("experimentation")
                self.state["current_phase"] = "paper_writing"
                self._save_state()
                return self._generate_paper_writing_task()
            else:
                return self._generate_experimentation_task()
        elif phase == "paper_writing":
            paper_file = self.results_dir / "research_paper.tex"
            if paper_file.exists():
                self.state["artifacts"]["paper"] = paper_file.read_text()
                self.state["completed_phases"].append("paper_writing")
                self.state["current_phase"] = "completed"
                self._save_state()
                return {"status": "completed", "message": "Research workflow complete!"}
            else:
                return self._generate_paper_writing_task()
        else:
            return {"status": "completed", "message": "All phases complete!"}

    def _generate_literature_review_task(self) -> Dict[str, Any]:
        """Generate literature review task."""
        self.state["current_phase"] = "literature_review"
        self._save_state()

        return {
            "task_id": "lit_review_001",
            "phase": "literature_review",
            "role": "PhD Student Researcher",
            "prompt": f"""# Literature Review Task

## Research Topic
{self.research_topic}

## Your Task
Conduct a comprehensive literature review by:

1. **Search for Papers**: Use WebSearch to find {self.config['num_papers_lit_review']} relevant papers on arXiv or academic sources
2. **Fetch Paper Details**: Use WebFetch to retrieve paper abstracts and key information
3. **Analyze and Synthesize**:
   - Identify key methods and approaches
   - Note research gaps and opportunities
   - Summarize main findings

## Expected Output
Write your findings to: `{self.results_dir}/literature_review.md`

Structure your output as:
```markdown
# Literature Review: {self.research_topic}

## Papers Reviewed
1. [Paper Title] - Authors (Year)
   - Key Contribution: ...
   - Methods: ...
   - Results: ...

## Key Methods in the Field
- Method 1: ...
- Method 2: ...

## Research Gaps Identified
- Gap 1: ...
- Gap 2: ...

## Recommended Research Direction
Based on the review, I recommend...
```

## Tools to Use
- **WebSearch**: Search for "arxiv {self.research_topic}" or "{self.research_topic} machine learning paper"
- **WebFetch**: Fetch paper pages from arxiv.org for details
- **Write**: Save your review to the output file

Please proceed with the literature review now.""",
            "tools_to_use": ["WebSearch", "WebFetch", "Write"],
            "output_file": str(self.results_dir / "literature_review.md")
        }

    def _generate_plan_formulation_task(self) -> Dict[str, Any]:
        """Generate plan formulation task."""
        self.state["current_phase"] = "plan_formulation"
        self._save_state()

        literature = self.state["artifacts"].get("literature", "")

        return {
            "task_id": "plan_001",
            "phase": "plan_formulation",
            "role": "Postdoc Researcher",
            "prompt": f"""# Research Plan Formulation Task

## Research Topic
{self.research_topic}

## Literature Review Summary
{literature[:5000] if len(literature) > 5000 else literature}

## Your Task
Based on the literature review, formulate a detailed research plan:

1. **Define Objectives**: Clear, measurable research objectives
2. **Formulate Hypotheses**: Testable hypotheses based on literature gaps
3. **Design Experiments**: Experimental methodology and evaluation metrics
4. **Identify Resources**: Datasets, compute requirements, tools needed

## Expected Output
Write your plan to: `{self.results_dir}/research_plan.md`

Structure your output as:
```markdown
# Research Plan: {self.research_topic}

## 1. Research Objectives
- Objective 1: ...
- Objective 2: ...

## 2. Hypotheses
- H1: ...
- H2: ...

## 3. Experimental Design
### 3.1 Methodology
...

### 3.2 Evaluation Metrics
- Metric 1: ...
- Metric 2: ...

### 3.3 Baselines for Comparison
...

## 4. Data Requirements
- Dataset 1: ...
- Dataset 2: ...

## 5. Implementation Plan
### Phase 1: Data Preparation
...
### Phase 2: Model Development
...
### Phase 3: Evaluation
...

## 6. Expected Outcomes
...

## 7. Potential Challenges
- Challenge 1: ... (Mitigation: ...)
- Challenge 2: ... (Mitigation: ...)
```

## Tools to Use
- **Read**: Read the literature review if needed
- **Write**: Save your plan to the output file

Please formulate the research plan now.""",
            "tools_to_use": ["Read", "Write"],
            "output_file": str(self.results_dir / "research_plan.md")
        }

    def _generate_data_preparation_task(self) -> Dict[str, Any]:
        """Generate data preparation task."""
        self.state["current_phase"] = "data_preparation"
        self._save_state()

        plan = self.state["artifacts"].get("plan", "")

        return {
            "task_id": "data_prep_001",
            "phase": "data_preparation",
            "role": "ML Engineer",
            "prompt": f"""# Data Preparation Task

## Research Topic
{self.research_topic}

## Research Plan (Data Requirements Section)
{plan[:3000] if len(plan) > 3000 else plan}

## Your Task
Identify and prepare suitable datasets for the experiments:

1. **Search Datasets**: Find relevant datasets on Hugging Face or other sources
2. **Evaluate Suitability**: Check dataset size, format, and relevance
3. **Document Loading**: Write instructions for loading the data

## Expected Output
Write dataset information to: `{self.results_dir}/dataset_info.md`

Structure your output as:
```markdown
# Dataset Information

## Selected Datasets

### Primary Dataset
- **Name**: ...
- **Source**: Hugging Face / Other
- **Size**: ... samples
- **Format**: ...
- **Why suitable**: ...

### Loading Code
```python
from datasets import load_dataset
# or other loading method

dataset = load_dataset("...")
# preprocessing steps
```

## Data Statistics
- Training samples: ...
- Validation samples: ...
- Test samples: ...
- Features: ...

## Preprocessing Steps
1. ...
2. ...
```

## Tools to Use
- **WebSearch**: Search "huggingface datasets {self.research_topic}" or similar
- **WebFetch**: Fetch dataset cards from Hugging Face
- **Write**: Save dataset information to output file

Please identify suitable datasets now.""",
            "tools_to_use": ["WebSearch", "WebFetch", "Write"],
            "output_file": str(self.results_dir / "dataset_info.md")
        }

    def _generate_experimentation_task(self) -> Dict[str, Any]:
        """Generate experimentation task."""
        self.state["current_phase"] = "experimentation"
        self._save_state()

        plan = self.state["artifacts"].get("plan", "")
        dataset_info = self.state["artifacts"].get("dataset_info", "")

        return {
            "task_id": "experiment_001",
            "phase": "experimentation",
            "role": "ML Engineer",
            "prompt": f"""# Experimentation Task

## Research Topic
{self.research_topic}

## Research Plan
{plan[:2000] if len(plan) > 2000 else plan}

## Dataset Information
{dataset_info[:2000] if len(dataset_info) > 2000 else dataset_info}

## Your Task
Implement and run the machine learning experiment:

1. **Write Code**: Create complete, runnable experiment code
2. **Run Experiment**: Execute the code using Bash tool
3. **Record Results**: Document all results and metrics

## Expected Outputs
1. Code file: `{self.results_dir}/experiment_code.py`
2. Results file: `{self.results_dir}/experiment_results.md`

### Code Structure
```python
#!/usr/bin/env python3
\"\"\"
Experiment: {self.research_topic}
\"\"\"
import numpy as np
# other imports...

def load_data():
    # Load and preprocess data
    pass

def create_model():
    # Create the model
    pass

def train(model, data):
    # Training loop
    pass

def evaluate(model, test_data):
    # Evaluation metrics
    pass

def main():
    print("Loading data...")
    # Your implementation

    print("Training model...")
    # Training

    print("Evaluating...")
    # Evaluation

    print("Results:")
    # Print final results

if __name__ == "__main__":
    main()
```

### Results Structure
```markdown
# Experiment Results

## Configuration
- Model: ...
- Hyperparameters: ...
- Training epochs: ...

## Results
| Metric | Value |
|--------|-------|
| Accuracy | ... |
| F1 Score | ... |

## Analysis
...

## Observations
...
```

## Tools to Use
- **Write**: Write the experiment code to file
- **Bash**: Run the experiment with `python {self.results_dir}/experiment_code.py`
- **Write**: Save results to the results file

Please implement and run the experiment now.""",
            "tools_to_use": ["Write", "Bash", "Read"],
            "output_file": str(self.results_dir / "experiment_code.py")
        }

    def _generate_paper_writing_task(self) -> Dict[str, Any]:
        """Generate paper writing task."""
        self.state["current_phase"] = "paper_writing"
        self._save_state()

        literature = self.state["artifacts"].get("literature", "")[:2000]
        plan = self.state["artifacts"].get("plan", "")[:2000]
        results = self.state["artifacts"].get("results", "")[:2000]

        return {
            "task_id": "paper_001",
            "phase": "paper_writing",
            "role": "Professor / Senior Researcher",
            "prompt": f"""# Research Paper Writing Task

## Research Topic
{self.research_topic}

## Literature Review Summary
{literature}

## Research Plan Summary
{plan}

## Experiment Results
{results}

## Your Task
Write a complete research paper in LaTeX format:

1. **Structure**: Follow standard academic paper structure
2. **Content**: Include all sections with proper citations
3. **Quality**: Academic writing standards, clear explanations

## Expected Output
Write the paper to: `{self.results_dir}/research_paper.tex`

### Paper Template
```latex
\\documentclass{{article}}
\\usepackage{{amsmath, amssymb, graphicx, hyperref}}

\\title{{[Your Title Here]}}
\\author{{AI Research Lab}}
\\date{{\\today}}

\\begin{{document}}
\\maketitle

\\begin{{abstract}}
[Brief summary of the research - problem, method, key results]
\\end{{abstract}}

\\section{{Introduction}}
[Problem statement, motivation, contributions]

\\section{{Related Work}}
[Literature review, positioning of this work]

\\section{{Methodology}}
[Detailed description of your approach]

\\section{{Experiments}}
\\subsection{{Setup}}
[Dataset, baselines, metrics]

\\subsection{{Results}}
[Main results with tables/figures]

\\section{{Discussion}}
[Analysis, limitations, implications]

\\section{{Conclusion}}
[Summary and future work]

\\bibliographystyle{{plain}}
\\begin{{thebibliography}}{{9}}
\\bibitem{{ref1}} ...
\\end{{thebibliography}}

\\end{{document}}
```

**IMPORTANT**: Do NOT include `\\usepackage[utf-8]{{inputenc}}` - this is legacy and unnecessary in modern LaTeX (UTF-8 is default since 2018).

## Tools to Use
- **Read**: Read literature, plan, and results files if needed
- **Write**: Write the LaTeX paper to the output file

Please write the research paper now.""",
            "tools_to_use": ["Read", "Write"],
            "output_file": str(self.results_dir / "research_paper.tex")
        }

    def get_current_status(self) -> str:
        """Get human-readable status of the workflow."""
        status_lines = [
            "=" * 60,
            "Claude Code Native Research Workflow Status",
            "=" * 60,
            f"Research Topic: {self.research_topic}",
            f"Current Phase: {self.state['current_phase']}",
            f"Completed Phases: {', '.join(self.state['completed_phases']) or 'None'}",
            f"Output Directory: {self.output_dir}",
            "",
            "Artifacts:",
        ]

        for name, content in self.state["artifacts"].items():
            if content:
                status_lines.append(f"  - {name}: {len(content)} chars ✓")
            else:
                status_lines.append(f"  - {name}: Not yet created")

        status_lines.append("=" * 60)
        return "\n".join(status_lines)


def print_claude_code_instructions(task: Dict[str, Any]):
    """Print instructions for Claude Code to execute."""
    print("\n" + "=" * 70)
    print("CLAUDE CODE NATIVE TASK")
    print("=" * 70)

    if task.get("status") == "completed":
        print(f"\n✓ {task['message']}")
        return

    print(f"\nTask ID: {task['task_id']}")
    print(f"Phase: {task['phase']}")
    print(f"Role: {task['role']}")
    print(f"Output File: {task['output_file']}")
    print(f"Tools to Use: {', '.join(task['tools_to_use'])}")
    print("\n" + "-" * 70)
    print("TASK INSTRUCTIONS:")
    print("-" * 70)
    print(task['prompt'])
    print("=" * 70)


def run_native_workflow(
    topic: str,
    output_dir: str = "./research_output",
    **config_kwargs
) -> ClaudeNativeWorkflow:
    """
    Initialize and return a native workflow instance.

    Args:
        topic: Research topic
        output_dir: Output directory
        **config_kwargs: Additional configuration

    Returns:
        Workflow instance ready for Claude Code execution
    """
    workflow = ClaudeNativeWorkflow(
        research_topic=topic,
        output_dir=output_dir,
        config=config_kwargs
    )

    print(workflow.get_current_status())

    # Generate and print the next task
    task = workflow.generate_next_task()
    print_claude_code_instructions(task)

    return workflow


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Claude Code Native Research Workflow",
        epilog="""
This runs research workflows directly within Claude Code (Claude Pro).
No API key needed - Claude Code uses its native tools (WebSearch, WebFetch,
Bash, Read, Write) to execute the research tasks.

Usage:
  1. Run this script to get the next task
  2. Claude Code executes the task using its tools
  3. Run again to get the next task
  4. Repeat until complete
        """
    )

    parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help="Research topic"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./research_output",
        help="Output directory"
    )
    parser.add_argument(
        "--papers",
        type=int,
        default=5,
        help="Number of papers to review"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show current status only"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset workflow state"
    )

    args = parser.parse_args()

    if args.reset:
        state_file = Path(args.output_dir) / "workflow_state.json"
        if state_file.exists():
            state_file.unlink()
            print(f"Workflow state reset. State file removed: {state_file}")
        else:
            print("No state file found to reset.")
        exit(0)

    workflow = ClaudeNativeWorkflow(
        research_topic=args.topic,
        output_dir=args.output_dir,
        config={"num_papers_lit_review": args.papers}
    )

    if args.status:
        print(workflow.get_current_status())
    else:
        print(workflow.get_current_status())
        task = workflow.generate_next_task()
        print_claude_code_instructions(task)
