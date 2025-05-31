"""Database performance monitoring specialist"""

from datetime import datetime
from typing import Dict, Any
from ..base import BaseAgent
from ...models.enums import AgentType
from ...models.state import SupportOpsState
from ...tools.database import database_metrics_collector, query_performance_analyzer
from langgraph.graph import END


class DatabasePerformanceSpecialist(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="database-performance-monitor",
            agent_type=AgentType.SPECIALIST,
            tools=[database_metrics_collector, query_performance_analyzer],
        )

    async def execute(self, state: SupportOpsState) -> SupportOpsState:
        """Analyze database performance metrics"""

        self.log_communication(state, "Starting database performance analysis")

        try:
            database_metrics = database_metrics_collector.invoke(
                {
                    "database_connections": ["prod-db-cluster"],
                    "performance_queries": [
                        "slow_queries",
                        "lock_analysis",
                        "connection_stats",
                    ],
                    "monitoring_scope": ["performance", "health", "capacity"],
                }
            )

            query_analysis = query_performance_analyzer.invoke(
                {
                    "query_logs": ["slow_query_log"],
                    "execution_plans": ["current_plans"],
                    "performance_thresholds": {"max_exec_time": 1000},
                }
            )

            analysis_result = self._analyze_database_performance(
                database_metrics, query_analysis
            )

            state["specialist_findings"]["database_analysis"] = {
                "raw_data": {
                    "metrics": database_metrics,
                    "query_analysis": query_analysis,
                },
                "analysis_result": analysis_result,
                "timestamp": datetime.now().isoformat(),
                "specialist_id": self.agent_id,
            }

            self.log_communication(
                state,
                f"Database analysis complete. Performance issues: {analysis_result.get('performance_issues', [])}",
            )

            if analysis_result["requires_response"]:
                state["current_agent"] = "response-squad"
                state["workflow_status"] = "analysis_requires_response"
            else:
                state["workflow_status"] = "database_analysis_complete"
                state["current_agent"] = END

        except Exception as e:
            self.log_communication(state, f"Error in database analysis: {e}")
            state["workflow_status"] = "database_analysis_complete"
            state["current_agent"] = END

        return state

    def _analyze_database_performance(
        self, db_data: Dict[str, Any], query_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze database performance metrics"""
        performance_issues = []

        # Check connection pool utilization
        conn_pool = db_data["database_metrics"]["connection_pool"]
        pool_utilization = conn_pool["active"] / conn_pool["max"]
        if pool_utilization > 0.8:
            performance_issues.append("high_connection_pool_utilization")

        # Check query performance
        query_perf = db_data["database_metrics"]["query_performance"]
        if query_perf["avg_exec_time_ms"] > 1000:
            performance_issues.append("slow_query_performance")

        # Check for locks
        lock_stats = db_data["database_metrics"]["lock_stats"]
        if lock_stats["blocking_sessions"] > 0:
            performance_issues.append("database_blocking")

        # Check slow queries from analysis
        if len(query_data["query_analysis"]["slow_queries"]) > 5:
            performance_issues.append("excessive_slow_queries")

        return {
            "performance_issues": performance_issues,
            "requires_response": len(performance_issues) > 0,
            "confidence_score": 0.92,
            "recommended_actions": [
                (
                    "optimize_queries"
                    if "slow_query_performance" in performance_issues
                    else "monitor"
                ),
                (
                    "scale_connections"
                    if "high_connection_pool_utilization" in performance_issues
                    else "monitor"
                ),
                (
                    "resolve_locks"
                    if "database_blocking" in performance_issues
                    else "monitor"
                ),
            ],
        }
