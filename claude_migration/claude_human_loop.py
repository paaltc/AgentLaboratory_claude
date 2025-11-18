"""
Human-in-the-Loop Checkpoint System

Manages human oversight and feedback at key workflow stages.
Mimics the human_in_loop functionality from original AgentLaboratory.
"""
from typing import Dict, List, Optional, Tuple


class HumanCheckpoint:
    """
    Manages human-in-the-loop checkpoints.

    Allows humans to review, approve, or reject phase outputs with feedback.
    Maintains compatibility with original ai_lab_repo.py human_in_loop system.
    """

    def __init__(
        self,
        enabled_phases: Optional[Dict[str, bool]] = None,
        verbose: bool = True
    ):
        """
        Initialize human checkpoint system.

        Args:
            enabled_phases: Dict mapping phase names to enabled status
                e.g., {
                    "literature review": True,
                    "plan formulation": False,
                    ...
                }
            verbose: Print detailed information
        """
        self.enabled_phases = enabled_phases or {}
        self.verbose = verbose
        self.feedback_notes: List[Dict[str, str]] = []

    def check(
        self,
        phase: str,
        output: str,
        label: str = "output"
    ) -> Tuple[bool, Optional[str]]:
        """
        Check with human if phase output should be approved.

        Mimics human_in_loop from original ai_lab_repo.py:547-574

        Args:
            phase: Phase name (e.g., "literature review")
            output: Phase output to review
            label: Label for output type (e.g., "plan", "code", "report")

        Returns:
            (should_retry, feedback_note)
            - should_retry: True if human wants to retry phase
            - feedback_note: Feedback text if rejecting, None if approving
        """
        # Check if checkpoint is enabled for this phase
        if not self.enabled_phases.get(phase, False):
            if self.verbose:
                print(f"[Human checkpoint disabled for: {phase}]")
            return (False, None)

        # Display output to human
        print("\n\n\n")
        print("=" * 70)
        print(f"HUMAN CHECKPOINT: {phase}")
        print("=" * 70)
        print(f"\nPresented is the result of the phase [{phase}]:\n")
        print("-" * 70)
        print(output)
        print("-" * 70)

        # Get human decision
        y_or_no = None
        while y_or_no not in ["y", "n"]:
            y_or_no = input(
                f"\n\nAre you happy with the presented {label}? Respond Y or N: "
            ).strip().lower()

            if y_or_no == "y":
                if self.verbose:
                    print(f"\n✓ {phase} approved by human\n")
                return (False, None)

            elif y_or_no == "n":
                # Get feedback from human
                feedback = input(
                    "\nPlease provide notes for the agent so that they can try again and improve performance:\n> "
                )

                # Store feedback
                self.feedback_notes.append({
                    "phase": phase,
                    "note": feedback
                })

                if self.verbose:
                    print(f"\n✗ {phase} rejected - will retry with feedback\n")

                return (True, feedback)

            else:
                print("Invalid response, please type Y or N")

        return (False, None)

    def get_notes_for_phase(self, phase: str) -> List[str]:
        """
        Get accumulated feedback notes for a specific phase.

        Args:
            phase: Phase name

        Returns:
            List of feedback note strings
        """
        return [
            note["note"]
            for note in self.feedback_notes
            if note["phase"] == phase
        ]

    def clear_notes_for_phase(self, phase: str):
        """
        Clear feedback notes for a specific phase.

        Args:
            phase: Phase name
        """
        self.feedback_notes = [
            note for note in self.feedback_notes
            if note["phase"] != phase
        ]

    def get_all_notes(self) -> List[Dict[str, str]]:
        """Get all feedback notes."""
        return self.feedback_notes.copy()

    def clear_all_notes(self):
        """Clear all feedback notes."""
        self.feedback_notes.clear()

    @staticmethod
    def get_default_config(human_mode: bool = False) -> Dict[str, bool]:
        """
        Get default human-in-loop configuration.

        Mimics the human_in_loop dict from ai_lab_repo.py:764-772

        Args:
            human_mode: If True, enable all checkpoints

        Returns:
            Configuration dict
        """
        return {
            "literature review": human_mode,
            "plan formulation": human_mode,
            "data preparation": human_mode,
            "running experiments": human_mode,
            "results interpretation": human_mode,
            "report writing": human_mode,
            "report refinement": human_mode,
        }


class NotesManager:
    """
    Manages notes and guidance for agents.

    Mimics the notes system from original AgentLaboratory where
    notes are injected into agent prompts for specific phases.
    """

    def __init__(self):
        """Initialize notes manager."""
        self.notes: List[Dict[str, Any]] = []

    def add_note(self, phases: List[str], note: str):
        """
        Add a note for specific phases.

        Args:
            phases: List of phase names this note applies to
            note: Note text
        """
        self.notes.append({
            "phases": phases,
            "note": note
        })

    def get_notes_for_phase(self, phase: str) -> List[str]:
        """
        Get all notes applicable to a phase.

        Args:
            phase: Phase name

        Returns:
            List of note strings
        """
        return [
            note["note"]
            for note in self.notes
            if phase in note["phases"]
        ]

    def format_notes_for_prompt(self, phase: str) -> str:
        """
        Format notes for inclusion in agent prompt.

        Args:
            phase: Phase name

        Returns:
            Formatted notes string
        """
        phase_notes = self.get_notes_for_phase(phase)

        if not phase_notes:
            return ""

        return f"Notes for the task objective: {phase_notes}\n"

    def clear(self):
        """Clear all notes."""
        self.notes.clear()

    def remove_notes_for_phase(self, phase: str):
        """
        Remove notes for a specific phase.

        Args:
            phase: Phase name
        """
        self.notes = [
            note for note in self.notes
            if phase not in note["phases"]
        ]
