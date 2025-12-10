# Example API Requests

## 1. Run Code Review Workflow

### Good Quality Code Example
```json
{
  "graph_id": "code-review-default",
  "initial_state": {
    "code": "def calculate_sum(numbers):\n    \"\"\"Calculate sum of numbers.\"\"\"\n    return sum(numbers)",
    "quality_threshold": 70
  }
}
```

### Poor Quality Code Example
```json
{
  "graph_id": "code-review-default",
  "initial_state": {
    "code": "def bad_function():\n    for i in range(100):\n        print(i)",
    "quality_threshold": 70
  }
}
```

## 2. List Available Tools

**Endpoint:** GET /tools

**Expected Response:**
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

## 3. Create Custom Workflow

**Endpoint:** POST /graph/create

**Request Body:**
```json
{
  "name": "Simple Code Analyzer",
  "nodes": [
    {"name": "extract", "tool": "extract_functions"},
    {"name": "analyze", "tool": "check_complexity"}
  ],
  "edges": [
    {"from_node": "extract", "to_node": "analyze"}
  ],
  "start_node": "extract",
  "end_nodes": ["analyze"]
}
```

## 4. Query Run Status

**Endpoint:** GET /graph/state/{run_id}

Replace `{run_id}` with the ID returned from /graph/run 
