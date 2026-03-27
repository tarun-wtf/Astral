import streamlit as st
import json
import time
import os
from dotenv import load_dotenv
from groq import Groq
from agent_tools import calculate_financial_impact, generate_k8s_yaml

# --- 1. SETUP & SECURITY ---
# Load the secret variables from the .env file
load_dotenv()

# Initialize Groq client using the hidden environment variable
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Astral SRE", page_icon="✨", layout="wide", initial_sidebar_state="collapsed")
# --- UI TWEAKS: HIDE STREAMLIT BRANDING & MENUS ---
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;} /* Hides the hamburger menu */
header {visibility: hidden;} /* Hides the top header bar and Deploy button */
footer {visibility: hidden;} /* Hides the 'Made with Streamlit' footer */
.stDeployButton {display:none;} /* Extra rule to guarantee Deploy button is gone */
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ... (Keep the rest of your app.py code exactly the same!) ...

# --- INITIALIZE AI MEMORY (SESSION STATE) ---
if "scan_complete" not in st.session_state:
    st.session_state.scan_complete = False
if "ai_data" not in st.session_state:
    st.session_state.ai_data = {}

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #e6edf3; font-family: 'Courier New', Courier, monospace; }
    .stButton>button { border: 1px solid #79c0ff; background-color: #1f6feb; color: #ffffff; font-weight: bold; transition: all 0.3s ease-in-out; }
    .stButton>button:hover { background-color: #388bfd; box-shadow: 0 0 15px #388bfd; }
    [data-testid="stMetricValue"] { color: #79c0ff; font-family: 'Courier New', monospace; }
    .terminal-box { background-color: #010409; border: 1px solid #30363d; border-radius: 5px; padding: 15px; color: #79c0ff; font-family: monospace; height: 200px; overflow-y: auto; }
    .streamlit-expanderHeader { font-weight: bold; color: #58a6ff; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.markdown("<h1>✨</h1>", unsafe_allow_html=True) 
with col_title:
    st.title("ASTRAL: Cloud Infrastructure Intelligence")
    st.markdown("`[Engine: Kubernetes / Docker Daemon] | [Architecture: Containerized Microservices] | Status: Online`")

st.divider()

# --- PRE-SCAN INTERACTIVE TOPOLOGY MAP ---
st.subheader("🕸️ Live Cluster Topology")
target_cluster = st.selectbox("Select Target Network Mesh:", ["All Clusters (Global Scan)", "US-East-1 (Microservices)", "EU-Central (Databases)"])

rack1, rack2, rack3, rack4 = st.columns(4)
with rack1:
    with st.container(border=True): st.markdown("🟢 **[Pod] AuthService**\n\n`Engine: K8s | Load: 42%`")
with rack2:
    with st.container(border=True): st.markdown("🟢 **[Pod] CartAPI**\n\n`Engine: K8s | Load: 68%`")
with rack3:
    with st.container(border=True): st.markdown("🟡 **[Pod] RecommendationDB**\n\n`Engine: K8s | Load: 85%`")
with rack4:
    with st.container(border=True): st.markdown("🔴 **[Pod] PaymentGateway**\n\n`Engine: K8s | Load: 2%`")

st.write("") 

# --- THE ENTERPRISE DROPZONE ---
st.markdown("### 📥 Telemetry Ingestion")
uploaded_file = st.file_uploader("Upload external cluster telemetry (JSON) or leave blank to use the internal live demo data:", type=["json"])

# --- THE AGENT TRIGGER ---
if st.button("🚀 INITIATE ASTRAL ROOT-CAUSE ANALYSIS", use_container_width=True):
    
    log_output = st.empty()
    logs = [
        "Initializing Astral FinOps Agent...",
        f"Targeting network mesh: {target_cluster}...",
        "Connecting to observability pipeline...",
        "Extracting container limits vs. actual hardware usage...",
        "Sending encrypted payload to LLM Reasoning Engine..."
    ]
    log_text = ""
    for log in logs:
        log_text += f"> {log}\n"
        log_output.markdown(f'<div class="terminal-box">{log_text}</div>', unsafe_allow_html=True)
        time.sleep(0.4)

    if uploaded_file is not None:
        data = json.load(uploaded_file)
        log_text += "> 📥 External telemetry file detected and ingested successfully.\n"
    else:
        with open("telemetry_snapshot.json", "r") as f:
            data = json.load(f)
        log_text += "> 📡 Defaulting to internal cluster diagnostic payload...\n"
        
    log_output.markdown(f'<div class="terminal-box">{log_text}</div>', unsafe_allow_html=True)

    # --- SAFE DATA EXTRACTION ---
# Check if the uploaded JSON has pricing info. If not, fallback to a standard AWS/GCP default rate.
    if "pricing_model" in data and "memory_per_gb_hour" in data["pricing_model"]:
        cost_per_hour = data["pricing_model"]["memory_per_gb_hour"]
    else:
        cost_per_hour = 0.043  # Default industry standard rate if missing

    prompt = f"""
    You are Astral, an autonomous FinOps Agent analyzing Kubernetes containers. Review this JSON telemetry: {json.dumps(data)}
    Find the container service that is massively over-provisioned (allocated RAM is way higher than used RAM).
    Respond ONLY with a valid JSON object in this exact format:
    {{
        "service_name": "Name", 
        "allocated_gb": 0.0, 
        "used_gb": 0.0,
        "root_cause": "Write 1 sentence explaining technically why an engineer would allocate so much extra RAM to this specific container."
    }}
    """
    
    log_text += "> Llama-3.1 engaged. Analyzing allocation patterns...\n"
    log_output.markdown(f'<div class="terminal-box">{log_text}</div>', unsafe_allow_html=True)
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
        response_format={"type": "json_object"},
    )
    
    ai_decision = json.loads(response.choices[0].message.content)
    
    # --- SAVE TO MEMORY INSTEAD OF JUST DRAWING IT ---
    st.session_state.ai_data = {
        "target_service": ai_decision["service_name"],
        "allocated": float(ai_decision["allocated_gb"]),
        "used": float(ai_decision["used_gb"]),
        "root_cause": ai_decision["root_cause"],
        "cost_per_hour": cost_per_hour
    }
    st.session_state.scan_complete = True # Tell the app the scan is done
    
    log_text += f"> ✅ Anomaly isolated in container: {ai_decision['service_name']}.\n"
    log_output.markdown(f'<div class="terminal-box">{log_text}</div>', unsafe_allow_html=True)
    time.sleep(1)
    log_output.empty() 

# --- OUTSIDE THE BUTTON: DRAW DASHBOARD IF MEMORY EXISTS ---
if st.session_state.scan_complete:
    
    # Retrieve our saved data
    d = st.session_state.ai_data
    wasted_gb = d["allocated"] - d["used"]
    monthly_cost_total = d["allocated"] * d["cost_per_hour"] * 24 * 30
    monthly_cost_actual = d["used"] * d["cost_per_hour"] * 24 * 30
    monthly_wasted = monthly_cost_total - monthly_cost_actual
    annual_saved = calculate_financial_impact(d["allocated"], d["used"], d["cost_per_hour"])
    new_limit = round(d["used"] * 1.2, 4)
    fix_code = generate_k8s_yaml(d["target_service"], new_limit)

    # --- 3. THE DIAGNOSTIC DASHBOARD ---
    st.error(f"🚨 **CRITICAL ANOMALY DETECTED:** Severe Resource Bloat in `{d['target_service']}`")
    st.info(f"**🧠 Astral Root Cause Analysis:** {d['root_cause']}")
    
    st.markdown("### 📊 Hardware Allocation")
    ram1, ram2, ram3 = st.columns(3)
    ram1.metric("RAM Limit Set", f"{d['allocated']:,.2f} GB", "Hard Limit")
    ram2.metric("Actual Hardware Used", f"{d['used']:,.4f} GB", "Active Workload", delta_color="off")
    ram3.metric("Idle / Hoarded RAM", f"{wasted_gb:,.2f} GB", "-Wasted Capacity", delta_color="inverse")

    st.divider()

    st.markdown("### 💸 Financial Audit")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Monthly Bill", f"${monthly_cost_total:,.2f}")
    col2.metric("Actual Compute Value", f"${monthly_cost_actual:,.2f}")
    col3.metric("Monthly Leakage", f"${monthly_wasted:,.2f}", delta=f"-${monthly_wasted:,.2f}", delta_color="inverse")
    col4.metric("Projected Annual Recovery", f"${annual_saved:,.2f}", delta="Action Required", delta_color="normal")
    
    st.divider()
    
    st.markdown("### 🛠️ Immutable Infrastructure Remediation")
    st.markdown(f"Astral has drafted the following Kubernetes patch to downsize `{d['target_service']}`:")
    st.code(fix_code, language="yaml")
    
    st.warning("⚠️ **Human-in-the-Loop Gateway:** Security policy prohibits autonomous AI deployment to production.")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        # --- CLOUD UPGRADE: Use Streamlit's native Download Button ---
        filename = "remediation_payment-gateway.yaml"
        
        st.download_button(
            label="⬇️ Authenticate & Download Patch",
            data=fix_code,
            file_name=filename,
            mime="text/yaml",
            use_container_width=True
        )
        
        # --- NEW: QUICK EXECUTION GUIDE ---
        st.markdown("### 🏃‍♂️ Next Steps: Apply to Local Cluster")
        st.info("Open your terminal where this file was downloaded and run:")
        st.code(f"kubectl apply -f {filename}\nkubectl get pods -w", language="bash")
            
    with col_btn2:
        if st.button("❌ Quarantine Recommendation", use_container_width=True):
            st.info("Agent action overridden. Recommendation quarantined for manual review.")
            st.session_state.scan_complete = False # Clears the dashboard
