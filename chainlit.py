"""
🤖 DevOps Healer - Chainlit Application
An interactive web interface for the autonomous DevOps incident response system
"""

import chainlit as cl
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.models.incident import IncidentData
from src.models.enums import IncidentSeverity, IncidentCategory
from src.models.state import SupportOpsState
from src.workflows.graph import create_supportops_workflow
from langchain_core.runnables import RunnableConfig

# Global workflow instance
workflow_app = None


@cl.on_chat_start
async def start():
    """Initialize the DevOps Healer system when chat starts"""
    global workflow_app

    # Create workflow instance
    workflow_app = create_supportops_workflow()

    # Welcome message with system capabilities
    welcome_msg = """
# 🤖 Welcome to DevOps Healer!

I'm your autonomous DevOps incident response assistant, powered by GPT-4 and specialized in:

## 🔍 **Intelligent Incident Analysis**
- CPU & Memory performance issues
- Database performance problems  
- Network connectivity issues
- Storage capacity emergencies
- Application performance degradation

## 🧠 **Autonomous Capabilities**
- **Smart Classification**: GPT-4 powered incident categorization
- **Root Cause Analysis**: Deep technical investigation
- **Remediation Planning**: Risk-aware action planning
- **Business Impact Assessment**: Considers criticality and SLA impact

## 📋 **How to Report an Incident**

You can report incidents in several ways:

### 🚨 **Quick Report** (Natural Language)
Just describe your issue:
*"Our production database is running slow and customers are complaining about timeouts"*

### 📊 **Structured Report** (JSON)
For detailed incidents:
```json
{
  "severity": "high",
  "category": "database_performance", 
  "description": "Database connection pool exhaustion",
  "affected_systems": ["prod-db-01", "app-server-tier"],
  "symptoms": ["slow queries", "connection timeouts"]
}
```

### 🎯 **Available Categories**
- `cpu_utilization` - CPU performance issues
- `memory_utilization` - Memory leaks/capacity  
- `disk_utilization` - Storage capacity/I/O
- `network_connectivity` - Network routing/latency
- `database_performance` - DB slowness/locks
- `application_performance` - App-level issues
- `security_incident` - Security breaches
- `backup_failure` - Backup/recovery issues

**Ready to help! Describe your incident or paste a structured report.**
    """

    await cl.Message(content=welcome_msg).send()

    # Set user session data
    cl.user_session.set("incident_counter", 0)
    cl.user_session.set("active_incidents", {})


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming incident reports"""
    global workflow_app

    # Get current incident counter
    incident_counter = cl.user_session.get("incident_counter", 0)
    incident_counter += 1
    cl.user_session.set("incident_counter", incident_counter)

    # Show processing message
    processing_msg = await cl.Message(
        content="🔄 **Processing incident report...**\n\n*Analyzing and classifying incident...*"
    ).send()

    try:
        # Parse the incident from user input
        incident_data = await parse_incident_input(message.content, incident_counter)

        # Create initial incident summary
        summary = create_incident_summary(incident_data)

        # Update the processing message
        processing_msg.content = f"📋 **Incident Created**\n\n{summary}\n\n🤖 *Starting autonomous analysis...*"
        await processing_msg.update()

        # Execute the workflow with streaming updates
        await execute_workflow_with_updates(incident_data, processing_msg)

    except Exception as e:
        error_msg = f"❌ **Error Processing Incident**\n\n```\n{str(e)}\n```\n\nPlease try again with a valid incident description or JSON format."
        processing_msg.content = error_msg
        await processing_msg.update()


async def parse_incident_input(user_input: str, incident_counter: int) -> IncidentData:
    """Parse user input into IncidentData"""

    # Try to parse as JSON first
    try:
        if user_input.strip().startswith("{"):
            incident_json = json.loads(user_input)
            return IncidentData(
                incident_id=incident_json.get(
                    "incident_id",
                    f"INC-{datetime.now().strftime('%Y%m%d')}-{incident_counter:03d}",
                ),
                timestamp=datetime.now(),
                severity=IncidentSeverity(incident_json.get("severity", "medium")),
                category=(
                    IncidentCategory(incident_json.get("category"))
                    if incident_json.get("category")
                    else None
                ),
                description=incident_json.get("description", ""),
                affected_systems=incident_json.get("affected_systems", []),
                symptoms=incident_json.get("symptoms", []),
                metadata=incident_json.get("metadata", {}),
            )
    except (json.JSONDecodeError, ValueError):
        pass

    # Parse as natural language
    return await parse_natural_language_incident(user_input, incident_counter)


async def parse_natural_language_incident(
    description: str, incident_counter: int
) -> IncidentData:
    """Parse natural language description into incident data"""

    # Simple keyword-based parsing (could be enhanced with GPT)
    severity = IncidentSeverity.MEDIUM
    category = None
    affected_systems = []
    symptoms = []

    description_lower = description.lower()

    # Determine severity
    if any(
        word in description_lower
        for word in ["critical", "down", "outage", "emergency", "urgent"]
    ):
        severity = IncidentSeverity.CRITICAL
    elif any(
        word in description_lower for word in ["high", "severe", "major", "serious"]
    ):
        severity = IncidentSeverity.HIGH
    elif any(word in description_lower for word in ["low", "minor", "small"]):
        severity = IncidentSeverity.LOW

    # Determine category
    if any(
        word in description_lower
        for word in ["database", "db", "sql", "query", "connection"]
    ):
        category = IncidentCategory.DATABASE_PERFORMANCE
    elif any(
        word in description_lower for word in ["cpu", "processor", "load", "compute"]
    ):
        category = IncidentCategory.CPU_UTILIZATION
    elif any(word in description_lower for word in ["memory", "ram", "leak"]):
        category = IncidentCategory.MEMORY_UTILIZATION
    elif any(
        word in description_lower for word in ["disk", "storage", "space", "filesystem"]
    ):
        category = IncidentCategory.DISK_UTILIZATION
    elif any(
        word in description_lower
        for word in ["network", "connectivity", "routing", "latency"]
    ):
        category = IncidentCategory.NETWORK_CONNECTIVITY
    elif any(
        word in description_lower for word in ["application", "app", "service", "api"]
    ):
        category = IncidentCategory.APPLICATION_PERFORMANCE
    elif any(
        word in description_lower
        for word in ["security", "breach", "attack", "unauthorized"]
    ):
        category = IncidentCategory.SECURITY_INCIDENT
    elif any(word in description_lower for word in ["backup", "restore", "recovery"]):
        category = IncidentCategory.BACKUP_FAILURE

    # Extract system names (simple pattern matching)
    import re

    system_patterns = re.findall(
        r"\b(?:prod-|staging-|dev-)?(?:db|app|web|api|server)-?\w*\b", description_lower
    )
    affected_systems = list(set(system_patterns))

    # Extract symptoms (split by common delimiters)
    if "symptoms:" in description_lower:
        symptoms_text = description_lower.split("symptoms:", 1)[1]
        symptoms = [s.strip() for s in re.split(r"[,;.\n]", symptoms_text) if s.strip()]

    return IncidentData(
        incident_id=f"INC-{datetime.now().strftime('%Y%m%d')}-{incident_counter:03d}",
        timestamp=datetime.now(),
        severity=severity,
        category=category,
        description=description,
        affected_systems=affected_systems,
        symptoms=symptoms,
        metadata={"source": "chainlit_interface", "parsed_from": "natural_language"},
    )


def create_incident_summary(incident: IncidentData) -> str:
    """Create a formatted incident summary"""

    severity_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}

    category_emoji = {
        "cpu_utilization": "⚡",
        "memory_utilization": "🧠",
        "disk_utilization": "💾",
        "network_connectivity": "🌐",
        "database_performance": "🗄️",
        "application_performance": "📱",
        "security_incident": "🔒",
        "backup_failure": "💿",
    }

    summary = f"""
