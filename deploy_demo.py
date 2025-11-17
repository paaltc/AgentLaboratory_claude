#!/usr/bin/env python3
"""
Agent Laboratory - Claude Sonnet 4.5 Deployment Demo with Human Oversight

Simplified deployment for demonstration with human oversight on each phase.
"""

import os
import sys

def check_api_key():
    """Verify API key is set"""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        print("\n" + "="*70)
        print("ERROR: ANTHROPIC_API_KEY not set")
        print("="*70)
        print("\nSet your API key:")
        print("  export ANTHROPIC_API_KEY='sk-ant-...'")
        print("\nThen run: python3 deploy_demo.py\n")
        sys.exit(1)
    return key

def show_deployment_info():
    """Display deployment information"""
    print("\n" + "="*70)
    print("AGENT LABORATORY - CLAUDE DEPLOYMENT WITH HUMAN OVERSIGHT")
    print("="*70)

    print("\n📊 DEPLOYMENT CONFIGURATION")
    print("-" * 70)
    print("\n✓ Agent Backbone: Claude Sonnet 4.5")
    print("  - Advanced reasoning and planning")
    print("  - Used for: All core research phases")
    print("  - Cost: ~$0.003 per 1K input tokens")

    print("\n✓ Literature Review: Claude Haiku 4.5")
    print("  - Fast, efficient processing")
    print("  - Used for: Paper search and summarization")
    print("  - Cost: ~$0.0008 per 1K input tokens")

    print("\n✓ Human Oversight: ENABLED")
    print("  - Phases with review: ALL 7 phases")
    print("  - For each phase: Accept or request improvements")
    print("  - Automatic checkpointing: After each phase")

    print("\n" + "="*70)
    print("RESEARCH WORKFLOW (7 PHASES)")
    print("="*70)

    phases = [
        ("1. Literature Review", "Search arXiv, summarize papers", "3-5 min"),
        ("2. Plan Formulation", "Design research methodology", "5-10 min"),
        ("3. Data Preparation", "Generate code for data loading", "5-10 min"),
        ("4. Running Experiments", "Implement and execute experiments", "10-15 min"),
        ("5. Results Interpretation", "Analyze findings and implications", "5-10 min"),
        ("6. Report Writing", "Generate full research paper", "10-20 min"),
        ("7. Report Refinement", "Peer review and feedback", "10-15 min"),
    ]

    for phase, task, time in phases:
        print(f"\n{phase}")
        print(f"  Task: {task}")
        print(f"  Est. time: {time}")

    print("\n" + "="*70)
    print("WHAT YOU'LL SEE")
    print("="*70)
    print("""
Each phase will:
  1. Execute the research task
  2. Display the output
  3. Ask for your feedback:
     • (Y) Accept and continue
     • (N) Request improvements

If you choose (N):
  • You can provide specific feedback
  • The agent will revise and try again
  • Automatic checkpointing saves progress
    """)

    print("="*70)
    print("TRYING TO START WORKFLOW...")
    print("="*70)

def show_missing_dependencies():
    """Show what modules are missing"""
    print("\n" + "="*70)
    print("NOTE: MISSING OPTIONAL DEPENDENCIES")
    print("="*70)
    print("""
Some optional modules are not installed:
  • PyPDF2 (for PDF handling)
  • pandas (for data processing)
  • torch (for model inference)
  • Other advanced features

To install all dependencies:
  pip install -r requirements.txt

For a quick test without all dependencies:
  • Core LLM features work (anthropic, openai)
  • Literature review and planning work
  • Advanced features may be limited

The system will work with available dependencies.
    """)

def main():
    # Check API key
    api_key = check_api_key()
    print(f"\n✓ API Key detected: {api_key[:20]}...")

    # Show deployment info
    show_deployment_info()

    # Try to import main module
    print("\n📦 Checking module imports...")

    try:
        from ai_lab_repo import LaboratoryWorkflow
        print("✓ LaboratoryWorkflow loaded")
    except ImportError as e:
        print(f"⚠ Could not import LaboratoryWorkflow: {e}")
        show_missing_dependencies()
        print("\nTo proceed with full deployment:")
        print("  pip install -r requirements.txt")
        print("  python3 deploy_with_oversight.py --topic 'your topic'")
        sys.exit(1)

    # Proceed with demo
    print("\n" + "="*70)
    print("DEPLOYMENT READY")
    print("="*70)

    research_topic = input("\n🔬 Enter your research topic: ").strip()
    if not research_topic:
        print("ERROR: Topic required")
        sys.exit(1)

    print(f"\n✓ Topic: {research_topic}")
    print("✓ Model: Claude Sonnet 4.5")
    print("✓ Oversight: Enabled on all phases")

    print("\n" + "="*70)
    print("Initializing workflow...")
    print("="*70 + "\n")

    # Set up human oversight for all phases
    human_in_loop_flag = {
        "literature review": True,
        "plan formulation": True,
        "data preparation": True,
        "running experiments": True,
        "results interpretation": True,
        "report writing": True,
        "report refinement": True
    }

    try:
        # Initialize workflow
        lab = LaboratoryWorkflow(
            research_topic=research_topic,
            openai_api_key=None,
            agent_model_backbone="claude-sonnet-4-5",
            max_steps=30,
            num_papers_lit_review=3,
            human_in_loop_flag=human_in_loop_flag,
            compile_pdf=False,
            mlesolver_max_steps=2,
            papersolver_max_steps=2
        )

        print("✓ Workflow initialized\n")
        print("Starting research...\n")

        # Run research
        lab.perform_research()

        print("\n" + "="*70)
        print("✓ RESEARCH COMPLETED")
        print("="*70)
        print(f"\nResults saved in: {lab.lab_dir}\n")

    except KeyboardInterrupt:
        print("\n\n⚠ Workflow interrupted by user")
        print("Your progress has been saved in checkpoints")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
