"""
User interface utilities using Rich for formatted output.
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
import rich.box
from typing import List, Dict, Any

console = Console()

def print_info(message: str):
    """Print an info message."""
    console.print(f"[bold blue][INFO][/bold blue] {message}")

def print_success(message: str):
    """Print a success message."""
    console.print(f"[bold green][✓][/bold green] {message}")

def print_error(message: str):
    """Print an error message."""
    console.print(f"[bold red][✗][/bold red] {message}")

def print_warning(message: str):
    """Print a warning message."""
    console.print(f"[bold yellow][!][/bold yellow] {message}")

def print_agent_thought(agent_name: str, thought: str):
    """Display an agent's reasoning."""
    console.print(Panel(thought, title=f"[bold cyan]{agent_name}[/bold cyan]", border_style="cyan", expand=False))

def display_plan(plan_id: str, plan: Dict[str, Any]):
    """Display a plan in table format."""
    table = Table(box=rich.box.ROUNDED)
    table.add_column("Step", style="cyan", no_wrap=True)
    table.add_column("Tool", style="magenta")
    table.add_column("Arguments", style="green")

    for i, step in enumerate(plan.get("steps", [])):
        args_str = str(step.get("args", {}))
        if len(args_str) > 100:
            args_str = args_str[:100] + "..."
            
        table.add_row(str(i + 1), step.get("tool", "unknown"), args_str)

    console.print(Panel(table, title=f"Plan: {plan_id}", border_style="blue"))

def display_plan_list(plans: List[Dict[str, Any]]):
    """Display a list of plans."""
    table = Table(title="Agent Plans", box=rich.box.HEAVY_EDGE)
    table.add_column("ID", style="cyan")
    table.add_column("Status", style="yellow")
    table.add_column("Prompt", style="white")
    table.add_column("Created", style="dim")

    for plan in plans:
        status = plan['status']
        
        # Color coding status
        if status == "COMPLETED":
            status = f"[green]{status}[/green]"
        elif status == "FAILED":
            status = f"[red]{status}[/red]"
        elif status == "IN_PROGRESS":
            status = f"[yellow]{status}[/yellow]"
            
        prompt_display = plan['prompt']
        if len(prompt_display) > 60:
            prompt_display = prompt_display[:60] + "..."
            
        created_at = plan.get('created_at', 'N/A')
        if isinstance(created_at, str) and len(created_at) > 10:
            created_at = created_at[:10]
            
        table.add_row(plan['plan_id'], status, prompt_display, created_at)

    console.print(table)

def display_tool_result(tool_name: str, result, verbose: bool = True):
    """Display the result of a tool execution."""
    if result.success:
        if verbose and result.stdout:
            console.print(Panel(
                result.stdout[:500], 
                title=f"[bold green]✓ {tool_name}[/bold green]", 
                border_style="green", 
                expand=False
            ))
        else:
            print_success(f"{tool_name} executed successfully")
    else:
        error_msg = result.stderr if result.stderr else f"Tool failed with code {result.return_code}"
        console.print(Panel(
            error_msg[:500], 
            title=f"[bold red]✗ {tool_name}[/bold red]", 
            border_style="red", 
            expand=False
        ))

def display_divider(title: str = ""):
    """Display a visual divider."""
    if title:
        console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
        console.print(f"[bold cyan]{title:^60}[/bold cyan]")
        console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")
    else:
        console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")
