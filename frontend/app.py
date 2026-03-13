import streamlit as st
import pandas as pd
import requests

# 1. THE "CYBER-DARK" CSS (Exact match for the video's look)
st.set_page_config(page_title="SystemOptimizer", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3, p, label { color: #00FFA3 !important; font-family: 'Courier New', Courier, monospace; }
    
    /* The Top Stepper Bar */
    .stepper-container {
        display: flex; justify-content: space-between;
        margin-bottom: 40px; padding: 10px;
    }
    .step { color: #555; font-weight: bold; border-bottom: 2px solid #555; width: 22%; text-align: center; }
    .step-active { color: #00FFA3; border-bottom: 2px solid #00FFA3; }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: rgba(0, 255, 163, 0.05);
        border: 1px solid rgba(0, 255, 163, 0.3);
        border-radius: 10px; padding: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. STATE INITIALIZATION
if 'step' not in st.session_state:
    st.session_state.step = 1

# 3. TOP STEPPER UI (From the recording)
steps = ["System Analysis", "User Decision", "Optimization", "Final Action"]
cols = st.columns(4)
for i, name in enumerate(steps):
    is_active = " (Active)" if st.session_state.step == i + 1 else ""
    cols[i].markdown(f"<div style='text-align:center; color:{'#00FFA3' if st.session_state.step >= i+1 else '#555'}'>● {name}</div>", unsafe_allow_html=True)
st.divider()

# 4. STEP LOGIC
# --- STEP 1: SYSTEM ANALYSIS ---
if st.session_state.step == 1:
    st.title("System Analysis")
    st.caption("Scan your system to identify performance bottlenecks")
    
    # Gauges Row
    c1, c2, c3 = st.columns(3)
    c1.metric("CPU Usage", "67%")
    c2.metric("RAM Usage", "72%")
    c3.metric("Disk Usage", "45%")

    st.subheader("Running Processes")
    # Table data from recording
    proc_data = {
        "PID": [1024, 2048, 512],
        "Process": ["chrome.exe", "vscode.exe", "system32.exe"],
        "CPU %": [45.2, 22.1, 5.3],
        "Memory %": [38.7, 28.3, 12.1],
        "Status": ["RUNNING", "RUNNING", "SYSTEM"]
    }
    st.dataframe(pd.DataFrame(proc_data), use_container_width=True, hide_index=True)

    if st.button("Next ➡️", key="next1"):
        st.session_state.step = 2
        st.rerun()

# --- STEP 2: USER DECISION ---
elif st.session_state.step == 2:
    st.title("User Decision")
    st.write("Select resource-heavy processes to terminate")
    
    # Multiselect logic for the "Terminate Selected" button in the video
    st.info("Currently viewing high-impact processes...")
    st.checkbox("chrome.exe (45.2% CPU)")
    st.checkbox("vscode.exe (22.1% CPU)")
    
    st.button("Terminate Selected (0)", disabled=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Previous"): st.session_state.step = 1; st.rerun()
    with col2:
        if st.button("Next ➡️"): st.session_state.step = 3; st.rerun()

# --- STEP 3: OPTIMIZATION ---
elif st.session_state.step == 3:
    st.title("Optimization")
    st.write("Toggle cleanup options to free up resources")
    
    st.toggle("Delete Temporary Files", value=True, help="-2.3 GB")
    st.toggle("Clear Recycle Bin", value=True, help="-850 MB")
    st.toggle("Disable Startup Apps", value=False, help="-12s boot")

    if st.button("Run Optimization ✨"):
        with st.spinner("Optimizing..."):
            # Trigger your FastAPI clear_temp here
            import time; time.sleep(2)
        st.success("Optimization Complete!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Previous"): st.session_state.step = 2; st.rerun()
    with col2:
        if st.button("Next ➡️"): st.session_state.step = 4; st.rerun()

# --- STEP 4: FINAL ACTION ---
elif st.session_state.step == 4:
    st.title("Final Action")
    st.warning("Restart Recommended")
    st.write("Performance is at 58%, which is below the 78% threshold.")
    
    if st.button("🔄 Restart System"):
        st.write("Sending restart command to agent...")
    
    if st.button("⬅️ Back to Start"):
        st.session_state.step = 1
        st.rerun()