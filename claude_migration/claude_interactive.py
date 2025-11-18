#!/usr/bin/env python3
"""
Claude Code Interactive Research Runner

This provides a simple interactive interface for running research workflows
directly within Claude Code / Claude Pro without API access.
"""
import json
from pathlib import Path
from datetime import datetime


def create_research_workspace(topic: str, workspace_dir: str = "./research") -> Path:
    """
    Create a workspace directory for the research project.

    Args:
        topic: Research topic
        workspace_dir: Base workspace directory

    Returns:
        Path to the workspace
    """
    workspace = Path(workspace_dir)
    workspace.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    (workspace / "literature").mkdir(exist_ok=True)
    (workspace / "plans").mkdir(exist_ok=True)
    (workspace / "experiments").mkdir(exist_ok=True)
    (workspace / "results").mkdir(exist_ok=True)
    (workspace / "papers").mkdir(exist_ok=True)

    # Create project info file
    info = {
        "topic": topic,
        "created": datetime.now().isoformat(),
        "phases": {
            "literature_review": "pending",
            "plan_formulation": "pending",
            "experimentation": "pending",
            "paper_writing": "pending"
        }
    }

    info_file = workspace / "project_info.json"
    with open(info_file, "w") as f:
        json.dump(info, f, indent=2)

    print(f"Research workspace created: {workspace}")
    print(f"Topic: {topic}")
    print("\nDirectory structure:")
    print(f"  {workspace}/")
    print(f"  ├── literature/     # Literature review documents")
    print(f"  ├── plans/          # Research plans")
    print(f"  ├── experiments/    # Code and data")
    print(f"  ├── results/        # Experiment results")
    print(f"  ├── papers/         # Research papers")
    print(f"  └── project_info.json")

    return workspace


def generate_literature_review_prompt(topic: str, num_papers: int = 5) -> str:
    """Generate prompt for literature review phase."""
    return f"""# Literature Review Task

## Research Topic
{topic}

## Instructions for Claude Code

Please conduct a literature review by:

1. **Search for Papers**
   Use WebSearch to find papers:
   ```
   Search: "arxiv {topic}"
   Search: "{topic} machine learning recent papers"
   ```

2. **Fetch Paper Details**
   Use WebFetch to get abstracts and details from arxiv.org URLs

3. **Analyze {num_papers} Papers**
   For each paper, note:
   - Title and authors
   - Key contribution
   - Methods used
   - Main results

4. **Identify Research Gaps**
   What opportunities exist for new research?

5. **Save Your Review**
   Write your findings to: `./research/literature/review.md`

## Output Template

```markdown
# Literature Review: {topic}

## Executive Summary
[2-3 sentence overview]

## Papers Reviewed

### Paper 1: [Title]
- Authors: ...
- Year: ...
- Key Contribution: ...
- Methods: ...
- Results: ...
- Relevance: ...

[Repeat for each paper]

## Key Methods in the Field
- ...

## Research Gaps
1. ...
2. ...

## Recommended Direction
Based on this review, I recommend...
```

Please execute this task now using your WebSearch, WebFetch, and Write tools.
"""


def generate_plan_prompt(topic: str) -> str:
    """Generate prompt for research plan formulation."""
    return f"""# Research Plan Formulation Task

## Research Topic
{topic}

## Instructions for Claude Code

1. **Read Literature Review**
   Use Read tool to load: `./research/literature/review.md`

2. **Design Research Plan**
   Based on identified gaps, create a detailed plan including:
   - Specific research objectives
   - Testable hypotheses
   - Experimental methodology
   - Evaluation metrics
   - Timeline

3. **Save Your Plan**
   Write to: `./research/plans/research_plan.md`

## Output Template

```markdown
# Research Plan: {topic}

## 1. Research Objectives
- O1: ...
- O2: ...

## 2. Hypotheses
- H1: ...
- H2: ...

## 3. Methodology
### 3.1 Approach
...

### 3.2 Evaluation Metrics
- Metric 1: ...
- Metric 2: ...

## 4. Data Requirements
- Dataset: ...
- Size: ...
- Format: ...

## 5. Implementation Steps
1. ...
2. ...

## 6. Expected Outcomes
...

## 7. Timeline
- Week 1: ...
- Week 2: ...
```

Please execute this task now using your Read and Write tools.
"""


def generate_experiment_prompt(topic: str) -> str:
    """Generate prompt for experimentation phase."""
    return f"""# Experimentation Task

## Research Topic
{topic}

## Instructions for Claude Code

1. **Read Research Plan**
   Use Read tool to load: `./research/plans/research_plan.md`

2. **Search for Datasets**
   Use WebSearch:
   ```
   Search: "huggingface datasets {topic}"
   ```

3. **Write Experiment Code**
   Create a complete, runnable Python script
   Save to: `./research/experiments/main.py`

4. **Run the Experiment**
   Use Bash tool:
   ```bash
   cd ./research/experiments && python main.py
   ```

5. **Save Results**
   Write results to: `./research/results/experiment_results.md`

## Code Template

```python
#!/usr/bin/env python3
\"\"\"
Experiment: {topic}
\"\"\"
import json
from datetime import datetime

def main():
    print(f"Starting experiment: {topic}")
    print(f"Time: {{datetime.now()}}")

    # Configuration
    config = {{
        "experiment": "{topic}",
        "parameters": {{}}
    }}

    # Data loading
    print("Loading data...")
    # Your data loading code here

    # Model/Method
    print("Running method...")
    # Your implementation here

    # Evaluation
    print("Evaluating...")
    results = {{
        "metric1": 0.0,
        "metric2": 0.0
    }}

    # Save results
    with open("../results/metrics.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"Results: {{results}}")
    return results

if __name__ == "__main__":
    main()
```

Please execute this task using your WebSearch, Read, Write, and Bash tools.
"""


