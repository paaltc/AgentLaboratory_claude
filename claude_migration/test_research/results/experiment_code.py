#!/usr/bin/env python3
"""
Experiment: Agentic Systems with Memory Organization and CI/CD Learning

This experiment implements a proof-of-concept for:
1. Hierarchical memory architecture (Working/Episodic/Semantic)
2. CI/CD failure log learning and pattern recognition
3. Session state persistence for web autonomy
4. Self-improvement through failure analysis
"""
import json
import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict


class HierarchicalMemory:
    """
    Three-tier memory system inspired by A-MEM Zettelkasten approach.
    - Working Memory: Current task context (limited size)
    - Episodic Memory: Task history and failure logs
    - Semantic Memory: Learned patterns and knowledge graph
    """

    def __init__(self, db_path: str = "agent_memory.db"):
        self.db_path = db_path
        self.working_memory: List[Dict] = []
        self.working_memory_limit = 10
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for episodic and semantic memory."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Episodic memory: task history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS episodic_memory (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                task_type TEXT,
                content TEXT,
                outcome TEXT,
                tags TEXT
            )
        """)

        # Semantic memory: learned patterns (knowledge graph)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS semantic_memory (
                id TEXT PRIMARY KEY,
                concept TEXT,
                connections TEXT,
                frequency INTEGER,
                last_accessed TEXT
            )
        """)

        # Failure patterns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS failure_patterns (
                id TEXT PRIMARY KEY,
                error_type TEXT,
                pattern TEXT,
                fix_suggestion TEXT,
                success_rate REAL,
                occurrences INTEGER
            )
        """)

        conn.commit()
        conn.close()

    def add_to_working_memory(self, item: Dict):
        """Add item to working memory with size limit."""
        self.working_memory.append({
            **item,
            "added_at": datetime.now().isoformat()
        })
        # Maintain size limit (FIFO)
        if len(self.working_memory) > self.working_memory_limit:
            evicted = self.working_memory.pop(0)
            self.store_episodic(evicted)

    def store_episodic(self, episode: Dict):
        """Store episode in episodic memory."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        episode_id = hashlib.md5(
            json.dumps(episode, sort_keys=True).encode()
        ).hexdigest()[:16]

        cursor.execute("""
            INSERT OR REPLACE INTO episodic_memory
            (id, timestamp, task_type, content, outcome, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            episode_id,
            episode.get("added_at", datetime.now().isoformat()),
            episode.get("task_type", "unknown"),
            json.dumps(episode),
            episode.get("outcome", "unknown"),
            json.dumps(episode.get("tags", []))
        ))

        conn.commit()
        conn.close()

    def learn_pattern(self, concept: str, connections: List[str]):
        """Learn or update a pattern in semantic memory (Zettelkasten style)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        concept_id = hashlib.md5(concept.encode()).hexdigest()[:16]

        # Check if concept exists
        cursor.execute("SELECT * FROM semantic_memory WHERE id = ?", (concept_id,))
        existing = cursor.fetchone()

        if existing:
            # Update existing concept
            old_connections = json.loads(existing[2])
            new_connections = list(set(old_connections + connections))
            cursor.execute("""
                UPDATE semantic_memory
                SET connections = ?, frequency = frequency + 1, last_accessed = ?
                WHERE id = ?
            """, (json.dumps(new_connections), datetime.now().isoformat(), concept_id))
        else:
            # Create new concept
            cursor.execute("""
                INSERT INTO semantic_memory
                (id, concept, connections, frequency, last_accessed)
                VALUES (?, ?, ?, ?, ?)
            """, (
                concept_id,
                concept,
                json.dumps(connections),
                1,
                datetime.now().isoformat()
            ))

        conn.commit()
        conn.close()

    def retrieve_related_memories(self, query: str, limit: int = 5) -> List[Dict]:
        """Retrieve related memories using keyword matching."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Simple keyword matching (in production, use embeddings)
        cursor.execute("""
            SELECT content FROM episodic_memory
            WHERE content LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (f"%{query}%", limit))

        results = []
        for row in cursor.fetchall():
            results.append(json.loads(row[0]))

        conn.close()
        return results

    def get_memory_stats(self) -> Dict:
        """Get statistics about memory usage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM episodic_memory")
        episodic_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM semantic_memory")
        semantic_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM failure_patterns")
        pattern_count = cursor.fetchone()[0]

        conn.close()

        return {
            "working_memory_items": len(self.working_memory),
            "episodic_memories": episodic_count,
            "semantic_concepts": semantic_count,
            "failure_patterns": pattern_count
        }


class CICDFailureLearner:
    """
    Learns from CI/CD failure logs to improve agent behavior.
    Implements pattern recognition and fix suggestions.
    """

    def __init__(self, memory: HierarchicalMemory):
        self.memory = memory
        self.failure_categories = {
            "dependency": ["npm ERR!", "ModuleNotFoundError", "pip install failed"],
            "syntax": ["SyntaxError", "IndentationError", "ParseError"],
            "test": ["AssertionError", "FAILED", "test_", "pytest"],
            "timeout": ["timeout", "exceeded maximum", "timed out"],
            "permission": ["Permission denied", "EACCES", "not permitted"]
        }

    def categorize_failure(self, log_message: str) -> str:
        """Categorize failure based on log message."""
        for category, keywords in self.failure_categories.items():
            if any(kw in log_message for kw in keywords):
                return category
        return "unknown"

    def learn_from_failure(self, log_message: str, fix_applied: Optional[str] = None):
        """Learn from a failure log entry."""
        category = self.categorize_failure(log_message)

        # Store in memory
        failure_episode = {
            "task_type": "ci_cd_failure",
            "error_type": category,
            "message": log_message[:500],  # Truncate long messages
            "fix_applied": fix_applied,
            "outcome": "learned",
            "tags": [category, "failure", "ci_cd"]
        }
        self.memory.add_to_working_memory(failure_episode)

        # Learn pattern
        self.memory.learn_pattern(
            f"failure_{category}",
            [log_message[:100], fix_applied or "unknown_fix"]
        )

        # Update failure pattern database
        self._update_failure_pattern(category, log_message, fix_applied)

    def _update_failure_pattern(self, category: str, message: str, fix: Optional[str]):
        """Update failure pattern in database."""
        conn = sqlite3.connect(self.memory.db_path)
        cursor = conn.cursor()

        pattern_id = hashlib.md5(f"{category}_{message[:50]}".encode()).hexdigest()[:16]

        cursor.execute(
            "SELECT * FROM failure_patterns WHERE id = ?", (pattern_id,)
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE failure_patterns
                SET occurrences = occurrences + 1
                WHERE id = ?
            """, (pattern_id,))
        else:
            cursor.execute("""
                INSERT INTO failure_patterns
                (id, error_type, pattern, fix_suggestion, success_rate, occurrences)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                pattern_id,
                category,
                message[:200],
                fix or "No fix recorded",
                0.0,
                1
            ))

        conn.commit()
        conn.close()

    def suggest_fix(self, log_message: str) -> str:
        """Suggest a fix based on learned patterns."""
        category = self.categorize_failure(log_message)

        # Check historical fixes
        conn = sqlite3.connect(self.memory.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT fix_suggestion, success_rate, occurrences
            FROM failure_patterns
            WHERE error_type = ?
            ORDER BY success_rate DESC, occurrences DESC
            LIMIT 1
        """, (category,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return f"Suggested fix (based on {result[2]} occurrences): {result[0]}"

        # Default suggestions
        default_fixes = {
            "dependency": "Try: pip install -r requirements.txt or npm install",
            "syntax": "Check for syntax errors, missing colons, or incorrect indentation",
            "test": "Review test assertions and expected values",
            "timeout": "Increase timeout or optimize slow operations",
            "permission": "Check file permissions or run with appropriate privileges"
        }

        return default_fixes.get(category, "Manual investigation required")

    def get_failure_summary(self) -> Dict:
        """Get summary of learned failures."""
        conn = sqlite3.connect(self.memory.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT error_type, SUM(occurrences) as total
            FROM failure_patterns
            GROUP BY error_type
            ORDER BY total DESC
        """)

        summary = {}
        for row in cursor.fetchall():
            summary[row[0]] = row[1]

        conn.close()
        return summary


class SessionPersistence:
    """
    Manages session state for web autonomy.
    Enables agents to resume across interrupted sessions.
    """

    def __init__(self, state_file: str = "agent_session.json"):
        self.state_file = Path(state_file)
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """Load state from file or create new."""
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {
            "session_id": hashlib.md5(
                datetime.now().isoformat().encode()
            ).hexdigest()[:12],
            "created_at": datetime.now().isoformat(),
            "task_queue": [],
            "completed_tasks": [],
            "checkpoints": [],
            "current_phase": "initialized"
        }

    def save_state(self):
        """Save current state to file."""
        self.state["last_saved"] = datetime.now().isoformat()
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def checkpoint(self, description: str, data: Any = None):
        """Create a checkpoint for recovery."""
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "phase": self.state["current_phase"],
            "data": data
        }
        self.state["checkpoints"].append(checkpoint)
        self.save_state()
        return len(self.state["checkpoints"])

    def add_task(self, task: Dict):
        """Add task to queue."""
        self.state["task_queue"].append({
            **task,
            "added_at": datetime.now().isoformat(),
            "status": "pending"
        })
        self.save_state()

    def complete_task(self, task_id: int, result: Any):
        """Mark task as completed."""
        if task_id < len(self.state["task_queue"]):
            task = self.state["task_queue"][task_id]
            task["status"] = "completed"
            task["result"] = result
            task["completed_at"] = datetime.now().isoformat()
            self.state["completed_tasks"].append(task)
        self.save_state()

    def get_continuity_score(self) -> float:
        """Calculate session continuity score."""
        if not self.state["checkpoints"]:
            return 1.0

        total_checkpoints = len(self.state["checkpoints"])
        completed = len(self.state["completed_tasks"])
        total_tasks = completed + len([
            t for t in self.state["task_queue"] if t["status"] == "pending"
        ])

        if total_tasks == 0:
            return 1.0

        return completed / total_tasks


class AgentSubmodule:
    """
    Git submodule-ready agent framework.
    Standardized interface for easy deployment.
    """

    def __init__(self, agent_dir: str = "./agent_module"):
        self.agent_dir = Path(agent_dir)
        self._setup_structure()

    def _setup_structure(self):
        """Create standardized agent directory structure."""
        # Create directories
        (self.agent_dir / "core").mkdir(parents=True, exist_ok=True)
        (self.agent_dir / "memory").mkdir(exist_ok=True)
        (self.agent_dir / "config").mkdir(exist_ok=True)
        (self.agent_dir / "logs").mkdir(exist_ok=True)

        # Create __init__.py files
        (self.agent_dir / "__init__.py").write_text(
            '"""Agent Submodule - Ready for deployment."""\n'
            'from .core.agent import Agent\n'
            '__version__ = "0.1.0"\n'
        )
        (self.agent_dir / "core" / "__init__.py").write_text("")
        (self.agent_dir / "memory" / "__init__.py").write_text("")

        # Create setup.py
        setup_content = '''
from setuptools import setup, find_packages

setup(
    name="agent_module",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sqlite3",
    ],
    python_requires=">=3.9",
)
'''
        (self.agent_dir / "setup.py").write_text(setup_content.strip())

        # Create README
        readme = '''# Agent Submodule

Git submodule-ready autonomous agent with memory and CI/CD learning.

## Usage

```bash
# Add as submodule
git submodule add <repo_url> agent

# Initialize
from agent import Agent
agent = Agent()
agent.run()
```

## Features
- Hierarchical memory (Working/Episodic/Semantic)
- CI/CD failure learning
- Session persistence
- Self-improvement
'''
        (self.agent_dir / "README.md").write_text(readme)

        # Create main agent file
        agent_code = '''
"""Main Agent Class"""
import json

class Agent:
    def __init__(self, config_path=None):
        self.config = self._load_config(config_path)
        self.memory = None  # Initialize memory system
        self.session = None  # Initialize session manager

    def _load_config(self, path):
        if path:
            with open(path) as f:
                return json.load(f)
        return {"name": "DefaultAgent", "version": "0.1.0"}

    def run(self):
        """Main agent execution loop."""
        print(f"Agent {self.config['name']} v{self.config['version']} running...")

    def checkpoint(self):
        """Save current state."""
        pass

    def resume(self):
        """Resume from checkpoint."""
        pass
'''
        (self.agent_dir / "core" / "agent.py").write_text(agent_code)

    def get_structure(self) -> Dict:
        """Get the directory structure."""
        structure = {}
        for path in self.agent_dir.rglob("*"):
            if path.is_file():
                rel_path = str(path.relative_to(self.agent_dir))
                structure[rel_path] = path.stat().st_size
        return structure


def run_experiment():
    """Main experiment execution."""
    print("=" * 60)
    print("EXPERIMENT: Agentic Systems with Memory and CI/CD Learning")
    print("=" * 60)

    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "metrics": {}
    }

    # Test 1: Hierarchical Memory System
    print("\n[TEST 1] Hierarchical Memory System")
    print("-" * 40)

    memory = HierarchicalMemory(db_path="test_memory.db")

    # Add items to working memory
    for i in range(15):
        memory.add_to_working_memory({
            "task_type": "code_generation",
            "content": f"Task {i}: Generate function",
            "tags": ["code", f"iteration_{i}"]
        })

    # Learn patterns
    memory.learn_pattern("code_generation", ["python", "functions", "testing"])
    memory.learn_pattern("error_handling", ["try-catch", "exceptions", "logging"])
    memory.learn_pattern("code_generation", ["refactoring", "optimization"])

    stats = memory.get_memory_stats()
    print(f"Memory Stats: {json.dumps(stats, indent=2)}")

    # Check if episodic memory works (items should be evicted from working memory)
    test1_passed = (
        stats["working_memory_items"] <= memory.working_memory_limit and
        stats["episodic_memories"] > 0 and
        stats["semantic_concepts"] > 0
    )
    results["tests"].append({
        "name": "Hierarchical Memory",
        "passed": test1_passed,
        "details": stats
    })
    print(f"Test 1 PASSED: {test1_passed}")

    # Test 2: CI/CD Failure Learning
    print("\n[TEST 2] CI/CD Failure Learning")
    print("-" * 40)

    learner = CICDFailureLearner(memory)

    # Simulate failures
    failures = [
        ("npm ERR! peer dep missing: react@^18.0.0", "npm install react@18"),
        ("ModuleNotFoundError: No module named 'pandas'", "pip install pandas"),
        ("AssertionError: Expected 5 but got 3", "Fix calculation logic"),
        ("SyntaxError: invalid syntax at line 42", "Fix missing colon"),
        ("Process timed out after 3600 seconds", "Optimize slow loop"),
    ]

    for msg, fix in failures:
        learner.learn_from_failure(msg, fix)
        category = learner.categorize_failure(msg)
        print(f"  Learned: {category} -> {fix}")

    # Test fix suggestion
    test_msg = "npm ERR! peer dep missing: lodash@^4.0.0"
    suggestion = learner.suggest_fix(test_msg)
    print(f"\n  Suggestion for '{test_msg[:50]}...':")
    print(f"    {suggestion}")

    summary = learner.get_failure_summary()
    print(f"\n  Failure Summary: {summary}")

    test2_passed = len(summary) > 0 and "dependency" in summary
    results["tests"].append({
        "name": "CI/CD Failure Learning",
        "passed": test2_passed,
        "details": summary
    })
    print(f"Test 2 PASSED: {test2_passed}")

    # Test 3: Session Persistence
    print("\n[TEST 3] Session Persistence")
    print("-" * 40)

    session = SessionPersistence(state_file="test_session.json")

    # Add tasks
    session.add_task({"type": "literature_review", "topic": "memory systems"})
    session.add_task({"type": "code_generation", "target": "memory.py"})
    session.add_task({"type": "testing", "suite": "unit_tests"})

    # Create checkpoints
    cp1 = session.checkpoint("After literature review", {"papers": 5})
    cp2 = session.checkpoint("After code generation", {"lines": 500})

    # Complete some tasks
    session.complete_task(0, {"status": "success", "papers_found": 5})
    session.complete_task(1, {"status": "success", "code_written": True})

    continuity_score = session.get_continuity_score()
    print(f"  Session ID: {session.state['session_id']}")
    print(f"  Checkpoints: {len(session.state['checkpoints'])}")
    print(f"  Tasks completed: {len(session.state['completed_tasks'])}")
    print(f"  Continuity Score: {continuity_score:.2%}")

    test3_passed = continuity_score > 0.5 and len(session.state["checkpoints"]) >= 2
    results["tests"].append({
        "name": "Session Persistence",
        "passed": test3_passed,
        "details": {
            "continuity_score": continuity_score,
            "checkpoints": len(session.state["checkpoints"])
        }
    })
    print(f"Test 3 PASSED: {test3_passed}")

    # Test 4: Agent Submodule Structure
    print("\n[TEST 4] Agent Submodule Structure")
    print("-" * 40)

    submodule = AgentSubmodule(agent_dir="./test_agent_module")
    structure = submodule.get_structure()

    print("  Generated structure:")
    for path, size in sorted(structure.items()):
        print(f"    {path}: {size} bytes")

    required_files = ["__init__.py", "setup.py", "README.md", "core/agent.py"]
    has_all_files = all(f in structure for f in required_files)

    test4_passed = has_all_files and len(structure) >= 5
    results["tests"].append({
        "name": "Agent Submodule Structure",
        "passed": test4_passed,
        "details": {"files": list(structure.keys())}
    })
    print(f"Test 4 PASSED: {test4_passed}")

    # Calculate overall metrics
    print("\n" + "=" * 60)
    print("EXPERIMENT RESULTS")
    print("=" * 60)

    passed_tests = sum(1 for t in results["tests"] if t["passed"])
    total_tests = len(results["tests"])

    results["metrics"] = {
        "tests_passed": passed_tests,
        "tests_total": total_tests,
        "success_rate": passed_tests / total_tests,
        "memory_efficiency": stats.get("episodic_memories", 0) / 15,  # vs naive approach
        "failure_learning_categories": len(summary),
        "session_continuity": continuity_score,
        "submodule_completeness": len(structure) / 7  # expected files
    }

    print(f"\nTests Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {results['metrics']['success_rate']:.2%}")
    print(f"Memory Efficiency: {results['metrics']['memory_efficiency']:.2%}")
    print(f"Session Continuity: {results['metrics']['session_continuity']:.2%}")
    print(f"Submodule Completeness: {results['metrics']['submodule_completeness']:.2%}")

    # Cleanup test files
    for f in ["test_memory.db", "test_session.json"]:
        Path(f).unlink(missing_ok=True)
    import shutil
    shutil.rmtree("./test_agent_module", ignore_errors=True)

    return results


if __name__ == "__main__":
    results = run_experiment()

    # Save results
    with open("experiment_output.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n[Results saved to experiment_output.json]")
