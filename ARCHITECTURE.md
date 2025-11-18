# Architecture & Design Documentation

## System Overview

Hack-Bot is a two-part system:

1. **Autonomous Agent**: Self-correcting coding task executor
2. **Security Framework** (Project OMEGA): 35+ offensive security modules

## Agent Architecture

### Core Concepts

The agent implements a **Plan → Execute → Verify → Self-Correct** loop:

```python
while not completed:
    # PLAN: Generate structured steps
    plan = planner.generate_plan(user_prompt, context)
    
    # BUILD: Execute each step
    for step in plan.steps:
        result = executor.execute(step)
        
        # VERIFY: Check for success
        if not result.success:
            # SELF-CORRECT: Generate fix plan
            plan = planner.generate_plan(error_analysis, context)
            break
        
    # Check overall completion
    if all_successful:
        mark_completed()
```

### Module Responsibilities

#### 1. **cli.py** - Command-Line Interface
- Entry point using Typer
- Handles user commands: `plan`, `build`, `list`, `resume`, `info`
- Dispatches to orchestrator
- Formatted output via Rich

#### 2. **orchestrator.py** - Main Execution Loop
- Implements ReAct pattern
- State machine (`AgentState`)
- Coordinates planner, executor, verifier
- Self-correction logic
- Database state updates

#### 3. **agents.py** - Specialized Agents
- **PlannerAgent**: Generates structured plans via LLM
- **EditorAgent**: Executes individual tool calls
- **VerifierAgent**: Analyzes failures and triggers corrections

#### 4. **tools.py** - System Capabilities
- `run_shell`: Execute OS commands
- `write_file`: Create/modify files
- `read_file`: Read file contents
- `list_files`: Directory listing
- `mkdir`, `remove_file`: File operations

#### 5. **llm.py** - Language Model Interface
- Abstraction for LLM calls
- Structured JSON output
- Simulated provider (extendable)
- Can be swapped with real API (Gemini, GPT, etc.)

#### 6. **state.py** - Persistent Storage
- SQLite database
- `plans` table: Task definitions
- `task_history` table: Execution logs
- Enables resumption after interruption

#### 7. **context.py** - Context Management
- Builds LLM prompts
- Includes recent history
- Filesystem state
- History summarization for long tasks

#### 8. **ui.py** - User Interface
- Rich console formatting
- Tables, panels, colors
- Status displays
- Plan visualization

### Data Flow

```
User Input (CLI)
    ↓
cli.py parses arguments
    ↓
orchestrator.plan() or orchestrator.build()
    ↓
PlannerAgent.generate_plan()
    ↓
llm.generate_json() → Structured plan
    ↓
state.create_plan() → Database
    ↓
EditorAgent.execute_step() for each step
    ↓
tools.* (actual system calls)
    ↓
VerifierAgent checks result
    ↓
If failure: loop back to PlannerAgent with error context
If success: state.update_plan_status() → COMPLETED
```

### State Machine Diagram

```
[PENDING] (new plan)
    ↓
[IN_PROGRESS] (build started)
    ↓
   ├─ [NEEDS_FIX] (verification failed)
   │   ↓
   │ (corrective planning)
   │   ↓
   │ [IN_PROGRESS] (retry)
   │   ↓
   └─ (back to verification)
    ↓
[COMPLETED] (all steps successful)

Or:
[FAILED] (max corrections exceeded)
```

## Project OMEGA Security Framework

Extracted from `.build` file. 35+ sections covering:

### Categories

1. **Network Attacks** (Sections 9, 39)
   - DNS manipulation, cache snooping
   - ARP spoofing
   - TCP SYN floods
   - Raw socket operations

2. **Evasion** (Section 20)
   - Anti-analysis checks
   - VM detection
   - Debugger detection
   - Sleep acceleration detection
   - Shellcode injection (Windows)

3. **ICS/SCADA** (Section 21)
   - Modbus protocol utilities
   - S7 PLC exploitation
   - Industrial device targeting

