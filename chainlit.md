# 🤖 DevOps Healer - Interactive Web Interface

Welcome to the **DevOps Healer** - your autonomous DevOps incident response assistant!

## 🚀 Quick Start

### Report an Incident

You can report incidents in multiple ways:

#### 🗣️ **Natural Language** (Recommended)
Just describe your problem naturally:

```
Our production database is running extremely slow. Customers are complaining about timeouts during checkout. The connection pool seems to be exhausted and we're seeing a lot of blocking queries.
```

#### 📊 **Structured JSON** (Advanced)
For precise control:

```json
{
  "severity": "critical",
  "category": "database_performance",
  "description": "Database connection pool exhaustion causing customer-facing timeouts",
  "affected_systems": ["prod-db-cluster-01", "app-server-tier", "load-balancer"],
  "symptoms": [
    "Connection pool at 98% utilization",
    "Average query response time: 5000ms", 
    "Customer checkout failures",
    "Database CPU at 95%"
  ],
  "metadata": {
    "alert_source": "datadog",
    "affected_users": 15000,
    "sla_breach_risk": "high"
  }
}
```

## 🎯 Incident Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `cpu_utilization` | CPU performance & capacity | High load, throttling |
| `memory_utilization` | Memory leaks & allocation | OOM errors, memory pressure |
| `disk_utilization` | Storage capacity & I/O | Disk full, slow I/O |
| `network_connectivity` | Network routing & latency | Packet loss, high latency |
| `database_performance` | DB slowness & locks | Slow queries, deadlocks |
| `application_performance` | App-level issues | API timeouts, errors |
| `security_incident` | Security breaches | Unauthorized access |
| `backup_failure` | Backup & recovery | Failed backups, corruption |

## 🔥 Severity Levels

- **🔴 CRITICAL**: System down, revenue impact
- **🟠 HIGH**: Significant performance degradation  
- **🟡 MEDIUM**: Moderate issues, some user impact
- **🟢 LOW**: Minor issues, minimal impact

## 🧠 AI Capabilities

### **Autonomous Classification**
- GPT-4 powered incident categorization
- Business impact assessment
- Urgency level determination

### **Intelligent Analysis** 
- Root cause investigation
- Cross-system correlation
- Historical pattern matching

### **Smart Remediation**
- Risk-aware action planning
- Primary & fallback strategies
- Approval workflow integration

## 📝 Example Incidents

Try these examples to see the system in action:

### Database Crisis
```
CRITICAL: Production database cluster showing severe performance degradation. Connection timeouts affecting 15,000 users. Revenue impact estimated at $10k/hour.
```

### Storage Emergency  
```
Disk space critical on prod-db-01. Transaction logs at 97% capacity. Automated cleanup failing for 3 days. Risk of database shutdown in 4 hours.
```

### Network Issues
```
HIGH: Intermittent connectivity between US-East and EU-West regions. 15% packet loss on primary link. WebRTC calls dropping. Failover not triggering.
```

## 🛠️ Advanced Features

- **Real-time Analysis**: Live updates as the AI works
- **Confidence Scoring**: AI shows confidence in decisions
- **Reasoning Trails**: Detailed explanation of decisions
- **Business Context**: Considers SLA and business impact
- **Approval Workflows**: Human oversight for risky actions

Start by describing your incident above! 👆