"""
Claude Code Migration - Agent System
Redesigned agents using Claude's native tool-calling capabilities
"""
import json
from typing import List, Dict, Any, Optional, Tuple
from claude_inference import ClaudeClient, get_current_cost, get_token_stats
from claude_tools import ToolExecutor, get_tools_for_role
from claude_commands import CommandParser, CommandInstructionBuilder


class ClaudeAgent:
    """Base agent class using Claude's native capabilities."""

    def __init__(
        self,
        role: str,
        name: str,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        temperature: float = 0.7,
        max_tool_rounds: int = 10
    ):
        """
        Initialize Claude agent.

        Args:
            role: Agent role (determines available tools)
            name: Display name for the agent
            api_key: Anthropic API key (optional)
            model: Claude model to use
            temperature: Sampling temperature
            max_tool_rounds: Max iterations of tool use
        """
        self.role = role
        self.name = name
        self.model = model
        self.temperature = temperature
        self.max_tool_rounds = max_tool_rounds

        # Initialize client and tools
        self.client = ClaudeClient(api_key=api_key)
        self.tools = get_tools_for_role(role)
        self.tool_executor = ToolExecutor()

        # Agent state
        self.conversation_history: List[Dict[str, Any]] = []
        self.research_artifacts = {
            "literature": [],
            "plan": "",
            "code": "",
            "results": "",
            "report": ""
        }

    def get_system_prompt(self, phase: str) -> str:
        """Get role-specific system prompt for a given phase."""
        base_prompt = f"""You are {self.name}, a {self.role.replace('_', ' ')} working on a machine learning research project.

Your role involves:
{self._get_role_description()}

Current phase: {phase}

Important guidelines:
- Be thorough and scientific in your approach
- Use available tools to gather information and execute tasks
- Provide clear, well-reasoned explanations
- Follow best practices for reproducible research
- Collaborate effectively with other team members
"""
        return base_prompt

    def _get_role_description(self) -> str:
        """Get detailed role description."""
        descriptions = {
            "phd_student": """
- Conducting comprehensive literature reviews
- Identifying relevant papers and synthesizing findings
- Assisting in experimental design and planning
- Interpreting results and drafting reports
- Learning from senior researchers' guidance""",

            "ml_engineer": """
- Designing and implementing ML experiments
- Searching for appropriate datasets
- Writing and debugging training code
- Optimizing model performance
- Ensuring code quality and reproducibility""",

            "sw_engineer": """
- Implementing data loading and preprocessing pipelines
- Writing clean, maintainable code
- Debugging software issues
- Ensuring code follows best practices
- Managing dependencies and environment""",

            "postdoc": """
- Providing expert guidance on research direction
- Suggesting experimental improvements
- Helping interpret complex results
- Mentoring junior researchers
- Ensuring scientific rigor""",

            "professor": """
- Overseeing the research project
- Making high-level strategic decisions
- Ensuring academic standards are met
- Writing and reviewing research papers
- Guiding the team towards impactful results""",

            "reviewer": """
- Evaluating research papers critically
- Providing constructive feedback
- Scoring papers on quality metrics
- Identifying strengths and weaknesses
- Suggesting improvements"""
        }
        return descriptions.get(self.role, "Conducting research tasks")

    def inference(
        self,
        task: str,
        context: Dict[str, Any],
        phase: str,
        use_tools: bool = True,
        print_cost: bool = True
    ) -> str:
        """
        Perform inference for a research task.

        Args:
            task: The task description
            context: Additional context (literature, plan, code, results, etc.)
            phase: Current research phase
            use_tools: Whether to enable tool use
            print_cost: Whether to print cost estimates

        Returns:
            Agent's response
        """
        system_prompt = self.get_system_prompt(phase)

        # Build user message with context
        user_message = self._build_context_message(task, context, phase)

        if not use_tools or not self.tools:
            # Simple query without tools
            return self.client.query(
                prompt=user_message,
                system_prompt=system_prompt,
                model=self.model,
                temperature=self.temperature,
                print_cost=print_cost
            )

        # Tool-augmented inference
        return self._tool_augmented_inference(
            user_message,
            system_prompt,
            print_cost
        )

    def _build_context_message(
        self,
        task: str,
        context: Dict[str, Any],
        phase: str
    ) -> str:
        """Build a context-rich message for the agent."""
        parts = [f"## Task\n{task}\n"]

        # Add relevant context based on phase
        if "literature" in context and context["literature"]:
            parts.append("## Literature Review Summary")
            for i, paper in enumerate(context["literature"][:10], 1):
                if isinstance(paper, dict):
                    parts.append(f"{i}. {paper.get('title', 'Untitled')}")
                    if "abstract" in paper:
                        parts.append(f"   Abstract: {paper['abstract'][:300]}...")
                else:
                    parts.append(f"{i}. {str(paper)[:500]}")
            parts.append("")

        if "plan" in context and context["plan"]:
            parts.append(f"## Research Plan\n{context['plan']}\n")

        if "code" in context and context["code"]:
            parts.append(f"## Current Code\n```python\n{context['code']}\n```\n")

        if "results" in context and context["results"]:
            parts.append(f"## Experimental Results\n{context['results']}\n")

        if "feedback" in context and context["feedback"]:
            parts.append(f"## Previous Feedback\n{context['feedback']}\n")

        if "notes" in context and context["notes"]:
            parts.append(f"## Task Notes\n{context['notes']}\n")

        return "\n".join(parts)

    def _tool_augmented_inference(
        self,
        user_message: str,
        system_prompt: str,
        print_cost: bool
    ) -> str:
        """
        Run inference with tool use, handling multiple rounds.

        Args:
            user_message: The user message
            system_prompt: System instructions
            print_cost: Whether to print costs

        Returns:
            Final response after tool use
        """
        messages = [{"role": "user", "content": user_message}]

        for round_num in range(self.max_tool_rounds):
            print(f"  [Agent {self.name}] Tool round {round_num + 1}/{self.max_tool_rounds}")

            # Query Claude with tools
            response = self.client.query_with_tools(
                prompt="" if round_num > 0 else user_message,
                system_prompt=system_prompt if round_num == 0 else "",
                tools=self.tools,
                model=self.model,
                temperature=self.temperature,
                print_cost=print_cost
            )

            # Check if there are tool calls
            tool_calls = response.get("tool_calls", [])
            text_response = response.get("text", "")
            stop_reason = response.get("stop_reason", "")

            if not tool_calls or stop_reason == "end_turn":
                # No more tool calls, return final response
                return text_response

            # Execute tool calls and continue conversation
            tool_results = []
            for tool_call in tool_calls:
                tool_name = tool_call["name"]
                tool_input = tool_call["input"]
                tool_id = tool_call["id"]

                print(f"    Executing tool: {tool_name}")
                result = self.tool_executor.execute_tool(tool_name, tool_input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": result
                })

            # Update messages for next round
            # Add assistant's response with tool uses
            messages.append({
                "role": "assistant",
                "content": response.get("content", [])
            })
            # Add tool results
            messages.append({
                "role": "user",
                "content": tool_results
            })

            # Continue conversation with updated context
            conv_response = self.client.conversation(
                messages=messages,
                system_prompt=system_prompt,
                model=self.model,
                temperature=self.temperature,
                tools=self.tools,
                print_cost=print_cost
            )

            # Parse the new response
            content = conv_response.get("content", [])
            text_parts = []
            new_tool_calls = []

            for block in content:
                if block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
                elif block.get("type") == "tool_use":
                    new_tool_calls.append(block)

            if not new_tool_calls:
                return "\n".join(text_parts)

            # Update for next round
            response = {
                "text": "\n".join(text_parts),
                "tool_calls": [
                    {
                        "id": tc.get("id"),
                        "name": tc.get("name"),
                        "input": tc.get("input")
                    }
                    for tc in new_tool_calls
                ],
                "stop_reason": conv_response.get("stop_reason", ""),
                "content": content
            }

        return f"Max tool rounds ({self.max_tool_rounds}) reached. Last response: {text_response}"

    def inference_with_commands(
        self,
        task: str,
        context: Dict[str, Any],
        phase: str,
        feedback: str = "",
        step: int = 0,
        available_commands: Optional[List[str]] = None,
        print_cost: bool = True
    ) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Perform inference that returns structured commands.

        Maintains compatibility with original AgentLaboratory command system.
        Agents respond with commands in format: ```COMMAND\ncontent\n```

        Args:
            task: The task description
            context: Additional context (research artifacts)
            phase: Current research phase
            feedback: Feedback from previous turn or tool execution
            step: Current step number
            available_commands: List of available command markers (e.g., ["DIALOGUE", "PLAN"])
            print_cost: Whether to print cost estimates

        Returns:
            (full_response, command_type, command_content)
            - full_response: Complete agent response
            - command_type: Parsed command (e.g., "submit_plan", "dialogue")
            - command_content: Content of the command
        """
        # Build system prompt with command instructions
        system_prompt = self.get_system_prompt(phase)

        # Add command-specific instructions based on phase and role
        command_instructions = self._get_command_instructions(phase)
        if command_instructions:
            system_prompt += "\n\n" + command_instructions

        # Build context-rich user message
        user_message = self._build_context_message(task, context, phase)

        # Add feedback if provided
        if feedback:
            user_message = f"{user_message}\n\nFeedback: {feedback}"

        # Add step information
        if step > 0:
            user_message = f"Step #{step}\n\n{user_message}"

        # Perform inference (no tools for command-based dialogue)
        response = self.client.query(
            prompt=user_message,
            system_prompt=system_prompt,
            model=self.model,
            temperature=self.temperature,
            print_cost=print_cost
        )

        # Parse response for commands
        command_type, command_content = CommandParser.extract_command(response)

        return (response, command_type, command_content)

    def _get_command_instructions(self, phase: str) -> str:
        """
        Get command instructions for current phase and role.

        Returns exact instruction strings from original AgentLaboratory.
        """
        builder = CommandInstructionBuilder()

        if phase == "literature review":
            return builder.get_literature_review_instructions()

        elif phase == "plan formulation":
            return builder.get_plan_formulation_instructions(self.role)

        elif phase == "data preparation":
            return builder.get_data_preparation_instructions(self.role)

        elif phase == "results interpretation":
            return builder.get_results_interpretation_instructions(self.role)

        elif phase == "report writing":
            return builder.get_report_writing_instructions(self.role)

        return ""

    def reset(self):
        """
        Reset agent state (mimics original BaseAgent.reset()).

        Clears conversation history to start fresh in new phase.
        """
        self.conversation_history.clear()
        # Note: In original, also clears prev_comm, but we don't track that separately

    def dialogue(
        self,
        other_agent: "ClaudeAgent",
        topic: str,
        context: Dict[str, Any],
        max_turns: int = 3
    ) -> str:
        """
        Engage in dialogue with another agent.

        Args:
            other_agent: The other agent to dialogue with
            topic: Topic of discussion
            context: Shared context
            max_turns: Maximum dialogue turns

        Returns:
            Dialogue transcript
        """
        transcript = []

        current_message = f"Let's discuss: {topic}"

        for turn in range(max_turns):
            # Self speaks first
            my_response = self.inference(
                task=current_message,
                context=context,
                phase="dialogue",
                use_tools=False,
                print_cost=True
            )
            transcript.append(f"[{self.name}]: {my_response}")

            # Other agent responds
            other_response = other_agent.inference(
                task=my_response,
                context=context,
                phase="dialogue",
                use_tools=False,
                print_cost=True
            )
            transcript.append(f"[{other_agent.name}]: {other_response}")

            current_message = other_response

        return "\n\n".join(transcript)


# Specialized agent classes
class PhDStudentAgent(ClaudeAgent):
    """PhD student agent for literature review and research assistance."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(
            role="phd_student",
            name="PhD Student",
            api_key=api_key,
            **kwargs
        )


