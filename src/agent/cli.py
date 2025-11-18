"""
CLI interface using Typer.
Main entry point for the agent system.
"""
import typer
import asyncio
import sys
from orchestrator import orchestrator
from state import state
import ui

# Windows asyncio fix
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except AttributeError:
        pass

app = typer.Typer(help="Autonomous coding agent with self-correction capabilities")

@app.command()
def plan(
    prompt: str = typer.Argument(..., help="Task description for the agent")
):
    """Generate a plan for a task (no execution)."""
    asyncio.run(orchestrator.plan(prompt))

@app.command()
def build(
    plan_id: str = typer.Argument(..., help="Plan ID to execute")
):
    """Execute a plan."""
    asyncio.run(orchestrator.build(plan_id))

@app.command(name="list")
def list_plans():
    """List all plans and their status."""
    plans = state.list_plans(limit=30)
    if not plans:
        ui.print_info("No plans found")
        return
    ui.display_plan_list(plans)

@app.command()
def resume(
    plan_id: str = typer.Argument(..., help="Plan ID to resume")
):
    """Resume a paused/failed plan."""
    asyncio.run(orchestrator.resume(plan_id))

@app.command()
def info(
    plan_id: str = typer.Argument(..., help="Plan ID to inspect")
):
    """Show detailed information about a plan."""
    plan_data = state.get_plan(plan_id)
    if not plan_data:
        ui.print_error(f"Plan {plan_id} not found")
        return
    
    ui.display_divider(f"Plan Details: {plan_id}")
    ui.print_info(f"Status: {plan_data['status']}")
    ui.print_info(f"Prompt: {plan_data['prompt']}")
    
    if plan_data['generated_plan']:
        plan = plan_data['generated_plan']
        ui.print_info(f"\nThought: {plan.get('thought', 'N/A')}")
        ui.display_plan(plan_id, plan)
    
    # Show history
    ui.print_info("\n--- Execution History ---")
    history = state.get_history(plan_id)
    for i, entry in enumerate(history[-10:], 1):  # Last 10 entries
        content = entry['content']
        if len(content) > 100:
            content = content[:100] + "..."
        ui.print_info(f"{i}. [{entry['role']}] {content}")

@app.command()
def clean():
    """Clean up old plans (keep last 10)."""
    all_plans = state.list_plans(limit=1000)
    if len(all_plans) > 10:
        ui.print_warning(f"Found {len(all_plans)} plans. Keeping only the 10 most recent.")
        # Note: Would implement deletion logic here
        ui.print_info("Cleanup not yet implemented")
    else:
        ui.print_info(f"Only {len(all_plans)} plans - no cleanup needed")

@app.callback()
def main(ctx: typer.Context):
    """Autonomous Coding Agent - CLI-first system for task automation."""
    if ctx.invoked_subcommand is None:
        ui.display_divider("OMEGA Agent System")
        ui.print_info("Use 'agent --help' to see available commands")
        ui.print_info("\nQuick start:")
        ui.print_info("  agent plan 'Create a Flask app with /health endpoint'")
        ui.print_info("  agent list  # Show plans")
        ui.print_info("  agent build <plan_id>  # Execute a plan")

if __name__ == "__main__":
    app()