4. **Persistence** (Section 22)
   - Windows Registry modification
   - Linux cron jobs
   - Startup/run key abuse

5. **Cloud Exploitation** (Section 24)
   - AWS IAM enumeration
   - S3 bucket analysis
   - Unauthenticated access testing

6. **Data Exfiltration** (Section 26)
   - LSB steganography
   - ICMP tunneling
   - Protocol tunneling

7. **Cryptographic Attacks** (Section 27)
   - RSA factorization (Fermat's method)
   - Common modulus attacks
   - Key recovery

8. **Advanced Concepts** (Sections 28-35)
   - Autonomous exploit generation
   - Machine learning for evasion
   - Zero-knowledge proofs
   - Advanced C2 protocols
   - Wireless exploitation
   - Supply chain attacks
   - OSINT/dark web operations
   - Kernel exploitation

## Database Schema

### plans table
```sql
CREATE TABLE plans (
    plan_id TEXT PRIMARY KEY,
    prompt TEXT NOT NULL,
    generated_plan TEXT (JSON),
    status TEXT NOT NULL,
    created_at DATETIME,
    updated_at DATETIME
);
```

### task_history table
```sql
CREATE TABLE task_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id TEXT,
    timestamp DATETIME,
    role TEXT NOT NULL (user|agent|system),
    content TEXT NOT NULL,
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id)
);
```

## Extension Points

### Adding New Tools

1. Create async function in `tools.py`
2. Add to `TOOLBOX` dictionary
3. Update `get_tool_help()` in tools.py
4. LLM will automatically use it

Example:
```python
async def deploy_docker(image: str, port: int) -> ToolResult:
    command = f"docker run -d -p {port}:8080 {image}"
    return await run_shell(command)

TOOLBOX["deploy_docker"] = deploy_docker
```

### Replacing the LLM

1. Modify `llm.py` 
2. Implement real API call in `generate_json()`
3. Handle response parsing
4. Map to structured JSON format

Example:
```python
import google.generativeai as genai

async def generate_json(self, prompt: str) -> Dict[str, Any]:
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return json.loads(response.text)
```

### Adding New Agents

Create subclass of base agent pattern:
```python
class CustomAgent:
    async def execute(self, task: str, context: str) -> Result:
        # Custom logic
        pass
```

Add to orchestrator and wire into execution loop.

## Error Handling Strategy

### Tool Failures
- Captured in `ToolResult`
- Analyzed by `VerifierAgent`
- Context added to history
- New plan generated for fix

### LLM Failures
- Gracefully degrade to default behavior
- Log to history
- Trigger manual feedback mode (future)

### State Corruption
- Database transactions ensure consistency
- Indices prevent slow queries
- Backups recommended for production

## Performance Considerations

- **Async execution**: Non-blocking tool calls
- **Database indices**: On `status`, `plan_id`
- **Context windows**: Summarization for long tasks
- **Timeout handling**: 30s per shell command
- **Cleanup**: Archiving old plans (future)

## Security Considerations

- No sensitive data in logs (sanitization needed)
- Shell commands run with user privileges
- File operations limited to working directory (configurable)
- No automatic network access
- OMEGA framework requires explicit authorization

## Future Enhancements

1. **Vector Database**: Semantic code search
2. **Multi-Agent**: Parallel execution with coordination
3. **Web Dashboard**: Real-time monitoring
4. **IDE Integration**: VSCode, PyCharm plugins
5. **Advanced Analysis**: AST parsing, type checking
6. **Distributed**: Kubernetes support
7. **Observability**: Tracing, metrics, dashboards
8. **Security Hardening**: Sandboxing, privilege separation

## Testing Strategy

- Unit tests: Individual components
- Integration tests: Agent flow with simulated tools
- End-to-end: Full planning → execution → verification
- Property testing: Generator-based fuzzing
- Performance: Benchmark tool execution

See `tests/test_agent.py` for examples.
