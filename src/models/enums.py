"""Core enumerations for the SupportOps framework"""
from enum import Enum

class IncidentSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AgentType(Enum):
    TRIBE = "tribe"
    SQUAD = "squad"
    SPECIALIST = "specialist"

class IncidentCategory(Enum):
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    DISK_UTILIZATION = "disk_utilization"
    NETWORK_CONNECTIVITY = "network_connectivity"
    DATABASE_PERFORMANCE = "database_performance"
    APPLICATION_PERFORMANCE = "application_performance"
    SECURITY_INCIDENT = "security_incident"
    BACKUP_FAILURE = "backup_failure"

class WorkflowStatus(Enum):
    INITIALIZED = "initialized"
    IN_PROGRESS = "in_progress"
    ANALYSIS_COMPLETE = "analysis_complete"
    COMPLETED = "completed"
    FAILED = "failed"

class CompletionStatus(Enum):
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    FAILED = "failed"


class SpecialistType(Enum):
    COMPUTE_MONITOR = "compute-monitor"
    DISK_MONITOR = "disk-monitor"
    NETWORK_MONITOR = "network-monitor"
    BACKUP_MONITOR = "backup-monitor"
    VMWARE_MONITOR = "vmware-monitor"
    AWS_MONITOR = "aws-monitor"
    KUBERNETES_MONITOR = "kubernetes-monitor"
    DATABASE_PERFORMANCE_MONITOR = "database-performance-monitor"
    APPLICATION_PERFORMANCE_MONITOR = "application-performance-monitor"
    SECURITY_MONITOR = "security-monitor"
    LOG_COLLECTOR = "log-collector"
    HISTORICAL_METRIC_SPECIALIST = "historical-metric-specialist"
    
    # Response Specialists
    COMPUTE_RESOURCE_SPECIALIST = "compute-resource-specialist"
    STORAGE_RESPONSE_SPECIALIST = "storage-response-specialist"
    NETWORK_RESPONSE_SPECIALIST = "network-response-specialist"
    APPLICATION_RESPONSE_SPECIALIST = "application-response-specialist"
    DATABASE_RESPONSE_SPECIALIST = "database-response-specialist"
    SECURITY_RESPONSE_SPECIALIST = "security-response-specialist"
    
    # Knowledge Specialists
    DOCUMENTATION_SPECIALIST = "documentation-specialist"
    TRAINING_SPECIALIST = "training-specialist"
    PROCESS_IMPROVEMENT_SPECIALIST = "process-improvement-specialist"
