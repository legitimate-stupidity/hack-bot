"""
Context management for agents.
Handles retrieval of relevant information for LLM prompts.
"""
from state import state
import os
from typing import List

def build_context(plan_id: str, history_limit: int = 10) -> str:
    """
    Build context string for LLM prompts.
    Includes recent history and current directory state.
    """
    context = ""
    
    # Add recent task history
    context += "--- Recent Task History ---\n"
    if plan_id:
        history = state.get_history(plan_id, limit=history_limit)
        for entry in history:
            content = entry['content']
            if len(content) > 200:
                content = content[:200] + "..."
            context += f"[{entry['role'].upper()}] {content}\n"
    else:
        context += "(No history available for new task)\n"
    
    # Add current filesystem state
    context += "\n--- Current Directory Structure ---\n"
    try:
        files = os.listdir(".")
        files_str = "\n".join(f"  - {f}" for f in files[:20])
        context += files_str
        if len(files) > 20:
            context += f"\n  ... and {len(files) - 20} more files"
    except Exception as e:
        context += f"(Error listing files: {e})"
    
    return context

def get_recent_context(plan_id: str) -> str:
    """Get minimal context for quick operations."""
    return build_context(plan_id, history_limit=5)

def summarize_history(plan_id: str) -> str:
    """Summarize the full history of a plan (useful for long tasks)."""
    history = state.get_history(plan_id)
    
    summary = f"Plan Summary (Total Interactions: {len(history)}):\n"
    
    # Group by role
    by_role = {}
    for entry in history:
        role = entry['role']
        if role not in by_role:
            by_role[role] = []
        by_role[role].append(entry['content'])
    
    for role, contents in by_role.items():
        summary += f"\n{role.upper()} ({len(contents)} entries):\n"
        # Show first and last
        if contents:
            first = contents[0]
            if len(first) > 100:
                first = first[:100] + "..."
            summary += f"  - Start: {first}\n"
            
            if len(contents) > 1:
                last = contents[-1]
                if len(last) > 100:
                    last = last[:100] + "..."
                summary += f"  - Latest: {last}\n"
    
    return summary
