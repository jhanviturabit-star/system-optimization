import streamlit as st
import pandas as pd
from client_api import get_systems, get_metrics, create_task

st.set_page_config(page_title="System Optimizer", layout="wide")

st.title("⚙ System Optimizer Dashboard")

# ---------------- SYSTEM SELECTION ---------------- #

systems = get_systems()["systems"]

system_options = {s["system_name"]: s["id"] for s in systems}

selected_system = st.selectbox(
    "Select System",
    list(system_options.keys())
)

system_id = system_options[selected_system]

# ---------------- START SCAN BUTTON ---------------- #

if st.button("🔍 Start Scan"):
    st.success("System scan started")

st.divider()

# ---------------- FETCH METRICS ---------------- #

metrics = get_metrics(system_id)

if "metrics" in metrics and len(metrics["metrics"]) > 0:

    df = pd.DataFrame(metrics["metrics"])

    latest = df.iloc[0]

    # ----------- METRIC CARDS ----------- #

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "CPU Usage",
            f"{latest['cpu_usage']} %"
        )

    with col2:
        st.metric(
            "RAM Usage",
            f"{latest['ram_usage']} %"
        )

    with col3:
        st.metric(
            "Disk Usage",
            f"{latest['disk_usage']} %"
        )

    st.divider()

    # ----------- CHARTS ----------- #

    st.subheader("System Metrics History")

    df["created_at"] = pd.to_datetime(df["created_at"])
    df = df.sort_values("created_at")

    chart_col1, chart_col2, chart_col3 = st.columns(3)

    with chart_col1:
        st.write("CPU Usage")
        st.line_chart(df.set_index("created_at")["cpu_usage"])

    with chart_col2:
        st.write("RAM Usage")
        st.line_chart(df.set_index("created_at")["ram_usage"])

    with chart_col3:
        st.write("Disk Usage")
        st.line_chart(df.set_index("created_at")["disk_usage"])

else:
    st.warning("No metrics available yet.")

# ---------------- OPTIMIZATION ACTIONS ---------------- #

st.divider()
st.subheader("Optimization Actions")

col1, col2 = st.columns(2)

with col1:
    if st.button("🧹 Clear Temp Files"):
        create_task(system_id, "clear_temp")
        st.success("Task created")

with col2:
    if st.button("🚀 Disable Startup Apps"):
        create_task(system_id, "disable_startup")
        st.success("Task created")