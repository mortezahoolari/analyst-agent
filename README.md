# Cellbyte Agentic Data Analyst

An AI-powered data analyst that answers natural language questions about tabular CSV data.

## Quick Start

### Option 1: Virtual Environment (Recommended)

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key
copy .env.example .env
# Edit .env and set OPEN_AI_API_KEY

# 4. Run
python main.py data/
```

### Option 2: Docker

```bash
# Set your API key
export OPEN_AI_API_KEY=your-key-here  # Linux/Mac
# $env:OPEN_AI_API_KEY="your-key-here"  # Windows PowerShell

# Run interactive
docker-compose run --rm analyst
```

---

## How I Approached the Problem

### 1. Understanding the Core Challenge

The task asks for an "agentic data analyst" - not just a chatbot, but an agent that can:
- Understand data structure automatically
- Generate and execute code to answer questions
- Show its reasoning transparently
- Handle follow-up questions with context

### 2. Key Design Decision: Custom Orchestrator vs Framework

I chose to build a **lightweight custom orchestrator** instead of using heavy frameworks (LangChain, Microsoft Agent Framework).

**Why?**
- The task evaluates *my* design thinking, not framework configuration skills
- Full control over the agent loop = easier to debug and explain
- No hidden "magic" - every step is visible to the user
- Simpler codebase, easier to maintain

### 3. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLI Interface (cli.py)                     │
│              Rich terminal UI with step transparency            │
├─────────────────────────────────────────────────────────────────┤
│                    Orchestrator (orchestrator.py)               │
│         Custom agent loop using OpenAI function calling         │
├──────────┬──────────┬──────────┬──────────────────────────────┤
│ analyze  │  chart   │  export  │  report (PDF/DOCX)           │
│ (pandas) │  (plt)   │ (CSV/XL) │  (reportlab/docx)            │
├──────────┴──────────┴──────────┴──────────────────────────────┤
│              Code Executor (executor.py)                        │
│          Sandboxed execution with output capture                │
├─────────────────────────────────────────────────────────────────┤
│              Data Loader (data_loader.py)                       │
│          CSV loading + automatic schema extraction              │
└─────────────────────────────────────────────────────────────────┘
```

### 4. The Agent Loop (orchestrator.py)

```python
while not done:
    # 1. Send query + context to LLM
    response = openai.chat.completions.create(
        messages=messages,
        tools=TOOLS,      # analyze, chart, export, report
        tool_choice="auto"
    )

    # 2. If LLM wants to use a tool, execute it
    if response.tool_calls:
        result = execute_tool(tool_call)
        messages.append(result)  # Feed back to LLM
    else:
        # 3. LLM gave final answer
        return response
```

This simple loop handles complex multi-step analyses because the LLM can call tools multiple times, building on previous results.

### 5. Transparency by Design

Every step is captured and displayed:
- **Tool call**: What tool was chosen, why (explanation), code generated
- **Result**: Output, errors, generated files
- **Final answer**: Summary with insights

This builds user trust and makes debugging easy.

---

## Features

| Feature | Status | Notes |
|---------|--------|-------|
| Natural language → pandas analysis | ✅ | Generates and executes Python code |
| Schema auto-detection | ✅ | Extracts column types, samples, unique counts |
| Multi-dataset joins | ✅ | Identifies common columns automatically |
| Chart generation | ✅ | matplotlib, saves to PNG |
| CSV/Excel export | ✅ | openpyxl for Excel |
| PDF/DOCX reports | ✅ | reportlab, python-docx |
| Conversation history | ✅ | Last 10 exchanges by default |
| Transparent steps | ✅ | Shows code, explanations, results |
| Error recovery | ✅ | Retries on execution errors |

---

## Example Queries (All Tested)

```
✓ "What are the average yearly therapy costs in Non-small cell lung cancer?"
✓ "Which active substances were also part of the appropriate comparative therapies?"
✓ "Show me the range of yearly therapy costs by additional benefit rating."
✓ "Give me a distribution of additional benefit ratings as a pie chart."
✓ "Are there any products that received a higher benefit rating in a reassessment?"
```

---

## Project Structure

```
cellbyte-task/
├── src/
│   ├── config.py           # Configuration (env vars)
│   ├── data_loader.py      # CSV loading + schema extraction
│   ├── executor.py         # Sandboxed Python execution
│   ├── tools.py            # LLM tool definitions
│   ├── orchestrator.py     # Custom agent loop (core)
│   ├── report_generator.py # PDF/DOCX generation
│   └── cli.py              # Terminal interface
├── data/                   # CSV files
├── output/                 # Generated files (charts, reports)
├── main.py                 # Entry point
├── test_queries.py         # Test all 5 example queries
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Trade-offs & Limitations

### What I Prioritized
1. **Working end-to-end flow** over feature completeness
2. **Code clarity** over optimization
3. **Transparency** over speed

### Current Limitations
- **Sandboxing**: Uses `exec()` with namespace isolation, not subprocess. Sufficient for demo but not production-secure.
- **No streaming**: Waits for full response before displaying
- **Single-threaded**: Sequential tool execution

### What I'd Add Next (Given More Time)
1. **Subprocess sandboxing**: Run code in isolated subprocess with timeouts
2. **Streaming responses**: Show results as they compute
3. **Result caching**: Avoid re-computing expensive analyses
4. **Better error messages**: More helpful suggestions when code fails
5. **Unit tests**: pytest suite for each component

---

## Security Considerations

- API key loaded from environment (not hardcoded)
- Code execution isolated in namespace (no file system access by default)
- Output directory is fixed (can't write arbitrary paths)
- No network access from generated code

For production, I'd add:
- Subprocess isolation with resource limits
- Input validation on tool parameters
- Rate limiting on API calls

---

## Running Tests

```bash
# Run all 5 example queries
python test_queries.py

# Interactive mode
python main.py data/
```

---

## Dependencies

Core:
- `openai>=1.30.0` - LLM API
- `pandas>=2.0.0` - Data analysis
- `matplotlib>=3.7.0` - Charts

Export:
- `openpyxl>=3.1.0` - Excel
- `reportlab>=4.0.0` - PDF
- `python-docx>=1.0.0` - Word

UI:
- `rich>=13.0.0` - Terminal formatting
