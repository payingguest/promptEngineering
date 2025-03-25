from datetime import datetime, timedelta
import json
from typing import List, Dict, Any

# ------------------------------
# 1. Dependency Graph Configuration
# ------------------------------
DEPENDENCY_GRAPH = {
    "abdcd": {
        "type": "application_server",
        "dependencies": ["mysql-cluster", "vpc-123"],
        "hostname": "abdcd"
    },
    "mysql-cluster": {
        "type": "database",
        "dependencies": ["vpc-123", "ebs-xyz"],
        "hostname": "db-primary-01"
    },
    "vpc-123": {
        "type": "network",
        "dependencies": ["igw-789"],
        "hostname": "vpc-us-east-1a"
    },
    "ebs-xyz": {
        "type": "storage",
        "dependencies": [],
        "hostname": "ebs-volume-4455"
    },
    "igw-789": {
        "type": "gateway",
        "dependencies": [],
        "hostname": "internet-gw-789"
    }
}

# ------------------------------
# 2. Sample Logs (All Systems)
# ------------------------------
LOGS = {
    "network": [
        '2023-10-05T14:25:00Z INFO [vpc-123] Gateway "igw-789" latency: 120ms',
        '2023-10-05T14:28:00Z ERROR [vpc-123] Gateway latency spike: 620ms',
        '2023-10-05T14:30:00Z WARN [vpc-123] DNS resolution delayed by 1500ms',
        '2023-10-05T14:32:00Z INFO [vpc-123] Latency restored: 110ms'
    ],
    "database": [
        '2023-10-05T14:25:00Z WARN [mysql-cluster] Slow query: 2200ms',
        '2023-10-05T14:28:30Z ERROR [mysql-cluster] Connection pool exhausted',
        '2023-10-05T14:29:00Z WARN [mysql-cluster] Deadlock detected',
        '2023-10-05T14:31:00Z INFO [mysql-cluster] High connections: 180'
    ],
    "application": [
        '2023-10-05T14:27:00Z INFO [abdcd] Started cron job "nightly_backup"',
        '2023-10-05T14:28:00Z ERROR [abdcd] API timeout: /checkout',
        '2023-10-05T14:30:00Z CRITICAL [abdcd] CPU: 95%'
    ],
    "storage": [
        '2023-10-05T14:28:00Z WARN [ebs-xyz] Write IOPS spike: 4500',
        '2023-10-05T14:30:00Z ERROR [ebs-xyz] Disk queue depth: 8'
    ]
}

# ------------------------------
# 3. Historical Incident Data
# ------------------------------
HISTORICAL_INCIDENTS = [
    {
        "incident_id": "INC-001",
        "summary": "High CPU due to DB deadlocks",
        "timestamp": "2023-07-12T09:45:00Z",
        "hostname": "abdcd",
        "root_cause": "Database deadlocks from unoptimized queries",
        "resolution": "Query optimization + connection pool increase"
    },
    {
        "incident_id": "INC-002",
        "summary": "Network latency spike",
        "timestamp": "2023-08-20T14:15:00Z",
        "hostname": "vpc-us-east-1a",
        "root_cause": "Misconfigured gateway",
        "resolution": "Gateway config rollback"
    }
]

# ------------------------------
# 4. Log Parser Functions
# ------------------------------
def parse_log_entry(log: str) -> Dict[str, Any]:
    """Parse raw log entry into structured format"""
    parts = log.split(' ', 4)
    return {
        "timestamp": datetime.fromisoformat(parts[0].replace('Z', '+00:00')),
        "level": parts[1],
        "component": parts[2].strip('[]'),
        "message": parts[4].strip()
    }

def get_relevant_logs(component: str, start_time: datetime, end_time: datetime) -> List[dict]:
    """Retrieve logs for a component within time window"""
    log_type = "database" if "mysql" in component else \
               "network" if "vpc" in component else \
               "application" if "abdcd" in component else \
               "storage"
    
    return [parse_log_entry(log) for log in LOGS[log_type]
            if start_time <= parse_log_entry(log)['timestamp'] <= end_time]

# ------------------------------
# 5. Dependency Health Checker
# ------------------------------
def check_dependency_health(node: str, anomaly_time: datetime) -> Dict[str, Any]:
    """Check health status of a node and its dependencies"""
    window_start = anomaly_time - timedelta(minutes=5)
    window_end = anomaly_time + timedelta(minutes=5)
    
    return {
        "node": node,
        "status": "unhealthy" if any(
            log["level"] in ["ERROR", "CRITICAL"]
            for log in get_relevant_logs(node, window_start, window_end)
        ) else "healthy",
        "logs": get_relevant_logs(node, window_start, window_end),
        "dependencies": DEPENDENCY_GRAPH[node]["dependencies"]
    }

# ------------------------------
# 6. Historical Incident Matcher
# ------------------------------
def find_similar_incidents(hostname: str, anomaly_time: datetime) -> List[dict]:
    """Find historically similar incidents"""
    return [
        incident for incident in HISTORICAL_INCIDENTS
        if incident["hostname"] == hostname
        and abs(datetime.fromisoformat(incident["timestamp"]) - anomaly_time) < timedelta(hours=24)
    ]

# ------------------------------
# 7. Topological RCA Engine
# ------------------------------
def perform_rca(root_node: str, anomaly_time: datetime) -> Dict[str, Any]:
    """Main RCA execution with dependency traversal"""
    results = []
    visited = set()
    
    def traverse(node: str):
        if node in visited:
            return
        visited.add(node)
        
        health = check_dependency_health(node, anomaly_time)
        results.append(health)
        
        for dependency in health["dependencies"]:
            traverse(dependency)
    
    traverse(root_node)
    
    # Find historical matches for root node
    hostname = DEPENDENCY_GRAPH[root_node]["hostname"]
    historical_matches = find_similar_incidents(hostname, anomaly_time)
    
    return {
        "root_causes": [r for r in results if r["status"] == "unhealthy"],
        "historical_matches": historical_matches,
        "dependency_chain": list(visited)
    }

# ------------------------------
# 8. Execution & Output Formatting
# ------------------------------
if __name__ == "__main__":
    # Simulate detected anomaly
    anomaly = {
        "node": "abdcd",
        "metric": "CPU",
        "value": 95,
        "timestamp": "2023-10-05T14:30:00Z"
    }
    
    # Execute RCA
    rca_results = perform_rca(
        root_node=anomaly["node"],
        anomaly_time=datetime.fromisoformat(anomaly["timestamp"])
    )
    
    # Format output
    final_output = {
        "anomaly": anomaly,
        "analysis": {
            "root_causes": [
                {
                    "component": rc["node"],
                    "hostname": DEPENDENCY_GRAPH[rc["node"]]["hostname"],
                    "status": rc["status"],
                    "evidence": [log["message"] for log in rc["logs"] if log["level"] in ["ERROR", "WARN"]]
                } for rc in rca_results["root_causes"]
            ],
            "historical_similar_incidents": rca_results["historical_matches"],
            "dependency_traversal_path": rca_results["dependency_chain"]
        }
    }
    
    print(json.dumps(final_output, indent=2, default=str))
