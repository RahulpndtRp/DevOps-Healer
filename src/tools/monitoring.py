"""Monitoring system integration tools"""
from langchain_core.tools import tool
from typing import Dict, List, Any
from datetime import datetime

@tool
def prometheus_metrics_collector(target_hosts: List[str], metric_queries: List[str], time_range: str) -> Dict[str, Any]:
    """Queries CPU and memory metrics from Prometheus"""
    return {
        "cpu_metrics": {
            host: {
                "current_utilization": 85.5 if "high" in host else 45.2,
                "avg_utilization_1h": 78.3,
                "peak_utilization_24h": 92.1
            }
            for host in target_hosts
        },
        "memory_metrics": {
            host: {
                "current_utilization": 89.1 if "high" in host else 52.3,
                "available_memory_gb": 2.1 if "high" in host else 15.7,
                "memory_pressure": "high" if "high" in host else "normal"
            }
            for host in target_hosts
        },
        "query_timestamp": datetime.now().isoformat()
    }

@tool
def disk_usage_analyzer(server_hostnames: List[str], filesystem_paths: List[str]) -> Dict[str, Any]:
    """Analyzes disk space utilization across filesystems"""
    return {
        "disk_usage_metrics": {
            host: {
                "/": {"used_percent": 87, "available_gb": 2.1, "total_gb": 20},
                "/var/log": {"used_percent": 92, "available_gb": 0.8, "total_gb": 10},
                "/tmp": {"used_percent": 45, "available_gb": 5.5, "total_gb": 10}
            }
            for host in server_hostnames
        },
        "filesystem_health": "degraded",
        "capacity_trends": {"growth_rate_gb_per_day": 0.3}
    }

@tool
def network_connectivity_tester(target_hosts: List[str], test_protocols: List[str]) -> Dict[str, Any]:
    """Tests network connectivity and latency"""
    return {
        "connectivity_status": {
            host: {
                "ping_success": True,
                "avg_latency_ms": 12.3,
                "packet_loss_percent": 0.1,
                "tcp_connect_time_ms": 45.2
            }
            for host in target_hosts
        },
        "latency_measurements": {"p50": 10.2, "p95": 25.1, "p99": 67.3},
        "packet_loss_data": {"total_packets": 1000, "lost_packets": 1}
    }