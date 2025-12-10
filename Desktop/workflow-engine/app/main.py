"""
FastAPI Application - Workflow Engine API
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import uuid
from datetime import datetime

# Import from app package
from app.models import (
    GraphCreateRequest, GraphCreateResponse,
    GraphRunRequest, GraphRunResponse,
    StateResponse, ExecutionLogResponse
)
from app.engine.workflow import WorkflowGraph, WorkflowState, WorkflowBuilder
from app.tools.registry import registry
from app.workflows.code_review import create_code_review_workflow

app = FastAPI(
    title="Workflow Engine API",
    description="A simple workflow engine with graph execution",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
graphs: Dict[str, WorkflowGraph] = {}
runs: Dict[str, dict] = {}


def build_graph_from_request(request: GraphCreateRequest) -> WorkflowGraph:
    """Build a WorkflowGraph from API request"""
    builder = WorkflowBuilder()
    
    for node_def in request.nodes:
        if not registry.has(node_def.tool):
            raise ValueError(f"Tool '{node_def.tool}' not found in registry")
        
        tool_func = registry.get(node_def.tool)
        builder.node(node_def.name, tool_func, node_def.description)
    
    for edge_def in request.edges:
        if edge_def.condition:
            def make_condition(condition_str: str):
                def condition_func(state: WorkflowState) -> str:
                    local_vars = {"state": state, "data": state.data}
                    return eval(condition_str, {}, local_vars)
                return condition_func
            
            builder.conditional_edge(edge_def.from_node, make_condition(edge_def.condition))
        else:
            builder.edge(edge_def.from_node, edge_def.to_node)
    
    builder.start(request.start_node)
    
    for end_node in request.end_nodes:
        builder.end(end_node)
    
    return builder.build()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Workflow Engine API",
        "version": "1.0.0",
        "endpoints": {
            "create_graph": "POST /graph/create",
            "run_graph": "POST /graph/run",
            "get_state": "GET /graph/state/{run_id}",
            "list_tools": "GET /tools"
        }
    }


@app.get("/tools")
async def list_tools():
    """List all available tools"""
    return {
        "tools": registry.list_tools()
    }


@app.post("/graph/create", response_model=GraphCreateResponse)
async def create_graph(request: GraphCreateRequest):
    """Create a new workflow graph"""
    try:
        graph = build_graph_from_request(request)
        graph_id = graph.graph_id
        graphs[graph_id] = graph
        
        return GraphCreateResponse(
            graph_id=graph_id,
            message=f"Graph '{request.name}' created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/graph/run", response_model=GraphRunResponse)
async def run_graph(request: GraphRunRequest, background_tasks: BackgroundTasks):
    """Run a workflow graph"""
    if request.graph_id not in graphs:
        raise HTTPException(status_code=404, detail=f"Graph '{request.graph_id}' not found")
    
    graph = graphs[request.graph_id]
    run_id = str(uuid.uuid4())
    
    initial_state = WorkflowState(data=request.initial_state)
    
    try:
        final_state, logs = await graph.run(initial_state, max_steps=request.max_steps)
        
        runs[run_id] = {
            "run_id": run_id,
            "graph_id": request.graph_id,
            "status": "completed",
            "final_state": final_state.model_dump(),
            "logs": [log.model_dump() for log in logs],
            "created_at": datetime.now().isoformat()
        }
        
        return GraphRunResponse(
            run_id=run_id,
            graph_id=request.graph_id,
            final_state=final_state.model_dump(),
            logs=[ExecutionLogResponse(**log.model_dump()) for log in logs],
            status="completed"
        )
    
    except Exception as e:
        runs[run_id] = {
            "run_id": run_id,
            "graph_id": request.graph_id,
            "status": "failed",
            "error": str(e),
            "created_at": datetime.now().isoformat()
        }
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@app.get("/graph/state/{run_id}", response_model=StateResponse)
async def get_state(run_id: str):
    """Get the state of a workflow run"""
    if run_id not in runs:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    
    run_data = runs[run_id]
    
    return StateResponse(
        run_id=run_data["run_id"],
        graph_id=run_data["graph_id"],
        current_state=run_data.get("final_state", {}),
        status=run_data["status"],
        logs=[ExecutionLogResponse(**log) for log in run_data.get("logs", [])]
    )


@app.get("/graph/list")
async def list_graphs():
    """List all created graphs"""
    return {
        "graphs": [
            {
                "graph_id": graph_id,
                "node_count": len(graph.nodes),
                "edge_count": len(graph.edges)
            }
            for graph_id, graph in graphs.items()
        ]
    }


@app.get("/runs/list")
async def list_runs():
    """List all workflow runs"""
    return {
        "runs": [
            {
                "run_id": run_data["run_id"],
                "graph_id": run_data["graph_id"],
                "status": run_data["status"],
                "created_at": run_data["created_at"]
            }
            for run_data in runs.values()
        ]
    }


@app.on_event("startup")
async def startup_event():
    """Initialize pre-built workflows on startup"""
    code_review = create_code_review_workflow()
    graph = code_review.build()
    graphs["code-review-default"] = graph
    
    print("✓ Workflow Engine started")
    print(f"✓ Pre-loaded workflow: code-review-default")
    print(f"✓ Available tools: {len(registry.list_tools())}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "graphs": len(graphs),
        "runs": len(runs),
        "tools": len(registry.list_tools())
    }