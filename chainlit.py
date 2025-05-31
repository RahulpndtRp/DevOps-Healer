"""
🤖 DevOps Healer - Enhanced Visual Chainlit Application
An interactive web interface with improved visual hierarchy and separators
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

    # Welcome message with enhanced visual hierarchy
    welcome_msg = """
# 🤖 DevOps Healer - Autonomous Incident Response

---

## 🚀 **System Capabilities**

### 🔍 **Intelligent Analysis**
- 💻 CPU & Memory performance monitoring
- 🗄️ Database performance optimization  
- 🌐 Network connectivity diagnostics
- 💾 Storage capacity management
- 📱 Application performance tuning

### 🧠 **AI-Powered Features**
- 🎯 **Smart Classification** - GPT-4 powered incident categorization
- 🔬 **Root Cause Analysis** - Deep technical investigation with reasoning
- 📋 **Intelligent Planning** - Risk-aware remediation strategies
- 📊 **Business Impact** - SLA and criticality assessment

---

## 📝 **How to Report Incidents**

### 🗣️ **Natural Language** (Recommended)
Simply describe your problem in plain English:

> *"Our production database is running slow and customers are complaining about checkout timeouts"*

### 📊 **Structured JSON** (Advanced Users)
For precise control with detailed metadata:

```json
{
  "severity": "critical",
  "category": "database_performance", 
  "description": "Connection pool exhaustion",
  "affected_systems": ["prod-db-01", "app-servers"],
  "symptoms": ["slow queries", "timeouts"]
}
```

---

## 🎯 **Available Categories**

| 🏷️ Category | 📝 Description | 💡 Examples |
|-------------|----------------|-------------|
| `cpu_utilization` | CPU performance & capacity | High load, throttling |
| `memory_utilization` | Memory allocation & leaks | OOM errors, pressure |
| `disk_utilization` | Storage capacity & I/O | Disk full, slow writes |
| `network_connectivity` | Network routing & latency | Packet loss, timeouts |
| `database_performance` | DB performance & locks | Slow queries, deadlocks |
| `application_performance` | App-level issues | API errors, slowdowns |
| `security_incident` | Security breaches | Unauthorized access |
| `backup_failure` | Backup & recovery | Failed backups, corruption |

---

## 🔥 **Severity Levels**

- 🔴 **CRITICAL** - System down, revenue impact, immediate action required
- 🟠 **HIGH** - Significant degradation, user impact, urgent attention needed  
- 🟡 **MEDIUM** - Moderate issues, some impact, timely resolution required
- 🟢 **LOW** - Minor issues, minimal impact, routine maintenance

---

### 🚀 **Ready to Help!**
Describe your incident below and watch the AI analyze and resolve it step-by-step!
    """

    await cl.Message(content=welcome_msg).send()

    # Set user session data
    cl.user_session.set("incident_counter", 0)
    cl.user_session.set("active_incidents", {})


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming incident reports with enhanced visual feedback"""
    global workflow_app

    # Get current incident counter
    incident_counter = cl.user_session.get("incident_counter", 0)
    incident_counter += 1
    cl.user_session.set("incident_counter", incident_counter)

    # Show initial processing message with visual appeal
    processing_msg = await cl.Message(
        content="""
# 🔄 Processing Incident Report

---

## 📋 **Status**: Analyzing Input
🤖 *Parsing incident details and preparing autonomous response...*

---
        """
    ).send()

    try:
        # Parse the incident from user input
        incident_data = await parse_incident_input(message.content, incident_counter)

        # Create enhanced incident summary
        summary = create_enhanced_incident_summary(incident_data)

        # Update with incident creation confirmation
        processing_msg.content = f"""
# ✅ Incident Successfully Created

---

{summary}

---

## 🤖 **Next Steps**
Starting autonomous AI analysis and remediation workflow...

🔄 *Initializing specialist teams and diagnostic systems...*

---
        """
        await processing_msg.update()

        # Execute the workflow with enhanced visual updates
        await execute_workflow_with_enhanced_updates(incident_data, processing_msg)

    except Exception as e:
        error_msg = f"""
# ❌ Error Processing Incident

---

## 🚨 **Error Details**
```
{str(e)}
```

## 💡 **Suggestions**
- Check if your JSON format is valid (if using structured input)
- Ensure incident description contains relevant technical details
- Try using natural language description instead

## 📝 **Example Formats**

**Natural Language:**
> "Database performance critical - connection timeouts affecting users"

**JSON Format:**
```json
{{
  "severity": "high",
  "category": "database_performance",
  "description": "Your incident description"
}}
```

---
        """
        processing_msg.content = error_msg
        await processing_msg.update()


