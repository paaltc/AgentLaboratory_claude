"""
Claude Code Migration - Configuration Management
Replaces YAML-based configuration with Python-native approach
"""
import os
import json
from typing import Any, Dict, Optional
from pathlib import Path
from dataclasses import dataclass, field, asdict


@dataclass
class ResearchConfig:
    """Configuration for Claude Code research workflow."""

    # Research settings
    research_topic: str = "Novel approaches for machine learning"
    num_papers_lit_review: int = 5
    num_papers_to_write: int = 1

    # Model settings
    model: str = "claude-sonnet-4-5-20250929"
    temperature: float = 0.7
    max_tokens: int = 8192

    # Execution settings
    max_experiment_iterations: int = 3
    max_paper_iterations: int = 2
    max_refinement_cycles: int = 2
    max_tool_rounds: int = 10

    # Budget and safety
    max_budget_usd: float = 50.0
    timeout_seconds: int = 600
    sandboxed_execution: bool = True

    # Human interaction
    human_in_loop: bool = False
    copilot_mode: bool = False

    # Output settings
    output_dir: str = "./research_output"
    save_checkpoints: bool = True
    compile_latex: bool = False

    # Task-specific notes
    task_notes: Dict[str, list] = field(default_factory=lambda: {
        "literature_review": [],
        "plan_formulation": [],
        "data_preparation": [],
        "running_experiments": [],
        "results_interpretation": [],
        "report_writing": [],
        "report_refinement": []
    })

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert config to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResearchConfig":
        """Create config from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def from_json(cls, json_str: str) -> "ResearchConfig":
        """Create config from JSON string."""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_file(cls, file_path: str) -> "ResearchConfig":
        """Load config from JSON file."""
        with open(file_path, "r") as f:
            return cls.from_json(f.read())

    def save(self, file_path: str):
        """Save config to JSON file."""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            f.write(self.to_json())

    def validate(self) -> bool:
        """Validate configuration settings."""
        errors = []

        if self.num_papers_lit_review < 1:
            errors.append("num_papers_lit_review must be >= 1")

        if self.max_experiment_iterations < 1:
            errors.append("max_experiment_iterations must be >= 1")

        if self.max_budget_usd <= 0:
            errors.append("max_budget_usd must be > 0")

        if self.temperature < 0 or self.temperature > 2:
            errors.append("temperature must be between 0 and 2")

        if self.max_tokens < 1 or self.max_tokens > 100000:
            errors.append("max_tokens must be between 1 and 100000")

        if errors:
            for error in errors:
                print(f"Config Error: {error}")
            return False

        return True


def create_default_config(output_path: Optional[str] = None) -> ResearchConfig:
    """
    Create a default configuration file.

    Args:
        output_path: Optional path to save the config

    Returns:
        Default ResearchConfig
    """
    config = ResearchConfig(
        research_topic="Novel approaches for few-shot learning in natural language processing",
        num_papers_lit_review=5,
        max_experiment_iterations=3,
        max_paper_iterations=2,
        max_budget_usd=50.0,
        human_in_loop=False,
        save_checkpoints=True,
        task_notes={
            "literature_review": [
                "Focus on papers from 2023-2025",
                "Include both theoretical and empirical work",
                "Note any datasets used"
            ],
            "plan_formulation": [
                "Ensure reproducibility",
                "Consider computational constraints",
                "Define clear success metrics"
            ],
            "data_preparation": [
                "Use publicly available datasets",
                "Document preprocessing steps",
                "Split data appropriately"
            ],
            "running_experiments": [
                "Track all hyperparameters",
                "Save model checkpoints",
                "Log training metrics"
            ],
            "results_interpretation": [
                "Compare with baselines",
                "Discuss statistical significance",
                "Note any limitations"
            ],
            "report_writing": [
                "Follow academic writing standards",
                "Include proper citations",
                "Use clear figures and tables"
            ],
            "report_refinement": [
                "Address all reviewer concerns",
                "Strengthen weak sections",
                "Ensure clarity"
            ]
        }
    )

    if output_path:
        config.save(output_path)
        print(f"Default config saved to: {output_path}")

    return config


def load_environment_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables.

    Environment variables:
        CLAUDE_RESEARCH_TOPIC: Research topic
        CLAUDE_MODEL: Model to use
        CLAUDE_MAX_BUDGET: Maximum budget in USD
        CLAUDE_OUTPUT_DIR: Output directory
        ANTHROPIC_API_KEY: API key (required)

    Returns:
        Dictionary of environment-based config values
    """
    env_config = {}

    if os.getenv("CLAUDE_RESEARCH_TOPIC"):
        env_config["research_topic"] = os.getenv("CLAUDE_RESEARCH_TOPIC")

    if os.getenv("CLAUDE_MODEL"):
        env_config["model"] = os.getenv("CLAUDE_MODEL")

    if os.getenv("CLAUDE_MAX_BUDGET"):
        env_config["max_budget_usd"] = float(os.getenv("CLAUDE_MAX_BUDGET"))

    if os.getenv("CLAUDE_OUTPUT_DIR"):
        env_config["output_dir"] = os.getenv("CLAUDE_OUTPUT_DIR")

    if os.getenv("CLAUDE_NUM_PAPERS"):
        env_config["num_papers_lit_review"] = int(os.getenv("CLAUDE_NUM_PAPERS"))

    if os.getenv("CLAUDE_MAX_EXPERIMENTS"):
        env_config["max_experiment_iterations"] = int(os.getenv("CLAUDE_MAX_EXPERIMENTS"))

    if os.getenv("CLAUDE_HUMAN_IN_LOOP"):
        env_config["human_in_loop"] = os.getenv("CLAUDE_HUMAN_IN_LOOP").lower() == "true"

    return env_config


if __name__ == "__main__":
    print("Claude Code Configuration Manager")
    print("=" * 50)

    # Create and show default config
    config = create_default_config()
    print("\nDefault Configuration:")
    print(config.to_json())

    # Validate
    print(f"\nConfiguration valid: {config.validate()}")

    # Save example config
    example_path = "./example_config.json"
    config.save(example_path)
    print(f"\nExample config saved to: {example_path}")

    # Show environment config
    print("\nEnvironment Configuration:")
    env_config = load_environment_config()
    if env_config:
        print(json.dumps(env_config, indent=2))
    else:
        print("No environment variables set. You can set:")
        print("  CLAUDE_RESEARCH_TOPIC - Research topic")
        print("  CLAUDE_MODEL - Model to use")
        print("  CLAUDE_MAX_BUDGET - Maximum budget (USD)")
        print("  CLAUDE_OUTPUT_DIR - Output directory")
        print("  ANTHROPIC_API_KEY - API key (required)")
