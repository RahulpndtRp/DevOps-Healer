from typing import TypedDict, Dict, List, Any, Optional
from .incident import IncidentData

class SupportOpsState(TypedDict):
    """Global state for the SupportOps system - LangGraph compatible"""
    # Core incident information
    incident: IncidentData
    
    # Agent observations and state updates  
    tribe_observations: Dict[str, Any]
    squad_diagnostics: Dict[str, Any]
    specialist_findings: Dict[str, Any]
    
    # Classification and routing
    incident_classification: Dict[str, Any]
    delegation_decision: Dict[str, Any]
    
    # Remediation and response
    remediation_plan: Dict[str, Any]
    execution_results: Dict[str, Any]
    
    # Approval and escalation
    approval_requests: List[Dict[str, Any]]
    escalation_history: List[Dict[str, Any]]
    
    # Communication and knowledge
    communication_logs: List[Dict[str, Any]]
    knowledge_updates: List[Dict[str, Any]]
    
    # Workflow control
    current_agent: str
    workflow_status: str
    completion_status: str