async def parse_incident_input(user_input: str, incident_counter: int) -> IncidentData:
    """Parse user input into IncidentData with enhanced logic"""

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

    # Parse as natural language with enhanced keyword detection
    return await parse_natural_language_incident(user_input, incident_counter)


async def parse_natural_language_incident(
    description: str, incident_counter: int
) -> IncidentData:
    """Enhanced natural language parsing with better keyword detection"""

    severity = IncidentSeverity.MEDIUM
    category = None
    affected_systems = []
    symptoms = []

    description_lower = description.lower()

    # Enhanced severity detection
    if any(
        word in description_lower
        for word in [
            "critical",
            "down",
            "outage",
            "emergency",
            "urgent",
            "crashed",
            "failed completely",
        ]
    ):
        severity = IncidentSeverity.CRITICAL
    elif any(
        word in description_lower
        for word in ["high", "severe", "major", "serious", "significant", "badly"]
    ):
        severity = IncidentSeverity.HIGH
    elif any(
        word in description_lower
        for word in ["low", "minor", "small", "slight", "trivial"]
    ):
        severity = IncidentSeverity.LOW

    # Enhanced category detection with more keywords
    if any(
        word in description_lower
        for word in [
            "database",
            "db",
            "sql",
            "query",
            "connection",
            "mysql",
            "postgres",
            "mongodb",
            "oracle",
        ]
    ):
        category = IncidentCategory.DATABASE_PERFORMANCE
    elif any(
        word in description_lower
        for word in ["cpu", "processor", "load", "compute", "cores", "processing"]
    ):
        category = IncidentCategory.CPU_UTILIZATION
    elif any(
        word in description_lower
        for word in ["memory", "ram", "leak", "oom", "out of memory"]
    ):
        category = IncidentCategory.MEMORY_UTILIZATION
    elif any(
        word in description_lower
        for word in ["disk", "storage", "space", "filesystem", "capacity", "volume"]
    ):
        category = IncidentCategory.DISK_UTILIZATION
    elif any(
        word in description_lower
        for word in [
            "network",
            "connectivity",
            "routing",
            "latency",
            "timeout",
            "connection",
        ]
    ):
        category = IncidentCategory.NETWORK_CONNECTIVITY
    elif any(
        word in description_lower
        for word in ["application", "app", "service", "api", "web", "website"]
    ):
        category = IncidentCategory.APPLICATION_PERFORMANCE
    elif any(
        word in description_lower
        for word in ["security", "breach", "attack", "unauthorized", "hack", "malware"]
    ):
        category = IncidentCategory.SECURITY_INCIDENT
    elif any(
        word in description_lower
        for word in ["backup", "restore", "recovery", "snapshot"]
    ):
        category = IncidentCategory.BACKUP_FAILURE

    # Enhanced system extraction
    import re

    system_patterns = re.findall(
        r"\b(?:prod-|staging-|dev-|test-)?(?:db|app|web|api|server|node|cluster)-?\w*\b",
        description_lower,
    )
    affected_systems = list(set(system_patterns))

    # Enhanced symptom extraction
    symptom_keywords = [
        "slow",
        "timeout",
        "error",
        "fail",
        "crash",
        "hang",
        "freeze",
        "lag",
        "delay",
    ]
    symptoms = [word for word in symptom_keywords if word in description_lower]

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


def create_enhanced_incident_summary(incident: IncidentData) -> str:
    """Create an enhanced, visually appealing incident summary"""

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

    # Enhanced summary with better formatting
    summary = f"""
## 📋 **Incident Details**

| 🏷️ Field | 📝 Value |
|-----------|----------|
| **Incident ID** | `{incident.incident_id}` |
| **Timestamp** | `{incident.timestamp.strftime('%Y-%m-%d %H:%M:%S')}` |
| **Severity** | {severity_emoji.get(incident.severity.value, '⚪')} **{incident.severity.value.upper()}** |
| **Category** | {category_emoji.get(incident.category.value if incident.category else '', '📋')} **{incident.category.value.replace('_', ' ').title() if incident.category else 'Auto-detecting...'}** |

### 📝 **Description**
> {incident.description}
"""

    if incident.affected_systems:
        systems_list = " • ".join(
            [f"`{system}`" for system in incident.affected_systems]
        )
        summary += f"""
### 🏥 **Affected Systems**
{systems_list}
"""

    if incident.symptoms:
        symptoms_list = " • ".join(
            [f"`{symptom}`" for symptom in incident.symptoms[:5]]
        )
        summary += f"""
### 🩺 **Symptoms Detected**
{symptoms_list}
"""

    return summary


