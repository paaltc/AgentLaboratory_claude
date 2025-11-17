#!/usr/bin/env python3
"""
Claude Code Research Lab - Main Entry Point
Runs autonomous AI-driven research workflows using Claude
"""
import argparse
import os
import sys
from pathlib import Path

from claude_config import ResearchConfig, load_environment_config, create_default_config
from claude_workflow import ClaudeResearchWorkflow
from claude_inference import get_current_cost, get_token_stats


def main():
    parser = argparse.ArgumentParser(
        description="Claude Code Research Lab - Autonomous ML Research",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings
  python run_claude_research.py --topic "Few-shot learning in NLP"

  # Run with custom configuration file
  python run_claude_research.py --config my_config.json

  # Run with more papers and experiments
  python run_claude_research.py --topic "Vision transformers" --papers 10 --experiments 5

  # Create default config file
  python run_claude_research.py --create-config my_config.json

  # Run with human-in-the-loop
  python run_claude_research.py --topic "RL for robotics" --human-in-loop

Environment Variables:
  ANTHROPIC_API_KEY     - Required: Your Anthropic API key
  CLAUDE_RESEARCH_TOPIC - Override research topic
  CLAUDE_MODEL          - Override model (default: claude-sonnet-4-5-20250929)
  CLAUDE_MAX_BUDGET     - Override max budget in USD
  CLAUDE_OUTPUT_DIR     - Override output directory
        """
    )

    # Research settings
    parser.add_argument(
        "--topic",
        type=str,
        help="Research topic/question to investigate"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to JSON configuration file"
    )
    parser.add_argument(
        "--create-config",
        type=str,
        metavar="PATH",
        help="Create a default configuration file at specified path"
    )

    # Workflow parameters
    parser.add_argument(
        "--papers",
        type=int,
        default=5,
        help="Number of papers to review (default: 5)"
    )
    parser.add_argument(
        "--experiments",
        type=int,
        default=3,
        help="Max experiment iterations (default: 3)"
    )
    parser.add_argument(
        "--paper-iterations",
        type=int,
        default=2,
        help="Max paper writing iterations (default: 2)"
    )

    # Model settings
    parser.add_argument(
        "--model",
        type=str,
        default="claude-sonnet-4-5-20250929",
        help="Claude model to use"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature (default: 0.7)"
    )

    # Output settings
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./research_output",
        help="Output directory for results (default: ./research_output)"
    )
    parser.add_argument(
        "--no-checkpoints",
        action="store_true",
        help="Disable checkpoint saving"
    )

    # Budget and safety
    parser.add_argument(
        "--max-budget",
        type=float,
        default=50.0,
        help="Maximum budget in USD (default: 50.0)"
    )

    # Interaction modes
    parser.add_argument(
        "--human-in-loop",
        action="store_true",
        help="Enable human-in-the-loop review at each phase"
    )
    parser.add_argument(
        "--copilot-mode",
        action="store_true",
        help="Run in copilot mode (more human interaction)"
    )

    # Utility options
    parser.add_argument(
        "--resume",
        type=str,
        metavar="CHECKPOINT",
        help="Resume from a checkpoint file"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show configuration without running"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Claude Code Research Lab v0.1.0"
    )

    args = parser.parse_args()

    # Handle config creation
    if args.create_config:
        config = create_default_config(args.create_config)
        print(f"Configuration file created: {args.create_config}")
        print("\nYou can now edit this file and run:")
        print(f"  python run_claude_research.py --config {args.create_config}")
        return 0

    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("\nPlease set your Anthropic API key:")
        print('  export ANTHROPIC_API_KEY="your-key-here"')
        print("\nOr create a .env file with:")
        print('  ANTHROPIC_API_KEY=your-key-here')
        return 1

    # Build configuration
    if args.config:
        # Load from file
        print(f"Loading configuration from: {args.config}")
        config = ResearchConfig.from_file(args.config)
    else:
        # Build from arguments and environment
        config = ResearchConfig()

    # Override with environment variables
    env_config = load_environment_config()
    for key, value in env_config.items():
        setattr(config, key, value)

    # Override with command line arguments
    if args.topic:
        config.research_topic = args.topic
    if args.papers:
        config.num_papers_lit_review = args.papers
    if args.experiments:
        config.max_experiment_iterations = args.experiments
    if args.paper_iterations:
        config.max_paper_iterations = args.paper_iterations
    if args.model:
        config.model = args.model
    if args.temperature:
        config.temperature = args.temperature
    if args.output_dir:
        config.output_dir = args.output_dir
    if args.no_checkpoints:
        config.save_checkpoints = False
    if args.max_budget:
        config.max_budget_usd = args.max_budget
    if args.human_in_loop:
        config.human_in_loop = True
    if args.copilot_mode:
        config.copilot_mode = True

    # Validate configuration
    if not config.validate():
        print("Invalid configuration. Please fix the errors above.")
        return 1

    # Ensure we have a research topic
    if not config.research_topic or config.research_topic == "Novel approaches for machine learning":
        if not args.topic:
            print("Error: No research topic specified")
            print("Use --topic to specify a research topic")
            print('  Example: --topic "Few-shot learning in NLP"')
            return 1

    # Show configuration
    print("=" * 60)
    print("Claude Code Research Lab")
    print("=" * 60)
    print(f"Research Topic: {config.research_topic}")
    print(f"Model: {config.model}")
    print(f"Papers to Review: {config.num_papers_lit_review}")
    print(f"Max Experiments: {config.max_experiment_iterations}")
    print(f"Max Paper Iterations: {config.max_paper_iterations}")
    print(f"Max Budget: ${config.max_budget_usd:.2f}")
    print(f"Output Directory: {config.output_dir}")
    print(f"Human-in-Loop: {config.human_in_loop}")
    print(f"Save Checkpoints: {config.save_checkpoints}")
    print("=" * 60)

    if args.dry_run:
        print("\n[DRY RUN] Configuration validated. Would run with above settings.")
        print("\nFull configuration:")
        print(config.to_json())
        return 0

    # Resume from checkpoint if requested
    if args.resume:
        print(f"\nResuming from checkpoint: {args.resume}")
        workflow = ClaudeResearchWorkflow.load_checkpoint(args.resume)
    else:
        # Create workflow
        workflow = ClaudeResearchWorkflow(
            research_topic=config.research_topic,
            output_dir=config.output_dir,
            config=config.to_dict()
        )

    # Run research
    print("\nStarting research workflow...")
    print("(Press Ctrl+C to interrupt)\n")

    try:
        result = workflow.perform_research()

        # Print final summary
        print("\n" + "=" * 60)
        print("RESEARCH COMPLETE")
        print("=" * 60)
        print(f"Literature Review: {len(str(result['literature']))} chars")
        print(f"Research Plan: {len(result['plan'])} chars")
        print(f"Experiment Code: {len(result['experiment_code'])} chars")
        print(f"Final Paper: {len(result['report'])} chars")
        print(f"\nTotal Cost: ${get_current_cost():.6f}")
        print(f"Output Directory: {config.output_dir}")

        # Show token stats
        stats = get_token_stats()
        print("\nToken Usage:")
        for model, usage in stats.items():
            print(f"  {model}:")
            print(f"    Input: {usage['input_tokens']:,}")
            print(f"    Output: {usage['output_tokens']:,}")
            print(f"    Total: {usage['total_tokens']:,}")

        return 0

    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted by user.")
        print(f"Current cost: ${get_current_cost():.6f}")
        print(f"Checkpoints saved to: {config.output_dir}/checkpoints/")
        return 130

    except Exception as e:
        print(f"\nError during research: {str(e)}")
        print(f"Current cost: ${get_current_cost():.6f}")
        if config.save_checkpoints:
            print(f"Check {config.output_dir}/checkpoints/ for recovery.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
