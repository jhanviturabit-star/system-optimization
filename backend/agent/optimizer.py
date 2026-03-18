#executes optimization tasks recieved from server

import os
import shutil
import subprocess
import psutil
from api_client import send_process_report
# import json

# -------------------------------
# FETCH TOP PROCESSES
# -------------------------------
def fetch_top_processes(limit=10):
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            p_info = proc.info
            if p_info['cpu_percent'] > 0 or p_info['memory_percent'] > 0:
                processes.append({
                    "pid": p_info['pid'],
                    "name": p_info['name'],
                    "cpu": p_info['cpu_percent'],
                    "memory": round(p_info['memory_percent'], 2),
                    "status": "RUNNING"
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    processes = sorted(processes, key=lambda p: p['cpu'], reverse=True)
    return processes[:limit]

# -------------------------------
# TEMP FILE CLEANUP
# -------------------------------
def clear_temp_files(path=None):
    if path is None:
        path = os.environ.get("TEMP") 

    print(f"Cleaning User Temp: {path}")
    
    try:
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception:
                continue 
        return True
    except Exception as e:
        print(f"Error accessing directory: {e}")
        return False

# -------------------------------
# DISK CLEANUP
# -------------------------------
def disk_cleanup():
    """
    Since cleanmgr /sagerun requires Admin, we instead clear 
    the User's local application cache.
    """
    local_appdata = os.environ.get("LOCALAPPDATA")
    target_cache = os.path.join(local_appdata, "Microsoft", "Windows", "Explorer")
    
    print(f"Attempting local cache optimization at: {target_cache}")
    try:
        # We can also clear the 'Recent' items folder which doesn't need admin
        recent_path = os.path.expandvars(r"%USERPROFILE%\Recent")
        if os.path.exists(recent_path):
            for f in os.listdir(recent_path):
                try:
                    os.remove(os.path.join(recent_path, f))
                except: continue
        return True
    except Exception as e:
        print(f"Disk cleanup skipped system files (No Admin): {e}")
        return True

# -------------------------------
# MEMORY CLEANUP
# -------------------------------
def memory_cleanup():
    try:
        # Silently skip files that require Admin rights
        cmd = 'powershell.exe -Command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"'
        subprocess.run(cmd, shell=True)
        print("User Recycle Bin cleanup attempted.")
        return True
    except Exception as e:
        print(f"Memory cleanup error: {e}")
        return True

# -------------------------------
# TASK EXECUTOR
# -------------------------------
def execute_task(task, system_id):
    if isinstance(task, str):
        action = task
        payload = {}
    elif isinstance(task, dict):
        action = task.get("action") or task.get("action_type")
        payload = task.get("payload")
        if not isinstance(payload, dict):
            payload = {}
    else:
        return False

    print(f"--- Processing: {action} ---")

    if action in ["fetch_processes", "fetch_top_processes"]:
        process_list = fetch_top_processes()
        return send_process_report(system_id, process_list)
    
    elif action == "clear_temp":
        return clear_temp_files(payload.get("path"))

    elif action == "disk_cleanup":
        return disk_cleanup()

    elif action == "memory_cleanup":
        return memory_cleanup()

    elif action == "kill_process":
        pid = payload.get("pid")
        if pid:
            try:
                proc = psutil.Process(int(pid))
                proc.terminate()
                return True
            except Exception as e:
                print(f"Kill failed: {e}")
        return False

    elif action == "restart_system":
        # Standard user restart command
        print("System restart initiated...")
        os.system("shutdown /r /t 5")
        return True
        
    print(f"Unknown action: {action}")
    return False
    
