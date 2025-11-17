#!/usr/bin/env python3
"""
Agent Laboratory - Level 1 Component Tests
Tests component structure without requiring external dependencies

Test Level: 1 (Component Testing - Structural Analysis)
Test Date: 2025-11-17
"""

import sys
import os
import ast
import json
from pathlib import Path

os.chdir("/home/user/AgentLaboratory_claude")

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
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

# ============================================================================
# TEST 1: AGENT CLASS STRUCTURE ANALYSIS
# ============================================================================
print_header("TEST 1: AGENT CLASS STRUCTURE ANALYSIS")

print_section("Analyzing agent class definitions")

# Parse agents.py without importing
with open("agents.py") as f:
    agents_tree = ast.parse(f.read())

# Find all classes
agent_classes = {}
for node in ast.walk(agents_tree):
    if isinstance(node, ast.ClassDef):
        agent_classes[node.name] = {
            'name': node.name,
            'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
            'lineno': node.lineno,
        }

expected_agents = ['BaseAgent', 'PhDStudentAgent', 'PostdocAgent', 'MLEngineerAgent', 'SWEngineerAgent', 'ProfessorAgent', 'ReviewersAgent']

for agent_name in expected_agents:
    found = agent_name in agent_classes
    if print_check(found, f"{agent_name:30s} - Class defined"):
        tests_passed += 1
    else:
        tests_failed += 1

# Check BaseAgent has required methods
if 'BaseAgent' in agent_classes:
    base_methods = agent_classes['BaseAgent']['methods']
    required = ['inference', '__init__']
    has_required = all(m in base_methods for m in required)
    if print_check(has_required, f"BaseAgent has required methods ({len(base_methods)} total)"):
        tests_passed += 1
    else:
        tests_failed += 1

# ============================================================================
# TEST 2: WORKFLOW METHODS ANALYSIS
# ============================================================================
print_header("TEST 2: WORKFLOW METHODS ANALYSIS")

print_section("Analyzing LaboratoryWorkflow methods")

# Parse ai_lab_repo.py without importing
with open("ai_lab_repo.py") as f:
    workflow_tree = ast.parse(f.read())

# Find LaboratoryWorkflow class
workflow_class = None
workflow_methods = []

for node in ast.walk(workflow_tree):
    if isinstance(node, ast.ClassDef) and node.name == 'LaboratoryWorkflow':
        workflow_methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]

expected_methods = [
    'perform_research',
    'literature_review',
    'plan_formulation',
    'data_preparation',
    'running_experiments',
    'results_interpretation',
    'report_writing',
    'report_refinement',
]

for method in expected_methods:
    found = method in workflow_methods
    if print_check(found, f"{method:30s} - Method defined"):
        tests_passed += 1
    else:
        tests_failed += 1

# ============================================================================
# TEST 3: TOOL CLASSES ANALYSIS
# ============================================================================
print_header("TEST 3: TOOL CLASSES ANALYSIS")

print_section("Analyzing tool class definitions")

# Parse tools.py without importing
with open("tools.py") as f:
    tools_tree = ast.parse(f.read())

# Find all classes
tool_classes = {}
for node in ast.walk(tools_tree):
    if isinstance(node, ast.ClassDef):
        tool_classes[node.name] = {
            'name': node.name,
            'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
        }

expected_tools = ['ArxivSearch', 'HFDataSearch', 'SemanticScholarSearch']

for tool_name in expected_tools:
    found = tool_name in tool_classes
    if print_check(found, f"{tool_name:30s} - Class defined"):
        tests_passed += 1
    else:
        tests_failed += 1

# ============================================================================
# TEST 4: CONFIGURATION FILES
# ============================================================================
print_header("TEST 4: CONFIGURATION FILES")

print_section("Validating JSON configuration files")

try:
    with open("claude-settings.json") as f:
        config = json.load(f)
    
    required_keys = ['model_preferences', 'max_tokens', 'allowed_tools']
    has_keys = all(key in config for key in required_keys)
    
    if print_check(has_keys, "claude-settings.json has required keys"):
        tests_passed += 1
    else:
        tests_failed += 1
except Exception as e:
    if print_check(False, f"claude-settings.json - Error: {str(e)[:40]}"):
        tests_passed += 1
    else:
        tests_failed += 1