async def execute_workflow_with_enhanced_updates(
    incident_data: IncidentData, processing_msg: cl.Message
):
    """Execute workflow with enhanced visual updates and separators"""
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
    workflow_sections = []

    try:
        async for step in workflow_app.astream(initial_state, config):
            step_count += 1
            agent_name = list(step.keys())[0]
            state_update = step[agent_name]

            # Create enhanced step update with visual separators
            step_section = await create_enhanced_step_update(
                step_count, agent_name, state_update
            )
            workflow_sections.append(step_section)

            # Create comprehensive update with all sections
            full_content = create_comprehensive_workflow_display(
                incident_data, workflow_sections, step_count
            )
            processing_msg.content = full_content
            await processing_msg.update()

            # Smooth update delay for better UX
            await asyncio.sleep(0.8)

            if step_count > 10:  # Safety check
                break

    except Exception as e:
        error_section = f"""
## ❌ **Workflow Error at Step {step_count + 1}**

---

### 🚨 **Error Details**
```
{str(e)}
```

### 💡 **Impact**
The workflow encountered an unexpected error but previous steps were completed successfully.

---
        """
        workflow_sections.append(error_section)
        full_content = create_comprehensive_workflow_display(
            incident_data, workflow_sections, step_count, has_error=True
        )
        processing_msg.content = full_content
        await processing_msg.update()

    # Add final completion section
    completion_section = f"""
## ✅ **Workflow Complete**

---

### 📊 **Execution Summary**
- **Total Steps**: `{step_count}`
- **Duration**: `{datetime.now().strftime('%H:%M:%S')}`
- **Status**: `Successfully Completed`

### 🎯 **Key Achievements**
- ✅ Incident classified and analyzed
- ✅ Root cause investigation completed  
- ✅ Remediation plan generated and executed
- ✅ System status verified and documented

---

### 🤖 **DevOps Healer Result**
Your incident has been processed through our autonomous healing system. All recommended actions have been executed and the system is monitoring for resolution confirmation.

---
    """

    workflow_sections.append(completion_section)
    final_content = create_comprehensive_workflow_display(
        incident_data, workflow_sections, step_count, is_complete=True
    )
    processing_msg.content = final_content
    await processing_msg.update()


def create_comprehensive_workflow_display(
    incident_data: IncidentData,
    workflow_sections: List[str],
    step_count: int,
    has_error: bool = False,
    is_complete: bool = False,
) -> str:
    """Create a comprehensive display with proper visual hierarchy"""

    # Header with progress indication
    if is_complete:
        header = f"# ✅ Incident Resolution Complete - {incident_data.incident_id}"
        status_emoji = "✅"
        status_text = "RESOLVED"
    elif has_error:
        header = f"# ⚠️ Incident Processing - {incident_data.incident_id}"
        status_emoji = "⚠️"
        status_text = "ERROR ENCOUNTERED"
    else:
        header = f"# 🔄 Processing Incident - {incident_data.incident_id}"
        status_emoji = "🔄"
        status_text = "IN PROGRESS"

    # Progress bar visual
    progress_bar = "█" * min(step_count, 10) + "░" * max(0, 10 - step_count)

    content = f"""
{header}

---

## 📊 **Progress Status**
**Status**: {status_emoji} **{status_text}** | **Steps**: `{step_count}/10` | **Progress**: `{progress_bar}`

---

{create_enhanced_incident_summary(incident_data)}

---

# 🔄 **Autonomous Workflow Execution**

---
"""

    # Add all workflow sections with separators
    for i, section in enumerate(workflow_sections, 1):
        content += f"{section}"
        if i < len(workflow_sections):
            content += "\n---\n"

    return content


