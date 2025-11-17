#!/usr/bin/env python3
"""
Claude Code Multi-Agent Orchestrator

This module creates actual subagents using Claude Code's Task tool.
Each agent (PhD Student, ML Engineer, Postdoc, etc.) runs as a separate
Claude instance with specialized prompts and tool access.

This is designed to be executed FROM WITHIN Claude Code, where the Task
tool can spawn real subagents.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class MultiAgentOrchestrator:
    """
    Orchestrates multiple Claude subagents for research workflows.

    Uses Claude Code's Task tool to spawn specialized agents that collaborate
    on research tasks, mimicking the original AgentLaboratory architecture.
    """

    def __init__(
        self,
        research_topic: str,
        output_dir: str = "./multi_agent_research",
        config: Optional[Dict[str, Any]] = None
    ):
        self.research_topic = research_topic
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Default configuration
        self.config = {
            "num_papers": 5,
            "max_dialogue_turns": 3,
            "agent_model": "haiku",  # Use haiku for speed/cost
        }
        if config:
            self.config.update(config)

        # State tracking
        self.state_file = self.output_dir / "orchestrator_state.json"
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load or create orchestrator state."""
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {
            "topic": self.research_topic,
            "created": datetime.now().isoformat(),
            "phases_completed": [],
            "artifacts": {},
            "agent_outputs": {}
        }

    def _save_state(self):
        """Save orchestrator state."""
        self.state["updated"] = datetime.now().isoformat()
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def get_phd_student_prompt(self, phase: str, context: str = "") -> str:
        """Generate prompt for PhD Student agent."""
        base = f"""You are a PhD Student researcher working on: {self.research_topic}

Your role:
- Conduct thorough literature reviews
- Assist in experimental design
- Draft research reports
- Learn from senior researchers' guidance

Current phase: {phase}

You have access to these tools:
- WebSearch: Search for academic papers
- WebFetch: Fetch paper details
- Read: Read files
- Write: Save your work

{context}

Important: Be thorough, cite sources, and save your work to the specified output file.
"""
        return base

    def get_ml_engineer_prompt(self, phase: str, context: str = "") -> str:
        """Generate prompt for ML Engineer agent."""
        base = f"""You are an ML Engineer working on: {self.research_topic}

Your role:
- Design and implement ML experiments
- Search for appropriate datasets
- Write clean, tested Python code
- Optimize model performance

Current phase: {phase}

You have access to these tools:
- WebSearch: Find datasets and papers
- WebFetch: Get dataset details
- Read: Read code and plans
- Write: Save code files
- Bash: Execute Python code

{context}

Important: Write production-quality code with error handling and clear comments.
"""
        return base

    def get_postdoc_prompt(self, phase: str, context: str = "") -> str:
        """Generate prompt for Postdoc researcher agent."""
        base = f"""You are a Postdoc researcher providing guidance on: {self.research_topic}

Your role:
- Provide expert guidance on research direction
- Suggest experimental improvements
- Help interpret complex results
- Mentor junior researchers
- Ensure scientific rigor

Current phase: {phase}

You have access to these tools:
- Read: Read research materials
- WebSearch: Find relevant papers

{context}

Important: Provide constructive, actionable guidance based on your expertise.
"""
        return base

    def get_professor_prompt(self, phase: str, context: str = "") -> str:
        """Generate prompt for Professor agent."""
        base = f"""You are a Professor overseeing research on: {self.research_topic}

Your role:
- Oversee the research project
- Ensure academic standards are met
- Write and review research papers
- Guide the team towards impactful results

Current phase: {phase}

You have access to these tools:
- Read: Read all research artifacts
- Write: Write and edit papers

{context}

Important: Maintain high academic standards with clear, rigorous writing.
"""
        return base

    def get_reviewer_prompt(self, context: str = "") -> str:
        """Generate prompt for Reviewer agent."""
        base = f"""You are a peer reviewer evaluating research on: {self.research_topic}

Your role:
- Critically evaluate the research paper
- Score on: originality, quality, clarity, significance, soundness
- Provide constructive feedback
- Identify strengths and weaknesses

You have access to:
- Read: Read the paper to review

{context}

Provide scores (1-10) and detailed feedback in JSON format:
{{
    "scores": {{
        "originality": X,
        "quality": X,
        "clarity": X,
        "significance": X,
        "soundness": X
    }},
    "recommendation": "Accept/Weak Accept/Weak Reject/Reject",
    "strengths": ["...", "..."],
    "weaknesses": ["...", "..."],
    "suggestions": ["...", "..."]
}}
"""
        return base

    def generate_literature_review_tasks(self) -> list:
        """Generate Task tool calls for literature review phase."""
        output_file = self.output_dir / "literature_review.md"

        task_prompt = f"""{self.get_phd_student_prompt("literature review")}

TASK: Conduct a literature review on "{self.research_topic}"

Steps:
1. Use WebSearch to find {self.config['num_papers']} relevant papers (search arXiv, academic sources)
2. Use WebFetch to get paper abstracts and details
3. Analyze key methods, findings, and research gaps
4. Write a comprehensive literature review

Save your review to: {output_file}

Format:
# Literature Review: {self.research_topic}

## Papers Reviewed
1. [Title] - Authors (Year)
   - Key Contribution: ...
   - Methods: ...
   - Results: ...

## Key Methods in the Field
...

## Research Gaps
...

## Recommended Direction
...

Return the path to your saved file and a brief summary of key findings."""

        return [{
            "agent_type": "phd_student",
            "task": task_prompt,
            "output_file": str(output_file),
            "description": "Literature review by PhD Student"
        }]

    def generate_plan_formulation_tasks(self) -> list:
        """Generate Task tool calls for plan formulation with dialogue."""
        lit_review_file = self.output_dir / "literature_review.md"
        plan_file = self.output_dir / "research_plan.md"

        # First: Postdoc provides guidance
        postdoc_prompt = f"""{self.get_postdoc_prompt("plan formulation")}

TASK: Provide guidance for research planning on "{self.research_topic}"

Read the literature review from: {lit_review_file}

Based on the literature review:
1. Identify the most promising research direction
2. Suggest specific hypotheses to test
3. Recommend experimental methodology
4. Highlight potential challenges

Save your guidance to: {self.output_dir / "postdoc_guidance.md"}

Be specific and actionable in your recommendations."""

        # Second: PhD Student creates plan based on guidance
        phd_plan_prompt = f"""{self.get_phd_student_prompt("plan formulation")}

TASK: Create detailed research plan for "{self.research_topic}"

Read:
1. Literature review from: {lit_review_file}
2. Postdoc guidance from: {self.output_dir / "postdoc_guidance.md"}

Create a comprehensive research plan including:
1. Research objectives (specific, measurable)
2. Hypotheses to test
3. Experimental design
4. Evaluation metrics
5. Timeline
6. Expected outcomes

Save your plan to: {plan_file}

Use the postdoc's guidance to strengthen your plan."""

        return [
            {
                "agent_type": "postdoc",
                "task": postdoc_prompt,
                "output_file": str(self.output_dir / "postdoc_guidance.md"),
                "description": "Research guidance from Postdoc"
            },
            {
                "agent_type": "phd_student",
                "task": phd_plan_prompt,
                "output_file": str(plan_file),
                "description": "Research plan by PhD Student",
                "depends_on": "postdoc_guidance"
            }
        ]

    def generate_experimentation_tasks(self) -> list:
        """Generate Task tool calls for experimentation phase."""
        plan_file = self.output_dir / "research_plan.md"
        dataset_file = self.output_dir / "dataset_info.md"
        code_file = self.output_dir / "experiment.py"
        results_file = self.output_dir / "results.md"

        # Data preparation
        data_prep_prompt = f"""{self.get_ml_engineer_prompt("data preparation")}

TASK: Prepare datasets for "{self.research_topic}"

Read the research plan from: {plan_file}

1. Use WebSearch to find suitable datasets on HuggingFace
2. Evaluate dataset suitability for the planned experiments
3. Document dataset details and loading code

Save dataset information to: {dataset_file}

Include:
- Dataset name and source
- Size and format
- Loading code example
- Preprocessing steps needed"""

        # Code implementation
        code_prompt = f"""{self.get_ml_engineer_prompt("experimentation")}

TASK: Implement experiment for "{self.research_topic}"

Read:
1. Research plan: {plan_file}
2. Dataset info: {dataset_file}

Write a complete, runnable Python experiment that:
1. Loads and preprocesses data
2. Implements the proposed method
3. Trains/evaluates the model
4. Logs results with metrics

Save your code to: {code_file}

Then run it using Bash tool and save results to: {results_file}

Code should be production-quality with:
- Clear comments
- Error handling
- Reproducible results
- Metric logging"""

        return [
            {
                "agent_type": "ml_engineer",
                "task": data_prep_prompt,
                "output_file": str(dataset_file),
                "description": "Data preparation by ML Engineer"
            },
            {
                "agent_type": "ml_engineer",
                "task": code_prompt,
                "output_file": str(code_file),
                "description": "Experiment implementation by ML Engineer",
                "depends_on": "dataset_info"
            }
        ]

    def generate_paper_writing_tasks(self) -> list:
        """Generate Task tool calls for paper writing phase."""
        paper_file = self.output_dir / "paper.tex"
        review_file = self.output_dir / "reviews.json"

        # Professor writes paper
        paper_prompt = f"""{self.get_professor_prompt("paper writing")}

TASK: Write research paper for "{self.research_topic}"

Read all artifacts in: {self.output_dir}
- literature_review.md
- research_plan.md
- dataset_info.md
- results.md (or experiment outputs)

Write a complete LaTeX research paper with:
- Abstract
- Introduction
- Related Work
- Methodology
- Experiments and Results
- Discussion
- Conclusion
- References

Save to: {paper_file}

Ensure academic rigor and proper citations."""

        # Reviewer evaluates
        review_prompt = f"""{self.get_reviewer_prompt()}

TASK: Review the research paper

Read the paper from: {paper_file}

Provide a thorough peer review with:
- Scores (1-10) for originality, quality, clarity, significance, soundness
- Overall recommendation
- Strengths and weaknesses
- Suggestions for improvement

Save your review as JSON to: {review_file}"""

        return [
            {
                "agent_type": "professor",
                "task": paper_prompt,
                "output_file": str(paper_file),
                "description": "Paper writing by Professor"
            },
            {
                "agent_type": "reviewer",
                "task": review_prompt,
                "output_file": str(review_file),
                "description": "Paper review by Reviewer",
                "depends_on": "paper"
            }
        ]

    def get_all_tasks(self) -> Dict[str, list]:
        """Get all tasks organized by phase."""
        return {
            "literature_review": self.generate_literature_review_tasks(),
            "plan_formulation": self.generate_plan_formulation_tasks(),
            "experimentation": self.generate_experimentation_tasks(),
            "paper_writing": self.generate_paper_writing_tasks()
        }

    def print_execution_instructions(self):
        """Print instructions for executing with Claude Code Task tool."""
        tasks = self.get_all_tasks()

        print("=" * 70)
        print("CLAUDE CODE MULTI-AGENT RESEARCH WORKFLOW")
        print("=" * 70)
        print(f"\nResearch Topic: {self.research_topic}")
        print(f"Output Directory: {self.output_dir}")
        print(f"Model: {self.config['agent_model']}")
        print("\n" + "=" * 70)
        print("EXECUTION PLAN")
        print("=" * 70)

        for phase, phase_tasks in tasks.items():
            print(f"\n## Phase: {phase.replace('_', ' ').title()}")
            print("-" * 50)
            for i, task in enumerate(phase_tasks, 1):
                print(f"\n  Task {i}: {task['description']}")
                print(f"  Agent: {task['agent_type']}")
                print(f"  Output: {task['output_file']}")
                if "depends_on" in task:
                    print(f"  Depends on: {task['depends_on']}")

        print("\n" + "=" * 70)
        print("TO EXECUTE THIS WORKFLOW:")
        print("=" * 70)
        print("""
Use Claude Code's Task tool to spawn each agent:

```python
# Example for Literature Review
Task(
    description="Literature review by PhD Student",
    prompt=orchestrator.generate_literature_review_tasks()[0]["task"],
    subagent_type="Explore",  # or "general-purpose"
    model="haiku"  # Use haiku for cost efficiency
)
```

IMPORTANT:
1. Execute tasks in order (respecting dependencies)
2. Wait for each task to complete before dependent tasks
3. Each agent saves its output to the specified file
4. Review outputs before proceeding to next phase

For automatic execution, run:
    python claude_multiagent_runner.py --topic "your topic"
""")

        # Save task manifest
        manifest_file = self.output_dir / "task_manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(tasks, f, indent=2)
        print(f"\nTask manifest saved to: {manifest_file}")


def create_orchestrator(topic: str, **kwargs) -> MultiAgentOrchestrator:
    """Factory function to create orchestrator."""
    return MultiAgentOrchestrator(topic, **kwargs)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Multi-Agent Research Orchestrator")
    parser.add_argument("--topic", type=str, required=True, help="Research topic")
    parser.add_argument("--output-dir", type=str, default="./multi_agent_research")
    parser.add_argument("--papers", type=int, default=5)
    parser.add_argument("--model", type=str, default="haiku", choices=["haiku", "sonnet", "opus"])

    args = parser.parse_args()

    orchestrator = MultiAgentOrchestrator(
        research_topic=args.topic,
        output_dir=args.output_dir,
        config={
            "num_papers": args.papers,
            "agent_model": args.model
        }
    )

    orchestrator.print_execution_instructions()
