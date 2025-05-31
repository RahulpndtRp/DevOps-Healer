"""Base agent class for all SupportOps agents"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
from langchain_openai import ChatOpenAI
from ..models.enums import AgentType, IncidentSeverity
from ..models.state import SupportOpsState


class BaseAgent(ABC):
    def __init__(self, agent_id: str, agent_type: AgentType, tools: List = None):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.tools = tools or []
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

    @abstractmethod
    async def execute(self, state: SupportOpsState) -> SupportOpsState:
        """Execute the agent's primary function"""
        pass

    def log_communication(
        self, state: SupportOpsState, message: str, target_agent: str = None
    ):
        """Log inter-agent communication"""
        communication_entry = {
            "timestamp": datetime.now().isoformat(),
            "from_agent": self.agent_id,
            "to_agent": target_agent or "system",
            "message": message,
            # Fix: Use dictionary access
            "incident_id": state["incident"].incident_id,
        }

        # Ensure communication_logs exists and is a list
        if "communication_logs" not in state:
            state["communication_logs"] = []
        state["communication_logs"].append(communication_entry)
