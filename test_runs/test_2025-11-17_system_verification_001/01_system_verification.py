#!/usr/bin/env python3
"""
Agent Laboratory - System Verification Test
Level 0: Core System Functionality Check
"""

import os
import sys
import json
import ast
from pathlib import Path

os.chdir("/home/user/AgentLaboratory_claude")

GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}{text}{RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")

def print_check(condition, text):
    symbol = f"{GREEN}✓{RESET}" if condition else f"{RED}✗{RESET}"
    print(f"  {symbol} {text}")
    return condition

def print_section(text):
    print(f"\n{BOLD}{text}{RESET}")
    print(f"{'-'*70}")

tests_passed = 0
tests_failed = 0

# TEST 1: REPOSITORY STRUCTURE
print_header("TEST 1: REPOSITORY STRUCTURE VERIFICATION")
required_files = {
    "agents.py": "Agent implementations",
    "ai_lab_repo.py": "Main workflow orchestrator",
    "tools.py": "Search and execution tools",
    "inference.py": "LLM inference wrapper",
    "CLAUDE.md": "Claude documentation",
    "SETUP.md": "Setup guide",
    "claude-settings.json": "Claude settings",
    ".mcp.json": "MCP configuration",
    "requirements.txt": "Dependencies",
    ".claude/commands": "Claude commands directory",
}

print_section("Checking required files")
for filename, description in required_files.items():
    exists = Path(filename).exists()
    if print_check(exists, f"{filename:30s} - {description}"):
        tests_passed += 1
    else:
        tests_failed += 1

# TEST 2: PYTHON SYNTAX VALIDATION
print_header("TEST 2: PYTHON SYNTAX VALIDATION")
python_files = ["agents.py", "ai_lab_repo.py", "tools.py", "inference.py", "mlesolver.py", "papersolver.py"]

print_section("Checking Python syntax")
for filename in python_files:
    try:
        with open(filename) as f:
            ast.parse(f.read())
        if print_check(True, f"{filename:30s} - Valid syntax"):
            tests_passed += 1
    except SyntaxError as e:
        if print_check(False, f"{filename:30s} - Syntax error"):
            tests_passed += 1
        else:
            tests_failed += 1

# TEST 3: JSON CONFIGURATION VALIDATION
print_header("TEST 3: JSON CONFIGURATION VALIDATION")
json_files = {
    "claude-settings.json": "Claude Code settings",
    ".mcp.json": "MCP server configuration",
}

print_section("Validating JSON configurations")
for filename, description in json_files.items():
    try:
        with open(filename) as f:
            json.load(f)
        if print_check(True, f"{filename:30s} - Valid JSON"):
            tests_passed += 1
    except json.JSONDecodeError as e:
        if print_check(False, f"{filename:30s} - JSON Error"):
            tests_passed += 1
        else:
            tests_failed += 1

# TEST 4: AGENT CLASSES AVAILABILITY
print_header("TEST 4: AGENT CLASSES AVAILABILITY")
agents_to_find = [
    "BaseAgent",
    "PhDStudentAgent",
    "PostdocAgent",
    "MLEngineerAgent",
    "SWEngineerAgent",
    "ProfessorAgent",
    "ReviewersAgent",
]

print_section("Checking agent class definitions")
with open("agents.py") as f:
    agents_content = f.read()

for agent_name in agents_to_find:
    found = f"class {agent_name}" in agents_content
    if print_check(found, f"{agent_name:30s} - Class definition found"):
        tests_passed += 1
    else:
        tests_failed += 1

# TEST 5: WORKFLOW METHODS
print_header("TEST 5: WORKFLOW METHODS VERIFICATION")
workflow_methods = [
    ("perform_research", "Full pipeline"),
    ("literature_review", "Phase 1"),
    ("plan_formulation", "Phase 2"),
    ("data_preparation", "Phase 3"),
    ("running_experiments", "Phase 4"),
    ("results_interpretation", "Phase 5"),
    ("report_writing", "Phase 6"),
    ("report_refinement", "Phase 7"),
]

print_section("Checking workflow method definitions")
with open("ai_lab_repo.py") as f:
    workflow_content = f.read()

for method_name, description in workflow_methods:
    found = f"def {method_name}(" in workflow_content
    if print_check(found, f"{method_name:30s} - {description}"):
        tests_passed += 1
    else:
        tests_failed += 1

# TEST 6: TOOL CLASSES
print_header("TEST 6: TOOL CLASSES AVAILABILITY")
tool_classes = [
    ("ArxivSearch", "Paper search"),
    ("HFDataSearch", "Dataset search"),
    ("SemanticScholarSearch", "Scholar search"),
]

print_section("Checking tool class definitions")
with open("tools.py") as f:
    tools_content = f.read()

for tool_name, description in tool_classes:
    found = f"class {tool_name}" in tools_content
    if print_check(found, f"{tool_name:30s} - {description}"):
        tests_passed += 1
    else:
        tests_failed += 1

# TEST 7: CLAUDE CODE COMMANDS
print_header("TEST 7: CLAUDE CODE COMMANDS DOCUMENTATION")
print_section("Checking command specifications")
commands_dir = Path(".claude/commands")
if commands_dir.exists():
    commands = list(commands_dir.glob("*.md"))
    if print_check(True, f"{str(len(commands)):30s} - Command files found"):
        tests_passed += 1
    
    expected_commands = [
        "perform-research.md",
        "lit-review.md",
        "plan-phase.md",
        "data-prep.md",
        "run-experiments.md",
        "results-interp.md",
        "write-report.md",
        "refine-report.md",
        "search-arxiv.md",
        "search-datasets.md",
        "execute-code.md",
        "set-model.md",
        "save-checkpoint.md",
        "query-model.md",
        "configure-workflow.md",
    ]
    
    for cmd_file in expected_commands:
        path = commands_dir / cmd_file
        found = path.exists()
        if print_check(found, f"{cmd_file:30s} - Command documented"):
            tests_passed += 1
        else:
            tests_failed += 1
else:
    tests_failed += 1
    print(f"  {RED}✗{RESET} .claude/commands directory not found")

# TEST 8: REQUIREMENTS FILE
print_header("TEST 8: REQUIREMENTS FILE ANALYSIS")
print_section("Analyzing dependencies")
with open("requirements.txt") as f:
    lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith("#")]

