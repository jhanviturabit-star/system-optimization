from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db.session import get_db
from datetime import datetime

router = APIRouter()

# Temporary in-memory storage for the live snapshots
# Key: system_id, Value: list of processes
live_process_cache = {}

@router.post("/system/report-processes/{system_id}")
def report_processes(system_id: int, processes: list):
    """
    Endpoint for the AGENT to push the live process list 
    after receiving a 'fetch_processes' task.
    """
    global live_process_cache

    # Store the snapshot in the cache
    live_process_cache[system_id] = {
        "data": processes,
        "timestamp": str(datetime.now())
    }
    print(f"Cache updated for system {system_id}")
    return {"status": "success", "message": f"Received {len(processes)} processes"}

@router.get("/system/live-processes/{system_id}")
def get_live_processes(system_id: int):
    """
    Endpoint for the UI (Streamlit) to fetch the latest 
    snapshot from the cache.
    """
    snapshot = live_process_cache.get(system_id)
    if not snapshot:
        return {"processes": [], "message": "No live scan data available. Trigger a scan first."}
    
    return {"processes": snapshot["data"], "last_updated": snapshot["timestamp"]}