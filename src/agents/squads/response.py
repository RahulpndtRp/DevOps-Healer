"""Response squad for coordinating remediation activities"""

from datetime import datetime
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from ..base import BaseAgent
from ...models.enums import AgentType, IncidentSeverity
from ...models.state import SupportOpsState


class RemediationPlan(BaseModel):
    primary_actions: list[str] = Field(
        description="Primary remediation actions to execute"
    )
    secondary_actions: list[str] = Field(
        description="Secondary/backup actions if primary fails"
    )
    requires_approval: bool = Field(description="Whether human approval is required")
    estimated_impact: str = Field(
        description="Estimated business impact during remediation"
    )
    estimated_duration: str = Field(
        description="Estimated time to complete remediation"
    )
    rollback_plan: str = Field(description="Rollback strategy if remediation fails")
    risk_assessment: str = Field(description="Risk level of performing these actions")
    success_criteria: list[str] = Field(
        description="Criteria to determine if remediation was successful"
    )
    reasoning: str = Field(
        description="Detailed reasoning for the remediation approach"
    )


class ResponseSquad(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="response-squad", agent_type=AgentType.SQUAD)

        # Check if we should use autonomous mode
        self.autonomous_mode = True  # Set to False to use deterministic mode

        if self.autonomous_mode:
            self.remediation_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """You are an expert DevOps incident response coordinator with extensive experience in:
                - Critical system remediation and recovery
                - Risk assessment and change management
                - Business impact analysis
                - Automated remediation strategies
                - Rollback and disaster recovery planning

                Your role is to create intelligent, safe remediation plans based on specialist analysis.
                Always prioritize system stability and business continuity.
                Consider the principle of least privilege and minimal viable remediation.
                
                Provide your remediation plan in valid JSON format.""",
                    ),
                    (
                        "human",
                        """Based on the following incident analysis, create a comprehensive remediation plan:

                INCIDENT DETAILS:
                - ID: {incident_id}
                - Severity: {severity}
                - Category: {category}
                - Description: {description}
                - Affected Systems: {affected_systems}
                - Business Hours: {business_hours}

                SPECIALIST ANALYSIS:
                {specialist_findings}

                BUSINESS CONTEXT:
                - System Criticality: {system_criticality}
                - User Impact: {user_impact}
                - SLA Requirements: {sla_requirements}

                OPERATIONAL CONSTRAINTS:
                - Maintenance Window Available: {maintenance_window}
                - Approval Process Required: {approval_required}
                - Rollback Capability: {rollback_available}

                Create a remediation plan that:
                1. Addresses the root cause identified by specialists
                2. Minimizes business impact and risk
                3. Provides clear success criteria
                4. Includes comprehensive rollback strategy
                5. Considers operational constraints and approval requirements

                Be specific about actions, timelines, and risk mitigation strategies.""",
                    ),
                ]
            )

            self.output_parser = JsonOutputParser(pydantic_object=RemediationPlan)

    async def execute(self, state: SupportOpsState) -> SupportOpsState:
        """Coordinate remediation response"""

        if self.autonomous_mode:
            try:
                return await self._autonomous_planning(state)
            except Exception as e:
                self.log_communication(
                    state, f"⚠️ GPT planning failed: {e}, using fallback planning"
                )
                return await self._deterministic_planning(state)
        else:
            return await self._deterministic_planning(state)

    async def _autonomous_planning(self, state: SupportOpsState) -> SupportOpsState:
        """Create autonomous remediation plan using GPT"""

        self.log_communication(
            state, "🤖 Starting autonomous remediation planning with GPT-4"
        )

        # Gather all specialist findings
        specialist_findings = self._compile_specialist_findings(state)

        # Assess business context
        business_context = self._assess_business_context(state)

        # Prepare context for GPT planning
        current_time = datetime.now()
        business_hours = 9 <= current_time.hour <= 17

        # Create the planning chain
        chain = self.remediation_prompt | self.llm | self.output_parser

        # Execute autonomous planning
        remediation_plan = await chain.ainvoke(
            {
                "incident_id": state["incident"].incident_id,
                "severity": state["incident"].severity.value,
                "category": (
                    state["incident"].category.value
                    if state["incident"].category
                    else "unknown"
                ),
                "description": state["incident"].description,
                "affected_systems": ", ".join(state["incident"].affected_systems),
                "business_hours": "Yes" if business_hours else "No",
                "specialist_findings": specialist_findings,
                "system_criticality": business_context["criticality"],
                "user_impact": business_context["user_impact"],
                "sla_requirements": business_context["sla"],
                "maintenance_window": (
                    "Available" if not business_hours else "Not Available"
                ),
                "approval_required": self._requires_approval(
                    state["incident"].severity
                ),
                "rollback_available": "Yes",
            }
        )

        # Store the comprehensive plan
        state["remediation_plan"] = {
            "actions": remediation_plan["primary_actions"],
            "secondary_actions": remediation_plan["secondary_actions"],
            "requires_approval": remediation_plan["requires_approval"],
            "estimated_impact": remediation_plan["estimated_impact"],
            "estimated_duration": remediation_plan["estimated_duration"],
            "rollback_plan": remediation_plan["rollback_plan"],
            "risk_assessment": remediation_plan["risk_assessment"],
            "success_criteria": remediation_plan["success_criteria"],
            "reasoning": remediation_plan["reasoning"],
            "plan_method": "autonomous_gpt4",
            "created_at": datetime.now().isoformat(),
        }

        # Enhanced communication with reasoning
        self.log_communication(
            state,
            f"🧠 GPT Remediation Plan Created - Actions: {remediation_plan['primary_actions']}, "
            f"Risk: {remediation_plan['risk_assessment']}, "
            f"Duration: {remediation_plan['estimated_duration']}",
        )

        # Intelligent routing to appropriate specialist
        next_specialist = self._determine_specialist(state, remediation_plan)
        state["current_agent"] = next_specialist

        return state

    async def _deterministic_planning(self, state: SupportOpsState) -> SupportOpsState:
        """Fallback deterministic planning"""

        # Fix: Use dictionary access and handle different finding types
        findings = {}
        analysis_result = {}

        # Check for different types of analysis findings
        if "compute_analysis" in state["specialist_findings"]:
            findings = state["specialist_findings"]["compute_analysis"]
            analysis_result = findings.get("analysis_result", {})
        elif "disk_analysis" in state["specialist_findings"]:
            findings = state["specialist_findings"]["disk_analysis"]
            analysis_result = findings.get("analysis_result", {})
        elif "database_analysis" in state["specialist_findings"]:
            findings = state["specialist_findings"]["database_analysis"]
            analysis_result = findings.get("analysis_result", {})
        elif "network_analysis" in state["specialist_findings"]:
            findings = state["specialist_findings"]["network_analysis"]
            analysis_result = findings.get("analysis_result", {})

        # Create remediation plan
        remediation_plan = {
            "actions": analysis_result.get("recommended_actions", ["monitor"]),
            "requires_approval": self._requires_approval(state["incident"].severity),
            "estimated_impact": "medium",
            "rollback_plan": "automated_rollback_available",
            "plan_method": "deterministic",
        }

        state["remediation_plan"] = remediation_plan

        self.log_communication(
            state, f"Remediation plan created: {remediation_plan['actions']}"
        )

        # Determine next agent based on incident category
        incident_category = (
            state["incident"].category.value
            if state["incident"].category
            else "cpu_utilization"
        )

        # Map categories to response specialists
        category_to_specialist = {
            "cpu_utilization": "compute-resource-specialist",
            "memory_utilization": "compute-resource-specialist",
            "disk_utilization": "storage-response-specialist",
            "network_connectivity": "network-response-specialist",
            "database_performance": "database-response-specialist",
            "application_performance": "application-response-specialist",
            "security_incident": "security-response-specialist",
            "backup_failure": "storage-response-specialist",
        }

        state["current_agent"] = category_to_specialist.get(
            incident_category, "compute-resource-specialist"
        )

        return state

    def _compile_specialist_findings(self, state: SupportOpsState) -> str:
        """Compile all specialist findings into a readable format for GPT"""
        findings = []

        for specialist_type, data in state["specialist_findings"].items():
            if "gpt_analysis" in data:
                # Use GPT analysis if available
                analysis = data["gpt_analysis"]
                findings.append(
                    f"""
                {specialist_type.upper()} ANALYSIS:
                - Issues Found: {analysis.get('issues', [])}
                - Confidence: {analysis.get('confidence_score', 0):.2f}
                - Severity: {analysis.get('severity', 'unknown')}
                - Recommended Actions: {analysis.get('recommended_actions', [])}
                - Reasoning: {analysis.get('reasoning', 'No reasoning provided')}
                """
                )
            elif "analysis_result" in data:
                # Use standard analysis
                analysis = data["analysis_result"]
                findings.append(
                    f"""
                {specialist_type.upper()} ANALYSIS:
                - Issues Found: {analysis.get('issues', [])}
                - Requires Response: {analysis.get('requires_response', False)}
                - Recommended Actions: {analysis.get('recommended_actions', [])}
                """
                )

        return "\n".join(findings) if findings else "No specialist findings available"

    def _assess_business_context(self, state: SupportOpsState) -> Dict[str, str]:
        """Assess business context for remediation planning"""
        severity = state["incident"].severity
        affected_systems = state["incident"].affected_systems

        # Determine criticality based on system names and severity
        criticality = (
            "high"
            if any("prod" in system.lower() for system in affected_systems)
            else "medium"
        )
        if severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]:
            criticality = "critical"

        user_impact = (
            "high"
            if severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]
            else "medium"
        )
        sla = (
            "99.9% uptime required"
            if criticality == "critical"
            else "99% uptime required"
        )

        return {"criticality": criticality, "user_impact": user_impact, "sla": sla}

    def _determine_specialist(
        self, state: SupportOpsState, plan: Dict[str, Any]
    ) -> str:
        """Intelligently determine which specialist should execute the plan"""
        incident_category = (
            state["incident"].category.value
            if state["incident"].category
            else "cpu_utilization"
        )

        # Enhanced mapping with risk consideration
        category_to_specialist = {
            "cpu_utilization": "compute-resource-specialist",
            "memory_utilization": "compute-resource-specialist",
            "disk_utilization": "storage-response-specialist",
            "network_connectivity": "network-response-specialist",
            "database_performance": "database-response-specialist",
            "application_performance": "application-response-specialist",
            "security_incident": "security-response-specialist",
            "backup_failure": "storage-response-specialist",
        }

        # Consider risk level for specialist selection
        if plan.get("risk_assessment") == "high" and plan.get("requires_approval"):
            # Route to senior specialist or add approval step
            return category_to_specialist.get(
                incident_category, "compute-resource-specialist"
            )

        return category_to_specialist.get(
            incident_category, "compute-resource-specialist"
        )

    def _requires_approval(self, severity: IncidentSeverity) -> bool:
        """Determine if human approval is required"""
        return severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]
