"""Autonomous compute monitoring specialist with GPT decision-making"""

from datetime import datetime
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from ..base import BaseAgent
from ...models.enums import AgentType
from ...models.state import SupportOpsState
from ...tools.monitoring import prometheus_metrics_collector
from ...tools.infrastructure import ssh_system_analyzer


class ComputeAnalysisResult(BaseModel):
    issues: list[str] = Field(description="List of identified performance issues")
    cpu_status: str = Field(description="Overall CPU status assessment")
    memory_status: str = Field(description="Overall memory status assessment")
    requires_response: bool = Field(
        description="Whether remediation actions are needed"
    )
    confidence_score: float = Field(description="Confidence in the analysis (0.0-1.0)")
    recommended_actions: list[str] = Field(
        description="List of recommended remediation actions"
    )
    reasoning: str = Field(
        description="Detailed reasoning for the analysis and recommendations"
    )
    severity: str = Field(
        description="Assessed severity level: low, medium, high, critical"
    )


class ComputeMonitorSpecialist(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="compute-monitor",
            agent_type=AgentType.SPECIALIST,
            tools=[prometheus_metrics_collector, ssh_system_analyzer],
        )

        # Check if we should use autonomous mode
        self.autonomous_mode = True  # Set to False to use deterministic mode

        if self.autonomous_mode:
            # Enhanced prompt for autonomous analysis
            self.analysis_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """You are an expert DevOps compute monitoring specialist with deep knowledge of:
                - CPU performance analysis and optimization
                - Memory management and leak detection
                - System resource scaling strategies
                - Performance bottleneck identification
                - Proactive incident prevention

                Your role is to analyze compute metrics and provide intelligent recommendations.
                Always consider business impact, system criticality, and operational risk.
                
                Provide analysis in valid JSON format matching the required schema.""",
                    ),
                    (
                        "human",
                        """Analyze the following compute performance data and provide recommendations:

                INCIDENT CONTEXT:
                - Incident ID: {incident_id}
                - Severity: {severity}
                - Description: {description}
                - Affected Systems: {affected_systems}
                - Symptoms: {symptoms}

                PROMETHEUS METRICS:
                {prometheus_data}

                SSH SYSTEM ANALYSIS:
                {ssh_data}

                HISTORICAL CONTEXT:
                - Time of Day: {current_time}
                - Business Hours: {business_hours}

                Please provide a comprehensive analysis including:
                1. Root cause assessment
                2. Business impact evaluation
                3. Recommended immediate actions
                4. Preventive measures
                5. Confidence level in your analysis

                Consider the system criticality and current operational context in your recommendations.""",
                    ),
                ]
            )

            self.output_parser = JsonOutputParser(pydantic_object=ComputeAnalysisResult)

    async def execute(self, state: SupportOpsState) -> SupportOpsState:
        """Analyze CPU and memory utilization"""

        if self.autonomous_mode:
            return await self._autonomous_analysis(state)
        else:
            return await self._deterministic_analysis(state)

    async def _autonomous_analysis(self, state: SupportOpsState) -> SupportOpsState:
        """Perform autonomous compute analysis using GPT"""

        self.log_communication(
            state, "🤖 Starting autonomous compute analysis with GPT-4"
        )

        if state["incident"].affected_systems:
            try:
                # Gather real metrics from tools
                metrics = prometheus_metrics_collector.invoke(
                    {
                        "target_hosts": state["incident"].affected_systems,
                        "metric_queries": ["cpu_usage", "memory_usage", "load_average"],
                        "time_range": "1h",
                    }
                )

                ssh_analysis = ssh_system_analyzer.invoke(
                    {
                        "server_hostnames": state["incident"].affected_systems,
                        "analysis_commands": [
                            "top -bn1",
                            "ps aux --sort=-%cpu",
                            "free -m",
                            "vmstat 1 3",
                        ],
                    }
                )

                # Prepare context for GPT analysis
                current_time = datetime.now()
                business_hours = 9 <= current_time.hour <= 17

                # Create the analysis chain
                chain = self.analysis_prompt | self.llm | self.output_parser

                # Execute autonomous analysis
                analysis_result = await chain.ainvoke(
                    {
                        "incident_id": state["incident"].incident_id,
                        "severity": state["incident"].severity.value,
                        "description": state["incident"].description,
                        "affected_systems": ", ".join(
                            state["incident"].affected_systems
                        ),
                        "symptoms": ", ".join(state["incident"].symptoms),
                        "prometheus_data": self._format_metrics_for_analysis(metrics),
                        "ssh_data": self._format_ssh_data_for_analysis(ssh_analysis),
                        "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "business_hours": "Yes" if business_hours else "No",
                    }
                )

                # Store comprehensive findings
                state["specialist_findings"]["compute_analysis"] = {
                    "raw_metrics": metrics,
                    "raw_ssh_analysis": ssh_analysis,
                    "gpt_analysis": analysis_result,
                    "analysis_result": analysis_result,  # For backward compatibility
                    "analysis_method": "autonomous_gpt4",
                    "timestamp": datetime.now().isoformat(),
                    "specialist_id": self.agent_id,
                }

                # Enhanced communication with reasoning
                self.log_communication(
                    state,
                    f"🧠 GPT Analysis Complete - Issues: {analysis_result['issues']}, "
                    f"Confidence: {analysis_result['confidence_score']:.2f}, "
                    f"Reasoning: {analysis_result['reasoning'][:100]}...",
                )

                # Intelligent routing based on GPT analysis
                if analysis_result["requires_response"]:
                    state["current_agent"] = "response-squad"
                    state["workflow_status"] = "analysis_requires_response"
                else:
                    state["workflow_status"] = "analysis_complete"

            except Exception as e:
                # Fallback to deterministic analysis if GPT fails
                self.log_communication(
                    state,
                    f"⚠️ GPT analysis failed: {e}, falling back to deterministic analysis",
                )
                return await self._deterministic_analysis(state)

        return state

    async def _deterministic_analysis(self, state: SupportOpsState) -> SupportOpsState:
        """Fallback deterministic analysis"""

        if state["incident"].affected_systems:
            # Gather metrics from Prometheus
            metrics = prometheus_metrics_collector.invoke(
                {
                    "target_hosts": state["incident"].affected_systems,
                    "metric_queries": ["cpu_usage", "memory_usage"],
                    "time_range": "1h",
                }
            )

            # Perform SSH analysis
            ssh_analysis = ssh_system_analyzer.invoke(
                {
                    "server_hostnames": state["incident"].affected_systems,
                    "analysis_commands": ["top", "ps aux", "free -m"],
                }
            )

            # Analyze findings
            analysis_result = self._fallback_analysis(metrics, ssh_analysis)

            state["specialist_findings"]["compute_analysis"] = {
                "metrics": metrics,
                "ssh_analysis": ssh_analysis,
                "analysis_result": analysis_result,
                "analysis_method": "deterministic",
                "timestamp": datetime.now().isoformat(),
            }

            self.log_communication(
                state,
                f"Compute analysis complete. Issues found: {analysis_result.get('issues', [])}",
            )

            # Determine next step
            if analysis_result["requires_response"]:
                state["current_agent"] = "response-squad"
            else:
                state["workflow_status"] = "analysis_complete"

        return state

    def _format_metrics_for_analysis(self, metrics: Dict[str, Any]) -> str:
        """Format Prometheus metrics for GPT analysis"""
        formatted = []

        for host, cpu_data in metrics["cpu_metrics"].items():
            formatted.append(
                f"""
            Host: {host}
            - CPU Utilization: {cpu_data['current_utilization']}%
            - 1h Average: {cpu_data['avg_utilization_1h']}%
            - 24h Peak: {cpu_data['peak_utilization_24h']}%
            """
            )

        for host, mem_data in metrics["memory_metrics"].items():
            formatted.append(
                f"""
            Host: {host}
            - Memory Utilization: {mem_data['current_utilization']}%
            - Available Memory: {mem_data['available_memory_gb']}GB
            - Memory Pressure: {mem_data['memory_pressure']}
            """
            )

        return "\n".join(formatted)

    def _format_ssh_data_for_analysis(self, ssh_data: Dict[str, Any]) -> str:
        """Format SSH analysis data for GPT"""
        formatted = []

        if "process_information" in ssh_data:
            formatted.append("HIGH CPU PROCESSES:")
            for proc in ssh_data["process_information"]["high_cpu_processes"]:
                formatted.append(
                    f"- PID {proc['pid']}: {proc['command']} ({proc['cpu_percent']}% CPU)"
                )

            formatted.append("\nHIGH MEMORY PROCESSES:")
            for proc in ssh_data["process_information"]["high_memory_processes"]:
                formatted.append(
                    f"- PID {proc['pid']}: {proc['command']} ({proc['memory_percent']}% Memory)"
                )

        if "system_status" in ssh_data:
            status = ssh_data["system_status"]
            formatted.append(
                f"""
            SYSTEM STATUS:
            - Load Average: {status['load_average']}
            - Uptime: {status['uptime']}
            - Disk I/O Wait: {status['disk_io_wait']}%
            """
            )

        return "\n".join(formatted)

    def _fallback_analysis(
        self, metrics: Dict[str, Any], ssh_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback deterministic analysis if GPT fails"""
        cpu_critical = any(
            host_data["current_utilization"] > 85
            for host_data in metrics["cpu_metrics"].values()
        )

        memory_critical = any(
            host_data["current_utilization"] > 90
            for host_data in metrics["memory_metrics"].values()
        )

        issues = []
        if cpu_critical:
            issues.append("high_cpu_utilization")
        if memory_critical:
            issues.append("high_memory_utilization")

        return {
            "issues": issues,
            "cpu_status": "critical" if cpu_critical else "normal",
            "memory_status": "critical" if memory_critical else "normal",
            "requires_response": cpu_critical or memory_critical,
            "confidence_score": 0.8,  # Lower confidence for fallback
            "recommended_actions": [
                "scale_resources" if cpu_critical else "monitor",
                "memory_cleanup" if memory_critical else "monitor",
            ],
            "reasoning": "Fallback deterministic analysis based on threshold rules",
            "severity": "high" if (cpu_critical or memory_critical) else "low",
        }
