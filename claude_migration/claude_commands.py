"""
Command Parser System for Claude Migration

Parses agent responses for commands in the format:
```COMMAND
content
```

Maintains compatibility with original AgentLaboratory command structure.
"""
import re
from typing import Tuple, Optional, Dict, Any


class CommandParser:
    """Parse agent responses for structured commands."""

    # Command mappings from original system
    COMMANDS = {
        "DIALOGUE": "dialogue",
        "PLAN": "submit_plan",
        "INTERPRETATION": "submit_interpretation",
        "SUBMIT_CODE": "submit_code",
        "LATEX": "submit_latex",
        "SUMMARY": "search_papers",
        "FULL_TEXT": "get_paper",
        "ADD_PAPER": "add_paper",
        "python": "execute_code",
        "SEARCH_HF": "search_datasets"
    }

    @staticmethod
    def extract_command(response: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract command and content from agent response.

        Looks for pattern: ```COMMAND\ncontent\n```

        Args:
            response: Full agent response text

        Returns:
            (command_type, content) where command_type is from COMMANDS mapping,
            or (None, None) if no command found
        """
        if not response:
            return (None, None)

        # Try each command pattern
        for cmd_marker, cmd_type in CommandParser.COMMANDS.items():
            # Pattern: ```COMMAND followed by content until closing ```
            pattern = rf"```{re.escape(cmd_marker)}\s*(.*?)```"
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)

            if match:
                content = match.group(1).strip()
                return (cmd_type, content)

        return (None, None)

    @staticmethod
    def extract_all_commands(response: str) -> list[Tuple[str, str]]:
        """
        Extract all commands from response (in case agent uses multiple).

        Returns:
            List of (command_type, content) tuples
        """
        commands = []

        for cmd_marker, cmd_type in CommandParser.COMMANDS.items():
            pattern = rf"```{re.escape(cmd_marker)}\s*(.*?)```"
            matches = re.finditer(pattern, response, re.DOTALL | re.IGNORECASE)

            for match in matches:
                content = match.group(1).strip()
                commands.append((cmd_type, content))

        return commands

    @staticmethod
    def has_command(response: str, command_type: str) -> bool:
        """
        Check if response contains a specific command.

        Args:
            response: Agent response
            command_type: Command type from COMMANDS values

        Returns:
            True if command is present
        """
        cmd_type, _ = CommandParser.extract_command(response)
        return cmd_type == command_type


def extract_prompt(text: str, marker: str) -> str:
    """
    Legacy function from original utils - extract content between markers.

    Equivalent to original extract_prompt from utils.py
    Used to extract: ```MARKER\ncontent\n```

    Args:
        text: Full text containing marker
        marker: Marker string (e.g., "DIALOGUE", "PLAN")

    Returns:
        Extracted content
    """
    parser = CommandParser()

    # Map marker to command type
    if marker in CommandParser.COMMANDS:
        cmd_type = CommandParser.COMMANDS[marker]
        extracted_cmd, content = parser.extract_command(text)

        if extracted_cmd == cmd_type and content:
            return content

    # Fallback: simple extraction
    pattern = rf"```{re.escape(marker)}\s*(.*?)```"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

    if match:
        return match.group(1).strip()

    return ""


class CommandInstructionBuilder:
    """Build command instruction strings for agent prompts."""

    @staticmethod
    def get_literature_review_instructions() -> str:
        """Instructions for literature review phase."""
        return """
To collect paper summaries, use the following command: ```SUMMARY
SEARCH QUERY
```
where SEARCH QUERY is a string that will be used to find papers with semantically similar content and SUMMARY is just the word SUMMARY. Make sure your search queries are very short.

To get the full paper text for an arXiv paper, use the following command: ```FULL_TEXT
arXiv paper ID
```
where arXiv paper ID is the ID of the arXiv paper (which can be found by using the SUMMARY command), and FULL_TEXT is just the word FULL_TEXT. Make sure to read the full text using the FULL_TEXT command before adding it to your list of relevant papers.

If you believe a paper is relevant to the research project proposal, you can add it to the official review after reading using the following command: ```ADD_PAPER
arXiv_paper_ID
PAPER_SUMMARY
```
where arXiv_paper_ID is the ID of the arXiv paper, PAPER_SUMMARY is a brief summary of the paper, and ADD_PAPER is just the word ADD_PAPER. You can only add one paper at a time.

Make sure to use ADD_PAPER when you see a relevant paper. DO NOT use SUMMARY too many times.

You can only use a single command per inference turn. Do not use more than one command per inference. If you use multiple commands, then only one of them will be executed, not both.

Make sure to extensively discuss the experimental results in your summary.

When performing a command, make sure to include the three ticks (```) at the top and bottom ```COMMAND
text
``` where COMMAND is the specific command you want to run (e.g. ADD_PAPER, FULL_TEXT, SUMMARY). Do not use the word COMMAND make sure to use the actual command.
"""

    @staticmethod
    def get_plan_formulation_instructions(role: str) -> str:
        """Instructions for plan formulation phase."""
        if role == "postdoc":
            return """
You can produce dialogue using the following command: ```DIALOGUE
dialogue here
```
where dialogue here is the actual dialogue you will send and DIALOGUE is just the word DIALOGUE.

When you believe a good plan has been arrived at between you and the PhD student you can use the following command to end the dialogue and submit the plan: ```PLAN
plan here
```
where plan here is the actual plan to be transmitted and PLAN is just the word PLAN. Plan here should provide a clear outline for how to achieve the task, including what machine learning models to use and implement, what types of datasets should be searched for and used to train the model, and the exact details of the experiment.

You can only use a SINGLE command per inference turn. Do not use more than one command per inference. If you use multiple commands, then only one of them will be executed, NOT BOTH.

Make sure not to produce too much dialogue and to submit a plan in reasonable time.

When performing a command, make sure to include the three ticks (```) at the top and bottom ```COMMAND
text
``` where COMMAND is the specific command you want to run (e.g. PLAN, DIALOGUE).
"""
        else:  # phd
            return """
You can produce dialogue using the following command: ```DIALOGUE
dialogue here
```
where 'dialogue here' is the actual dialogue you will send and DIALOGUE is just the word DIALOGUE.

You can only use a single command per inference turn. Do not use more than one command per inference. If you use multiple commands, then only one of them will be executed, not both.

When performing a command, make sure to include the three ticks (```) at the top and bottom ```COMMAND
text
``` where COMMAND is the specific command you want to run (e.g. DIALOGUE).
"""

    @staticmethod
    def get_data_preparation_instructions(role: str) -> str:
        """Instructions for data preparation phase."""
        if role == "sw_engineer":
            return """
You can produce dialogue using the following command: ```DIALOGUE
dialogue here
```
where 'dialogue here' is the actual dialogue you will send and DIALOGUE is just the word DIALOGUE.

When you and the ML engineer have finalized your dataset preparation code and are ready to submit the final code, please use the following command: ```SUBMIT_CODE
code here
```
where 'code here' is the finalized code you will send and SUBMIT_CODE is just the word SUBMIT_CODE. Do not use any classes or functions. The submitted code must have a HuggingFace dataset import and must use an external HuggingFace dataset. If your code returns any errors, they will be provided to you, and you are also able to see print statements. Make sure function variables are created inside the function or passed as a function parameter. DO NOT CREATE A MAIN FUNCTION.

Make sure to submit code in a reasonable amount of time. Do not make the code too complex, try to make it simple. Do not take too long to submit code. Submit the code early. You should submit the code ASAP.

You can only use a single command per inference turn. Do not use more than one command per inference. If you use multiple commands, then only one of them will be executed, not both.

When performing a command, make sure to include the three ticks (```) at the top and bottom ```COMMAND
text
``` where COMMAND is the specific command you want to run (e.g. SUBMIT_CODE, DIALOGUE).
"""
        else:  # ml_engineer
            return """
You can produce dialogue using the following command: ```DIALOGUE
dialogue here
```
where dialogue here is the actual dialogue you will send, and DIALOGUE is just the word DIALOGUE.

To test dataset loading code, you can execute Python code using: ```python
code here
```
where code here is the Python code to execute.

To search for datasets on HuggingFace, use: ```SEARCH_HF
search query
```
where search query is your search terms.

You can only use a single command per inference turn. Do not use more than one command per inference.

When performing a command, make sure to include the three ticks (```) at the top and bottom ```COMMAND
text
``` where COMMAND is the specific command you want to run (e.g. python, DIALOGUE, SEARCH_HF).
"""

    @staticmethod
    def get_results_interpretation_instructions(role: str) -> str:
        """Instructions for results interpretation phase."""
        if role == "postdoc":
            return """
You can produce dialogue using the following command: ```DIALOGUE
dialogue here
```
where dialogue here is the actual dialogue you will send and DIALOGUE is just the word DIALOGUE.

When you believe a good interpretation has been arrived at between you and the PhD student you can use the following command to end the dialogue and submit the interpretation: ```INTERPRETATION
interpretation here
```
where interpretation here is the actual interpretation to be transmitted and INTERPRETATION is just the word INTERPRETATION. Please provide an INTERPRETATION in a reasonable amount of time.

You must submit the interpretation during this phase in a reasonable amount of time. Do not delay the submission.

When performing a command, make sure to include the three ticks (```) at the top and bottom ```COMMAND
text
``` where COMMAND is the specific command you want to run (e.g. INTERPRETATION, DIALOGUE).
"""
        else:  # phd
            return """
You can produce dialogue using the following command: ```DIALOGUE
dialogue here
```
where 'dialogue here' is the actual dialogue you will send and DIALOGUE is just the word DIALOGUE.

When performing a command, make sure to include the three ticks (```) at the top and bottom ```COMMAND
text
``` where COMMAND is the specific command you want to run (e.g. DIALOGUE).
"""

    @staticmethod
    def get_report_writing_instructions(role: str) -> str:
        """Instructions for report writing phase."""
        if role == "professor":
            return """
You can produce dialogue using the following command: ```DIALOGUE
dialogue here
```
where dialogue here is the actual dialogue you will send and DIALOGUE is just the word DIALOGUE.

When you believe a good report has been arrived at between you and the PhD student you can use the following command to end the dialogue and submit the report: ```LATEX
report here
```
where report here is the actual report written in compilable latex to be transmitted and LATEX is just the word LATEX.

Your report should include numbers, relevant metrics to the experiment (e.g. accuracy or loss) and measures of significance. You must propagate this information accurately. You must also submit the report promptly. Do not delay too long.

You must be incredibly detailed about what you did for the experiment and all of the findings.

When performing a command, make sure to include the three ticks (```) at the top and bottom ```COMMAND
<Insert command here>
``` where COMMAND is the specific command you want to run (e.g. REPORT, DIALOGUE).
"""
        else:  # phd
            return """
You can produce dialogue using the following command: ```DIALOGUE
dialogue here
```
where 'dialogue here' is the actual dialogue you will send and DIALOGUE is just the word DIALOGUE.

When performing a command, make sure to include the three ticks (```) at the top and bottom ```COMMAND
text
``` where COMMAND is the specific command you want to run (e.g. DIALOGUE).
"""
