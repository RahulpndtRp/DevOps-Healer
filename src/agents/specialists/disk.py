"""Disk monitoring specialist"""

from datetime import datetime
from typing import Dict, Any
from ..base import BaseAgent
from ...models.enums import AgentType
from ...models.state import SupportOpsState
from ...tools.monitoring import disk_usage_analyzer
from langgraph.graph import END


class DiskMonitorSpecialist(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="disk-monitor",
            agent_type=AgentType.SPECIALIST,
            tools=[disk_usage_analyzer],
        )

    async def execute(self, state: SupportOpsState) -> SupportOpsState:
        """Analyze disk usage and storage health"""

        self.log_communication(state, "Starting disk analysis")

        if state["incident"].affected_systems:
            try:
                disk_analysis = disk_usage_analyzer.invoke(
                    {
                        "server_hostnames": state["incident"].affected_systems,
                        "filesystem_paths": ["/", "/var", "/tmp", "/home"],
                    }
                )

                analysis_result = self._analyze_disk_usage(disk_analysis)

                state["specialist_findings"]["disk_analysis"] = {
                    "raw_data": disk_analysis,
                    "analysis_result": analysis_result,
                    "timestamp": datetime.now().isoformat(),
                    "specialist_id": self.agent_id,
                }

                self.log_communication(
                    state,
                    f"Disk analysis complete. Critical filesystems: {analysis_result.get('critical_filesystems', [])}",
                )

                if analysis_result["requires_response"]:
                    state["current_agent"] = "response-squad"
                    state["workflow_status"] = "analysis_requires_response"
                else:
                    state["workflow_status"] = "disk_analysis_complete"
                    state["current_agent"] = END

            except Exception as e:
                self.log_communication(state, f"Error in disk analysis: {e}")
                state["workflow_status"] = "disk_analysis_complete"
                state["current_agent"] = END
        else:
            self.log_communication(state, "No affected systems to analyze")
            state["workflow_status"] = "disk_analysis_complete"
            state["current_agent"] = END

        return state

    def _analyze_disk_usage(self, disk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze disk usage data and determine response requirements"""
        critical_filesystems = []

        for host, filesystems in disk_data["disk_usage_metrics"].items():
            for fs_path, fs_data in filesystems.items():
                if fs_data["used_percent"] > 90:
                    critical_filesystems.append(f"{host}:{fs_path}")

        return {
            "critical_filesystems": critical_filesystems,
            "requires_response": len(critical_filesystems) > 0,
            "confidence_score": 0.95,
            "recommended_actions": [
                "cleanup_logs" if critical_filesystems else "monitor",
                "expand_storage" if len(critical_filesystems) > 2 else "monitor",
            ],
            "severity_assessment": "high" if critical_filesystems else "low",
        }