**{severity_emoji.get(incident.severity.value, '⚪')} Incident ID:** `{incident.incident_id}`
**📅 Timestamp:** {incident.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
**🔥 Severity:** {incident.severity.value.upper()}
**{category_emoji.get(incident.category.value if incident.category else '', '📋')} Category:** {incident.category.value.replace('_', ' ').title() if incident.category else 'Auto-detecting...'}
**📝 Description:** {incident.description}
"""

    if incident.affected_systems:
        summary += f"**🏥 Affected Systems:** {', '.join(incident.affected_systems)}\n"

    if incident.symptoms:
        summary += f"**🩺 Symptoms:** {', '.join(incident.symptoms[:3])}{'...' if len(incident.symptoms) > 3 else ''}\n"

    return summary


async def execute_workflow_with_updates(
    incident_data: IncidentData, processing_msg: cl.Message
):
    """Execute the workflow with real-time updates"""
    global workflow_app

    # Initialize state
    initial_state: SupportOpsState = {
        "incident": incident_data,
        "tribe_observations": {},
        "squad_diagnostics": {},
        "specialist_findings": {},
        "incident_classification": {},
        "delegation_decision": {},
        "remediation_plan": {},
        "execution_results": {},
        "approval_requests": [],
        "escalation_history": [],
        "communication_logs": [],
        "knowledge_updates": [],
        "current_agent": "",
        "workflow_status": "initialized",
        "completion_status": "in_progress",
    }

    config = RunnableConfig(configurable={"thread_id": incident_data.incident_id})

    step_count = 0
    workflow_messages = []

    try:
        async for step in workflow_app.astream(initial_state, config):
            step_count += 1
            agent_name = list(step.keys())[0]
            state_update = step[agent_name]

            # Create step update message
            step_msg = await create_step_update(step_count, agent_name, state_update)
            workflow_messages.append(step_msg)

            # Update the processing message with all steps
            full_content = (
                create_incident_summary(incident_data)
                + "\n\n"
                + "\n\n".join(workflow_messages)
            )
            processing_msg.content = full_content
            await processing_msg.update()

            # Add a small delay for better UX
            await asyncio.sleep(0.5)

            if step_count > 10:  # Safety check
                break

    except Exception as e:
        error_step = (
            f"❌ **Workflow Error at Step {step_count + 1}**\n```\n{str(e)}\n```"
        )
        workflow_messages.append(error_step)
        full_content = (
            create_incident_summary(incident_data)
            + "\n\n"
            + "\n\n".join(workflow_messages)
        )
        processing_msg.content = full_content
        await processing_msg.update()

    # Add completion summary
    completion_msg = f"\n\n✅ **Workflow Complete!** ({step_count} steps executed)"
    full_content = (
        create_incident_summary(incident_data)
        + "\n\n"
        + "\n\n".join(workflow_messages)
        + completion_msg
    )
    processing_msg.content = full_content
    await processing_msg.update()


async def create_step_update(
    step_count: int, agent_name: str, state_update: Dict[str, Any]
) -> str:
    """Create a formatted step update message"""

    agent_emoji = {
        "tribe_orchestrator": "🎯",
        "diagnostics-squad": "🔍",
        "response-squad": "⚡",
        "compute-monitor": "💻",
        "disk-monitor": "💾",
        "network-monitor": "🌐",
        "database-performance-monitor": "🗄️",
        "compute-resource-specialist": "⚙️",
        "storage-response-specialist": "💾",
        "database-response-specialist": "🗄️",
        "network-response-specialist": "🌐",
    }

    agent_display = agent_name.replace("_", " ").replace("-", " ").title()
    emoji = agent_emoji.get(agent_name, "🤖")

    step_msg = f"**{emoji} Step {step_count}: {agent_display}**"

    # Add status
    status = state_update.get("workflow_status", "unknown")
    step_msg += f"\n📊 Status: `{status}`"

    # Add classification info
    if state_update.get("incident_classification"):
        classification = state_update["incident_classification"]
        if classification.get("classification_method") == "autonomous_gpt4":
            step_msg += f"\n🧠 **GPT Classification:**"
            step_msg += f"\n  • Category: `{classification.get('incident_category', 'Unknown')}`"
            step_msg += (
                f"\n  • Confidence: `{classification.get('confidence_score', 0):.2f}`"
            )
            step_msg += f"\n  • Business Impact: `{classification.get('business_impact_assessment', 'Unknown')}`"
            if classification.get("reasoning"):
                step_msg += f"\n  • Reasoning: *{classification['reasoning'][:80]}...*"
        else:
            step_msg += f"\n📋 **Classification:**"
            step_msg += f"\n  • Category: `{classification.get('incident_category', 'Unknown')}`"
            step_msg += (
                f"\n  • Confidence: `{classification.get('confidence_score', 0):.2f}`"
            )

    # Add specialist findings
    if state_update.get("specialist_findings"):
        for finding_type, finding_data in state_update["specialist_findings"].items():
            if isinstance(finding_data, dict):
                if (
                    finding_data.get("analysis_method") == "autonomous_gpt4"
                    and "gpt_analysis" in finding_data
                ):
                    gpt_analysis = finding_data["gpt_analysis"]
                    step_msg += f"\n🔍 **GPT Analysis ({finding_type.replace('_', ' ').title()}):**"
                    step_msg += (
                        f"\n  • Issues: `{', '.join(gpt_analysis.get('issues', []))}`"
                    )
                    step_msg += f"\n  • Confidence: `{gpt_analysis.get('confidence_score', 0):.2f}`"
                    step_msg += f"\n  • Actions: `{', '.join(gpt_analysis.get('recommended_actions', []))}`"
                elif "analysis_result" in finding_data:
                    analysis = finding_data["analysis_result"]
                    step_msg += (
                        f"\n🔍 **Analysis ({finding_type.replace('_', ' ').title()}):**"
                    )
                    issues_key = next(
                        (
                            k
                            for k in [
                                "performance_issues",
                                "critical_filesystems",
                                "connectivity_issues",
                                "issues",
                            ]
                            if k in analysis
                        ),
                        None,
                    )
                    if issues_key:
                        step_msg += (
                            f"\n  • Issues: `{', '.join(analysis.get(issues_key, []))}`"
                        )
                    step_msg += f"\n  • Actions: `{', '.join(analysis.get('recommended_actions', []))}`"

    # Add remediation plan
    if state_update.get("remediation_plan"):
        plan = state_update["remediation_plan"]
        if plan.get("plan_method") == "autonomous_gpt4":
            step_msg += f"\n📋 **GPT Remediation Plan:**"
            step_msg += f"\n  • Actions: `{', '.join(plan.get('actions', []))}`"
            step_msg += f"\n  • Risk: `{plan.get('risk_assessment', 'Unknown')}`"
            step_msg += f"\n  • Duration: `{plan.get('estimated_duration', 'Unknown')}`"
            step_msg += (
                f"\n  • Approval Required: `{plan.get('requires_approval', False)}`"
            )
        else:
            step_msg += f"\n📋 **Remediation Plan:**"
            step_msg += f"\n  • Actions: `{', '.join(plan.get('actions', []))}`"

    # Add execution results
    if state_update.get("execution_results"):
        step_msg += f"\n⚡ **Execution Results:**"
        for action, result in state_update["execution_results"].items():
            if isinstance(result, dict):
                status = result.get("status", "Unknown")
                step_msg += f"\n  • {action.replace('_', ' ').title()}: `{status}`"
            else:
                step_msg += f"\n  • {action.replace('_', ' ').title()}: `{str(result)}`"

    return step_msg


# Custom author renaming
@cl.author_rename
def rename(orig_author: str):
    rename_dict = {"Assistant": "🤖 DevOps Healer", "User": "👤 DevOps Engineer"}
    return rename_dict.get(orig_author, orig_author)


if __name__ == "__main__":
    # This allows running the app directly
    import subprocess

    subprocess.run(["chainlit", "run", __file__, "-w"])
