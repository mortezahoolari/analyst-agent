# Cellbyte Agentic Data Analyst

An AI-powered data analyst that answers natural language questions about tabular CSV data.

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key
copy .env.example .env
# Edit .env and add your OPEN_AI_API_KEY

# 4. Run
python main.py data/
```

## What I Built

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLI Interface (cli.py)                     │
│              Rich terminal UI with step transparency            │
├─────────────────────────────────────────────────────────────────┤
│                    Orchestrator (orchestrator.py)               │
│         Custom agent loop using OpenAI Chat Completions         │
│                     with function calling                       │
├──────────────────┬──────────────────┬───────────────────────────┤
│  analyze_data    │  create_chart    │  export_data              │
│  (pandas code)   │  (matplotlib)    │  (CSV/Excel)              │
├──────────────────┴──────────────────┴───────────────────────────┤
│                   Code Executor (executor.py)                   │
│         Sandboxed Python execution with output capture          │
├─────────────────────────────────────────────────────────────────┤
│                   Data Loader (data_loader.py)                  │
│           CSV loading + automatic schema extraction             │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **Custom Orchestrator vs Framework**: I chose to build a lightweight custom orchestrator instead of using a heavy framework (LangChain, Microsoft Agent Framework) because:
   - Full control over the agent loop
   - Easier to debug and explain
   - No hidden "magic" - every step is visible
   - The task evaluates my design skills, not framework configuration

2. **OpenAI Function Calling**: Used the Chat Completions API with function calling (tool use) rather than the deprecated Assistants API. This gives:
   - Direct control over tool execution
   - Transparent step-by-step reasoning
   - No vendor lock-in to specific features

3. **Code Generation over Fixed Queries**: The agent generates and executes Python code rather than using predefined query templates. This allows:
   - Flexibility to handle any question
   - Complex multi-step analyses
   - User can see exactly what code ran

4. **Transparency First**: Every step is shown to the user:
   - What the agent decided to do (thinking)
   - What code it generated
   - The actual execution results
   - Clear error messages if something fails

### Features Implemented

- [x] Natural language questions → pandas analysis
- [x] Automatic schema understanding from CSV files
- [x] Chart generation (matplotlib)
- [x] Export to CSV/Excel
- [x] Conversation history (follows up on previous context)
- [x] Transparent step display
- [x] Error handling with retry

### Limitations & Future Work

**Current Limitations:**
- Code execution uses `exec()` - basic sandboxing only (no subprocess isolation)
- PDF/DOCX export not implemented (noted as "nice-to-have" in requirements)
- No streaming responses
- Single-threaded execution

**What I'd Add Next:**
1. **Subprocess sandboxing**: Run code in isolated subprocess with resource limits
2. **Result caching**: Cache expensive computations
3. **PDF/DOCX export**: Using reportlab and python-docx
4. **Streaming**: Show results as they compute
5. **Better error recovery**: Auto-fix common code errors

## Example Queries

The agent handles all example queries from the assignment:

```
# Average yearly therapy costs
"What are the average yearly therapy costs in Non-small cell lung cancer?"

# Cross-reference analysis
"Which active substances were also part of the appropriate comparative therapies?"

# Multi-dataset analysis
"Show me the range of yearly therapy costs by additional benefit rating."

# Visualization
"Give me a distribution of additional benefit ratings as a pie chart."

# Complex analysis
"Are there any products that received a higher benefit rating in a reassessment?"
```

## Project Structure

```
cellbyte-task/
├── src/
│   ├── __init__.py
│   ├── config.py        # Configuration management
│   ├── data_loader.py   # CSV loading + schema extraction
│   ├── executor.py      # Sandboxed code execution
│   ├── tools.py         # LLM tool definitions
│   ├── orchestrator.py  # Custom agent loop
│   └── cli.py           # Terminal interface
├── data/                # CSV files
├── output/              # Generated charts/exports
├── main.py              # Entry point
├── requirements.txt
├── .env.example
└── README.md
```

## How It Works

1. **Load Data**: CSV files are loaded and their schemas (column names, types, sample values) are extracted
2. **Build Context**: Schema information is injected into the system prompt
3. **Agent Loop**:
   - User asks a question
   - LLM decides which tool to use (or answer directly)
   - Tool generates Python code with explanation
   - Code executes in sandboxed environment
   - Results sent back to LLM for interpretation
   - Final answer presented with full transparency
4. **History**: Previous Q&A pairs are included for follow-up questions

## My Approach

I approached this as a product problem, not just a technical one:

1. **Understand the user**: An analyst wants to quickly get insights without writing code
2. **Transparency is key**: Users need to trust the results - showing the code builds trust
3. **Keep it simple**: A working MVP beats an over-engineered system
4. **Pragmatic choices**: Used OpenAI function calling (stable, well-documented) over newer but less proven APIs

Time was limited, so I focused on:
- Core functionality that works end-to-end
- Clean, readable code structure
- Clear documentation

## Running Tests

```bash
# Interactive mode
python main.py data/

# Specific files
python main.py path/to/file1.csv path/to/file2.csv
```

## Dependencies

- `openai>=1.30.0` - LLM API client
- `pandas>=2.0.0` - Data manipulation
- `matplotlib>=3.7.0` - Visualization
- `openpyxl>=3.1.0` - Excel export
- `rich>=13.0.0` - Terminal UI
- `python-dotenv>=1.0.0` - Environment config
