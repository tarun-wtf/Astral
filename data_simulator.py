import json
import random
from datetime import datetime

def generate_telemetry():
    # 1. The Enterprise Pricing Sheet (What things cost per hour)
    # This is crucial for your "quantifiable financial impact" evaluation.
    pricing = {
        "memory_per_gb_hour": 0.05, 
        "cpu_per_core_hour": 0.04   
    }

    # 2. The Microservices Status (Simulating Kubernetes/Docker containers)
    services = [
        {
            "service_name": "AuthService",
            "allocated_memory_gb": 2.0,
            "allocated_cpu_cores": 1.0,
            "avg_memory_used_gb": round(random.uniform(1.5, 1.8), 2), # Healthy usage
            "avg_cpu_used_cores": round(random.uniform(0.6, 0.9), 2),
            "status": "Healthy"
        },
        {
            "service_name": "CartService",
            "allocated_memory_gb": 4.0,
            "allocated_cpu_cores": 2.0,
            "avg_memory_used_gb": round(random.uniform(2.8, 3.5), 2), # Healthy usage
            "avg_cpu_used_cores": round(random.uniform(1.2, 1.8), 2),
            "status": "Healthy"
        },
        # 3. THE TRAP: This is the anomaly your AI agent needs to find.
        # Allocated 16GB, but only using ~1.2GB. Massive cost leakage.
        {
            "service_name": "PaymentGateway",
            "allocated_memory_gb": 16.0,
            "allocated_cpu_cores": 4.0,
            "avg_memory_used_gb": round(random.uniform(0.8, 1.2), 2), # Unhealthy/Bloated
            "avg_cpu_used_cores": round(random.uniform(0.2, 0.5), 2),
            "status": "Running" 
        }
    ]

    # Combine into a single snapshot
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "environment": "Production-Cluster-A",
        "pricing_model": pricing,
        "telemetry": services
    }

    # Save it to a JSON file so our AI backend can read it later
    with open("telemetry_snapshot.json", "w") as f:
        json.dump(snapshot, f, indent=4)
    
    print("✅ Mock telemetry data generated successfully: 'telemetry_snapshot.json'")
    return snapshot

if __name__ == "__main__":
    generate_telemetry()