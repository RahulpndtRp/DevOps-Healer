"""Infrastructure management tools"""
from langchain_core.tools import tool
from typing import Dict, List, Any

@tool
def ssh_system_analyzer(server_hostnames: List[str], analysis_commands: List[str]) -> Dict[str, Any]:
    """Executes system commands for detailed analysis via SSH"""
    return {
        "command_outputs": {
            "top": "Tasks: 245 total, 2 running, 243 sleeping",
            "df -h": "/dev/sda1 85% /var/log",
            "netstat -tuln": "Active connections: 1247"
        },
        "process_information": {
            "high_cpu_processes": [
                {"pid": 1234, "command": "java -Xmx4g", "cpu_percent": 45.2}
            ],
            "high_memory_processes": [
                {"pid": 5678, "command": "elasticsearch", "memory_percent": 35.1}
            ]
        },
        "system_status": {
            "load_average": [2.1, 1.8, 1.5],
            "uptime": "15 days, 4:32",
            "disk_io_wait": 12.3
        }
    }

@tool
def storage_cleanup_engine(cleanup_parameters: Dict[str, Any], safety_thresholds: Dict[str, Any]) -> Dict[str, Any]:
    """Performs automated storage cleanup and optimization"""
    return {
        "cleanup_results": {
            "log_rotation": {"space_freed_gb": 2.3, "files_rotated": 145},
            "temp_file_removal": {"space_freed_gb": 0.8, "files_removed": 892},
            "cache_cleanup": {"space_freed_gb": 1.2, "cache_cleared": ["browser", "app"]}
        },
        "space_recovered": 4.3,
        "safety_confirmations": {
            "backup_verified": True,
            "critical_files_preserved": True,
            "rollback_available": True
        }
    }

@tool
def cmdb_enrichment_tool(incident_id: str, server_hostname: str, alert_details: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieves application context and business impact data from ServiceNow CMDB"""
    return {
        "application_context": {
            "application_name": f"App-{server_hostname}",
            "business_service": "Customer Portal",
            "environment": "production"
        },
        "business_criticality": "high" if "prod" in server_hostname.lower() else "medium",
        "service_dependencies": [
            {"service": "database-cluster", "criticality": "high"},
            {"service": "auth-service", "criticality": "medium"}
        ],
        "user_impact_data": {
            "affected_users": 1500 if "prod" in server_hostname.lower() else 50,
            "revenue_impact": "high"
        }
    }