class MLEngineerAgent(ClaudeAgent):
    """ML Engineer agent for experiment implementation."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(
            role="ml_engineer",
            name="ML Engineer",
            api_key=api_key,
            **kwargs
        )


class SWEngineerAgent(ClaudeAgent):
    """Software Engineer agent for code quality and data pipelines."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(
            role="sw_engineer",
            name="Software Engineer",
            api_key=api_key,
            **kwargs
        )


class PostdocAgent(ClaudeAgent):
    """Postdoc agent for research guidance."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(
            role="postdoc",
            name="Postdoc Researcher",
            api_key=api_key,
            **kwargs
        )


class ProfessorAgent(ClaudeAgent):
    """Professor agent for project oversight."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(
            role="professor",
            name="Professor",
            api_key=api_key,
            **kwargs
        )


class ReviewerAgent(ClaudeAgent):
    """Reviewer agent for paper evaluation."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(
            role="reviewer",
            name="Reviewer",
            api_key=api_key,
            **kwargs
        )

    def review_paper(self, paper_content: str) -> Dict[str, Any]:
        """
        Review a research paper and provide scores.

        Args:
            paper_content: The paper text or LaTeX content

        Returns:
            Dictionary with scores and feedback
        """
        review_prompt = f"""Please review the following research paper and provide:

