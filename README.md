# Agentic Data Analyst

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
export OPEN_AI_API_KEY=your-key-here      # Linux/Mac
$env:OPEN_AI_API_KEY="your-key-here"      # Windows PowerShell

# Run interactive
docker-compose run --rm analyst
```

---

## Using Your Own Data

The system is **data-agnostic** - it works with any CSV files:

```bash
# Option 1: Replace files in data/ folder
cp your_data.csv data/
python main.py data/

# Option 2: Specify custom path
python main.py /path/to/your/csvs/

# Option 3: Docker (put CSVs in data/ folder)
docker-compose run --rm analyst
```

The agent automatically:
- Detects column names, types, and sample values
- Identifies common columns for joins across multiple CSVs
- Generates appropriate pandas code based on actual schema

No configuration needed - just drop your CSVs and start asking questions.

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
│          Namespace-isolated execution with output capture       │
├─────────────────────────────────────────────────────────────────┤
│              Data Loader (data_loader.py)                       │
│          CSV loading + automatic schema extraction              │
└─────────────────────────────────────────────────────────────────┘
```

### 4. The Agent Loop (orchestrator.py)

```python
max_iterations = 10  # Safety limit to prevent infinite loops

while iteration < max_iterations:
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

This loop handles complex multi-step analyses (LLM can call tools multiple times). The `max_iterations=10` prevents infinite loops if the LLM keeps requesting tools without concluding.

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
| Conversation history | ✅ | Last 50 message pairs in context |
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
analyst-agent/
├── src/
│   ├── config.py           # Configuration (env vars)
│   ├── data_loader.py      # CSV loading + schema extraction
│   ├── executor.py         # Code execution with namespace isolation
│   ├── tools.py            # LLM tool definitions
│   ├── orchestrator.py     # Custom agent loop (core)
│   ├── report_generator.py # PDF/DOCX generation
│   └── cli.py              # Terminal interface
├── data/                   # CSV files
├── output/                 # Generated files (charts, reports)
├── main.py                 # Entry point
├── test_queries.py         # E2E tests for 5 example queries
├── test_all.py             # Integration tests (components + API)
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
- **Code execution**: Uses `exec()` with namespace isolation only. NOT truly sandboxed - generated code can still import modules and access system resources. Sufficient for demo with trusted LLM output, but NOT production-secure.
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
- Code execution uses namespace isolation (see Limitations section for caveats)
- Output directory is fixed for generated files
- LLM-generated code is relatively trusted (not arbitrary user input)

For production, I'd add:
- Subprocess isolation with resource limits
- Input validation on tool parameters
- Rate limiting on API calls

---

## Running Tests

```bash
# Run integration tests (components + LLM queries)
python test_all.py

# Run E2E tests for the 5 example queries
python test_queries.py

# Interactive mode
python main.py data/
```

---

## Dependencies

Core:
- `openai>=2.8.0` - LLM API (Chat Completions with function calling)
- `pandas>=2.3.0` - Data analysis
- `matplotlib>=3.10.0` - Charts

Export:
- `openpyxl>=3.1.5` - Excel
- `reportlab>=4.4.0` - PDF
- `python-docx>=1.2.0` - Word

UI:
- `rich>=14.0.0` - Terminal formatting
