"""
Tool definitions for agent execution.
These are the "hands" of the agent - what it can actually do.
"""
import asyncio
import subprocess
import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class ToolResult:
    """Result of a tool execution."""
    success: bool
    stdout: str = ""
    stderr: str = ""
    return_code: Optional[int] = None

async def run_shell(command: str) -> ToolResult:
    """Execute a shell command asynchronously."""
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
        
        return ToolResult(
            success=(process.returncode == 0),
            stdout=stdout.decode(errors='ignore').strip(),
            stderr=stderr.decode(errors='ignore').strip(),
            return_code=process.returncode
        )
    except asyncio.TimeoutError:
        return ToolResult(success=False, stderr="Command timeout (30s)")
    except Exception as e:
        return ToolResult(success=False, stderr=str(e))

async def write_file(path: str, content: str) -> ToolResult:
    """Write content to a file."""
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return ToolResult(success=True, stdout=f"Wrote {len(content)} bytes to {path}")
    except Exception as e:
        return ToolResult(success=False, stderr=str(e))

async def read_file(path: str) -> ToolResult:
    """Read content from a file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return ToolResult(success=True, stdout=content)
    except Exception as e:
        return ToolResult(success=False, stderr=str(e))

async def list_files(path: str = ".") -> ToolResult:
    """List files in a directory."""
    try:
        files = os.listdir(path)
        return ToolResult(success=True, stdout="\n".join(files))
    except Exception as e:
        return ToolResult(success=False, stderr=str(e))

async def mkdir(path: str) -> ToolResult:
    """Create a directory."""
    try:
        os.makedirs(path, exist_ok=True)
        return ToolResult(success=True, stdout=f"Created directory: {path}")
    except Exception as e:
        return ToolResult(success=False, stderr=str(e))

async def remove_file(path: str) -> ToolResult:
    """Remove a file."""
    try:
        if os.path.isfile(path):
            os.remove(path)
            return ToolResult(success=True, stdout=f"Removed file: {path}")
        else:
            return ToolResult(success=False, stderr=f"File not found: {path}")
    except Exception as e:
        return ToolResult(success=False, stderr=str(e))

# Toolbox available to agents
TOOLBOX = {
    "run_shell": run_shell,
    "write_file": write_file,
    "read_file": read_file,
    "list_files": list_files,
    "mkdir": mkdir,
    "remove_file": remove_file,
}

def get_tool_help() -> str:
    """Return help text for available tools."""
    return """
Available tools:
- run_shell(command): Execute a shell command
- write_file(path, content): Write content to a file
- read_file(path): Read content from a file
- list_files(path): List files in a directory (default: current)
- mkdir(path): Create a directory
- remove_file(path): Delete a file
"""
