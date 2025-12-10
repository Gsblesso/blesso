"""
Core Workflow Engine
Supports: nodes, edges, conditional routing, loops
"""
from typing import Dict, Any, Callable, Optional, List
from pydantic import BaseModel
import uuid
from datetime import datetime


class ExecutionLog(BaseModel):
    """Track execution steps"""
    step: int
    node_name: str
    timestamp: str
    state_snapshot: Dict[str, Any]
    

class WorkflowState(BaseModel):
    """Base state that flows through workflow"""
    data: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    
    class Config:
        arbitrary_types_allowed = True


class Node:
    """Represents a workflow node"""
    def __init__(self, name: str, func: Callable, description: str = ""):
        self.name = name
        self.func = func
        self.description = description
    
    async def execute(self, state: WorkflowState) -> WorkflowState:
        """Execute node function"""
        if hasattr(self.func, '__call__'):
            result = self.func(state)
            if hasattr(result, '__await__'):
                result = await result
            return result
        return state


class ConditionalEdge:
    """Conditional routing based on state"""
    def __init__(self, condition: Callable[[WorkflowState], str]):
        self.condition = condition
    
    def evaluate(self, state: WorkflowState) -> str:
        """Return the name of next node"""
        return self.condition(state)


class WorkflowGraph:
    """Main workflow engine"""
    def __init__(self, graph_id: str = None):
        self.graph_id = graph_id or str(uuid.uuid4())
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, str | ConditionalEdge] = {}
        self.start_node: Optional[str] = None
        self.end_nodes: List[str] = []
        
    def add_node(self, name: str, func: Callable, description: str = ""):
        """Add a node to the graph"""
        self.nodes[name] = Node(name, func, description)
        
    def add_edge(self, from_node: str, to_node: str):
        """Add a simple edge"""
        self.edges[from_node] = to_node
        
    def add_conditional_edge(self, from_node: str, condition: Callable):
        """Add conditional routing"""
        self.edges[from_node] = ConditionalEdge(condition)
        
    def set_start(self, node_name: str):
        """Set starting node"""
        self.start_node = node_name
        
    def set_end(self, node_name: str):
        """Mark a node as end node"""
        if node_name not in self.end_nodes:
            self.end_nodes.append(node_name)
    
    async def run(self, initial_state: WorkflowState, max_steps: int = 50) -> tuple[WorkflowState, List[ExecutionLog]]:
        """Execute the workflow"""
        if not self.start_node:
            raise ValueError("No start node defined")
        
        current_node = self.start_node
        state = initial_state
        logs = []
        step = 0
        
        while step < max_steps:
            if current_node in self.end_nodes:
                break
            
            if current_node not in self.nodes:
                raise ValueError(f"Node '{current_node}' not found in graph")
            
            node = self.nodes[current_node]
            state = await node.execute(state)
            
            logs.append(ExecutionLog(
                step=step,
                node_name=current_node,
                timestamp=datetime.now().isoformat(),
                state_snapshot=state.model_dump()
            ))
            
            if current_node not in self.edges:
                break
            
            edge = self.edges[current_node]
            
            if isinstance(edge, ConditionalEdge):
                current_node = edge.evaluate(state)
            else:
                current_node = edge
            
            step += 1
        
        if step >= max_steps:
            raise RuntimeError(f"Workflow exceeded max steps ({max_steps})")
        
        return state, logs


class WorkflowBuilder:
    """Helper to build workflows fluently"""
    def __init__(self, graph_id: str = None):
        self.graph = WorkflowGraph(graph_id)
    
    def node(self, name: str, func: Callable, description: str = ""):
        """Add node"""
        self.graph.add_node(name, func, description)
        return self
    
    def edge(self, from_node: str, to_node: str):
        """Add edge"""
        self.graph.add_edge(from_node, to_node)
        return self
    
    def conditional_edge(self, from_node: str, condition: Callable):
        """Add conditional edge"""
        self.graph.add_conditional_edge(from_node, condition)
        return self
    
    def start(self, node_name: str):
        """Set start node"""
        self.graph.set_start(node_name)
        return self
    
    def end(self, node_name: str):
        """Set end node"""
        self.graph.set_end(node_name)
        return self
    
    def build(self) -> WorkflowGraph:
        """Return completed graph"""
        return self.graph