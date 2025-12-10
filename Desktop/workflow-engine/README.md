# Workflow Engine - AI Engineering Internship Assignment

A lightweight, production-ready workflow engine supporting sequential execution, conditional branching, and loops. Built with FastAPI and async Python.

## 🚀 Features

### Core Engine
- ✅ **Node-based execution** - Define workflow steps as Python functions
- ✅ **Shared state management** - Type-safe state flow with Pydantic
- ✅ **Conditional routing** - Branch based on runtime state
- ✅ **Loop support** - Repeat steps until conditions are met
- ✅ **Async execution** - Support for both sync and async functions
- ✅ **Execution logging** - Track every step with timestamps

### Tool System
- ✅ **Simple registry** - Register functions as reusable tools
- ✅ **Decorator pattern** - Easy tool registration with `@tool`
- ✅ **Dynamic invocation** - Call tools by name at runtime

### REST API
- ✅ **Create workflows** - Define graphs via JSON
- ✅ **Execute workflows** - Run with custom initial state
- ✅ **Query status** - Get execution logs and final state
- ✅ **List resources** - View all graphs, runs, and tools

### Example: Code Review Agent
A complete workflow demonstrating all engine features:
1. **Extract functions** from Python code
2. **Check complexity** (lines, nesting depth)
3. **Detect issues** (missing docstrings, long lines, etc.)
4. **Suggest improvements**
5. **Calculate quality score**
6. **Loop** if score < threshold (max 3 iterations)

---

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- pip

### Setup

```bash
# Clone repository
git clone <your-repo-url>
cd workflow-engine

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🏃 Running the Server

```bash
# Start the FastAPI server
uvicorn app.main:app --reload

# Server starts at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

You should see:
```
✓ Workflow Engine started
✓ Pre-loaded workflow: code-review-default
✓ Available tools: 5
```

---

## 💻 Usage Examples

### 1. View API Documentation

Open browser: **http://localhost:8000/docs**

Interactive Swagger UI with all endpoints!

### 2. List Available Tools

```bash
curl http://localhost:8000/tools
```

Response:
```json
{
  "tools": {
    "extract_functions": "Extract function definitions from code",
    "check_complexity": "Check code complexity",
    "detect_issues": "Detect basic code issues",
    "suggest_improvements": "Generate improvement suggestions",
    "calculate_quality_score": "Calculate overall quality score"
  }
}
```

### 3. Run Pre-Built Code Review Workflow

```bash
curl -X POST http://localhost:8000/graph/run \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "code-review-default",
    "initial_state": {
      "code": "def bad_function():\n    print(\"test\")\n    for i in range(100):\n        print(i)",
      "quality_threshold": 70
    }
  }'
```

Response includes:
- `run_id` - Unique execution ID
- `final_state` - Quality score, issues, suggestions
- `logs` - Step-by-step execution trace
- `status` - "completed" or "failed"

### 4. Create Custom Workflow

```bash
curl -X POST http://localhost:8000/graph/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Simple Code Check",
    "nodes": [
      {"name": "extract", "tool": "extract_functions"},
      {"name": "analyze", "tool": "check_complexity"}
    ],
    "edges": [
      {"from_node": "extract", "to_node": "analyze"}
    ],
    "start_node": "extract",
    "end_nodes": ["analyze"]
  }'
```

Returns `graph_id` - use this to run the workflow!

### 5. Query Run Status

```bash
curl http://localhost:8000/graph/state/{run_id}
```

Get complete execution history for any run.

---

## 📁 Project Structure

```
workflow-engine/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app & endpoints
│   ├── models.py            # Pydantic request/response models
│   ├── engine/
│   │   ├── __init__.py
│   │   └── workflow.py      # Core workflow engine
│   ├── tools/
│   │   ├── __init__.py
│   │   └── registry.py      # Tool registry system
│   └── workflows/
│       ├── __init__.py
│       └── code_review.py   # Example code review workflow
├── venv/                    # Virtual environment
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── .gitignore             # Git ignore rules
```

---

## 🧪 Testing Examples

### Test 1: Good Quality Code

```python
code = '''
def calculate_sum(numbers):
    """Calculate sum of numbers."""
    return sum(numbers)
'''
```

**Expected Result:**
- Quality score: 90-100
- Few or no issues
- Minimal suggestions

### Test 2: Poor Quality Code

```python
code = '''
def bad_function():
    for i in range(100):
        if i > 0:
            for j in range(100):
                if j > 0:
                    print(i * j)
    return True
'''
```

**Expected Result:**
- Quality score: 30-50
- Issues: Missing docstrings, high nesting, print statements
- Suggestions: Refactor, add logging, break into smaller functions

### Test 3: Loop Behavior

Set `quality_threshold: 90` with poor code:
- First iteration: Low score
- Second iteration: Detects more issues
- Third iteration: Max reached, stops
- Final state shows all 3 iterations

---

## 🏗️ Architecture

### Workflow Engine Design

```
User Request
    ↓
FastAPI Endpoint
    ↓
Build WorkflowGraph
    ↓
Execute Nodes Sequentially
    ↓
    ├→ Simple Edge → Next Node
    ├→ Conditional Edge → Evaluate → Next Node
    └→ End Node → Return State
```

### State Flow

```python
Initial State → Node 1 → Modified State → Node 2 → ... → Final State
```

