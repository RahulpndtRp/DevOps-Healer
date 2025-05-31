"""Main workflow graph construction"""

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from ..models.state import SupportOpsState
from ..agents.tribe.orchestrator import TribeOrchestrator
from ..agents.squads.diagnostics import DiagnosticsSquad
from ..agents.squads.response import ResponseSquad
from ..agents.specialists.compute import ComputeMonitorSpecialist
from ..agents.specialists.disk import DiskMonitorSpecialist
from ..agents.specialists.network import NetworkMonitorSpecialist
from ..agents.specialists.database import DatabasePerformanceSpecialist
from ..agents.specialists.response import ComputeResourceSpecialist


def create_supportops_workflow():
    """Create the complete SupportOps workflow graph with all specialists"""

    # Initialize all agents
    tribe_orchestrator = TribeOrchestrator()
    diagnostics_squad = DiagnosticsSquad()
    response_squad = ResponseSquad()

    # Initialize all monitoring specialists
    compute_monitor = ComputeMonitorSpecialist()
    disk_monitor = DiskMonitorSpecialist()
    network_monitor = NetworkMonitorSpecialist()
    database_monitor = DatabasePerformanceSpecialist()

    # Initialize response specialists
    compute_resource_specialist = ComputeResourceSpecialist()

    # Import additional response specialists
    try:
        from ..agents.specialists.storage_response import StorageResponseSpecialist
        from ..agents.specialists.database_response import DatabaseResponseSpecialist
        from ..agents.specialists.network_response import NetworkResponseSpecialist

        storage_response_specialist = StorageResponseSpecialist()
        database_response_specialist = DatabaseResponseSpecialist()
        network_response_specialist = NetworkResponseSpecialist()

        additional_specialists = {
            "storage-response-specialist": storage_response_specialist.execute,
            "database-response-specialist": database_response_specialist.execute,
            "network-response-specialist": network_response_specialist.execute,
        }
    except ImportError as e:
        print(f"⚠️ Additional response specialists not found: {e}")
        additional_specialists = {}

    # Create workflow graph
    workflow = StateGraph(SupportOpsState)

    # Add all nodes
    workflow.add_node("tribe_orchestrator", tribe_orchestrator.execute)
    workflow.add_node("diagnostics-squad", diagnostics_squad.execute)
    workflow.add_node("response-squad", response_squad.execute)

    # Add specialist nodes
    workflow.add_node("compute-monitor", compute_monitor.execute)
    workflow.add_node("disk-monitor", disk_monitor.execute)
    workflow.add_node("network-monitor", network_monitor.execute)
    workflow.add_node("database-performance-monitor", database_monitor.execute)

    # Add response specialist nodes
    workflow.add_node(
        "compute-resource-specialist", compute_resource_specialist.execute
    )

    # Add additional response specialists if available
    for specialist_name, specialist_func in additional_specialists.items():
        workflow.add_node(specialist_name, specialist_func)

    # Enhanced routing functions with debug
    def route_from_tribe(state: SupportOpsState) -> str:
        next_agent = state.get("current_agent", "diagnostics-squad")
        print(f"🔀 Tribe routing to: {next_agent}")
        return next_agent

    def route_from_diagnostics(state: SupportOpsState) -> str:
        next_agent = state.get("current_agent", "compute-monitor")
        print(f"🔀 Diagnostics routing to: {next_agent}")
        return next_agent

    def route_from_specialist(state: SupportOpsState) -> str:
        workflow_status = state.get("workflow_status", "")
        next_agent = state.get("current_agent", "response-squad")

        print(f"🔀 Specialist routing - Status: {workflow_status}, Next: {next_agent}")

        if workflow_status.endswith("_complete"):
            return END
        elif next_agent == "response-squad" or state.get("specialist_findings"):
            return "response-squad"
        else:
            return next_agent

    def route_from_response(state: SupportOpsState) -> str:
        next_agent = state.get("current_agent", "compute-resource-specialist")
        print(f"🔀 Response routing to: {next_agent}")
        return next_agent

    def route_from_remediation(state: SupportOpsState) -> str:
        completion_status = state.get("completion_status", "")
        print(f"🔀 Remediation routing - Status: {completion_status}")

        if completion_status == "resolved":
            return END
        else:
            return END

    # Add edges with enhanced routing
    workflow.add_edge(START, "tribe_orchestrator")
    workflow.add_conditional_edges("tribe_orchestrator", route_from_tribe)
    workflow.add_conditional_edges("diagnostics-squad", route_from_diagnostics)

    # Add edges for all specialists
    workflow.add_conditional_edges("compute-monitor", route_from_specialist)
    workflow.add_conditional_edges("disk-monitor", route_from_specialist)
    workflow.add_conditional_edges("network-monitor", route_from_specialist)
    workflow.add_conditional_edges(
        "database-performance-monitor", route_from_specialist
    )

    workflow.add_conditional_edges("response-squad", route_from_response)
    workflow.add_conditional_edges(
        "compute-resource-specialist", route_from_remediation
    )

    # Add edges for additional response specialists
    for specialist_name in additional_specialists.keys():
        workflow.add_conditional_edges(specialist_name, route_from_remediation)

    # Set up checkpointer
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)
