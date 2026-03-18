import streamlit as st
import requests
import pandas as pd
import time
import json
from streamlit_autorefresh import st_autorefresh

# --- CONFIG & THEME ---
st.set_page_config(page_title="System Optimizer", layout="wide")

# Custom CSS for that grid-pattern dark theme and neon accents
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        background-image: radial-gradient(#1f2937 1px, transparent 1px);
        background-size: 20px 20px;
        color: #00ffcc;
    }
    .stButton>button {
        border: 1px solid #00ffcc;
        background-color: transparent;
        color: #00ffcc;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00ffcc;
        color: #0e1117;
        box-shadow: 0 0 10px #00ffcc;
    }
    .step-box {
        padding: 20px;
        border: 1px solid #333;
        border-radius: 10px;
        background: rgba(17, 25, 40, 0.75);
    }
    </style>
    """, unsafe_allow_html=True)

API_BASE = "http://127.0.0.1:8000"

# Auto-refresh every 5 seconds to catch the background process updates
st_autorefresh(interval=5000, key="datarefresh")

# --- STATE MANAGEMENT ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'selected_system' not in st.session_state: st.session_state.selected_system = None

# --- SIDEBAR: SYSTEM CONNECTION ---
with st.sidebar:
    st.markdown("### Connection")
    try:
        systems = requests.get(f"{API_BASE}/system").json().get("systems", [])
        system_map = {s['system_name']: s['id'] for s in systems}
        choice = st.selectbox("Select Target Workstation", options=list(system_map.keys()))
        st.session_state.selected_system = system_map[choice]
        st.success(f"Connected to {choice}")
    except:
        st.error("FastAPI Server Offline")

# --- STEPPER HEADER ---
cols = st.columns(4)
step_names = ["System Analysis", "User Decision", "Optimization", "Final Action"]
for i, name in enumerate(step_names):
    is_active = st.session_state.step == i + 1
    color = "#00ffcc" if is_active else "#555"
    cols[i].markdown(f"<p style='text-align:center; color:{color}; font-weight:bold;'>{'●' if is_active else '○'} {name}</p>", unsafe_allow_html=True)

st.markdown("---")

# --- STEP 1: SYSTEM ANALYSIS ---
if st.session_state.step == 1:
    st.title("1. Analysis")
    
    # 1. THE GAUGES (Matching Lovable UI)
    m_resp = requests.get(f"{API_BASE}/system/metrics/{st.session_state.selected_system}").json()
    if m_resp.get("metrics"):
        m = m_resp["metrics"][0]
        col1, col2, col3 = st.columns(3)
        
        # We use custom HTML/CSS to make these look like Gauges rather than plain text
        for col, label, val in zip([col1, col2, col3], ["CPU", "RAM", "Disk"], [m['cpu_usage'], m['ram_usage'], m['disk_usage']]):
            color = "#00ffcc" if val < 70 else "#ff4b4b"
            col.markdown(f"""
                <div style="border: 2px solid #333; border-radius: 15px; padding: 20px; text-align: center; background: #111;">
                    <h3 style="color: white; margin-bottom: 0;">{label}</h3>
                    <h1 style="color: {color}; margin-top: 10px;">{val}%</h1>
                    <div style="background-color: #333; border-radius: 10px; height: 10px; width: 100%;">
                        <div style="background-color: {color}; height: 10px; width: {val}%; border-radius: 10px;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # 2. THE BACKGROUND PROGRAMS (Real-time list)
    st.subheader("Background Processes")
    p_resp = requests.get(f"{API_BASE}/system/live-processes/{st.session_state.selected_system}").json()
    procs = p_resp.get("processes", [])

    if procs:
        df_procs = pd.DataFrame(procs)
        # Using st.dataframe with custom styling for that 'Pro' feel
        st.dataframe(
            df_procs[['pid', 'name', 'cpu', 'memory', 'status']], 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.info("Scanning for background programs... ensure Agent is running.")

    if st.button("Next →"): st.session_state.step = 2

# --- STEP 2: USER DECISION ---
elif st.session_state.step == 2:
    st.subheader("User Decision")
    st.caption("Select resource-heavy processes to terminate")
    
    p_resp = requests.get(f"{API_BASE}/system/live-processes/{st.session_state.selected_system}").json()
    processes = p_resp.get("processes", [])
    
    if processes:
        df = pd.DataFrame(processes)
        df.insert(0, "Select", False)
        edited_df = st.data_editor(df, hide_index=True, use_container_width=True)
        
        to_kill = edited_df[edited_df["Select"] == True]
        if st.button(f"Terminate Selected ({len(to_kill)})", type="primary"):
            for pid in to_kill['pid']:

                payload_data = json.dumps({"pid": pid})

                requests.post(f"{API_BASE}/tasks/create", params={
                    "system_id": st.session_state.selected_system, 
                    "action_type": "kill_process",
                    "payload": payload_data
                })
            st.success("Kill tasks sent!")
            time.sleep(1)
            st.rerun()
    else:
        st.info("No scan data available. Go back and Start Scan.")

    c1, c2 = st.columns(2)
    if c1.button("← Previous"): st.session_state.step = 1
    if c2.button("Next →"): st.session_state.step = 3

# --- STEP 3: OPTIMIZATION ---
if st.session_state.step == 3:
    st.subheader("Optimization")
    
    col1, col2, col3 = st.columns(3)
    
    # Note: We must pass payload="{}" to satisfy the DB procedure
    if col1.button("🧹 Clear Temp"):
        requests.post(f"{API_BASE}/tasks/create", params={
            "system_id": st.session_state.selected_system, 
            "action_type": "clear_temp",
            "payload": "{}"
        })
        st.success("Clear Temp task issued!")

    if col2.button("⚙️ Disk Cleanup"):
        requests.post(f"{API_BASE}/tasks/create", params={
            "system_id": st.session_state.selected_system, 
            "action_type": "disk_cleanup",
            "payload": "{}"
        })
        st.success("Disk Cleanup task issued!")

    if col3.button("🗑️ Empty Bin"):
        requests.post(f"{API_BASE}/tasks/create", params={
            "system_id": st.session_state.selected_system, 
            "action_type": "memory_cleanup",
            "payload": "{}"
        })
        st.success("Memory Cleanup task issued!")

# --- STEP 4: FINAL ACTION (Adding Restart Logic) ---
elif st.session_state.step == 4:
    # st.balloons()
    st.header("Optimization Complete")
    st.success("Your system has been optimized successfully.")
    
    # Matching the "Recommendation" box from the Lovable UI
    st.info("💡 **Recommendation:** Your system performance has improved, but a restart is recommended to clear deep-level system cache.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Restart System Now"):
            requests.post(f"{API_BASE}/tasks/create", params={
                "system_id": st.session_state.selected_system, 
                "action_type": "restart_system",
                "payload": "{}"
            })
            st.warning("Restart command sent to workstation.")
    with col_b:
        if st.button("Finish & Exit"):
            st.session_state.step = 1
            st.rerun()