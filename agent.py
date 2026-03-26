import json
from groq import Groq
import os
from dotenv import load_dotenv
from agent_tools import calculate_financial_impact, generate_k8s_yaml

# 1. Initialize the AI Client
# Replace this string with your actual Groq API key
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY")) 

def run_finops_agent():
    print("🤖 Waking up AI Agent...")
    
    # 2. Read the telemetry data we generated in Phase 1
    try:
        with open("telemetry_snapshot.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Error: Run data_simulator.py first to generate the data!")
        return

    print("📡 Reading microservice telemetry data...")

    # 3. Prompt the AI
    # We ask the AI to act as an SRE and return a strict JSON response 
    # so our Python code can easily read its decision.
    prompt = f"""
    You are an autonomous FinOps Agent. Review the following JSON telemetry data:
    {json.dumps(data)}
    
    Find the one service that is massively over-provisioned (allocated memory is much higher than used memory).
    
    Respond ONLY with a valid JSON object in this exact format, with no other text:
    {{"service_name": "NameOfService", "allocated_gb": 0.0, "used_gb": 0.0}}
    """

    print("🧠 Analyzing anomalies using Llama-3 on Groq...")
    
    # Send the data to Groq
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant", # The upgraded Llama 3.1 model, # This model is lightning fast and great at JSON
        response_format={"type": "json_object"}, # Forces the AI to return perfect JSON
    )

    # 4. Parse the AI's answer
    ai_decision = json.loads(response.choices[0].message.content)
    target_service = ai_decision["service_name"]
    allocated = float(ai_decision["allocated_gb"])
    used = float(ai_decision["used_gb"])
    
    # Get the cost from our mock data
    cost_per_hour = data["pricing_model"]["memory_per_gb_hour"]

    print(f"\n🚨 ANOMALY DETECTED BY AI: '{target_service}'")
    print(f"   -> Allocated: {allocated}GB | Actually Using: {used}GB")

    # 5. Trigger our Python Tools
    # The AI found the target, now we use our tools to do the exact math and write the fix.
    money_saved = calculate_financial_impact(allocated, used, cost_per_hour)
    new_limit = round(used * 1.2, 1) # Give it a 20% safety buffer
    fix_code = generate_k8s_yaml(target_service, new_limit)

    # 6. The Final Output (What the UI will show)
    print(f"\n💰 QUANTIFIABLE FINANCIAL IMPACT:")
    print(f"   -> Shrinking this container will save you ${money_saved} per year.")
    
    print(f"\n🛠️ ACTIONABLE PLAYBOOK GENERATED:")
    print(f"   -> Ready to deploy new Kubernetes configuration:")
    print(fix_code)
    print("⏳ STATUS: PENDING HUMAN APPROVAL")

if __name__ == "__main__":
    run_finops_agent()