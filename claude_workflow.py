"""
Claude Code Migration - Main Workflow Orchestrator
Replaces ai_lab_repo.py with Claude-native research workflow
"""
import os
import json
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

from claude_agents import (
    create_research_team,
    PhDStudentAgent,
    MLEngineerAgent,
    PostdocAgent,
    ProfessorAgent,
    ReviewerAgent
)
from claude_inference import get_current_cost, get_token_stats


class ClaudeResearchWorkflow:
    """
    Main workflow orchestrator for Claude Code-based research.
    Manages the end-to-end research process from literature review to paper writing.
    """

    PHASES = [
        ("literature_review", ["literature review"]),
        ("plan_formulation", ["plan formulation"]),
        ("experimentation", ["data preparation", "running experiments"]),
        ("results_interpretation", ["results interpretation", "report writing", "report refinement"]),
    ]

    def __init__(
        self,
        research_topic: str,
        api_key: Optional[str] = None,
        output_dir: str = "./research_output",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize research workflow.

        Args:
            research_topic: The main research question/topic
            api_key: Anthropic API key
            output_dir: Directory for saving outputs
            config: Configuration options
        """
        self.research_topic = research_topic
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Default configuration
        self.config = {
            "num_papers_lit_review": 5,
            "max_experiment_iterations": 3,
            "max_paper_iterations": 2,
            "max_refinement_cycles": 2,
            "human_in_loop": False,
            "save_checkpoints": True,
        }
        if config:
            self.config.update(config)

        # Create research team
        self.team = create_research_team(api_key=api_key)

        # Research state
        self.state = {
            "literature": [],
            "plan": "",
            "dataset_info": "",
            "experiment_code": "",
            "results": "",
            "interpretation": "",
            "report": "",
            "reviews": [],
            "phase_history": [],
            "start_time": datetime.now().isoformat(),
        }

        # Phase tracking
        self.current_phase = None
        self.phase_status = {}

    def perform_research(self) -> Dict[str, Any]:
        """
        Execute the full research workflow.

        Returns:
            Final research state including all artifacts
        """
        print("=" * 60)
        print(f"Starting Claude Code Research Workflow")
        print(f"Topic: {self.research_topic}")
        print(f"Output Directory: {self.output_dir}")
        print("=" * 60)

        try:
            # Phase 1: Literature Review
            self._run_literature_review()

            # Phase 2: Plan Formulation
            self._run_plan_formulation()

            # Phase 3: Experimentation
            self._run_experimentation()

            # Phase 4: Results and Writing
            self._run_results_and_writing()

            # Save final state
            self._save_checkpoint("final")

            print("\n" + "=" * 60)
            print("Research Workflow Complete!")
            print(f"Total Cost: ${get_current_cost():.6f}")
            print(f"Output saved to: {self.output_dir}")
            print("=" * 60)

        except Exception as e:
            print(f"\nError in workflow: {str(e)}")
            self._save_checkpoint("error")
            raise

        return self.state

    def _run_literature_review(self):
        """Phase 1: Conduct literature review."""
        print("\n" + "-" * 60)
        print("PHASE 1: Literature Review")
        print("-" * 60)

        self.current_phase = "literature_review"
        start_time = time.time()

        # PhD student conducts literature review
        phd = self.team["phd_student"]

        lit_review_prompt = f"""Conduct a comprehensive literature review on: {self.research_topic}

Please:
1. Search for relevant papers on arXiv
2. Identify {self.config['num_papers_lit_review']} most relevant papers
3. Summarize key findings, methods, and gaps in the literature
4. Identify potential research directions based on the gaps

Format your response as:
## Papers Reviewed
[List of papers with key findings]

## Key Methods and Approaches
[Summary of main methods]

## Research Gaps
[Identified gaps and opportunities]

## Recommended Research Direction
[Your suggestion based on the review]"""

        literature_summary = phd.inference(
            task=lit_review_prompt,
            context={"notes": "Focus on recent papers (2023-2025) if available."},
            phase="literature review",
            use_tools=True,
            print_cost=True
        )

        self.state["literature"] = literature_summary
        elapsed = time.time() - start_time

        print(f"\nLiterature review completed in {elapsed:.1f}s")
        print(f"Summary length: {len(literature_summary)} characters")

        self.phase_status["literature_review"] = {
            "completed": True,
            "duration": elapsed,
            "cost": get_current_cost()
        }

        if self.config["save_checkpoints"]:
            self._save_checkpoint("literature_review")

        # Human-in-loop check
        if self.config["human_in_loop"]:
            self._human_review("literature review", literature_summary)

    def _run_plan_formulation(self):
        """Phase 2: Formulate research plan."""
        print("\n" + "-" * 60)
        print("PHASE 2: Plan Formulation")
        print("-" * 60)

        self.current_phase = "plan_formulation"
        start_time = time.time()

        postdoc = self.team["postdoc"]
        phd = self.team["phd_student"]

        # Postdoc provides guidance
        guidance_prompt = f"""Based on the literature review below, provide guidance for formulating a research plan.

Research Topic: {self.research_topic}

Literature Review:
{self.state['literature'][:10000]}

Please suggest:
1. Specific hypotheses to test
2. Experimental methodology
3. Evaluation metrics
4. Potential challenges and mitigations"""

        postdoc_guidance = postdoc.inference(
            task=guidance_prompt,
            context={"literature": self.state["literature"]},
            phase="plan formulation",
            use_tools=False,
            print_cost=True
        )

        print("\nPostdoc guidance received.")

        # PhD student creates detailed plan
        plan_prompt = f"""Create a detailed research plan based on:

Research Topic: {self.research_topic}

Postdoc Guidance:
{postdoc_guidance}

Your plan should include:
1. Research objectives (specific, measurable)
2. Hypotheses to test
3. Data requirements
4. Experimental design
5. Evaluation criteria
6. Timeline and milestones
7. Expected outcomes

Format as a structured research proposal."""

        research_plan = phd.inference(
            task=plan_prompt,
            context={
                "literature": self.state["literature"],
                "feedback": postdoc_guidance
            },
            phase="plan formulation",
            use_tools=False,
            print_cost=True
        )

        self.state["plan"] = research_plan
        elapsed = time.time() - start_time

        print(f"\nPlan formulation completed in {elapsed:.1f}s")

        self.phase_status["plan_formulation"] = {
            "completed": True,
            "duration": elapsed,
            "cost": get_current_cost()
        }

        if self.config["save_checkpoints"]:
            self._save_checkpoint("plan_formulation")

        if self.config["human_in_loop"]:
            self._human_review("research plan", research_plan)

    def _run_experimentation(self):
        """Phase 3: Data preparation and experiments."""
        print("\n" + "-" * 60)
        print("PHASE 3: Experimentation")
        print("-" * 60)

        self.current_phase = "experimentation"
        start_time = time.time()

        ml_engineer = self.team["ml_engineer"]
        sw_engineer = self.team["sw_engineer"]

        # Data preparation
        print("\nStep 3.1: Data Preparation")

        data_prep_prompt = f"""Based on the research plan, identify and prepare the necessary datasets.

Research Plan:
{self.state['plan'][:5000]}

Please:
1. Search for appropriate datasets on Hugging Face
2. Write code to load and preprocess the data
3. Verify the data is suitable for the planned experiments

Provide the dataset selection rationale and loading code."""

        dataset_result = ml_engineer.inference(
            task=data_prep_prompt,
            context={"plan": self.state["plan"]},
            phase="data preparation",
            use_tools=True,
            print_cost=True
        )

        self.state["dataset_info"] = dataset_result
        print(f"Dataset preparation complete.")

        # Code implementation
        print("\nStep 3.2: Running Experiments")

        for iteration in range(self.config["max_experiment_iterations"]):
            print(f"\n  Experiment iteration {iteration + 1}/{self.config['max_experiment_iterations']}")

            if iteration == 0:
                experiment_prompt = f"""Implement the machine learning experiment based on the plan.

Research Plan:
{self.state['plan'][:3000]}

Dataset Info:
{self.state['dataset_info'][:2000]}

Please:
1. Write complete, runnable Python code for the experiment
2. Include data loading, model training, and evaluation
3. Implement proper logging of results
4. Handle potential errors gracefully

The code should be self-contained and reproducible."""
            else:
                experiment_prompt = f"""Improve the experiment based on previous results.

Previous Code:
{self.state['experiment_code'][:3000]}

Previous Results:
{self.state['results'][:2000]}

Please optimize the code to improve performance. Consider:
- Hyperparameter tuning
- Model architecture improvements
- Better preprocessing
- Additional evaluation metrics"""

            experiment_code = ml_engineer.inference(
                task=experiment_prompt,
                context={
                    "plan": self.state["plan"],
                    "code": self.state["experiment_code"] if iteration > 0 else "",
                    "results": self.state["results"] if iteration > 0 else ""
                },
                phase="running experiments",
                use_tools=True,
                print_cost=True
            )

            self.state["experiment_code"] = experiment_code

            # Extract and run code (simplified - in production would execute)
            results_summary = f"Iteration {iteration + 1} results:\n{experiment_code[-1000:]}"
            self.state["results"] = results_summary

        elapsed = time.time() - start_time

        print(f"\nExperimentation completed in {elapsed:.1f}s")

        self.phase_status["experimentation"] = {
            "completed": True,
            "duration": elapsed,
            "cost": get_current_cost()
        }

        if self.config["save_checkpoints"]:
            self._save_checkpoint("experimentation")

        if self.config["human_in_loop"]:
            self._human_review("experiment code", self.state["experiment_code"])

    def _run_results_and_writing(self):
        """Phase 4: Interpret results and write paper."""
        print("\n" + "-" * 60)
        print("PHASE 4: Results Interpretation and Paper Writing")
        print("-" * 60)

        self.current_phase = "results_interpretation"
        start_time = time.time()

        postdoc = self.team["postdoc"]
        phd = self.team["phd_student"]
        professor = self.team["professor"]
        reviewer = self.team["reviewer"]

        # Results interpretation
        print("\nStep 4.1: Interpreting Results")

        interpretation_prompt = f"""Analyze and interpret the experimental results.

Research Plan:
{self.state['plan'][:3000]}

Experiment Results:
{self.state['results'][:5000]}

Please provide:
1. Summary of key findings
2. Statistical analysis of results
3. Comparison with baseline/literature
4. Discussion of implications
5. Limitations and future work"""

        # Postdoc interprets first
        postdoc_interpretation = postdoc.inference(
            task=interpretation_prompt,
            context={
                "plan": self.state["plan"],
                "results": self.state["results"]
            },
            phase="results interpretation",
            use_tools=False,
            print_cost=True
        )

        # PhD student expands interpretation
        phd_interpretation = phd.inference(
            task=f"Expand on this interpretation with additional insights:\n{postdoc_interpretation}",
            context={
                "results": self.state["results"],
                "feedback": postdoc_interpretation
            },
            phase="results interpretation",
            use_tools=False,
            print_cost=True
        )

        self.state["interpretation"] = f"{postdoc_interpretation}\n\n{phd_interpretation}"

        # Paper writing
        print("\nStep 4.2: Writing Research Paper")

        for paper_iteration in range(self.config["max_paper_iterations"]):
            print(f"\n  Paper writing iteration {paper_iteration + 1}/{self.config['max_paper_iterations']}")

            if paper_iteration == 0:
                paper_prompt = f"""Write a complete research paper in LaTeX format.

Title: Research on {self.research_topic}

Literature Review:
{self.state['literature'][:3000]}

Methods (from plan):
{self.state['plan'][:3000]}

Results:
{self.state['results'][:2000]}

Interpretation:
{self.state['interpretation'][:3000]}

Include standard sections:
- Abstract
- Introduction
- Related Work
- Methods
- Experiments and Results
- Discussion
- Conclusion
- References

Write in academic style with proper LaTeX formatting."""
            else:
                paper_prompt = f"""Improve the paper based on reviewer feedback.

Current Paper:
{self.state['report'][:8000]}

Reviews:
{json.dumps(self.state['reviews'], indent=2)[:3000]}

Address the reviewers' concerns and strengthen weak sections."""

            paper_content = professor.inference(
                task=paper_prompt,
                context={
                    "literature": self.state["literature"],
                    "results": self.state["results"],
                    "feedback": json.dumps(self.state["reviews"]) if paper_iteration > 0 else ""
                },
                phase="report writing",
                use_tools=True,
                print_cost=True
            )

            self.state["report"] = paper_content

            # Get reviews
            if paper_iteration < self.config["max_paper_iterations"] - 1:
                print(f"\n  Getting peer reviews...")
                review = reviewer.review_paper(paper_content[:15000])
                self.state["reviews"].append(review)

        elapsed = time.time() - start_time

        print(f"\nPaper writing completed in {elapsed:.1f}s")

        self.phase_status["results_writing"] = {
            "completed": True,
            "duration": elapsed,
            "cost": get_current_cost()
        }

        # Save final paper
        paper_path = self.output_dir / "research_paper.tex"
        paper_path.write_text(self.state["report"])
        print(f"\nPaper saved to: {paper_path}")

        if self.config["save_checkpoints"]:
            self._save_checkpoint("final_paper")

    def _save_checkpoint(self, checkpoint_name: str):
        """Save current state to checkpoint file."""
        checkpoint_dir = self.output_dir / "checkpoints"
        checkpoint_dir.mkdir(exist_ok=True)

        checkpoint_path = checkpoint_dir / f"{checkpoint_name}.json"

        checkpoint_data = {
            "state": self.state,
            "phase_status": self.phase_status,
            "config": self.config,
            "timestamp": datetime.now().isoformat(),
            "cost": get_current_cost(),
            "token_stats": get_token_stats()
        }

        with open(checkpoint_path, "w") as f:
            json.dump(checkpoint_data, f, indent=2, default=str)

        print(f"Checkpoint saved: {checkpoint_path}")

    def _human_review(self, artifact_name: str, content: str):
        """Pause for human review (placeholder for human-in-loop)."""
        print(f"\n[Human Review Required] Please review the {artifact_name}:")
        print("-" * 40)
        print(content[:2000])
        if len(content) > 2000:
            print(f"\n... [{len(content) - 2000} more characters]")
        print("-" * 40)
        # In interactive mode, would wait for user input
        # input("Press Enter to continue...")

    @classmethod
    def load_checkpoint(cls, checkpoint_path: str) -> "ClaudeResearchWorkflow":
        """Load workflow from checkpoint file."""
        with open(checkpoint_path, "r") as f:
            checkpoint_data = json.load(f)

        # Create workflow with saved config
        workflow = cls(
            research_topic="Loaded from checkpoint",
            config=checkpoint_data["config"]
        )
        workflow.state = checkpoint_data["state"]
        workflow.phase_status = checkpoint_data["phase_status"]

        return workflow


def run_research(
    topic: str,
    api_key: Optional[str] = None,
    output_dir: str = "./research_output",
    **config_kwargs
) -> Dict[str, Any]:
    """
    Convenience function to run a complete research workflow.

    Args:
        topic: Research topic
        api_key: Anthropic API key
        output_dir: Output directory
        **config_kwargs: Additional configuration options

    Returns:
        Final research state
    """
    workflow = ClaudeResearchWorkflow(
        research_topic=topic,
        api_key=api_key,
        output_dir=output_dir,
        config=config_kwargs
    )

    return workflow.perform_research()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Claude Code Research Workflow")
    parser.add_argument(
        "--topic",
        type=str,
        default="Novel approaches for few-shot learning in NLP",
        help="Research topic"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./research_output",
        help="Output directory"
    )
    parser.add_argument(
        "--num-papers",
        type=int,
        default=5,
        help="Number of papers to review"
    )
    parser.add_argument(
        "--max-experiments",
        type=int,
        default=3,
        help="Max experiment iterations"
    )
    parser.add_argument(
        "--human-in-loop",
        action="store_true",
        help="Enable human-in-loop review"
    )

    args = parser.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set")
        print("Please set your API key:")
        print('  export ANTHROPIC_API_KEY="your-key-here"')
        exit(1)

    result = run_research(
        topic=args.topic,
        output_dir=args.output_dir,
        num_papers_lit_review=args.num_papers,
        max_experiment_iterations=args.max_experiments,
        human_in_loop=args.human_in_loop
    )

    print("\nFinal Research Summary:")
    print(f"- Literature items: {len(str(result['literature']))}")
    print(f"- Plan length: {len(result['plan'])} chars")
    print(f"- Code length: {len(result['experiment_code'])} chars")
    print(f"- Paper length: {len(result['report'])} chars")
    print(f"- Total cost: ${get_current_cost():.6f}")