def generate_paper_prompt(topic: str) -> str:
    """Generate prompt for paper writing phase."""
    return f"""# Research Paper Writing Task

## Research Topic
{topic}

## Instructions for Claude Code

1. **Read All Artifacts**
   Use Read tool:
   - `./research/literature/review.md`
   - `./research/plans/research_plan.md`
   - `./research/results/experiment_results.md`

2. **Write Research Paper**
   Create a complete LaTeX paper
   Save to: `./research/papers/paper.tex`

## LaTeX Template

```latex
\\documentclass{{article}}
\\usepackage{{amsmath, graphicx, hyperref}}
\\title{{{topic}}}
\\author{{AI Research Lab}}
\\date{{\\today}}

\\begin{{document}}
\\maketitle

\\begin{{abstract}}
[Summary of your research]
\\end{{abstract}}

\\section{{Introduction}}
[Problem, motivation, contributions]

\\section{{Related Work}}
[From literature review]

\\section{{Methodology}}
[From research plan]

\\section{{Experiments}}
[Setup and results]

\\section{{Discussion}}
[Analysis and implications]

\\section{{Conclusion}}
[Summary and future work]

\\end{{document}}
```

**IMPORTANT**: Do NOT include `\\usepackage[utf-8]{{inputenc}}` - this is legacy and unnecessary in modern LaTeX (UTF-8 is default since 2018).

Please execute this task using your Read and Write tools.
"""


def print_interactive_menu():
    """Print interactive menu for research workflow."""
    print("\n" + "=" * 60)
    print("Claude Code Interactive Research Lab")
    print("=" * 60)
    print("\nCommands:")
    print("  1. Create new research workspace")
    print("  2. Show literature review task")
    print("  3. Show plan formulation task")
    print("  4. Show experimentation task")
    print("  5. Show paper writing task")
    print("  6. Check workspace status")
    print("  q. Quit")
    print("\n" + "=" * 60)


def main():
    """Main interactive loop."""
    import argparse

    parser = argparse.ArgumentParser(description="Interactive Research Runner")
    parser.add_argument("--topic", type=str, help="Research topic")
    parser.add_argument("--phase", type=str, choices=[
        "setup", "literature", "plan", "experiment", "paper"
    ], help="Show specific phase task")
    parser.add_argument("--workspace", type=str, default="./research",
                        help="Workspace directory")

    args = parser.parse_args()

    if args.phase:
        # Non-interactive mode - show specific phase
        topic = args.topic or "Machine Learning Research"

        if args.phase == "setup":
            create_research_workspace(topic, args.workspace)
        elif args.phase == "literature":
            print(generate_literature_review_prompt(topic))
        elif args.phase == "plan":
            print(generate_plan_prompt(topic))
        elif args.phase == "experiment":
            print(generate_experiment_prompt(topic))
        elif args.phase == "paper":
            print(generate_paper_prompt(topic))
        return

    # Interactive mode
    topic = args.topic or "Few-shot Learning in NLP"
    workspace = Path(args.workspace)

    while True:
        print_interactive_menu()
        choice = input("Enter choice: ").strip()

        if choice == "1":
            new_topic = input(f"Research topic [{topic}]: ").strip()
            if new_topic:
                topic = new_topic
            create_research_workspace(topic, str(workspace))

        elif choice == "2":
            print(generate_literature_review_prompt(topic))
            input("\nPress Enter to continue...")

        elif choice == "3":
            print(generate_plan_prompt(topic))
            input("\nPress Enter to continue...")

        elif choice == "4":
            print(generate_experiment_prompt(topic))
            input("\nPress Enter to continue...")

        elif choice == "5":
            print(generate_paper_prompt(topic))
            input("\nPress Enter to continue...")

        elif choice == "6":
            if workspace.exists():
                info_file = workspace / "project_info.json"
                if info_file.exists():
                    with open(info_file) as f:
                        info = json.load(f)
                    print(f"\nWorkspace: {workspace}")
                    print(f"Topic: {info.get('topic', 'Unknown')}")
                    print(f"Created: {info.get('created', 'Unknown')}")
                    print("\nPhase Status:")
                    for phase, status in info.get("phases", {}).items():
                        print(f"  - {phase}: {status}")
                else:
                    print("No project info found.")
            else:
                print("Workspace not created yet.")
            input("\nPress Enter to continue...")

        elif choice.lower() == "q":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