1. Scores (1-10) for each criterion:
   - Originality: Novel contribution to the field
   - Quality: Technical quality of the work
   - Clarity: Clear presentation and writing
   - Significance: Impact and importance
   - Soundness: Correctness of methods and claims
   - Contribution: Advancement of knowledge
   - Presentation: Quality of figures, organization

2. Overall recommendation: Accept / Weak Accept / Weak Reject / Reject

3. Detailed feedback:
   - Strengths (at least 3 points)
   - Weaknesses (at least 3 points)
   - Suggestions for improvement

Paper content:
{paper_content[:30000]}

Provide your review in JSON format."""

        response = self.inference(
            task=review_prompt,
            context={},
            phase="report refinement",
            use_tools=False,
            print_cost=True
        )

        # Try to parse JSON from response
        try:
            # Find JSON in response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

        # Return raw response if JSON parsing fails
        return {"raw_review": response}


def create_research_team(api_key: Optional[str] = None) -> Dict[str, ClaudeAgent]:
    """
    Create a complete research team.

    Args:
        api_key: Anthropic API key

    Returns:
        Dictionary of agents by role
    """
    return {
        "phd_student": PhDStudentAgent(api_key=api_key),
        "ml_engineer": MLEngineerAgent(api_key=api_key),
        "sw_engineer": SWEngineerAgent(api_key=api_key),
        "postdoc": PostdocAgent(api_key=api_key),
        "professor": ProfessorAgent(api_key=api_key),
        "reviewer": ReviewerAgent(api_key=api_key)
    }


if __name__ == "__main__":
    print("Claude Agent System - Test")
    print("=" * 50)

    import os

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set.")
        print("Set it to test the agent system:")
        print('  export ANTHROPIC_API_KEY="your-key-here"')
    else:
        # Create a simple test agent
        agent = PhDStudentAgent()

        # Test simple inference
        response = agent.inference(
            task="Summarize what makes a good machine learning research paper.",
            context={},
            phase="literature review",
            use_tools=False,
            print_cost=True
        )

        print(f"\nAgent Response:\n{response[:1000]}...")
        print(f"\nToken Stats: {get_token_stats()}")
        print(f"Total Cost: ${get_current_cost():.6f}")
