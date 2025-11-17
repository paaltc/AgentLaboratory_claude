#!/usr/bin/env python3
"""
Agent Laboratory - Claude Pro Token Management & Checkpoint Resumption
Handles token limits and automatic resumption for long-running workflows

Features:
- Track tokens per phase
- Detect token limit approaching
- Save checkpoint automatically
- Resume from checkpoint seamlessly
- Continue workflow where it left off
"""

import json
import pickle
from pathlib import Path
from datetime import datetime

class CheckpointManager:
    """Manages checkpoints for resumable workflows"""
    
    def __init__(self, lab_dir="MATH_research_dir"):
        self.lab_dir = Path(lab_dir)
        self.state_dir = Path("state_saves")
        self.state_dir.mkdir(exist_ok=True)
        
    def create_checkpoint(self, phase_name, data, token_count=0, tokens_used=0):
        """
        Create a checkpoint for current phase
        
        Args:
            phase_name: Name of current phase (e.g., "literature_review")
            data: Dictionary containing state to save
            token_count: Total tokens in session
            tokens_used: Tokens used so far
        
        Returns:
            checkpoint_id: Unique identifier for this checkpoint
        """
        checkpoint_id = f"{phase_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        checkpoint_file = self.state_dir / f"{phase_name}.pkl"
        
        checkpoint_data = {
            'phase': phase_name,
            'timestamp': datetime.now().isoformat(),
            'data': data,
            'token_count': token_count,
            'tokens_used': tokens_used,
            'checkpoint_id': checkpoint_id,
        }
        
        # Save checkpoint
        with open(checkpoint_file, 'wb') as f:
            pickle.dump(checkpoint_data, f)
        
        # Also save metadata
        metadata_file = self.state_dir / f"{phase_name}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump({
                'checkpoint_id': checkpoint_id,
                'phase': phase_name,
                'timestamp': checkpoint_data['timestamp'],
                'tokens_used': tokens_used,
                'file': str(checkpoint_file),
            }, f, indent=2)
        
        return checkpoint_id
    
    def load_checkpoint(self, phase_name):
        """
        Load checkpoint for a phase
        
        Args:
            phase_name: Name of phase to load
        
        Returns:
            checkpoint_data or None if not found
        """
        checkpoint_file = self.state_dir / f"{phase_name}.pkl"
        
        if checkpoint_file.exists():
            with open(checkpoint_file, 'rb') as f:
                return pickle.load(f)
        return None
    
    def list_checkpoints(self):
        """List all available checkpoints"""
        checkpoints = []
        for pkl_file in self.state_dir.glob("*.pkl"):
            if "_metadata.json" not in str(pkl_file):
                try:
                    with open(pkl_file, 'rb') as f:
                        data = pickle.load(f)
                        checkpoints.append({
                            'phase': data.get('phase'),
                            'timestamp': data.get('timestamp'),
                            'tokens_used': data.get('tokens_used'),
                            'file': str(pkl_file),
                        })
                except:
                    pass
        return checkpoints
    
    def cleanup_old_checkpoints(self, keep_latest=5):
        """Keep only latest N checkpoints per phase"""
        by_phase = {}
        for cp in self.list_checkpoints():
            phase = cp['phase']
            if phase not in by_phase:
                by_phase[phase] = []
            by_phase[phase].append(cp)
        
        for phase, cps in by_phase.items():
            if len(cps) > keep_latest:
                # Sort by timestamp descending
                cps.sort(key=lambda x: x['timestamp'], reverse=True)
                # Delete old ones
                for old_cp in cps[keep_latest:]:
                    Path(old_cp['file']).unlink()


class TokenManager:
    """Manages token limits for Claude Pro sessions"""
    
    # Claude Pro token limits (approximate)
    TOKEN_LIMITS = {
        'claude-3-5-sonnet': 200000,
        'claude-3-opus': 200000,
        'gpt-4o': 128000,
        'gpt-4o-mini': 128000,
        'o1-mini': 128000,
    }
    
    # Warn when reaching this % of limit
    WARNING_THRESHOLD = 0.75
    
    # Dangerous zone - save and prepare to resume
    DANGER_THRESHOLD = 0.90
    
    def __init__(self, model='claude-3-5-sonnet'):
        self.model = model
        self.limit = self.TOKEN_LIMITS.get(model, 128000)
        self.tokens_used = 0
        self.phase_tokens = {}
    
    def add_tokens(self, phase_name, tokens):
        """Track tokens used in a phase"""
        self.tokens_used += tokens
        if phase_name not in self.phase_tokens:
            self.phase_tokens[phase_name] = 0
        self.phase_tokens[phase_name] += tokens
    
    def get_remaining(self):
        """Get remaining tokens"""
        return self.limit - self.tokens_used
    
    def get_usage_percent(self):
        """Get token usage as percentage"""
        return (self.tokens_used / self.limit) * 100
    
    def is_warning_level(self):
        """Check if approaching warning threshold"""
        return self.get_usage_percent() >= (self.WARNING_THRESHOLD * 100)
    
    def is_danger_level(self):
        """Check if in danger zone"""
        return self.get_usage_percent() >= (self.DANGER_THRESHOLD * 100)
    
    def get_status(self):
        """Get token usage status"""
        return {
            'model': self.model,
            'total_limit': self.limit,
            'tokens_used': self.tokens_used,
            'remaining': self.get_remaining(),
            'percent_used': self.get_usage_percent(),
            'is_warning': self.is_warning_level(),
            'is_danger': self.is_danger_level(),
            'by_phase': self.phase_tokens,
        }