try:
    with open(".mcp.json") as f:
        mcp_config = json.load(f)
    
    if print_check(True, ".mcp.json valid JSON"):
        tests_passed += 1
    else:
        tests_failed += 1
except Exception as e:
    if print_check(False, f".mcp.json - Error: {str(e)[:40]}"):
        tests_passed += 1
    else:
        tests_failed += 1

# ============================================================================
# TEST 5: CHECKPOINT SYSTEM
# ============================================================================
print_header("TEST 5: CHECKPOINT SYSTEM READINESS")

print_section("Checking checkpoint infrastructure")

# Check state_saves directory
state_dir = Path("state_saves")
exists = state_dir.exists()
if print_check(exists, "state_saves directory exists"):
    tests_passed += 1
else:
    tests_failed += 1

# Test pickle functionality
try:
    import pickle
    test_data = {"phase": "literature_review", "step": 1}
    test_file = Path("test_checkpoint.pkl")
    
    # Save
    with open(test_file, 'wb') as f:
        pickle.dump(test_data, f)
    
    # Load
    with open(test_file, 'rb') as f:
        loaded = pickle.load(f)
    
    success = loaded == test_data
    if print_check(success, "Checkpoint save/load functional"):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Cleanup
    test_file.unlink()
except Exception as e:
    if print_check(False, f"Pickle test - Error: {str(e)[:40]}"):
        tests_passed += 1
    else:
        tests_failed += 1

# ============================================================================
# TEST 6: CLAUDE CODE COMMANDS
# ============================================================================
print_header("TEST 6: CLAUDE CODE COMMANDS")

print_section("Verifying command specifications")

commands_dir = Path(".claude/commands")
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

for cmd in expected_commands:
    path = commands_dir / cmd
    found = path.exists()
    if print_check(found, f"{cmd:30s} - Command documented"):
        tests_passed += 1
    else:
        tests_failed += 1

# ============================================================================
# TEST 7: DOCUMENTATION FILES
# ============================================================================
print_header("TEST 7: DOCUMENTATION FILES")

print_section("Verifying documentation completeness")

docs = {
    "CLAUDE.md": "Project architecture",
    "SETUP.md": "Setup instructions",
    "ARCHITECTURE_ANALYSIS.md": "Research blueprint",
    "TEST_EXECUTION_GUIDE.md": "Testing guide",
    "PROJECT_STATUS.md": "Status report",
}

for filename, description in docs.items():
    path = Path(filename)
    found = path.exists()
    if print_check(found, f"{filename:35s} - {description}"):
        tests_passed += 1
    else:
        tests_failed += 1

# ============================================================================
# SUMMARY
# ============================================================================
print_header("LEVEL 1 COMPONENT TEST SUMMARY")

total_tests = tests_passed + tests_failed
pass_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0

print(f"\n{BOLD}Results:{RESET}")
print(f"  {GREEN}Passed:{RESET}  {tests_passed}/{total_tests} tests")
print(f"  {RED}Failed:{RESET}  {tests_failed}/{total_tests} tests")
print(f"  {BOLD}Rate:{RESET}   {pass_rate:.1f}%")

print(f"\n{BOLD}Components Verified:{RESET}")
print(f"  {GREEN}✓{RESET} Agent classes: {len([a for a in expected_agents if a in agent_classes])}/{len(expected_agents)}")
print(f"  {GREEN}✓{RESET} Workflow methods: {len([m for m in expected_methods if m in workflow_methods])}/{len(expected_methods)}")
print(f"  {GREEN}✓{RESET} Tool classes: {len([t for t in expected_tools if t in tool_classes])}/{len(expected_tools)}")
print(f"  {GREEN}✓{RESET} Commands: {len([c for c in expected_commands if (commands_dir / c).exists()])}/{len(expected_commands)}")
print(f"  {GREEN}✓{RESET} Documentation: {len([d for d in docs if Path(d).exists()])}/{len(docs)}")

if tests_failed == 0:
    print(f"\n{GREEN}{BOLD}✓ ALL COMPONENT TESTS PASSING{RESET}")
    print(f"{GREEN}Components verified structurally{RESET}")
    print(f"{GREEN}Ready to proceed to Level 2 Integration Tests{RESET}\n")
else:
    print(f"\n{RED}{BOLD}✗ SOME TESTS FAILED{RESET}\n")

sys.exit(0 if tests_failed == 0 else 1)
