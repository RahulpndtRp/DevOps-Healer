"""Network monitoring specialist"""

from datetime import datetime
from typing import Dict, Any, List
from ..base import BaseAgent
from ...models.enums import AgentType
from ...models.state import SupportOpsState
from ...tools.monitoring import network_connectivity_tester
from langgraph.graph import END


class NetworkMonitorSpecialist(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="network-monitor",
            agent_type=AgentType.SPECIALIST,
            tools=[network_connectivity_tester],
        )

    async def execute(self, state: SupportOpsState) -> SupportOpsState:
        """Analyze network connectivity and performance"""

        self.log_communication(state, "Starting network analysis")

        if state["incident"].affected_systems:
            try:
                network_test = network_connectivity_tester.invoke(
                    {
                        "target_hosts": state["incident"].affected_systems,
                        "test_protocols": ["icmp", "tcp", "udp"],
                    }
                )

                analysis_result = self._analyze_network_health(network_test)

                state["specialist_findings"]["network_analysis"] = {
                    "raw_data": network_test,
                    "analysis_result": analysis_result,
                    "timestamp": datetime.now().isoformat(),
                    "specialist_id": self.agent_id,
                }

                self.log_communication(
                    state,
                    f"Network analysis complete. Connectivity issues: {analysis_result.get('connectivity_issues', [])}",
                )

                if analysis_result["requires_response"]:
                    state["current_agent"] = "response-squad"
                    state["workflow_status"] = "analysis_requires_response"
                else:
                    state["workflow_status"] = "network_analysis_complete"
                    state["current_agent"] = END

            except Exception as e:
                self.log_communication(state, f"Error in network analysis: {e}")
                state["workflow_status"] = "network_analysis_complete"
                state["current_agent"] = END
        else:
            self.log_communication(state, "No affected systems to analyze")
            state["workflow_status"] = "network_analysis_complete"
            state["current_agent"] = END

        return state

    def _analyze_network_health(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze network connectivity data"""
        connectivity_issues = []
        high_latency_hosts = []

        for host, conn_data in network_data["connectivity_status"].items():
            if not conn_data["ping_success"]:
                connectivity_issues.append(f"{host}:unreachable")
            elif conn_data["avg_latency_ms"] > 100:
                high_latency_hosts.append(f"{host}:{conn_data['avg_latency_ms']}ms")
            elif conn_data["packet_loss_percent"] > 5:
                connectivity_issues.append(
                    f"{host}:packet_loss_{conn_data['packet_loss_percent']}%"
                )

        return {
            "connectivity_issues": connectivity_issues,
            "high_latency_hosts": high_latency_hosts,
            "requires_response": len(connectivity_issues) > 0
            or len(high_latency_hosts) > 0,
            "confidence_score": 0.88,
            "recommended_actions": [
                "investigate_routing" if connectivity_issues else "monitor",
                "optimize_network" if high_latency_hosts else "monitor",
            ],
        }