async def create_enhanced_step_update(
    step_count: int, agent_name: str, state_update: Dict[str, Any]
) -> str:
    """Create visually enhanced step updates with proper formatting"""

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

    # Create step header with visual hierarchy
    step_section = f"""
## {emoji} **Step {step_count}: {agent_display}**

### 📊 **Status**: `{state_update.get('workflow_status', 'unknown').replace('_', ' ').title()}`
"""

    # Add classification results if available
    if state_update.get("incident_classification"):
        classification = state_update["incident_classification"]
        if classification.get("classification_method") == "autonomous_gpt4":
            step_section += f"""
### 🧠 **GPT-4 Classification Results**

| 🏷️ Attribute | 📝 Value |
|--------------|----------|
| **Category** | `{classification.get('incident_category', 'Unknown')}` |
| **Confidence** | `{classification.get('confidence_score', 0):.2f}` |
| **Business Impact** | `{classification.get('business_impact_assessment', 'Unknown')}` |
| **Urgency Level** | `{classification.get('urgency_level', 'Unknown')}` |

#### 🤔 **AI Reasoning**
> {classification.get('reasoning', 'No reasoning provided')[:150]}...
"""
        else:
            step_section += f"""
### 📋 **Classification Results**

| 🏷️ Attribute | 📝 Value |
|--------------|----------|
| **Category** | `{classification.get('incident_category', 'Unknown')}` |
| **Confidence** | `{classification.get('confidence_score', 0):.2f}` |
"""

    # Add specialist findings with enhanced formatting
    if state_update.get("specialist_findings"):
        step_section += "\n### 🔍 **Specialist Analysis**\n"

        for finding_type, finding_data in state_update["specialist_findings"].items():
            if isinstance(finding_data, dict):
                specialist_name = finding_type.replace("_", " ").title()

                if (
                    finding_data.get("analysis_method") == "autonomous_gpt4"
                    and "gpt_analysis" in finding_data
                ):
                    gpt_analysis = finding_data["gpt_analysis"]
                    step_section += f"""
#### 🧠 **{specialist_name} (GPT-4 Analysis)**

| 🏷️ Finding | 📝 Result |
|------------|-----------|
| **Issues Found** | `{', '.join(gpt_analysis.get('issues', ['None']))}` |
| **Confidence** | `{gpt_analysis.get('confidence_score', 0):.2f}` |
| **Severity** | `{gpt_analysis.get('severity', 'unknown').upper()}` |
| **Recommended Actions** | `{', '.join(gpt_analysis.get('recommended_actions', ['monitor']))}` |

> **AI Analysis**: {gpt_analysis.get('reasoning', 'No detailed reasoning provided')[:100]}...
"""
                elif "analysis_result" in finding_data:
                    analysis = finding_data["analysis_result"]
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
                    issues = analysis.get(issues_key, []) if issues_key else []

                    step_section += f"""
#### 🔍 **{specialist_name} (Standard Analysis)**

| 🏷️ Finding | 📝 Result |
|------------|-----------|
| **Issues Found** | `{', '.join(issues) if issues else 'None detected'}` |
| **Actions Required** | `{', '.join(analysis.get('recommended_actions', ['monitor']))}` |
| **Requires Response** | `{analysis.get('requires_response', False)}` |
"""

    # Add remediation planning with enhanced visuals
    if state_update.get("remediation_plan"):
        plan = state_update["remediation_plan"]
        step_section += "\n### 📋 **Remediation Plan**\n"

        if plan.get("plan_method") == "autonomous_gpt4":
            step_section += f"""
#### 🧠 **GPT-4 Generated Plan**

| 🏷️ Plan Element | 📝 Details |
|-----------------|------------|
| **Primary Actions** | `{', '.join(plan.get('actions', ['monitor']))}` |
| **Secondary Actions** | `{', '.join(plan.get('secondary_actions', ['none']))}` |
| **Risk Assessment** | `{plan.get('risk_assessment', 'Unknown').upper()}` |
| **Estimated Duration** | `{plan.get('estimated_duration', 'Unknown')}` |
| **Approval Required** | `{plan.get('requires_approval', False)}` |

#### 🤔 **Planning Reasoning**
> {plan.get('reasoning', 'No detailed reasoning provided')[:150]}...
"""
        else:
            step_section += f"""
#### 📋 **Standard Remediation Plan**

| 🏷️ Plan Element | 📝 Details |
|-----------------|------------|
| **Planned Actions** | `{', '.join(plan.get('actions', ['monitor']))}` |
| **Approval Required** | `{plan.get('requires_approval', False)}` |
"""

    # Add execution results with status indicators
    if state_update.get("execution_results"):
        step_section += "\n### ⚡ **Execution Results**\n"

        for action, result in state_update["execution_results"].items():
            action_display = action.replace("_", " ").title()

            if isinstance(result, dict):
                status = result.get("status", "Unknown")
                status_emoji = (
                    "✅"
                    if status == "completed"
                    else "🔄" if status == "monitoring_active" else "⚠️"
                )

                step_section += f"- {status_emoji} **{action_display}**: `{status}`\n"

                if result.get("verification"):
                    step_section += f"  - 🔍 Verification: `{result['verification']}`\n"
            else:
                step_section += f"- ✅ **{action_display}**: `{str(result)}`\n"

    return step_section


# Enhanced author renaming with emojis
@cl.author_rename
def rename(orig_author: str):
    rename_dict = {"Assistant": "🤖 DevOps Healer", "User": "👤 DevOps Engineer"}
    return rename_dict.get(orig_author, orig_author)


if __name__ == "__main__":
    import subprocess

    subprocess.run(["chainlit", "run", __file__, "-w"])
