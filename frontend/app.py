import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# ===================== CONFIG =====================
st.set_page_config(page_title="System Optimization Tool", page_icon="⚡", layout="wide")

API_BASE_URL = "http://127.0.0.1:8000"  # ← your FastAPI URL

# Simple system selector (in real app you might have login → list systems)
if 'system_id' not in st.session_state:
    st.session_state.system_id = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
    st.session_state.metrics = None
    st.session_state.processes = None
    st.session_state.selected_processes = []

# ===================== SIDEBAR =====================
with st.sidebar:
    st.title("⚡ System Optimization Tool")
    st.markdown("Internal multi-system utility")

    system_id_input = st.text_input("Enter System ID", value=st.session_state.system_id or "")
    if st.button("Load / Refresh System"):
        if system_id_input.strip():
            st.session_state.system_id = system_id_input.strip()
            st.success(f"Working with system: {st.session_state.system_id}")
            st.rerun()
        else:
            st.warning("Enter a valid system_id")

    st.markdown("---")
    try:
        resp = requests.get(f"{API_BASE_URL}/system/status/{st.session_state.system_id}", timeout=5)
        status = "🟢 Online" if resp.status_code == 200 else "🔴 Error"
    except:
        status = "🔴 Offline / Invalid ID"
    st.metric("Selected System", status)

    if st.button("Reset Flow", type="secondary"):
        st.session_state.current_step = 1
        st.session_state.metrics = None
        st.session_state.processes = None
        st.rerun()

# ===================== MAIN =====================
if not st.session_state.system_id:
    st.title("Welcome to System Optimization Tool")
    st.info("Enter a **system_id** in the sidebar to start.\n\n"
            "(Agents register via POST /system/register and report data automatically)")
    st.stop()

st.title(f"Optimization Dashboard – System {st.session_state.system_id}")
progress = st.progress((st.session_state.current_step - 1) / 3)
steps = ["1. System Analysis", "2. Review & Decide", "3. Cleanup & Optimize", "4. Final Recommendation"]
st.subheader(steps[st.session_state.current_step - 1])

# Auto-refresh helper
def refresh_data():
    try:
        m = requests.get(f"{API_BASE_URL}/system/metrics/{st.session_state.system_id}", timeout=6)
        if m.status_code == 200:
            st.session_state.metrics = m.json()

        p = requests.get(f"{API_BASE_URL}/system/live-processes/{st.session_state.system_id}", timeout=6)
        if p.status_code == 200:
            st.session_state.processes = p.json()  # assume list of dicts: [{'name':.., 'cpu':.., 'mem':..}, ...]
    except:
        pass

# ===================== STEP 1: ANALYSIS =====================
if st.session_state.current_step == 1:
    st.markdown("Waiting for Agent to report latest metrics & processes (auto-reported via API).")

    col1, col2 = st.columns([1,4])
    with col1:
        if st.button("Refresh Data Now", type="primary"):
            refresh_data()
            st.rerun()

    if st.session_state.metrics:
        col1, col2, col3 = st.columns(3)
        col1.metric("CPU", f"{st.session_state.metrics.get('cpu_percent', 'N/A')}%")
        col2.metric("RAM", f"{st.session_state.metrics.get('memory_percent', 'N/A')}%")
        col3.metric("Disk", f"{st.session_state.metrics.get('disk_percent', 'N/A')}%")

    if st.session_state.processes:
        st.subheader("Top Resource Consumers")
        df = pd.DataFrame(st.session_state.processes)

        st.write("DEBUG: Available columns in processes data:")
        st.write(df.columns.tolist())

        st.write("DEBUG: First 3 rows (raw):")
        st.write(df.head(3))

        st.dataframe(df, use_container_width=True)
       # st.dataframe(df.sort_values("cpu", ascending=False).head(15), use_container_width=True)

    if st.button("Proceed to Review →", type="primary", disabled=not st.session_state.processes):
        st.session_state.current_step = 2
        st.rerun()

    st.caption("Agent should call POST /system/report and /system/report-processes/{system_id} periodically.")

# ===================== STEP 2: USER DECISION =====================
elif st.session_state.current_step == 2:
    st.markdown("Select heavy / non-critical processes to terminate.")

    if st.session_state.processes:
        df = pd.DataFrame(st.session_state.processes)
        options = df['name'].tolist()  # adjust key if your process dict uses 'pid_name' etc.

        selected = st.multiselect(
            "Select processes to kill",
            options=options,
            default=st.session_state.selected_processes,
            format_func=lambda x: f"{x}  (CPU: {df[df['name']==x]['cpu'].values[0]:.1f}%)"
        )

        if st.button("Queue Termination Task", type="primary"):
            if selected:
                # Create task – adjust payload to match your /tasks/create schema
                payload = {
                    "system_id": st.session_state.system_id,
                    "action": "terminate_processes",
                    "parameters": {"process_names": selected},
                    "status": "pending"
                }
                try:
                    r = requests.post(f"{API_BASE_URL}/tasks/create", json=payload)
                    r.raise_for_status()
                    task_id = r.json().get("task_id", "unknown")
                    st.success(f"Task created! ID: {task_id} — Agent will execute soon.")
                    st.session_state.current_step = 3
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to create task: {e}")
            else:
                st.warning("Select at least one process.")
    else:
        st.info("No process data yet. Go back and refresh.")

# ===================== STEP 3: ADDITIONAL OPTIMIZATION =====================
elif st.session_state.current_step == 3:
    st.markdown("Additional one-click optimizations (queued as tasks).")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🗑️ Clean Temp Files + Recycle Bin"):
            payload = {"system_id": st.session_state.system_id, "action": "cleanup_temp", "status": "pending"}
            try:
                requests.post(f"{API_BASE_URL}/tasks/create", json=payload)
                st.success("Cleanup task queued.")
            except:
                st.error("Failed.")

    with col2:
        if st.button("Disable Unnecessary Startup Items"):
            payload = {"system_id": st.session_state.system_id, "action": "disable_startup", "status": "pending"}
            try:
                requests.post(f"{API_BASE_URL}/tasks/create", json=payload)
                st.success("Startup disable task queued.")
            except:
                st.error("Failed.")

    with col3:
        if st.button("Re-analyze (refresh data)"):
            refresh_data()
            st.rerun()

    if st.button("Go to Final Step →", type="primary"):
        st.session_state.current_step = 4
        st.rerun()

# ===================== STEP 4: FINAL ACTION =====================
elif st.session_state.current_step == 4:
    st.markdown("If performance is still poor after cleanup, recommend restart.")

    high_usage = False
    if st.session_state.metrics:
        if st.session_state.metrics.get('cpu_percent', 0) > 70 or st.session_state.metrics.get('memory_percent', 0) > 80:
            high_usage = True
            st.warning("High resource usage detected — restart may help.")

    restart = st.checkbox("Queue system restart", value=high_usage)

    if st.button("Complete Optimization", type="primary"):
        if restart:
            payload = {"system_id": st.session_state.system_id, "action": "restart_system", "status": "pending"}
            try:
                requests.post(f"{API_BASE_URL}/tasks/create", json=payload)
                st.success("Restart task queued — agent will confirm with user & reboot.")
            except:
                st.error("Failed to queue restart.")
        else:
            st.balloons()
            st.success("Optimization flow complete! Monitor via /tasks/{system_id}")

# Footer
st.markdown("---")
st.caption(f"Connected to FastAPI @ {API_BASE_URL} | Last refresh: {datetime.now().strftime('%H:%M:%S')}")