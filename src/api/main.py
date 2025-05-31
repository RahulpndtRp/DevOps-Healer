"""FastAPI application for SupportOps framework"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from ..models.incident import IncidentData
from ..models.enums import IncidentSeverity, IncidentCategory
from ..models.state import SupportOpsState
from ..workflows.graph import create_supportops_workflow
from langchain_core.runnables import RunnableConfig

app = FastAPI(title="SupportOps Healing System API", version="1.0.0")

# Initialize workflow
workflow_app = create_supportops_workflow()

class IncidentRequest(BaseModel):
    incident_id: Optional[str] = None
    severity: str = "medium"
    category: Optional[str] = None
    description: str
    affected_systems: List[str] = []
    symptoms: List[str] = []
    metadata: Dict[str, Any] = {}

class IncidentResponse(BaseModel):
    incident_id: str
    status: str
    resolution_status: str
    message: str

@app.post("/incidents", response_model=IncidentResponse)
async def create_incident(incident: IncidentRequest):
    """Create and process a new incident"""
    try:
        # Generate incident ID if not provided
        incident_id = incident.incident_id or f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create incident data
        incident_data = IncidentData(
            incident_id=incident_id,
            timestamp=datetime.now(),
            severity=IncidentSeverity(incident.severity),
            category=IncidentCategory(incident.category) if incident.category else None,
            description=incident.description,
            affected_systems=incident.affected_systems,
            symptoms=incident.symptoms,
            metadata=incident.metadata
        )
        
        # Initialize state
        initial_state = SupportOpsState(incident=incident_data)
        config = RunnableConfig(configurable={"thread_id": incident_id})
        
        # Execute workflow
        final_state = None
        async for step in workflow_app.astream(initial_state, config):
            final_state = list(step.values())[0]
        
        return IncidentResponse(
            incident_id=incident_id,
            status="created",
            resolution_status=final_state.completion_status if final_state else "in_progress",
            message="Incident processing completed"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "SupportOps Healing System API", "docs": "/docs"}