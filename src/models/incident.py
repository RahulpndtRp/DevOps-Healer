"""Incident data models and related structures"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from .enums import IncidentSeverity, IncidentCategory, AgentType

@dataclass
class IncidentData:
    incident_id: str
    timestamp: datetime
    severity: IncidentSeverity
    category: Optional[IncidentCategory] = None
    description: str = ""
    affected_systems: List[str] = field(default_factory=list)
    symptoms: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.value,
            "category": self.category.value if self.category else None,
            "description": self.description,
            "affected_systems": self.affected_systems,
            "symptoms": self.symptoms,
            "metadata": self.metadata
        }

@dataclass
class AgentObservation:
    agent_id: str
    agent_type: AgentType
    timestamp: datetime
    findings: Dict[str, Any]
    confidence_score: float
    recommended_actions: List[str] = field(default_factory=list)
    escalation_needed: bool = False