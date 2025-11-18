# Quick Start Guide

## Installation & Setup

### 1. Clone & Navigate
```bash
cd /workspaces/hack-bot
```

### 2. Create Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Using the Agent

### Example 1: Create a Flask Application

```bash
# Step 1: Generate a plan
python -m agent.cli plan "Create a Flask REST API with /health and /info endpoints"

# Step 2: View the plan
python -m agent.cli list
# Note the plan_id (e.g., plan_abc12345)

# Step 3: Execute the plan
python -m agent.cli build plan_abc12345

# Step 4: Check results
python -m agent.cli info plan_abc12345
```

**What the agent will do:**
1. Install Flask and pytest
2. Create `app.py` with the API endpoints
3. Create `test_app.py` with unit tests
4. Run the tests and verify they pass
5. Mark the plan as COMPLETED

### Example 2: Handle Failures Automatically

Try this task that will initially fail (intentional bug):
```bash
python -m agent.cli plan "Create a Python script that prints 'Hello World'"
```

The agent will:
1. Generate a plan
2. Execute the plan
3. If there's an error, automatically detect it
4. Generate a fix
5. Execute the fix
6. Verify success

### Example 3: List & Manage Plans

```bash
# Show all plans
python -m agent.cli list

# View details of a specific plan
python -m agent.cli info plan_abc12345

# Resume a previously started plan
python -m agent.cli resume plan_abc12345
```

## Command Reference

### `plan <PROMPT>`
**Generate a plan without executing it**
```bash
python -m agent.cli plan "Your task description here"
```

Examples:
- `python -m agent.cli plan "Build a Python web scraper"`
- `python -m agent.cli plan "Create a TODO list CLI app"`
- `python -m agent.cli plan "Set up a pytest test suite"`

### `build <PLAN_ID>`
**Execute a plan**
```bash
python -m agent.cli build plan_abc12345
```

### `list`
**Show all plans and their status**
```bash
python -m agent.cli list
```

### `info <PLAN_ID>`
**View detailed information about a plan**
```bash
python -m agent.cli info plan_abc12345
```

Shows:
- Plan status
- Original prompt
- Execution steps
- Recent history
- Any errors

### `resume <PLAN_ID>`
**Continue a paused or failed plan**
```bash
python -m agent.cli resume plan_abc12345
```

## Understanding Agent Output

### Status Colors
- 🟢 **Green**: Success, complete, or good status
- 🔵 **Blue**: Info messages
- 🟡 **Yellow**: Warnings or in-progress
- 🔴 **Red**: Errors or failures

### Plan Status
- **PENDING**: Plan created but not executed
- **IN_PROGRESS**: Currently executing
- **NEEDS_FIX**: Execution failed, attempting self-correction
- **COMPLETED**: Task finished successfully
- **FAILED**: Task failed after max correction attempts

### Example Output

```
[*] EXECUTION PHASE: plan_abc12345 [*]
[i] Starting execution...
[i] Step 1/4: run_shell
[✓] Step 1 completed

[i] Step 2/4: write_file
[✓] Step 2 completed

[i] Step 3/4: run_shell
[✗] Step 3 failed

--- SELF-CORRECTION (Attempt 1) ---
[!] Step 3 failed. Generating fix...
[i] New correction plan generated.

[i] Step 3/4 (re-attempt): run_shell
[✓] Step 3 completed

[i] Step 4/4: run_shell
[✓] Step 4 completed

[✓] Task completed successfully!
```

## Tips & Tricks

### 1. Be Specific With Prompts
❌ Bad: `"Make a Flask app"`
✅ Good: `"Create a Flask REST API with GET /users endpoint that returns a JSON list"`

### 2. Check Status Before Building
```bash
# Always list to see what you're building
python -m agent.cli list
python -m agent.cli info plan_xyz
# Then build if it looks right
python -m agent.cli build plan_xyz
```

### 3. Use `info` to Debug
If a plan failed:
```bash
python -m agent.cli info failed_plan_id
# See exactly what went wrong in the execution history
```

### 4. Resume Instead of Replan
Don't create new plans for the same task - use `resume` to continue from where it failed.

```bash
# Don't do this:
python -m agent.cli plan "Same task again"

# Do this instead:
python -m agent.cli resume plan_xyz
```

### 5. Short Iteration Cycles
Start with simpler tasks:
- `"Create a hello.py that prints Hello"`
- Then expand: `"Add command line arguments to hello.py"`
- Then iterate: `"Add a config file to hello.py"`

## Troubleshooting

### Issue: Plan generation seems slow
**Solution**: The simulated LLM adds 100ms latency. This is normal.

### Issue: Tool execution times out
**Solution**: The default timeout is 30 seconds. For long-running tasks, break them into smaller plans.

### Issue: Database locked error
**Solution**: Only one `build` command should run at a time. Either wait for the first to complete or use a different terminal.

### Issue: Changes aren't showing up
**Solution**: The agent stores everything in `agent_flow.db`. 
- To reset: Delete `agent_flow.db` and start fresh
- To inspect: Use any SQLite client: `sqlite3 agent_flow.db`

### Issue: Import errors in generated code
**Solution**: The agent will auto-correct these. Just let it run - it will detect the error and fix it automatically.

## Next Steps

Once you're comfortable:

1. **Customize tools** (`src/agent/tools.py`): Add domain-specific tools
2. **Replace LLM** (`src/agent/llm.py`): Connect to real Gemini/GPT API
3. **Add agents** (`src/agent/agents.py`): Create specialized agents
4. **Extend state** (`src/agent/state.py`): Add custom metadata
5. **Run tests**: `pytest tests/ -v`

## Project Structure Reference

```
hack-bot/
├── src/agent/              # Agent system (what you're using now)
│   ├── cli.py             # Command interface
│   ├── orchestrator.py    # Main execution loop
│   ├── agents.py          # PlannerAgent, EditorAgent, VerifierAgent
│   ├── tools.py           # Available operations
│   ├── llm.py             # Language model interface
│   ├── state.py           # Database management
│   ├── context.py         # Context building
│   └── ui.py              # Output formatting
├── src/omega/              # Security framework (future)
├── tests/                  # Test suite
├── README.md              # Full documentation
├── ARCHITECTURE.md        # Design & technical details
├── requirements.txt       # Dependencies
├── setup.py              # Python packaging
└── agent_flow.db         # Auto-created database
```

## Getting Help

- **How the agent works?** → See `ARCHITECTURE.md`
- **What commands are available?** → Run `python -m agent.cli --help`
- **Code examples?** → Check `src/agent/llm.py` for plan generation examples
- **Database questions?** → See `src/agent/state.py` docstrings
- **Want to add features?** → See `src/agent/tools.py` and `src/agent/agents.py`

---

**Happy automating!** 🚀
