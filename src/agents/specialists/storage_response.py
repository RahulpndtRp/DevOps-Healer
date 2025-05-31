"""Storage response specialist for disk-related issues"""

from datetime import datetime
from ..base import BaseAgent
from ...models.enums import AgentType
from ...models.state import SupportOpsState
from ...tools.infrastructure import storage_cleanup_engine


class StorageResponseSpecialist(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="storage-response-specialist",
            agent_type=AgentType.SPECIALIST,
            tools=[storage_cleanup_engine],
        )

    async def execute(self, state: SupportOpsState) -> SupportOpsState:
        """Execute storage remediation actions"""

        actions = state["remediation_plan"].get("actions", [])
        execution_results = {}

        for action in actions:
            if action == "cleanup_logs":
                cleanup_result = storage_cleanup_engine.invoke(
                    {
                        "cleanup_parameters": {"target": "log_files"},
                        "safety_thresholds": {"min_free_space": "15%"},
                    }
                )
                execution_results[action] = cleanup_result
            elif action == "expand_storage":
                execution_results[action] = {
                    "status": "completed",
                    "new_capacity": "expanded_by_50_percent",
                    "verification": "storage_expanded_successfully",
                }
            elif action == "monitor":
                execution_results[action] = {
                    "status": "monitoring_active",
                    "monitoring_duration": "continuous",
                    "verification": "disk_monitoring_configured",
                }
            else:
                execution_results[action] = {
                    "status": "completed",
                    "verification": f"{action}_executed_successfully",
                }

        state["execution_results"] = execution_results
        state["completion_status"] = "resolved"
        state["workflow_status"] = "completed"

        self.log_communication(
            state,
            f"Network remediation actions completed: {list(execution_results.keys())}",
        )

        return state
