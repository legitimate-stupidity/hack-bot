"""Basic tests for the agent framework."""
import pytest
import asyncio
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent.tools import run_shell, write_file, read_file, ToolResult
from agent.state import state, PlanStatus
from agent.llm import llm


@pytest.mark.asyncio
async def test_run_shell_success():
    """Test successful shell command execution."""
    result = await run_shell("echo 'test'")
    assert result.success
    assert "test" in result.stdout


@pytest.mark.asyncio
async def test_run_shell_failure():
    """Test failed shell command execution."""
    result = await run_shell("false")
    assert not result.success
    assert result.return_code != 0


@pytest.mark.asyncio
async def test_write_and_read_file(tmp_path):
    """Test file writing and reading."""
    test_file = tmp_path / "test.txt"
    content = "Hello, World!"
    
    # Write file
    result = await write_file(str(test_file), content)
    assert result.success
    
    # Read file
    result = await read_file(str(test_file))
    assert result.success
    assert result.stdout == content


def test_state_create_plan():
    """Test creating a plan in the database."""
    prompt = "Test task"
    plan = {
        "thought": "Test thought",
        "steps": [
            {"tool": "list_files", "args": {"path": "."}}
        ]
    }
    
    plan_id = state.create_plan(prompt, plan)
    assert plan_id.startswith("plan_")
    
    # Retrieve plan
    retrieved = state.get_plan(plan_id)
    assert retrieved is not None
    assert retrieved['prompt'] == prompt
    assert retrieved['status'] == PlanStatus.PENDING.value


def test_state_update_status():
    """Test updating plan status."""
    prompt = "Test status update"
    plan = {"steps": []}
    
    plan_id = state.create_plan(prompt, plan)
    state.update_plan_status(plan_id, PlanStatus.IN_PROGRESS)
    
    retrieved = state.get_plan(plan_id)
    assert retrieved['status'] == PlanStatus.IN_PROGRESS.value


def test_state_history():
    """Test plan history tracking."""
    prompt = "Test history"
    plan = {"steps": []}
    
    plan_id = state.create_plan(prompt, plan)
    state.add_history(plan_id, "user", "test message")
    state.add_history(plan_id, "agent", "test response")
    
    history = state.get_history(plan_id)
    assert len(history) >= 2  # At least the initial and two added entries


@pytest.mark.asyncio
async def test_llm_planning():
    """Test LLM plan generation."""
    prompt = "Create a Flask app"
    context = "Current directory: /tmp"
    
    plan = await llm.generate_json(f"generate a structured plan: {prompt}")
    assert "steps" in plan
    assert isinstance(plan["steps"], list)


@pytest.mark.asyncio
async def test_llm_correction():
    """Test LLM error correction."""
    error_prompt = "fix the error: ModuleNotFoundError"
    plan = await llm.generate_json(error_prompt)
    
    assert "steps" in plan
    assert len(plan["steps"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
