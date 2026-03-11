import streamlit as st
from services.api_client import get_system, get_tasks

st.set_page_config(page_title="System Optimization Dashboard", layout="wide")

st.title("System Optimization Dashboard")

#Sidebar for system info
st.sidebar.title("System Control Panel")

systems = get_system()

system_ids = []

systems = get_system()

system_ids = []

if systems and isinstance(systems, list):
    system_ids = [s["id"] for s in systems]
else:
    st.error("Failed to fetch systems from API")

selected_system = st.sidebar.selectbox("Select System", system_ids)

st.sidebar.button("Refresh Data")

st.write("Selected System ID:", selected_system)

st.info("Fetching tasks for selected system...")