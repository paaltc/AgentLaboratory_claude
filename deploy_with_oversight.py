#!/usr/bin/env python3
"""
Agent Laboratory - Claude Sonnet 4.5 & Haiku 4.5 Deployment with Human Oversight

This script runs the full research workflow with:
- Claude Sonnet 4.5 as the main agent (agent_model_backbone)
- Claude Haiku 4.5 as the literature review agent
- Human oversight enabled on ALL 7 phases
- Token management and checkpoint system enabled

Usage:
    python3 deploy_with_oversight.py [--topic "your research topic"]

Environment:
    ANTHROPIC_API_KEY: Required - your Claude API key

Example:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python3 deploy_with_oversight.py --topic "prompt engineering for math problems"
"""

import os
import sys
import argparse
from ai_lab_repo import LaboratoryWorkflow

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Deploy Agent Laboratory with Claude Sonnet 4.5 and human oversight"
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Research topic for the agents to explore"
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=50,
        help="Maximum steps for exploration (default: 50)"
    )
    parser.add_argument(
        "--papers",
        type=int,
        default=5,
        help="Number of papers to review in literature phase (default: 5)"
    )

    args = parser.parse_args()

    # Check API key - works with explicit key OR Claude Code Web authentication
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    # If no explicit key, Claude Code Web will use built-in authentication
    if not anthropic_key:
        anthropic_base_url = os.getenv("ANTHROPIC_BASE_URL")
        if anthropic_base_url:
            print("✓ Using Claude Code Web authentication (no explicit API key needed)")
        else:
            print("ERROR: Neither ANTHROPIC_API_KEY nor Claude Code Web environment detected")
            print("Please either:")
            print("  1. Export API key: export ANTHROPIC_API_KEY='sk-ant-...'")
            print("  2. Or run in Claude Code Web where authentication is built-in")
            sys.exit(1)

    # Get research topic
    if args.topic:
        research_topic = args.topic
    else:
        print("\n" + "="*70)
        print("AGENT LABORATORY - CLAUDE DEPLOYMENT WITH HUMAN OVERSIGHT")
        print("="*70)
        print("\nModels being used:")
        print("  • Agent Backbone: Claude Sonnet 4.5")
        print("  • Literature Review: Claude Haiku 4.5")
        print("  • Human Oversight: ENABLED on all 7 phases")
        print("\n" + "-"*70)
        research_topic = input("\nEnter your research topic: ").strip()
        if not research_topic:
            print("ERROR: Research topic required")
            sys.exit(1)

    print(f"\nResearch Topic: {research_topic}")
    print(f"Max Steps: {args.steps}")
    print(f"Papers to Review: {args.papers}")

    # Define human oversight for all phases
    # You will see the output of each phase and can approve/reject it
    human_in_loop_flag = {
        "literature review": True,
        "plan formulation": True,
        "data preparation": True,
        "running experiments": True,
        "results interpretation": True,
        "report writing": True,
        "report refinement": True
    }

    print("\n" + "="*70)
    print("HUMAN OVERSIGHT ENABLED FOR ALL PHASES")
    print("="*70)
    print("\nYou will be asked to review each phase output.")
    print("For each phase, you can:")
    print("  • (y) Accept and continue")
    print("  • (n) Reject and provide feedback for improvement")
    print("\nCheckpoints are saved automatically after each phase.")
    print("=" * 70 + "\n")

    # Initialize the workflow
    lab = LaboratoryWorkflow(
        research_topic=research_topic,
        openai_api_key=None,  # We're using Claude, not OpenAI
        agent_model_backbone="claude-sonnet-4-5",  # Main agent: Sonnet 4.5
        max_steps=args.steps,
        num_papers_lit_review=args.papers,
        human_in_loop_flag=human_in_loop_flag,
        compile_pdf=False,  # Skip PDF compilation for speed
        mlesolver_max_steps=2,
        papersolver_max_steps=2
    )

    # Run the research workflow
    print("\nStarting research workflow...\n")
    try:
        lab.perform_research()
        print("\n" + "="*70)
        print("RESEARCH WORKFLOW COMPLETED SUCCESSFULLY")
        print("="*70)
        print(f"\nResults saved in: {lab.lab_dir}")
        print("\nGenerated artifacts:")
        print("  • literature_review.txt - Summary of reviewed papers")
        print("  • research_plan.txt - The research plan")
        print("  • data_preparation.py - Data loading code")
        print("  • experiments/experiment_code.py - Experiment implementation")
        print("  • experiments/results.json - Experiment results")
        print("  • interpretation.txt - Results analysis")
        print("  • report.tex - LaTeX source for the paper")
        print("  • readme.md - Markdown summary")
        print("  • reviews/ - Peer review feedback")
        print("="*70 + "\n")

    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted by user")
        print("Your progress has been saved in checkpoints")
        print(f"Resume later with: python3 deploy_with_oversight.py --topic '{research_topic}'")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        print("Your progress has been saved in checkpoints")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
