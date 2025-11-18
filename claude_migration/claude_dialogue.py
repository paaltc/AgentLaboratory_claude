"""
Dialogue Loop System for Claude Migration

Manages multi-agent dialogue loops that mimic the original AgentLaboratory
interaction patterns between agents.
"""
from typing import Dict, Any, List, Optional, Callable
from claude_agents import ClaudeAgent
from claude_commands import CommandParser


class DialogueLoop:
    """
    Manages iterative dialogue between two agents.

    Mimics the original AgentLaboratory dialogue pattern where agents
    alternate turns, exchanging dialogue until one submits a final output.
    """

    def __init__(
        self,
        agent1: ClaudeAgent,
        agent2: ClaudeAgent,
        topic: str,
        context: Dict[str, Any],
        phase: str,
        max_turns: int = 100,
        verbose: bool = True
    ):
        """
        Initialize dialogue loop.

        Args:
            agent1: First agent (usually senior: Postdoc, Professor, SW Engineer)
            agent2: Second agent (usually junior: PhD, ML Engineer)
            topic: Topic of discussion / task to accomplish
            context: Shared context (research artifacts)
            phase: Current phase name
            max_turns: Maximum dialogue turns before timeout
            verbose: Print dialogue to console
        """
        self.agent1 = agent1
        self.agent2 = agent2
        self.topic = topic
        self.context = context
        self.phase = phase
        self.max_turns = max_turns
        self.verbose = verbose
        self.dialogue_history = []

    def run_until_submission(
        self,
        submission_commands: List[str],
        agent1_commands: Optional[List[str]] = None,
        agent2_commands: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run dialogue loop until one agent submits final output.

        Mimics the pattern from ai_lab_repo.py where agents alternate,
        passing dialogue back and forth until submission.

        Args:
            submission_commands: Commands that end the loop (e.g., ["submit_plan"])
            agent1_commands: Available commands for agent1 (optional)
            agent2_commands: Available commands for agent2 (optional)

        Returns:
            {
                "submitted_by": agent_name,
                "submission_type": command_type,
                "submission_content": content,
                "dialogue_history": [...],
                "steps": number_of_steps
            }

        Raises:
            Exception: If max_turns reached without submission
        """
        dialogue = ""  # Current dialogue message to pass as feedback
        step = 0

        for turn in range(self.max_turns):
            # ============================================================
            # AGENT 1 TURN
            # ============================================================
            if self.verbose:
                print(f"\n{'='*50}")
                print(f"{self.agent1.name} Turn (Step {step})")
                print(f"{'='*50}")

            response1, cmd_type1, cmd_content1 = self.agent1.inference_with_commands(
                task=self.topic,
                context=self.context,
                phase=self.phase,
                feedback=dialogue,
                step=step,
                available_commands=agent1_commands
            )

            if self.verbose:
                print(f"\n{self.agent1.name}: {response1}\n")

            self.dialogue_history.append({
                "agent": self.agent1.name,
                "step": step,
                "response": response1,
                "command": cmd_type1,
                "content": cmd_content1
            })

            # Check for submission command
            if cmd_type1 in submission_commands:
                if self.verbose:
                    print(f"\n{'#'*50}")
                    print(f"{self.agent1.name} SUBMITTED: {cmd_type1}")
                    print(f"{'#'*50}\n")

                return {
                    "submitted_by": self.agent1.name,
                    "submission_type": cmd_type1,
                    "submission_content": cmd_content1,
                    "dialogue_history": self.dialogue_history,
                    "steps": step
                }

            # Extract dialogue for agent2
            dialogue = ""
            if cmd_type1 == "dialogue" and cmd_content1:
                dialogue = f"The following is dialogue produced by {self.agent1.name}: {cmd_content1}"
                if self.verbose:
                    print(f"{'#'*40}")
                    print(f"{self.agent1.name} Dialogue: {cmd_content1}")
                    print(f"{'#'*40}\n")

            # ============================================================
            # AGENT 2 TURN
            # ============================================================
            if self.verbose:
                print(f"\n{'='*50}")
                print(f"{self.agent2.name} Turn (Step {step})")
                print(f"{'='*50}")

            response2, cmd_type2, cmd_content2 = self.agent2.inference_with_commands(
                task=self.topic,
                context=self.context,
                phase=self.phase,
                feedback=dialogue,
                step=step,
                available_commands=agent2_commands
            )

            if self.verbose:
                print(f"\n{self.agent2.name}: {response2}\n")

            self.dialogue_history.append({
                "agent": self.agent2.name,
                "step": step,
                "response": response2,
                "command": cmd_type2,
                "content": cmd_content2
            })

            # Check for submission command
            if cmd_type2 in submission_commands:
                if self.verbose:
                    print(f"\n{'#'*50}")
                    print(f"{self.agent2.name} SUBMITTED: {cmd_type2}")
                    print(f"{'#'*50}\n")

                return {
                    "submitted_by": self.agent2.name,
                    "submission_type": cmd_type2,
                    "submission_content": cmd_content2,
                    "dialogue_history": self.dialogue_history,
                    "steps": step
                }

            # Extract dialogue for next round
            dialogue = ""
            if cmd_type2 == "dialogue" and cmd_content2:
                dialogue = f"The following is dialogue produced by {self.agent2.name}: {cmd_content2}"
                if self.verbose:
                    print(f"{'#'*40}")
                    print(f"{self.agent2.name} Dialogue: {cmd_content2}")
                    print(f"{'#'*40}\n")

            step += 1

        # Max turns reached
        raise Exception(
            f"Max turns ({self.max_turns}) reached without submission in phase: {self.phase}"
        )


class ToolAugmentedDialogue(DialogueLoop):
    """
    Dialogue loop with tool execution support.

    Used for phases like data_preparation where agents can execute
    commands that trigger tool use (e.g., execute code, search datasets).
    """

    def __init__(
        self,
        agent1: ClaudeAgent,
        agent2: ClaudeAgent,
        topic: str,
        context: Dict[str, Any],
        phase: str,
        tool_executors: Dict[str, Callable],
        max_turns: int = 100,
        verbose: bool = True
    ):
        """
        Initialize tool-augmented dialogue.

        Args:
            agent1: First agent
            agent2: Second agent
            topic: Discussion topic
            context: Shared context
            phase: Current phase
            tool_executors: Map of command_type -> execution function
                e.g., {"execute_code": lambda code: ..., "search_datasets": lambda q: ...}
            max_turns: Max turns
            verbose: Print output
        """
        super().__init__(agent1, agent2, topic, context, phase, max_turns, verbose)
        self.tool_executors = tool_executors

    def run_with_tools(
        self,
        submission_commands: List[str],
        agent1_commands: Optional[List[str]] = None,
        agent2_commands: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run dialogue loop where agents can execute tools.

        Agents can:
        - Use DIALOGUE to communicate
        - Use tool commands (e.g., python, SEARCH_HF)
        - Submit final output (e.g., SUBMIT_CODE)

        Tool execution results are fed back as feedback to the agent.

        Args:
            submission_commands: Commands that end the loop
            agent1_commands: Available commands for agent1
            agent2_commands: Available commands for agent2

        Returns:
            Same as run_until_submission, with tool execution logs
        """
        dialogue = ""
        tool_feedback = ""
        step = 0

        # Track which agent's turn it is
        agents = [
            (self.agent1, agent1_commands, self.agent1.name),
            (self.agent2, agent2_commands, self.agent2.name)
        ]
        agent_idx = 0

        for turn in range(self.max_turns * 2):  # *2 because we may stay on same agent
            agent, commands, agent_name = agents[agent_idx]

            if self.verbose:
                print(f"\n{'='*50}")
                print(f"{agent_name} Turn (Step {step})")
                print(f"{'='*50}")

            # Combine dialogue and tool feedback
            combined_feedback = f"{dialogue}\n{tool_feedback}".strip()

            response, cmd_type, cmd_content = agent.inference_with_commands(
                task=self.topic,
                context=self.context,
                phase=self.phase,
                feedback=combined_feedback,
                step=step,
                available_commands=commands
            )

            if self.verbose:
                print(f"\n{agent_name}: {response}\n")

            self.dialogue_history.append({
                "agent": agent_name,
                "step": step,
                "response": response,
                "command": cmd_type,
                "content": cmd_content
            })

            # Check for submission
            if cmd_type in submission_commands:
                if self.verbose:
                    print(f"\n{'#'*50}")
                    print(f"{agent_name} SUBMITTED: {cmd_type}")
                    print(f"{'#'*50}\n")

                return {
                    "submitted_by": agent_name,
                    "submission_type": cmd_type,
                    "submission_content": cmd_content,
                    "dialogue_history": self.dialogue_history,
                    "steps": step
                }

            # Execute tool if tool command
            tool_feedback = ""
            if cmd_type and cmd_type in self.tool_executors:
                if self.verbose:
                    print(f"\n{'!'*50}")
                    print(f"EXECUTING TOOL: {cmd_type}")
                    print(f"{'!'*50}")

                try:
                    tool_result = self.tool_executors[cmd_type](cmd_content)
                    tool_feedback = f"Feedback from previous command:\n{tool_result}"

                    if self.verbose:
                        print(f"Tool Result: {tool_result}\n")

                except Exception as e:
                    tool_feedback = f"[CODE EXECUTION ERROR]: {str(e)}"

                    if self.verbose:
                        print(f"Tool Error: {str(e)}\n")

                # Stay on same agent for tool feedback
                dialogue = ""
                step += 1
                continue

            # Handle dialogue
            dialogue = ""
            if cmd_type == "dialogue" and cmd_content:
                dialogue = f"The following is dialogue produced by {agent_name}: {cmd_content}"

                if self.verbose:
                    print(f"{'#'*40}")
                    print(f"{agent_name} Dialogue: {cmd_content}")
                    print(f"{'#'*40}\n")

            # Switch to other agent
            agent_idx = (agent_idx + 1) % 2
            tool_feedback = ""  # Clear tool feedback after passing to other agent
            step += 1

        raise Exception(
            f"Max turns ({self.max_turns * 2}) reached without submission in phase: {self.phase}"
        )