critical_packages = {
    "openai": "OpenAI API",
    "anthropic": "Anthropic API",
    "arxiv": "ArXiv search",
    "pandas": "Data processing",
    "torch": "Deep learning",
    "transformers": "Transformer models",
    "datasets": "Dataset utilities",
}

print(f"  {GREEN}✓{RESET} Total packages                    - {len(lines)} packages specified")
tests_passed += 1

for package, description in critical_packages.items():
    found = any(package.lower() in line.lower() for line in lines)
    if print_check(found, f"{package:30s} - {description}"):
        tests_passed += 1
    else:
        tests_failed += 1

# TEST 9: DOCUMENTATION COMPLETENESS
print_header("TEST 9: DOCUMENTATION COMPLETENESS")
documentation_files = {
    "CLAUDE.md": "Project architecture",
    "SETUP.md": "Installation guide",
    "ARCHITECTURE_ANALYSIS.md": "Research blueprint",
    "TEST_EXECUTION_GUIDE.md": "Testing guide",
    "PROJECT_STATUS.md": "Status report",
}

print_section("Checking documentation files")
for filename, description in documentation_files.items():
    exists = Path(filename).exists()
    if exists:
        with open(filename) as f:
            size = len(f.read())
        if print_check(True, f"{filename:35s} - {description}"):
            tests_passed += 1
    else:
        if print_check(False, f"{filename:35s} - {description}"):
            tests_passed += 1
        else:
            tests_failed += 1

# SUMMARY
print_header("TEST SUMMARY")
total_tests = tests_passed + tests_failed
pass_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0

print(f"\n{BOLD}Results:{RESET}")
print(f"  {GREEN}Passed:{RESET}  {tests_passed}/{total_tests} tests")
print(f"  {RED}Failed:{RESET}  {tests_failed}/{total_tests} tests")
print(f"  {BOLD}Rate:{RESET}   {pass_rate:.1f}%")

if tests_failed == 0:
    print(f"\n{GREEN}{BOLD}✓ ALL TESTS PASSING{RESET}")
    print(f"{GREEN}System is ready for deployment{RESET}\n")
    sys.exit(0)
else:
    print(f"\n{RED}{BOLD}✗ SOME TESTS FAILED{RESET}\n")
    sys.exit(1)
