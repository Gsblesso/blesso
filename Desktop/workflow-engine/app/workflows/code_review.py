"""
Code Review Mini-Agent Workflow
Steps:
1. Extract functions
2. Check complexity
3. Detect basic issues
4. Suggest improvements
5. Loop until quality_score >= threshold
"""
import re
from app.engine.workflow import WorkflowBuilder, WorkflowState
from app.tools.registry import tool


@tool(description="Extract function definitions from code")
def extract_functions(state: WorkflowState) -> WorkflowState:
    """Extract all function definitions from code"""
    code = state.data.get("code", "")
    
    function_pattern = r'def\s+(\w+)\s*\([^)]*\):'
    functions = re.findall(function_pattern, code)
    
    function_details = []
    for func_name in functions:
        pattern = rf'def\s+{func_name}\s*\([^)]*\):.*?(?=\ndef\s|\Z)'
        match = re.search(pattern, code, re.DOTALL)
        if match:
            lines = match.group(0).count('\n')
            function_details.append({
                "name": func_name,
                "lines": lines
            })
    
    state.data["functions"] = function_details
    state.data["function_count"] = len(function_details)
    state.metadata["step"] = "extract_functions"
    
    return state


@tool(description="Check code complexity")
def check_complexity(state: WorkflowState) -> WorkflowState:
    """Analyze complexity of extracted functions"""
    functions = state.data.get("functions", [])
    code = state.data.get("code", "")
    
    complexity_issues = []
    total_complexity = 0
    
    for func in functions:
        lines = func["lines"]
        name = func["name"]
        
        complexity_score = 0
        
        if lines > 50:
            complexity_score += 3
            complexity_issues.append(f"Function '{name}' is too long ({lines} lines)")
        elif lines > 30:
            complexity_score += 2
        
        func_code_pattern = rf'def\s+{name}\s*\([^)]*\):.*?(?=\ndef\s|\Z)'
        match = re.search(func_code_pattern, code, re.DOTALL)
        if match:
            func_code = match.group(0)
            nesting_level = func_code.count('    if ') + func_code.count('    for ') + func_code.count('    while ')
            
            if nesting_level > 5:
                complexity_score += 2
                complexity_issues.append(f"Function '{name}' has high nesting level")
        
        func["complexity_score"] = complexity_score
        total_complexity += complexity_score
    
    state.data["complexity_issues"] = complexity_issues
    state.data["total_complexity"] = total_complexity
    state.metadata["step"] = "check_complexity"
    
    return state


@tool(description="Detect basic code issues")
def detect_issues(state: WorkflowState) -> WorkflowState:
    """Detect common code smells and issues"""
    code = state.data.get("code", "")
    issues = []
    
    if '"""' not in code and "'''" not in code:
        issues.append("Missing docstrings")
    
    global_vars = len(re.findall(r'^[A-Z_][A-Z0-9_]*\s*=', code, re.MULTILINE))
    if global_vars > 5:
        issues.append(f"Too many global variables ({global_vars})")
    
    long_lines = [i+1 for i, line in enumerate(code.split('\n')) if len(line) > 100]
    if long_lines:
        issues.append(f"Lines too long: {long_lines[:3]}")
    
    if re.search(r'except\s*:', code):
        issues.append("Bare except clause found - be specific")
    
    print_count = len(re.findall(r'\bprint\s*\(', code))
    if print_count > 3:
        issues.append(f"Too many print statements ({print_count}) - use logging")
    
    state.data["issues"] = issues
    state.data["issue_count"] = len(issues)
    state.metadata["step"] = "detect_issues"
    
    return state


@tool(description="Generate improvement suggestions")
def suggest_improvements(state: WorkflowState) -> WorkflowState:
    """Generate actionable improvement suggestions"""
    functions = state.data.get("functions", [])
    issues = state.data.get("issues", [])
    
    suggestions = []
    
    for func in functions:
        if func.get("complexity_score", 0) > 3:
            suggestions.append(f"Refactor '{func['name']}' - break into smaller functions")
    
    for issue in issues:
        if "docstring" in issue.lower():
            suggestions.append("Add docstrings to all functions and classes")
        if "print statement" in issue.lower():
            suggestions.append("Replace print() with proper logging")
        if "except" in issue.lower():
            suggestions.append("Use specific exception types in try-except blocks")
    
    if len(functions) > 10:
        suggestions.append("Consider splitting into multiple modules")
    
    state.data["suggestions"] = suggestions
    state.metadata["step"] = "suggest_improvements"
    
    return state


@tool(description="Calculate overall quality score")
def calculate_quality_score(state: WorkflowState) -> WorkflowState:
    """Calculate overall code quality score"""
    issue_count = state.data.get("issue_count", 0)
    total_complexity = state.data.get("total_complexity", 0)
    
    base_score = 100
    score = base_score - (issue_count * 10) - (total_complexity * 5)
    score = max(0, min(100, score))
    
    state.data["quality_score"] = score
    state.data["iteration"] = state.data.get("iteration", 0) + 1
    state.metadata["step"] = "calculate_quality_score"
    
    return state


def create_code_review_workflow() -> WorkflowBuilder:
    """Create the code review workflow graph"""
    
    def route_after_score(state: WorkflowState) -> str:
        """Decide whether to loop or end"""
        score = state.data.get("quality_score", 0)
        iteration = state.data.get("iteration", 0)
        threshold = state.data.get("quality_threshold", 70)
        
        if score >= threshold or iteration >= 3:
            return "end"
        else:
            return "detect_issues"
    
    workflow = (
        WorkflowBuilder()
        .node("extract_functions", extract_functions, "Extract function definitions from code")
        .node("check_complexity", check_complexity, "Analyze code complexity")
        .node("detect_issues", detect_issues, "Detect code smells and issues")
        .node("suggest_improvements", suggest_improvements, "Generate improvement suggestions")
        .node("calculate_quality_score", calculate_quality_score, "Calculate overall quality score")
        .node("end", lambda s: s, "End node")
        
        .edge("extract_functions", "check_complexity")
        .edge("check_complexity", "detect_issues")
        .edge("detect_issues", "suggest_improvements")
        .edge("suggest_improvements", "calculate_quality_score")
        .conditional_edge("calculate_quality_score", route_after_score)
        
        .start("extract_functions")
        .end("end")
    )
    
    return workflow