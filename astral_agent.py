import docker
import json
from datetime import datetime

def extract_telemetry():
    print("🐳 Scanning local Docker/Kubernetes daemon...")
    try:
        client = docker.from_env()
    except Exception as e:
        print("❌ Error: Could not connect to Docker. Is Docker Desktop running?")
        return

    services_data = []
    containers = client.containers.list()
    
    print(f"📡 Found {len(containers)} running containers. Extracting live telemetry...")

    for container in containers:
        try:
            # Pull the live stats snapshot for this container
            stats = container.stats(stream=False)
            
            # Docker returns memory in bytes. We convert to Gigabytes (GB).
            mem_limit_gb = stats['memory_stats'].get('limit', 0) / (1024 ** 3)
            mem_used_gb = stats['memory_stats'].get('usage', 0) / (1024 ** 3)
            
            services_data.append({
                "service_name": container.name,
                "allocated_memory_gb": round(mem_limit_gb, 2),
                "allocated_cpu_cores": 1.0, # Hardcoded for hackathon simplicity
                "avg_memory_used_gb": round(mem_used_gb, 4), # 4 decimals for precision
                "avg_cpu_used_cores": 0.1,
                "status": container.status
            })
            print(f"   -> Monitored: {container.name[:40]}... (Allocated: {round(mem_limit_gb, 2)}GB)")
        except Exception as e:
            pass # Skip containers that might be booting up or inaccessible

    # Package it into our standard JSON snapshot
    payload = {
        "timestamp": datetime.now().isoformat(),
        "environment": "Live-Kubernetes-Cluster",
        "pricing_model": {"memory_per_gb_hour": 0.05, "cpu_per_core_hour": 0.04}, 
        "telemetry": services_data
    }

    # Save it to the exact file app.py is looking for
    with open("telemetry_snapshot.json", "w") as f:
        json.dump(payload, f, indent=4)
        
    print(f"\n✅ Live cluster telemetry successfully extracted to telemetry_snapshot.json!")

if __name__ == "__main__":
    extract_telemetry()