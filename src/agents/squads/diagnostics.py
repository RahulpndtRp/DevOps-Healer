"""Diagnostics squad for system health monitoring"""

from datetime import datetime
from ..base import BaseAgent
from ...models.enums import AgentType
from ...models.state import SupportOpsState
from ...tools.monitoring import prometheus_metrics_collector


class DiagnosticsSquad(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="diagnostics-squad",
            agent_type=AgentType.SQUAD,
            tools=[prometheus_metrics_collector],
        )

    async def execute(self, state: SupportOpsState) -> SupportOpsState:
        """Coordinate diagnostic activities across specialists"""

        # Determine which specialists to engage
        category = state["incident_classification"].get(
            "incident_category", "cpu_utilization"
        )
        specialists_needed = self._get_specialists_for_category(category)

        state["squad_diagnostics"]["assigned_specialists"] = specialists_needed
        state["squad_diagnostics"][
            "coordination_timestamp"
        ] = datetime.now().isoformat()
        state["workflow_status"] = "diagnostics_coordinating"

        # Set next agent - route to the primary specialist
        if specialists_needed:
            state["current_agent"] = specialists_needed[0]
        else:
            state["current_agent"] = "compute-monitor"  # Default fallback

        self.log_communication(
            state,
            f"Diagnostics squad coordinating. Assigned specialists: {specialists_needed}. Routing to: {state['current_agent']}",
        )

        return state

    def _get_specialists_for_category(self, category: str) -> list:
        """Map incident categories to required specialists"""
        mapping = {
            "cpu_utilization": ["compute-monitor"],
            "memory_utilization": ["compute-monitor"],
            "disk_utilization": ["disk-monitor"],
            "network_connectivity": ["network-monitor"],
            "database_performance": ["database-performance-monitor"],
            "application_performance": ["application-performance-monitor"],
            "security_incident": ["security-monitor"],
            "backup_failure": ["backup-monitor"],
        }
        return mapping.get(category, ["compute-monitor"])
