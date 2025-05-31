"""Autonomous tribe orchestrator with GPT-driven incident classification"""

from datetime import datetime
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from ..base import BaseAgent
from ...models.enums import AgentType
from ...models.state import SupportOpsState
from ...tools.infrastructure import cmdb_enrichment_tool


class IncidentClassification(BaseModel):
    incident_category: str = Field(description="Primary category of the incident")
    secondary_categories: list[str] = Field(
        description="Additional relevant categories"
    )
    confidence_score: float = Field(
        description="Confidence in classification (0.0-1.0)"
    )
    recommended_squad: str = Field(
        description="Squad best suited to handle this incident"
    )
    business_impact_assessment: str = Field(description="Assessment of business impact")
    urgency_level: str = Field(description="Urgency level for response")
    estimated_resolution_time: str = Field(description="Estimated time to resolve")
    next_actions: list[str] = Field(description="Recommended immediate actions")
    reasoning: str = Field(
        description="Detailed reasoning for classification decisions"
    )
    similar_incidents: list[str] = Field(
        description="References to similar past incidents"
    )


class TribeOrchestrator(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="support-ops-tribe",
            agent_type=AgentType.TRIBE,
            tools=[cmdb_enrichment_tool],
        )

        # Check if we should use autonomous mode (you can add config loading here)
        self.autonomous_mode = True  # Set to False to use deterministic mode

        if self.autonomous_mode:
            self.classification_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """You are an expert DevOps incident classification and orchestration specialist with deep knowledge of:
                - Infrastructure incident patterns and root causes
                - Service dependencies and business impact analysis
                - Incident categorization and priority assessment
                - Squad specialization and workload distribution
                - Historical incident analysis and pattern recognition

                Your role is to intelligently classify incidents and route them to the most appropriate specialized teams.
                Consider business impact, technical complexity, and resource availability in your decisions.
                
                Available specialist squads and their capabilities:
                - DIAGNOSTICS SQUAD: System health monitoring, performance analysis, root cause investigation
                - RESPONSE SQUAD: Remediation planning, change coordination, escalation management
                - KNOWLEDGE SQUAD: Documentation, learning capture, process improvement
                
                Available categories:
                - cpu_utilization: CPU performance and capacity issues
                - memory_utilization: Memory leaks, capacity, and allocation issues  
                - disk_utilization: Storage capacity, I/O performance, filesystem issues
                - network_connectivity: Network routing, latency, connectivity problems
                - database_performance: Database slowness, locks, capacity issues
                - application_performance: Application-level performance and availability
                - security_incident: Security breaches, policy violations, threats
                - backup_failure: Backup and recovery system issues
                
                Provide classification in valid JSON format.""",
                    ),
                    (
                        "human",
                        """Analyze and classify the following incident:

                INCIDENT DETAILS:
                - ID: {incident_id}
                - Timestamp: {timestamp}
                - Severity: {severity}
                - Description: {description}
                - Affected Systems: {affected_systems}
                - Reported Symptoms: {symptoms}
                - Metadata: {metadata}

                CMDB ENRICHMENT DATA:
                {cmdb_data}

                OPERATIONAL CONTEXT:
                - Current Time: {current_time}
                - Business Hours: {business_hours}
                - Recent System Changes: {recent_changes}
                - System Load: {system_load}

                Based on this information, provide:
                1. Primary and secondary incident categories
                2. Business impact assessment considering affected systems
                3. Recommended squad assignment with reasoning
                4. Urgency level and estimated resolution timeline
                5. Immediate next actions to begin investigation
                6. References to similar historical incidents (if any)
                7. Confidence level in your classification

                Consider the technical symptoms, business context, and operational constraints.""",
                    ),
                ]
            )

            self.output_parser = JsonOutputParser(
                pydantic_object=IncidentClassification
            )

    async def execute(self, state: SupportOpsState) -> SupportOpsState:
        """Process and classify incoming incident"""

        if self.autonomous_mode:
            return await self._autonomous_classification(state)
        else:
            return await self._deterministic_classification(state)

    async def _autonomous_classification(
        self, state: SupportOpsState
    ) -> SupportOpsState:
        """Perform autonomous incident classification using GPT"""

        self.log_communication(
            state, "🤖 Starting autonomous incident classification with GPT-4"
        )

        try:
            # Get CMDB enrichment if systems are affected
            cmdb_data = "No CMDB data available"
            if state["incident"].affected_systems:
                try:
                    cmdb_result = cmdb_enrichment_tool.invoke(
                        {
                            "incident_id": state["incident"].incident_id,
                            "server_hostname": state["incident"].affected_systems[0],
                            "alert_details": state["incident"].metadata,
                        }
                    )
                    state["tribe_observations"]["cmdb_data"] = cmdb_result
                    cmdb_data = self._format_cmdb_data(cmdb_result)
                except Exception as e:
                    self.log_communication(state, f"⚠️ CMDB enrichment failed: {e}")
                    state["tribe_observations"]["cmdb_data"] = {
                        "status": "enrichment_failed"
                    }

            # Prepare operational context
            current_time = datetime.now()
            business_hours = 9 <= current_time.hour <= 17

            # Create the classification chain
            chain = self.classification_prompt | self.llm | self.output_parser

            # Execute autonomous classification
            classification = await chain.ainvoke(
                {
                    "incident_id": state["incident"].incident_id,
                    "timestamp": state["incident"].timestamp.isoformat(),
                    "severity": state["incident"].severity.value,
                    "description": state["incident"].description,
                    "affected_systems": ", ".join(state["incident"].affected_systems),
                    "symptoms": ", ".join(state["incident"].symptoms),
                    "metadata": str(state["incident"].metadata),
                    "cmdb_data": cmdb_data,
                    "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "business_hours": "Yes" if business_hours else "No",
                    "recent_changes": "None identified",  # Could be enriched from change management
                    "system_load": "Normal",  # Could be enriched from monitoring
                }
            )

            # Store comprehensive classification
            state["incident_classification"] = {
                "incident_category": classification["incident_category"],
                "secondary_categories": classification["secondary_categories"],
                "confidence_score": classification["confidence_score"],
                "recommended_squad": classification["recommended_squad"],
                "business_impact_assessment": classification[
                    "business_impact_assessment"
                ],
                "urgency_level": classification["urgency_level"],
                "estimated_resolution_time": classification[
                    "estimated_resolution_time"
                ],
                "next_actions": classification["next_actions"],
                "reasoning": classification["reasoning"],
                "similar_incidents": classification["similar_incidents"],
                "classification_method": "autonomous_gpt4",
                "classified_at": datetime.now().isoformat(),
            }

            # Set routing based on GPT recommendation
            state["current_agent"] = classification["recommended_squad"]
            state["workflow_status"] = "classified"

            # Enhanced communication with reasoning
            self.log_communication(
                state,
                f"🧠 GPT Classification Complete - Category: {classification['incident_category']}, "
                f"Confidence: {classification['confidence_score']:.2f}, "
                f"Squad: {classification['recommended_squad']}, "
                f"Reasoning: {classification['reasoning'][:100]}...",
            )

        except Exception as e:
            # Fallback to deterministic classification
            self.log_communication(
                state,
                f"⚠️ GPT classification failed: {e}, using fallback classification",
            )
            return await self._deterministic_classification(state)

        return state

    async def _deterministic_classification(
        self, state: SupportOpsState
    ) -> SupportOpsState:
        """Fallback deterministic classification"""

        # Get CMDB enrichment if systems are affected
        if state["incident"].affected_systems:
            try:
                cmdb_data = cmdb_enrichment_tool.invoke(
                    {
                        "incident_id": state["incident"].incident_id,
                        "server_hostname": state["incident"].affected_systems[0],
                        "alert_details": state["incident"].metadata,
                    }
                )
                state["tribe_observations"]["cmdb_data"] = cmdb_data
            except Exception as e:
                print(f"⚠️ CMDB enrichment failed: {e}")
                state["tribe_observations"]["cmdb_data"] = {
                    "status": "enrichment_failed"
                }

        # Simple deterministic classification based on incident category
        incident_category = (
            state["incident"].category.value
            if state["incident"].category
            else "cpu_utilization"
        )

        # Map categories to squads (standardized names)
        category_to_squad = {
            "cpu_utilization": "diagnostics-squad",
            "memory_utilization": "diagnostics-squad",
            "disk_utilization": "diagnostics-squad",
            "network_connectivity": "diagnostics-squad",
            "database_performance": "diagnostics-squad",
            "application_performance": "diagnostics-squad",
            "security_incident": "diagnostics-squad",
            "backup_failure": "diagnostics-squad",
        }

        classification = {
            "incident_category": incident_category,
            "confidence_score": 0.95,
            "recommended_squad": category_to_squad.get(
                incident_category, "diagnostics-squad"
            ),
            "business_impact_assessment": (
                "high"
                if state["incident"].severity.value in ["high", "critical"]
                else "medium"
            ),
            "next_actions": ["gather_metrics", "analyze_performance"],
            "classification_method": "deterministic",
        }

        state["incident_classification"] = classification
        state["current_agent"] = classification["recommended_squad"]
        state["workflow_status"] = "classified"

        self.log_communication(
            state,
            f"Incident classified as {classification['incident_category']} with {classification['confidence_score']:.2f} confidence, routing to {classification['recommended_squad']}",
        )

        return state

    def _format_cmdb_data(self, cmdb_data: Dict[str, Any]) -> str:
        """Format CMDB data for GPT analysis"""
        if not cmdb_data or cmdb_data.get("status") == "enrichment_failed":
            return "CMDB enrichment not available"

        return f"""
        APPLICATION CONTEXT:
        - Application: {cmdb_data.get('application_context', {}).get('application_name', 'Unknown')}
        - Business Service: {cmdb_data.get('application_context', {}).get('business_service', 'Unknown')}
        - Environment: {cmdb_data.get('application_context', {}).get('environment', 'Unknown')}
        - Business Criticality: {cmdb_data.get('business_criticality', 'Unknown')}
        
        SERVICE DEPENDENCIES:
        {self._format_dependencies(cmdb_data.get('service_dependencies', []))}
        
        USER IMPACT:
        - Affected Users: {cmdb_data.get('user_impact_data', {}).get('affected_users', 'Unknown')}
        - Revenue Impact: {cmdb_data.get('user_impact_data', {}).get('revenue_impact', 'Unknown')}
        """

    def _format_dependencies(self, dependencies: list) -> str:
        """Format service dependencies for analysis"""
        if not dependencies:
            return "- No dependencies identified"

        formatted = []
        for dep in dependencies:
            formatted.append(
                f"- {dep.get('service', 'Unknown')}: {dep.get('criticality', 'Unknown')} criticality"
            )
        return "\n".join(formatted)
