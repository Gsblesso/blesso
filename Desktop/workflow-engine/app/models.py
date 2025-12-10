"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class NodeDefinition(BaseModel):
    """Definition of a workflow node"""
    name: str
    tool: str
    description: Optional[str] = ""


class EdgeDefinition(BaseModel):
    """Definition of a workflow edge"""
    from_node: str
    to_node: str
    condition: Optional[str] = None


class GraphCreateRequest(BaseModel):
    """Request to create a new workflow graph"""
    nodes: List[NodeDefinition]
    edges: List[EdgeDefinition]
    start_node: str
    end_nodes: List[str] = Field(default_factory=list)
    name: Optional[str] = "Unnamed Workflow"
    description: Optional[str] = ""


class GraphCreateResponse(BaseModel):
    """Response after creating a graph"""
    graph_id: str
    message: str = "Graph created successfully"


class GraphRunRequest(BaseModel):
    """Request to run a workflow"""
    graph_id: str
    initial_state: Dict[str, Any] = Field(default_factory=dict)
    max_steps: Optional[int] = 50


class ExecutionLogResponse(BaseModel):
    """Single execution log entry"""
    step: int
    node_name: str
    timestamp: str
    state_snapshot: Dict[str, Any]


class GraphRunResponse(BaseModel):
    """Response after running a workflow"""
    run_id: str
    graph_id: str
    final_state: Dict[str, Any]
    logs: List[ExecutionLogResponse]
    status: str = "completed"


class StateResponse(BaseModel):
    """Response for state query"""
    run_id: str
    graph_id: str
    current_state: Dict[str, Any]
    status: str
    logs: List[ExecutionLogResponse]