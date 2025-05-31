from langchain_core.tools import tool
from typing import Dict, List, Any
from datetime import datetime

@tool
def cloudwatch_metrics_collector(aws_regions: List[str], service_namespaces: List[str], metric_filters: List[str]) -> Dict[str, Any]:
    """Gathers AWS service metrics from CloudWatch"""
    return {
        "cloudwatch_metrics": {
            "ec2_instances": {
                "i-1234567890": {"CPUUtilization": 78.5, "NetworkIn": 1250000},
                "i-0987654321": {"CPUUtilization": 45.2, "NetworkOut": 850000}
            },
            "rds_instances": {
                "db-prod-01": {"DatabaseConnections": 45, "ReadLatency": 0.002}
            }
        },
        "service_health_data": {"ec2": "healthy", "rds": "healthy", "elb": "degraded"},
        "cost_metrics": {"daily_spend_usd": 245.67, "monthly_projection_usd": 7370.10}
    }

@tool
def aws_systems_manager_interface(instance_ids: List[str], command_documents: List[str], execution_parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Executes commands on EC2 instances via SSM"""
    return {
        "command_execution_results": {
            instance_id: {
                "status": "success",
                "output": f"Command executed on {instance_id}",
                "exit_code": 0
            }
            for instance_id in instance_ids
        },
        "instance_status": {instance_id: "online" for instance_id in instance_ids},
        "system_information": {"platform": "linux", "agent_version": "3.1.1"}
    }