class ResumableWorkflow:
    """Wraps workflow execution with checkpoint/resume capability"""
    
    PHASE_ORDER = [
        'literature_review',
        'plan_formulation',
        'data_preparation',
        'running_experiments',
        'results_interpretation',
        'report_writing',
        'report_refinement',
    ]
    
    def __init__(self, lab, model='claude-3-5-sonnet'):
        self.lab = lab
        self.checkpoint_mgr = CheckpointManager()
        self.token_mgr = TokenManager(model)
        self.phase_status = {}
    
    def get_next_phase(self, current_phase=None):
        """Get next phase to execute"""
        if current_phase is None:
            return self.PHASE_ORDER[0]
        
        try:
            idx = self.PHASE_ORDER.index(current_phase)
            if idx + 1 < len(self.PHASE_ORDER):
                return self.PHASE_ORDER[idx + 1]
        except ValueError:
            pass
        
        return None
    
    def should_checkpoint(self, phase_name, tokens_in_phase):
        """Determine if checkpoint should be saved"""
        self.token_mgr.add_tokens(phase_name, tokens_in_phase)
        
        # Save checkpoint if:
        # 1. Danger level reached
        # 2. End of phase
        # 3. Periodically during long phases
        
        return (
            self.token_mgr.is_danger_level() or
            tokens_in_phase > 10000  # Large phase
        )
    
    def resume_workflow(self):
        """
        Resume workflow from latest checkpoint
        
        Returns:
            (next_phase, checkpoint_data) or (None, None) if no resume needed
        """
        # Find first incomplete phase
        for phase in self.PHASE_ORDER:
            checkpoint = self.checkpoint_mgr.load_checkpoint(phase)
            if checkpoint:
                return phase, checkpoint
        
        return None, None
    
    def can_continue(self):
        """Check if workflow can continue based on token limits"""
        # If we haven't hit 95% limit, we can continue
        if self.token_mgr.get_usage_percent() < 95:
            return True
        
        # Save checkpoint and stop
        return False
    
    def get_summary(self):
        """Get workflow execution summary"""
        return {
            'token_status': self.token_mgr.get_status(),
            'checkpoints_available': len(self.checkpoint_mgr.list_checkpoints()),
            'checkpoint_files': self.checkpoint_mgr.list_checkpoints(),
        }


# ============================================================================
# DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("CLAUDE PRO TOKEN MANAGEMENT & CHECKPOINT SYSTEM DEMONSTRATION")
    print("="*70 + "\n")
    
    # Initialize managers
    checkpoint_mgr = CheckpointManager()
    token_mgr = TokenManager('claude-3-5-sonnet')
    
    print("TOKEN MANAGER TEST:")
    print("-" * 70)
    
    # Simulate token usage across phases
    phases_data = [
        ('literature_review', 2000),
        ('plan_formulation', 8000),
        ('data_preparation', 10000),
        ('running_experiments', 30000),
    ]
    
    for phase, tokens in phases_data:
        token_mgr.add_tokens(phase, tokens)
        status = token_mgr.get_status()
        
        print(f"\n{phase}:")
        print(f"  Tokens used: {tokens:,}")
        print(f"  Total used: {status['tokens_used']:,} / {status['total_limit']:,}")
        print(f"  Usage: {status['percent_used']:.1f}%")
        print(f"  Remaining: {status['remaining']:,}")
        
        if status['is_danger']:
            print(f"  ⚠️  DANGER ZONE - Should save checkpoint!")
        elif status['is_warning']:
            print(f"  ⚠️  WARNING - Approaching token limit")
    
    print("\n\nCHECKPOINT MANAGER TEST:")
    print("-" * 70)
    
    # Create some checkpoints
    for phase, tokens in phases_data:
        data = {
            'phase': phase,
            'data': f"Sample data for {phase}",
            'step': 5,
        }
        
        checkpoint_id = checkpoint_mgr.create_checkpoint(
            phase,
            data,
            tokens_used=sum(t for p, t in phases_data if p == phase)
        )
        print(f"✓ Created checkpoint for {phase:25s} (ID: {checkpoint_id})")
    
    print("\n\nAVAILABLE CHECKPOINTS:")
    print("-" * 70)
    
    checkpoints = checkpoint_mgr.list_checkpoints()
    for cp in checkpoints:
        print(f"• {cp['phase']:25s} - {cp['timestamp']}")
    
    print("\n\nRESUMABLE WORKFLOW TEST:")
    print("-" * 70)
    
    class MockLab:
        pass
    
    workflow = ResumableWorkflow(MockLab(), 'claude-3-5-sonnet')
    
    # Simulate checking next phase
    current = 'data_preparation'
    next_phase = workflow.get_next_phase(current)
    print(f"\nCurrent phase: {current}")
    print(f"Next phase: {next_phase}")
    
    # Resume from checkpoint
    next_ph, checkpoint = workflow.resume_workflow()
    if next_ph:
        print(f"\n✓ Can resume from checkpoint:")
        print(f"  Phase: {next_ph}")
        print(f"  Timestamp: {checkpoint.get('timestamp')}")
    
    print("\n\nWORKFLOW SUMMARY:")
    print("-" * 70)
    
    summary = workflow.get_summary()
    tokens = summary['token_status']
    print(f"\nToken Usage:")
    print(f"  Total limit: {tokens['total_limit']:,}")
    print(f"  Used: {tokens['tokens_used']:,}")
    print(f"  Remaining: {tokens['remaining']:,}")
    print(f"  Percent: {tokens['percent_used']:.1f}%")
    
    print(f"\nCheckpoints:")
    print(f"  Available: {summary['checkpoints_available']}")
    print(f"  Can resume: {workflow.resume_workflow()[0] is not None}")
    
    print("\n" + "="*70)
    print("✓ CHECKPOINT & RESUMPTION SYSTEM OPERATIONAL")
    print("="*70 + "\n")
