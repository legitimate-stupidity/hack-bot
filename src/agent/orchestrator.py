"""
Core orchestrator - manages the plan -> execute -> verify loop.
"""
import asyncio
from enum import Enum, auto
from state import state, PlanStatus
from agents import PlannerAgent, EditorAgent, VerifierAgent
from context import build_context, get_recent_context
import ui

class AgentState(Enum):
    """Agent execution states."""
    EXECUTING = auto()
    SELF_CORRECTING = auto()
    TASK_COMPLETE = auto()
    TASK_FAILED = auto()

class Orchestrator:
    """Manages the overall execution flow."""
    
    def __init__(self, max_corrections: int = 3):
        self.planner = PlannerAgent()
        self.editor = EditorAgent()
        self.verifier = VerifierAgent()
        self.max_corrections = max_corrections

    async def plan(self, prompt: str):
        """Generate a plan for the user's request."""
        ui.display_divider("PLANNING PHASE")
        ui.print_info("Analyzing task and generating plan...")
        
        # Build context for planning
        context = build_context("")
        
        # Generate plan
        plan = await self.planner.generate_plan(prompt, context)
        
        if plan and "steps" in plan and len(plan["steps"]) > 0:
            plan_id = state.create_plan(prompt, plan)
            ui.display_plan(plan_id, plan)
            ui.print_success(f"Plan created: {plan_id}")
            print(f"\nRun: python -m agent.cli build {plan_id}")
        else:
            ui.print_error("Failed to generate a valid plan")

    async def build(self, plan_id: str):
        """Execute a plan."""
        # Validate plan exists
        plan_data = state.get_plan(plan_id)
        if not plan_data:
            ui.print_error(f"Plan {plan_id} not found")
            return

        if plan_data['status'] == PlanStatus.COMPLETED:
            ui.print_info("Plan already completed")
            return

        if plan_data['status'] == PlanStatus.FAILED:
            ui.print_warning("Plan previously failed")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return

        ui.display_divider(f"EXECUTION PHASE: {plan_id}")
        ui.print_info("Starting execution...")
        state.update_plan_status(plan_id, PlanStatus.IN_PROGRESS)
        
        # Run execution loop
        await self._execution_loop(plan_id)

    async def _execution_loop(self, plan_id: str):
        """Main ReAct-style execution loop."""
        current_state = AgentState.EXECUTING
        attempts = 0

        while attempts <= self.max_corrections:
            # Load current plan (may change during correction)
            plan_data = state.get_plan(plan_id)
            if not plan_data:
                ui.print_error("Plan lost during execution")
                state.update_plan_status(plan_id, PlanStatus.FAILED)
                return

            steps = plan_data['generated_plan'].get('steps', [])
            if not steps:
                ui.print_error("No steps in plan")
                state.update_plan_status(plan_id, PlanStatus.FAILED)
                return

            success = True
            failed_step = None

            # Execute each step
            for i, step in enumerate(steps):
                ui.print_info(f"Step {i+1}/{len(steps)}: {step.get('tool', 'unknown')}")
                
                # Act: Execute the tool
                result = await self.editor.execute_step(step)
                
                # Observe: Display result
                state.add_history(
                    plan_id,
                    "system",
                    f"Step {i+1} ({step.get('tool')}): {'Success' if result.success else 'Failed'}"
                )
                
                # Brief output display
                if result.success:
                    ui.print_success(f"Step {i+1} completed")
                    if result.stdout and len(result.stdout) < 100:
                        ui.print_info(f"Output: {result.stdout}")
                else:
                    ui.print_error(f"Step {i+1} failed")
                    ui.display_tool_result(step.get('tool', 'unknown'), result)

                # Check if this step was critical
                needs_fix, error = self.verifier.should_fix(result, step)
                if needs_fix:
                    success = False
                    failed_step = (i, step, result, error)
                    break

            # Process result
            if success:
                # All steps completed successfully
                current_state = AgentState.TASK_COMPLETE
                break
            elif current_state == AgentState.EXECUTING:
                # Step failed, attempt correction
                current_state = AgentState.SELF_CORRECTING
                attempts += 1

                if attempts > self.max_corrections:
                    current_state = AgentState.TASK_FAILED
                    break

                ui.display_divider(f"SELF-CORRECTION (Attempt {attempts})")
                ui.print_warning(f"Step {failed_step[0]+1} failed. Generating fix...")

                # Build context for correction
                context = get_recent_context(plan_id)
                error_msg = failed_step[3]
                state.add_history(plan_id, "system", f"Error: {error_msg}")

                # Generate corrective plan
                correction_prompt = (
                    f"Step {failed_step[0]+1} failed with error:\n{error_msg}\n\n"
                    f"Generate a new plan to fix this issue and complete the task."
                )

                new_plan = await self.planner.generate_plan(correction_prompt, context)

                if new_plan and "steps" in new_plan:
                    ui.display_plan(f"{plan_id}_fix_{attempts}", new_plan)
                    state.update_plan_data(plan_id, new_plan)
                    state.update_plan_status(plan_id, PlanStatus.IN_PROGRESS)
                    # Loop continues with new plan
                else:
                    ui.print_error("Failed to generate correction plan")
                    current_state = AgentState.TASK_FAILED
                    break

        # Finalize
        ui.display_divider("EXECUTION COMPLETE")
        if current_state == AgentState.TASK_COMPLETE:
            state.update_plan_status(plan_id, PlanStatus.COMPLETED)
            ui.print_success("Task completed successfully!")
        else:
            state.update_plan_status(plan_id, PlanStatus.FAILED)
            ui.print_error(f"Task failed after {attempts} correction attempts")

    async def resume(self, plan_id: str):
        """Resume a paused plan."""
        await self.build(plan_id)

    async def feedback(self, plan_id: str, message: str):
        """Handle user feedback (future feature)."""
        ui.print_warning("User feedback feature coming soon")
        state.add_history(plan_id, "user_feedback", message)

# Global orchestrator instance
orchestrator = Orchestrator()