Each node:
1. Receives current state
2. Executes its function
3. Returns modified state
4. State flows to next node

### Key Components

| Component | Purpose |
|-----------|---------|
| `WorkflowGraph` | Manages nodes, edges, execution flow |
| `WorkflowState` | Type-safe state container |
| `Node` | Wraps functions for execution |
| `ConditionalEdge` | Enables dynamic routing |
| `ToolRegistry` | Central function registry |

---

## 🎯 What the Engine Supports

| Feature | Status | Description |
|---------|--------|-------------|
| Sequential execution | ✅ | Nodes run in order |
| Conditional branching | ✅ | Route based on state |
| Loops | ✅ | Repeat until condition |
| Max step limit | ✅ | Prevent infinite loops |
| Shared state | ✅ | Pydantic models |
| Async support | ✅ | Async and sync functions |
| Tool registry | ✅ | Reusable functions |
| Execution logs | ✅ | Step-by-step tracking |
| REST API | ✅ | Full CRUD operations |
| In-memory storage | ✅ | Fast development |

---

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/tools` | GET | List available tools |
| `/graph/create` | POST | Create new workflow |
| `/graph/run` | POST | Execute workflow |
| `/graph/state/{run_id}` | GET | Query run status |
| `/graph/list` | GET | List all graphs |
| `/runs/list` | GET | List all runs |
| `/health` | GET | Health check |

---

## 🚧 What I Would Improve With More Time

### 1. Persistence Layer
**Current:** In-memory storage (fast but temporary)  
**Improvement:** PostgreSQL/SQLite with SQLAlchemy
- Persistent storage across restarts
- Database migrations with Alembic
- Graph versioning and history
- Audit trails

### 2. Advanced Execution Features
- **Parallel execution** - Run independent nodes concurrently
- **Retry logic** - Exponential backoff for failures
- **Timeout handling** - Kill long-running nodes
- **Workflow scheduling** - Cron-like triggers
- **Background jobs** - Celery integration

### 3. Real-Time Updates
- **WebSocket endpoint** - Stream logs as they happen
- **Progress tracking** - Real-time execution percentage
- **Live state updates** - Push state changes to clients

### 4. Error Handling & Resilience
- **Custom exceptions** - Domain-specific error types
- **Rollback mechanisms** - Undo failed operations
- **Circuit breakers** - Prevent cascading failures
- **Dead letter queues** - Capture failed executions

### 5. Security
- **Authentication** - JWT tokens, API keys
- **Authorization** - Role-based access control
- **Rate limiting** - Prevent abuse
- **Input sanitization** - Safe eval() replacement
- **Sandboxed execution** - Isolate tool execution

### 6. Monitoring & Observability
- **Structured logging** - JSON logs with context
- **Metrics** - Prometheus integration
  - Execution times
  - Success/failure rates
  - Active workflows
- **Distributed tracing** - OpenTelemetry
- **Alerting** - Slack/email notifications

### 7. Developer Experience
- **CLI tool** - Create workflows from command line
- **Visual editor** - Drag-and-drop workflow builder
- **Workflow templates** - Pre-built common patterns
- **Better documentation** - Auto-generated from code
- **Type stubs** - IDE autocomplete support

### 8. Testing & Quality
- **Unit tests** - pytest for all components
- **Integration tests** - End-to-end API tests
- **Load tests** - Locust for performance
- **Code coverage** - 80%+ coverage target
- **CI/CD pipeline** - GitHub Actions

### 9. Advanced Workflow Features
- **Subworkflows** - Compose workflows
- **Dynamic graphs** - Generate nodes at runtime
- **Human-in-the-loop** - Await user input
- **Event-driven** - Trigger on external events
- **Time-based routing** - Schedule-aware branching

### 10. Tool Ecosystem
- **Plugin system** - Load tools dynamically
- **Tool marketplace** - Share community tools
- **Tool versioning** - Manage tool updates
- **Tool dependencies** - Auto-install requirements

---

## 🧪 Running Tests (Future)

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Run integration tests
pytest tests/integration/
```

---

## 📝 Example: Creating a Custom Workflow

```python
from app.engine.workflow import WorkflowBuilder, WorkflowState
from app.tools.registry import tool

# Define custom tools
@tool(description="My custom tool")
def my_tool(state: WorkflowState) -> WorkflowState:
    state.data["processed"] = True
    return state

# Build workflow
workflow = (
    WorkflowBuilder()
    .node("step1", my_tool)
    .node("step2", another_tool)
    .edge("step1", "step2")
    .start("step1")
    .end("step2")
    .build()
)

# Execute
initial_state = WorkflowState(data={"input": "value"})
final_state, logs = await workflow.run(initial_state)
```

---

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is already in use
# Windows:
netstat -ano | findstr :8000
# Mac/Linux:
lsof -i :8000

# Use different port
uvicorn app.main:app --port 8001
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Workflow execution fails
- Check logs in terminal
- Verify tool is registered
- Ensure all edges are defined
- Check max_steps limit

---

## 📄 License

MIT License - feel free to use for learning!

---

## 👤 Author

**[Your Name]**  
AI Engineering Internship Assignment  
[Your Email]  
[Your GitHub]

---

## 🙏 Acknowledgments

- FastAPI for excellent async framework
- Pydantic for type safety
- Assignment inspiration from LangGraph

---

**⭐ If you found this helpful, please star the repo!**
