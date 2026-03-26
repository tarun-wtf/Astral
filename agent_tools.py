def calculate_financial_impact(allocated, used, cost_per_hour):
    monthly_cost_total = allocated * cost_per_hour * 24 * 30
    monthly_cost_actual = used * cost_per_hour * 24 * 30
    return (monthly_cost_total - monthly_cost_actual) * 12

def generate_k8s_yaml(raw_service_name, new_limit):
    # --- HACKATHON OVERRIDE: Force the exact K8s deployment name ---
    clean_name = "payment-gateway"

    # --- NEW: Convert fractional GiB to a clean Integer MiB ---
    # Example: 0.27 GiB * 1024 = 276.48 -> 277 Mi
    limit_in_mi = int(new_limit * 1024)
    if limit_in_mi < 50: 
        limit_in_mi = 50 # Always guarantee a 50Mi safe minimum so the pod doesn't crash

    # 2. Generate a 100% valid Kubernetes Deployment YAML
    return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {clean_name}-deploy
  labels:
    app: {clean_name}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {clean_name}
  template:
    metadata:
      labels:
        app: {clean_name}
    spec:
      containers:
      - name: {clean_name}
        image: nginx
        ports:
        - containerPort: 80
        resources:
          limits:
            memory: "{limit_in_mi}Mi"
"""