# Hack-Bot: Autonomous Coding Agent + Security Framework

A Python 3.11+ system combining an autonomous coding agent with a comprehensive security/hacking framework (Project OMEGA).

## Overview

This project has two major components:

### 1. **Autonomous Coding Agent** (`src/agent/`)
A CLI-first, self-correcting autonomous agent that can plan and execute coding tasks. Built with:
- **Typer**: CLI interface
- **Rich**: Beautiful console output  
- **SQLite**: State persistence for long-running tasks
- **Asyncio**: Non-blocking execution
- **LLM Integration**: ReAct-style reasoning loop

### 2. **Project OMEGA** (`src/omega/`)
A comprehensive security framework covering 35+ offensive security domains (extracted from `.build` file)

## Quick Start

### Installation

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Using the Agent

```bash
# Generate a plan (no execution)
python -m agent.cli plan "Create a Flask app with /health endpoint"

# List all plans
python -m agent.cli list

# Execute a plan
python -m agent.cli build plan_abc12345

# View plan details
python -m agent.cli info plan_abc12345

# Resume a paused plan
python -m agent.cli resume plan_abc12345
```

## Architecture

### Agent Flow (Plan → Build → Verify → Self-Correct)

```
User Prompt
    ↓
[PLAN] PlannerAgent generates structured steps
    ↓
[BUILD] EditorAgent executes each step via tools
    ↓
[VERIFY] VerifierAgent checks for success/failure
    ↓
[SELF-CORRECT] If failed, generate new plan and retry
    ↓
Task Complete or Failed
```

### State Management

- **Database**: SQLite (persistent across sessions)
- **Tables**: 
  - `plans`: Task definitions and status
  - `task_history`: Execution history and logs

### Available Tools

Tools agents can use to interact with the system:

- `run_shell`: Execute shell commands
- `write_file`: Create/modify files
- `read_file`: Read file contents
- `list_files`: List directory contents
- `mkdir`: Create directories
- `remove_file`: Delete files

### Context Management

The agent maintains context by:
1. Storing recent execution history
2. Including current filesystem state
3. Summarizing long histories to fit LLM context windows
4. Using vector embeddings for relevant file retrieval (future)

## Project Structure

```
hack-bot/
├── src/
│   ├── agent/           # Autonomous coding agent
│   │   ├── cli.py       # CLI entry point
│   │   ├── orchestrator.py  # Main execution loop
│   │   ├── agents.py    # Agent definitions
│   │   ├── tools.py     # Tool definitions
│   │   ├── llm.py       # LLM interface
│   │   ├── state.py     # State management
│   │   ├── context.py   # Context building
│   │   └── ui.py        # User interface
│   └── omega/           # Security framework (modularized)
├── tests/               # Test suite
├── README.md
├── requirements.txt
└── agent_flow.db        # SQLite state (auto-created)
```

## Examples

### Example 1: Create a Flask API

```bash
python -m agent.cli plan "Create a Flask app with a GET /status endpoint that returns JSON"
python -m agent.cli list
python -m agent.cli build plan_xyz789
```

The agent will:
1. Install dependencies
2. Create `app.py` with Flask server
3. Create `test_status.py` with tests
4. Run tests and verify

### Example 2: Handle Failures Automatically

If a step fails (e.g., import error), the agent will:
1. Detect the error
2. Analyze the failure
3. Generate a corrective plan
4. Execute the fix
5. Re-verify

### Example 3: Continue After Interruption

```bash
# Start a plan
python -m agent.cli build plan_abc123
# (Ctrl+C to interrupt)

# Later, resume it
python -m agent.cli resume plan_abc123
```

The agent loads the plan state and continues from where it left off.

## Configuration

### LLM Provider

The system includes a simulated LLM (`src/agent/llm.py`). To use a real LLM:

1. Modify `llm.py` to call Gemini/GPT API
2. Set up authentication (API keys)
3. Update prompts as needed

### Database Location

Change `DB_PATH` in `src/agent/state.py` to customize database location.

### Concurrency & Timeouts

- Max correction attempts: 3 (configurable in `orchestrator.py`)
- Shell command timeout: 30 seconds (in `tools.py`)
- LLM call timeout: adjustable per request

## Advanced Usage

### Viewing Execution History

```bash
python -m agent.cli info plan_abc123  # Shows all steps and output
```

### Manual Feedback (Future Feature)

```bash
python -m agent.cli feedback plan_abc123 "The test failed because..."
```

### Monitoring Long Tasks

Plans are persisted, so you can:
1. Start a complex task
2. Interrupt if needed
3. Check status later with `list` or `info`
4. Resume and let it continue

## Technical Details

### ReAct Loop Implementation

The orchestrator implements a reasoning + acting loop:

1. **Reason**: LLM generates next action(s) based on context
2. **Act**: Execute action(s) via tools
3. **Observe**: Capture results in database
4. **Reflect**: Determine success/failure
5. **Correct**: If failed, loop back to Reason with error context

### Error Handling

- Tool failures trigger self-correction
- Network timeouts are retried
- Invalid JSON responses are handled gracefully
- Partial failures in multi-step tasks trigger selective re-execution

### Performance Optimizations

- Async tool execution
- Database indices on frequently queried columns
- History summarization for long tasks
- Lazy-loading of file contents

## Testing

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/agent --cov-report=html
```

## Limitations & Future Work

### Current Limitations
- LLM provider is simulated (stub implementation)
- No vector database for code retrieval
- Limited to local filesystem operations
- Single-threaded execution

### Planned Enhancements
- [ ] Real LLM integration (Gemini, GPT-4)
- [ ] Vector database for semantic file search
- [ ] Multi-agent collaboration
- [ ] Advanced code analysis (AST, type checking)
- [ ] IDE integration
- [ ] Distributed execution
- [ ] Web dashboard

## Project OMEGA (Security Framework)

The `.build` file contains extensive offensive security implementations:

- **Network Exploitation**: DNS cache snooping, ARP spoofing, SYN floods
- **ICS/SCADA**: Modbus protocol, S7 PLC exploitation
- **Evasion**: Anti-analysis checks, shellcode injection, VM detection
- **Cloud**: AWS IAM enumeration, S3 bucket analysis
- **Cryptography**: RSA attacks, zero-knowledge proofs
- **Data Exfiltration**: Steganography, ICMP tunneling
- **Wireless**: 802.11 deauth, BLE enumeration, RF capture
- **Persistence**: Registry modification, cron jobs
- **OSINT**: Image metadata, dark web routing, breach monitoring
- **Kernel Exploitation**: Windows/Linux kernel structure analysis

## Security & Ethical Use

This framework is provided for **authorized security testing, educational purposes, and authorized penetration testing only**.

Unauthorized access to computer systems is illegal. Ensure you have proper authorization before using any security tools.

## Contributing

Contributions welcome! Please:
1. Follow PEP 8 style
2. Add tests for new features
3. Update documentation
4. Submit a pull request

## License

MIT License - See LICENSE file

## Contact & Support

For issues, feature requests, or questions:
- Open a GitHub issue
- Check existing documentation
- Review the architecture overview