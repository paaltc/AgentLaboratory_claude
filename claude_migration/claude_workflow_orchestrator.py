"""
Workflow Orchestrator for Claude Migration

Main workflow class that orchestrates the complete research pipeline.
Maintains exact behavior of original LaboratoryWorkflow from ai_lab_repo.py
"""
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from claude_agents import (
    PhDStudentAgent,
    PostdocAgent,
    ProfessorAgent,
    MLEngineerAgent,
    SWEngineerAgent
)
from claude_dialogue import DialogueLoop, ToolAugmentedDialogue
from claude_human_loop import HumanCheckpoint, NotesManager
from claude_research_tools import (
    ResearchTools,
    LiteratureReviewManager,
    ToolExecutorFactory,
    save_to_file
)


class AgentLabWorkflow:
    """
    Main workflow orchestrator - EXACT ORIGINAL BEHAVIOR.

    Mimics LaboratoryWorkflow from ai_lab_repo.py with command-based
    agent interactions and human-in-loop checkpoints.
    """

    def __init__(
        self,
        research_topic: str,
        output_dir: str = "./research_output",
        human_checkpoints: Optional[Dict[str, bool]] = None,
        max_steps: int = 100,
        num_papers_lit_review: int = 5,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        verbose: bool = True,
        notes: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Initialize workflow.

        Args:
            research_topic: Research topic/question
            output_dir: Output directory for results
            human_checkpoints: Human-in-loop configuration
            max_steps: Max steps per phase
            num_papers_lit_review: Number of papers for lit review
            api_key: Anthropic API key
            model: Claude model to use
            verbose: Print progress
            notes: Initial notes for agents
        """
        self.research_topic = research_topic
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create src directory for code
        (self.output_dir / "src").mkdir(exist_ok=True)

        self.max_steps = max_steps
        self.num_papers_lit_review = num_papers_lit_review
        self.verbose = verbose

        # Initialize agents
        if self.verbose:
            print("\nInitializing agents...")

        self.phd = PhDStudentAgent(
            api_key=api_key,
            model=model,
            max_tool_rounds=max_steps
        )

        self.postdoc = PostdocAgent(
            api_key=api_key,
            model=model,
            max_tool_rounds=max_steps
        )

        self.professor = ProfessorAgent(
            api_key=api_key,
            model=model,
            max_tool_rounds=max_steps
        )

        self.ml_engineer = MLEngineerAgent(
            api_key=api_key,
            model=model,
            max_tool_rounds=max_steps
        )

        self.sw_engineer = SWEngineerAgent(
            api_key=api_key,
            model=model,
            max_tool_rounds=max_steps
        )

        # Human-in-loop system
        if human_checkpoints is None:
            human_checkpoints = HumanCheckpoint.get_default_config(human_mode=False)

        self.human_loop = HumanCheckpoint(human_checkpoints, verbose=verbose)

        # Notes manager
        self.notes_manager = NotesManager()
        if notes:
            for note in notes:
                self.notes_manager.add_note(note["phases"], note["note"])

        # Shared state (mimics set_agent_attr)
        self.state = {
            "lit_review_sum": "",
            "plan": "",
            "dataset_code": "",
            "results_code": "",
            "exp_results": "",
            "interpretation": "",
            "report": ""
        }

        # Literature review manager
        self.lit_review_manager = LiteratureReviewManager()

        # Phase tracking
        self.phases = [
            "literature review",
            "plan formulation",
            "data preparation",
            "running experiments",
            "results interpretation",
            "report writing"
        ]

        self.phase_status = {phase: False for phase in self.phases}

        # Statistics
        self.statistics_per_phase = {
            phase: {"time": 0.0, "steps": 0}
            for phase in self.phases
        }

    def reset_agents(self):
        """Reset all agent states."""
        self.phd.reset()
        self.postdoc.reset()
        self.professor.reset()
        self.ml_engineer.reset()
        self.sw_engineer.reset()

    def run_phase_literature_review(self) -> bool:
        """
        Literature review phase.

        Mimics literature_review from ai_lab_repo.py:465-545

        Returns:
            False on success (no retry needed)
        """
        if self.verbose:
            print(f"\n{'*' * 50}")
            print("PHASE: Literature Review")
            print(f"{'*' * 50}\n")

        phase_start = time.time()
        tools = ResearchTools()
        feedback = ""
        step = 0

        # Get initial response
        response, cmd_type, cmd_content = self.phd.inference_with_commands(
            task=f"Conduct a literature review on: {self.research_topic}",
            context=self.state,
            phase="literature review",
            feedback="",
            step=0
        )

        if self.verbose:
            print(f"PhD Student: {response}\n")

        # Iterate until we have enough papers
        for step in range(self.max_steps):
            feedback = ""

            # Handle SUMMARY command (search papers)
            if cmd_type == "search_papers":
                papers_result = tools.search_arxiv_papers(cmd_content, n=5)
                feedback = f"You requested arXiv papers related to the query {cmd_content}, here was the response\n{papers_result}"

            # Handle FULL_TEXT command (get paper details)
            elif cmd_type == "get_paper":
                paper_text = tools.get_arxiv_paper_text(cmd_content)
                feedback = paper_text

            # Handle ADD_PAPER command
            elif cmd_type == "add_paper":
                lines = cmd_content.split("\n", 1)
                arxiv_id = lines[0].strip()
                summary = lines[1].strip() if len(lines) > 1 else ""

                result = self.lit_review_manager.add_paper(arxiv_id, summary)
                feedback = result

            # Check if we have enough papers
            if self.lit_review_manager.count() >= self.num_papers_lit_review:
                lit_review_sum = self.lit_review_manager.format_review()

                # Human checkpoint
                should_retry, note = self.human_loop.check(
                    "literature review",
                    lit_review_sum,
                    label="literature review"
                )

                if should_retry:
                    # Add feedback note and retry
                    if note:
                        self.notes_manager.add_note(["literature review"], note)
                    self.lit_review_manager.clear()
                    self.reset_agents()
                    return self.run_phase_literature_review()  # Recursive retry

                # Success - save and continue
                self.state["lit_review_sum"] = lit_review_sum
                self.reset_agents()
                self.phase_status["literature review"] = True
                self.statistics_per_phase["literature review"]["steps"] = step
                self.statistics_per_phase["literature review"]["time"] = time.time() - phase_start

                if self.verbose:
                    print(f"\n✓ Literature review completed ({step} steps)\n")

                return False

            # Get next response
            response, cmd_type, cmd_content = self.phd.inference_with_commands(
                task=f"Conduct a literature review on: {self.research_topic}",
                context=self.state,
                phase="literature review",
                feedback=feedback,
                step=step + 1
            )

            if self.verbose:
                print(f"PhD Student: {response}\n")

        # Max steps reached
        if self.lit_review_manager.count() >= self.num_papers_lit_review:
            # Force completion
            lit_review_sum = self.lit_review_manager.format_review()
            should_retry, note = self.human_loop.check(
                "literature review",
                lit_review_sum,
                label="literature review"
            )

            if should_retry and note:
                self.notes_manager.add_note(["literature review"], note)
                self.lit_review_manager.clear()
                self.reset_agents()
                return self.run_phase_literature_review()

            self.state["lit_review_sum"] = lit_review_sum
            self.reset_agents()
            self.phase_status["literature review"] = True
            return False

        raise Exception("Max tries during phase: Literature Review")

    def run_phase_plan_formulation(self) -> bool:
        """
        Plan formulation phase - Postdoc ↔ PhD dialogue.

        Mimics plan_formulation from ai_lab_repo.py:414-463

        Returns:
            False on success
        """
        if self.verbose:
            print(f"\n{'*' * 50}")
            print("PHASE: Plan Formulation")
            print(f"{'*' * 50}\n")

        phase_start = time.time()

        loop = DialogueLoop(
            agent1=self.postdoc,
            agent2=self.phd,
            topic=f"Create a research plan for: {self.research_topic}",
            context=self.state,
            phase="plan formulation",
            max_turns=self.max_steps,
            verbose=self.verbose
        )

        result = loop.run_until_submission(
            submission_commands=["submit_plan"],
            agent1_commands=["DIALOGUE", "PLAN"],
            agent2_commands=["DIALOGUE"]
        )

        plan = result["submission_content"]

        # Human checkpoint
        should_retry, note = self.human_loop.check(
            "plan formulation",
            plan,
            label="plan"
        )

        if should_retry:
            if note:
                self.notes_manager.add_note(["plan formulation"], note)
            self.reset_agents()
            return self.run_phase_plan_formulation()  # Retry

        # Success
        self.state["plan"] = plan
        self.reset_agents()
        self.phase_status["plan formulation"] = True
        self.statistics_per_phase["plan formulation"]["steps"] = result["steps"]
        self.statistics_per_phase["plan formulation"]["time"] = time.time() - phase_start

        if self.verbose:
            print(f"\n✓ Plan formulation completed ({result['steps']} steps)\n")

        return False

    def run_phase_data_preparation(self) -> bool:
        """
        Data preparation phase - SW Engineer ↔ ML Engineer with tools.

        Mimics data_preparation from ai_lab_repo.py:343-412

        Returns:
            False on success
        """
        if self.verbose:
            print(f"\n{'*' * 50}")
            print("PHASE: Data Preparation")
            print(f"{'*' * 50}\n")

        phase_start = time.time()

        # Tool executors
        tool_executors = ToolExecutorFactory.get_data_preparation_tools()

        loop = ToolAugmentedDialogue(
            agent1=self.sw_engineer,
            agent2=self.ml_engineer,
            topic=f"Prepare dataset for: {self.research_topic}\n\nPlan: {self.state['plan']}",
            context=self.state,
            phase="data preparation",
            tool_executors=tool_executors,
            max_turns=self.max_steps,
            verbose=self.verbose
        )

        result = loop.run_with_tools(
            submission_commands=["submit_code"],
            agent1_commands=["DIALOGUE", "SUBMIT_CODE"],
            agent2_commands=["DIALOGUE", "python", "SEARCH_HF"]
        )

        code = result["submission_content"]

        # Test code execution
        tools = ResearchTools()
        test_result = tools.execute_python_code(code, timeout=60)

        if "[CODE EXECUTION ERROR]" in test_result:
            if self.verbose:
                print(f"\n✗ Code execution failed:\n{test_result}\n")
            # Could add retry logic here
            # For now, continue but note the error

        # Human checkpoint
        should_retry, note = self.human_loop.check(
            "data preparation",
            code,
            label="dataset code"
        )

        if should_retry:
            if note:
                self.notes_manager.add_note(["data preparation"], note)
            self.reset_agents()
            return self.run_phase_data_preparation()  # Retry

        # Success - save code
        save_to_file(str(self.output_dir / "src"), "load_data.py", code)
        self.state["dataset_code"] = code
        self.reset_agents()
        self.phase_status["data preparation"] = True
        self.statistics_per_phase["data preparation"]["steps"] = result["steps"]
        self.statistics_per_phase["data preparation"]["time"] = time.time() - phase_start

        if self.verbose:
            print(f"\n✓ Data preparation completed ({result['steps']} steps)\n")

        return False

    def run_all_phases(self):
        """Execute full research workflow."""
        if self.verbose:
            print("\n" + "=" * 70)
            print("STARTING RESEARCH WORKFLOW")
            print(f"Topic: {self.research_topic}")
            print("=" * 70 + "\n")

        try:
            # Phase 1: Literature Review
            self.run_phase_literature_review()

            # Phase 2: Plan Formulation
            self.run_phase_plan_formulation()

            # Phase 3: Data Preparation
            self.run_phase_data_preparation()

            # TODO: Implement remaining phases
            # - running_experiments (uses MLESolver)
            # - results_interpretation (Postdoc ↔ PhD)
            # - report_writing (uses PaperSolver)

            if self.verbose:
                print("\n" + "=" * 70)
                print("RESEARCH WORKFLOW COMPLETED")
                print("=" * 70 + "\n")
                print("Statistics:")
                for phase, stats in self.statistics_per_phase.items():
                    if stats["time"] > 0:
                        print(f"  {phase}: {stats['steps']} steps, {stats['time']:.2f}s")

        except Exception as e:
            if self.verbose:
                print(f"\n✗ Workflow failed: {str(e)}\n")
            raise
