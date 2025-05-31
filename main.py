import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import json

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.models.incident import IncidentData
from src.models.enums import IncidentSeverity, IncidentCategory
from src.models.state import SupportOpsState
from src.workflows.graph import create_supportops_workflow
from langchain_core.runnables import RunnableConfig

load_dotenv(override=True)


async def run_autonomous_test_scenarios():
    """Run test scenarios showcasing autonomous GPT decision-making"""

    print("🤖 DevOps Healer - AUTONOMOUS GPT Framework Testing")
    print("=" * 70)
    print(
        "🧠 Features: GPT-4 Classification | Autonomous Analysis | Intelligent Planning"
    )
    print("=" * 70)

    # Create workflow
    app = create_supportops_workflow()

    # Enhanced test scenarios with more realistic data
    test_scenarios = [
        {
            "name": "🔥 Production Database Crisis",
            "incident": IncidentData(
                incident_id="INC-2024-001",
                timestamp=datetime.now(),
                severity=IncidentSeverity.CRITICAL,
                category=IncidentCategory.DATABASE_PERFORMANCE,
                description="Critical database performance degradation affecting customer transactions. Multiple slow queries detected, connection pool exhaustion, and user-reported timeouts.",
                affected_systems=[
                    "prod-db-cluster-01",
                    "prod-db-replica-02",
                    "app-server-tier",
                ],
                symptoms=[
                    "Average query time increased from 100ms to 5000ms",
                    "Connection pool utilization at 98%",
                    "Customer complaints about checkout failures",
                    "Database CPU at 95%",
                    "Lock wait timeouts increasing",
                ],
                metadata={
                    "alert_source": "datadog",
                    "first_detected": "2024-06-01T14:30:00Z",
                    "business_impact": "revenue_affecting",
                    "affected_users": 15000,
                    "sla_breach_risk": "high",
                },
            ),
        },
        {
            "name": "⚡ Kubernetes Cluster Resource Exhaustion",
            "incident": IncidentData(
                incident_id="INC-2024-002",
                timestamp=datetime.now(),
                severity=IncidentSeverity.HIGH,
                category=IncidentCategory.CPU_UTILIZATION,
                description="Kubernetes cluster showing signs of resource exhaustion. Multiple pods in pending state, CPU throttling detected across nodes, and auto-scaling failing to provision new capacity.",
                affected_systems=[
                    "k8s-prod-cluster",
                    "worker-node-01",
                    "worker-node-02",
                    "worker-node-03",
                ],
                symptoms=[
                    "15 pods stuck in Pending state",
                    "CPU throttling on 80% of containers",
                    "Node memory utilization above 90%",
                    "Failed to schedule pods due to insufficient resources",
                    "Application response times degrading",
                ],
                metadata={
                    "alert_source": "prometheus",
                    "cluster_version": "1.28",
                    "node_count": 8,
                    "pending_pods": 15,
                    "auto_scaler_status": "failed",
                },
            ),
        },
        {
            "name": "🌐 Multi-Region Network Connectivity Issues",
            "incident": IncidentData(
                incident_id="INC-2024-003",
                timestamp=datetime.now(),
                severity=IncidentSeverity.HIGH,
                category=IncidentCategory.NETWORK_CONNECTIVITY,
                description="Intermittent network connectivity issues between US-East and EU-West regions. Packet loss detected on primary links, increased latency affecting real-time services, and failover mechanisms not triggering properly.",
                affected_systems=[
                    "us-east-gateway",
                    "eu-west-gateway",
                    "vpn-tunnel-primary",
                    "load-balancer-global",
                ],
                symptoms=[
                    "Packet loss of 12% on primary inter-region link",
                    "Latency increased from 50ms to 250ms",
                    "WebRTC calls dropping frequently",
                    "API timeouts between regions",
                    "Failover not triggering automatically",
                ],
                metadata={
                    "alert_source": "network_monitor",
                    "affected_regions": ["us-east-1", "eu-west-1"],
                    "backup_link_status": "degraded",
                    "traffic_volume": "peak_hours",
                },
            ),
        },
        {
            "name": "💾 Critical Storage Capacity Emergency",
            "incident": IncidentData(
                incident_id="INC-2024-004",
                timestamp=datetime.now(),
                severity=IncidentSeverity.CRITICAL,
                category=IncidentCategory.DISK_UTILIZATION,
                description="Critical storage capacity reached on primary database storage. Transaction logs filling rapidly, backup storage at 95%, and automated cleanup failing. Risk of database shutdown imminent.",
                affected_systems=[
                    "prod-db-storage-tier",
                    "backup-storage-san",
                    "log-archive-system",
                ],
                symptoms=[
                    "Primary DB storage at 97% capacity",
                    "Transaction log growth rate: 1GB/hour",
                    "Backup storage at 95% capacity",
                    "Log rotation job failing for 3 days",
                    "Database write operations slowing down",
                ],
                metadata={
                    "alert_source": "storage_monitor",
                    "storage_type": "high_performance_ssd",
                    "growth_rate": "1GB_per_hour",
                    "cleanup_job_status": "failed",
                    "estimated_time_to_full": "6_hours",
                },
            ),
        },
    ]

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🧪 SCENARIO {i}/4: {scenario['name']}")
        print(f"📋 Incident: {scenario['incident'].incident_id}")
        print(f"🔥 Severity: {scenario['incident'].severity.value.upper()}")
        print(
            f"🏷️  Category: {scenario['incident'].category.value.replace('_', ' ').title()}"
        )
        print(f"📝 Description: {scenario['incident'].description[:100]}...")
        print(
            f"🏥 Affected Systems: {len(scenario['incident'].affected_systems)} systems"
        )
        print("=" * 70)

        # Initialize state as dictionary (LangGraph requirement)
        initial_state: SupportOpsState = {
            "incident": scenario["incident"],
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

        config = RunnableConfig(
            configurable={"thread_id": scenario["incident"].incident_id}
        )

        step_count = 0
        start_time = datetime.now()

        try:
            async for step in app.astream(initial_state, config):
                step_count += 1
                agent_name = list(step.keys())[0]
                state_update = step[agent_name]

                print(
                    f"🤖 Step {step_count}: {agent_name.upper().replace('_', ' ').replace('-', ' ')}"
                )
                print(f"📊 Status: {state_update.get('workflow_status', 'unknown')}")
                print(f"🔄 Current Agent: {state_update.get('current_agent', 'none')}")

                # Show GPT classification results
                if state_update.get("incident_classification"):
                    classification = state_update["incident_classification"]
                    if classification.get("classification_method") == "autonomous_gpt4":
                        print(f"🧠 GPT Classification:")
                        print(
                            f"   📂 Category: {classification.get('incident_category', 'Unknown')}"
                        )
                        print(
                            f"   🎯 Confidence: {classification.get('confidence_score', 0):.2f}"
                        )
                        print(
                            f"   ⚡ Urgency: {classification.get('urgency_level', 'Unknown')}"
                        )
                        print(
                            f"   🏥 Business Impact: {classification.get('business_impact_assessment', 'Unknown')}"
                        )
                        print(
                            f"   ⏱️  ETA: {classification.get('estimated_resolution_time', 'Unknown')}"
                        )
                        if classification.get("reasoning"):
                            print(
                                f"   🤔 Reasoning: {classification['reasoning'][:80]}..."
                            )

                # Show GPT analysis results
                if state_update.get("specialist_findings"):
                    for finding_type, finding_data in state_update[
                        "specialist_findings"
                    ].items():
                        if isinstance(finding_data, dict):
                            # Check for GPT analysis
                            if (
                                finding_data.get("analysis_method") == "autonomous_gpt4"
                                and "gpt_analysis" in finding_data
                            ):
                                gpt_analysis = finding_data["gpt_analysis"]
                                print(
                                    f"🔍 GPT {finding_type.replace('_', ' ').title()}:"
                                )
                                print(f"   🚨 Issues: {gpt_analysis.get('issues', [])}")
                                print(
                                    f"   🎯 Confidence: {gpt_analysis.get('confidence_score', 0):.2f}"
                                )
                                print(
                                    f"   ⚡ Severity: {gpt_analysis.get('severity', 'unknown')}"
                                )
                                print(
                                    f"   💡 Actions: {gpt_analysis.get('recommended_actions', [])}"
                                )
                                if gpt_analysis.get("reasoning"):
                                    print(
                                        f"   🤔 Reasoning: {gpt_analysis['reasoning'][:80]}..."
                                    )
                            elif "analysis_result" in finding_data:
                                # Fallback analysis
                                analysis = finding_data["analysis_result"]
                                print(f"🔍 {finding_type.replace('_', ' ').title()}:")
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
                                    print(
                                        f"   🚨 Issues: {analysis.get(issues_key, [])}"
                                    )
                                print(
                                    f"   💡 Actions: {analysis.get('recommended_actions', [])}"
                                )

                # Show GPT remediation planning
                if state_update.get("remediation_plan"):
                    plan = state_update["remediation_plan"]
                    if plan.get("plan_method") == "autonomous_gpt4":
                        print(f"📋 GPT Remediation Plan:")
                        print(f"   🎯 Primary Actions: {plan.get('actions', [])}")
                        print(
                            f"   🔄 Secondary Actions: {plan.get('secondary_actions', [])}"
                        )
                        print(
                            f"   ⚠️  Risk Assessment: {plan.get('risk_assessment', 'Unknown')}"
                        )
                        print(
                            f"   ⏱️  Duration: {plan.get('estimated_duration', 'Unknown')}"
                        )
                        print(
                            f"   ✅ Approval Required: {plan.get('requires_approval', False)}"
                        )
                        if plan.get("reasoning"):
                            print(f"   🤔 Reasoning: {plan['reasoning'][:80]}...")

                # Show execution results
                if state_update.get("execution_results"):
                    print(f"⚡ Execution Results:")
                    for action, result in state_update["execution_results"].items():
                        if isinstance(result, dict):
                            status = result.get("status", "Unknown")
                            print(f"   ✅ {action.replace('_', ' ').title()}: {status}")
                        else:
                            print(
                                f"   ✅ {action.replace('_', ' ').title()}: {str(result)}"
                            )

                print("-" * 50)

                if step_count > 8:  # Safety check
                    break

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback

            traceback.print_exc()

        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()

        print(f"✅ Scenario {i} Complete!")
        print(f"⏱️  Total Time: {total_time:.1f}s")
        print(f"🔄 Steps Executed: {step_count}")

        if i < len(test_scenarios):
            print(f"\n{'='*20} Moving to Next Scenario {'='*20}")


def start_api_server():
    """Start the API server"""
    import uvicorn

    print("🌐 Starting SupportOps API Server...")
    print("📡 API Documentation: http://localhost:8000/docs")
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)


async def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        start_api_server()
    else:
        await run_autonomous_test_scenarios()


if __name__ == "__main__":
    asyncio.run(main())
