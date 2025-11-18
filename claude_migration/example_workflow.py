#!/usr/bin/env python3
"""
Example: Running Claude Migration Workflow

Demonstrates how to use the command-based migration system that maintains
compatibility with the original AgentLaboratory behavior.
"""
import os
from claude_workflow_orchestrator import AgentLabWorkflow
from claude_human_loop import HumanCheckpoint


def example_basic_workflow():
    """
    Basic example - run workflow without human-in-loop.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE: Basic Automated Workflow")
    print("=" * 70 + "\n")

    # Initialize workflow
    workflow = AgentLabWorkflow(
        research_topic="Using transformers for time series forecasting",
        output_dir="./example_output",
        human_checkpoints=HumanCheckpoint.get_default_config(human_mode=False),
        max_steps=10,
        num_papers_lit_review=3,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        verbose=True
    )

    # Run phases
    try:
        workflow.run_all_phases()
        print("\n✓ Workflow completed successfully!")

    except Exception as e:
        print(f"\n✗ Workflow failed: {str(e)}")


def example_human_in_loop():
    """
    Example with human-in-loop enabled for all phases.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE: Workflow with Human-in-Loop")
    print("=" * 70 + "\n")

    # Enable human checkpoints
    human_config = HumanCheckpoint.get_default_config(human_mode=True)

    workflow = AgentLabWorkflow(
        research_topic="Self-supervised learning for protein structure prediction",
        output_dir="./example_output_human",
        human_checkpoints=human_config,
        max_steps=15,
        num_papers_lit_review=5,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        verbose=True
    )

    # Run with human oversight
    try:
        workflow.run_all_phases()
        print("\n✓ Workflow completed with human approval!")

    except Exception as e:
        print(f"\n✗ Workflow failed: {str(e)}")


def example_with_notes():
    """
    Example with predefined notes/guidance for agents.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE: Workflow with Agent Notes")
    print("=" * 70 + "\n")

    # Define notes for agents
    notes = [
        {
            "phases": ["literature review", "plan formulation"],
            "note": "Focus on recent papers from 2023-2024 using transformer architectures"
        },
        {
            "phases": ["data preparation"],
            "note": "Use only publicly available datasets from HuggingFace"
        }
    ]

    workflow = AgentLabWorkflow(
        research_topic="Multimodal learning for medical image analysis",
        output_dir="./example_output_notes",
        human_checkpoints=HumanCheckpoint.get_default_config(human_mode=False),
        max_steps=20,
        num_papers_lit_review=5,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        notes=notes,
        verbose=True
    )

    try:
        workflow.run_all_phases()
        print("\n✓ Workflow completed with guidance notes!")

    except Exception as e:
        print(f"\n✗ Workflow failed: {str(e)}")


def example_single_phase():
    """
    Example: Run just the literature review phase.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE: Single Phase (Literature Review)")
    print("=" * 70 + "\n")

    workflow = AgentLabWorkflow(
        research_topic="Graph neural networks for molecular property prediction",
        output_dir="./example_output_litreview",
        human_checkpoints={"literature review": True},
        max_steps=15,
        num_papers_lit_review=5,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        verbose=True
    )

    try:
        workflow.run_phase_literature_review()
        print(f"\nLiterature Review Summary:")
        print("-" * 70)
        print(workflow.state["lit_review_sum"])
        print("-" * 70)

    except Exception as e:
        print(f"\n✗ Phase failed: {str(e)}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        example_name = sys.argv[1]

        if example_name == "basic":
            example_basic_workflow()
        elif example_name == "human":
            example_human_in_loop()
        elif example_name == "notes":
            example_with_notes()
        elif example_name == "single":
            example_single_phase()
        else:
            print(f"Unknown example: {example_name}")
            print("Available: basic, human, notes, single")
    else:
        print("Usage: python example_workflow.py <example_name>")
        print("\nAvailable examples:")
        print("  basic  - Automated workflow without human oversight")
        print("  human  - Workflow with human-in-loop checkpoints")
        print("  notes  - Workflow with predefined agent guidance")
        print("  single - Run only literature review phase")
        print("\nExample:")
        print("  python example_workflow.py basic")
