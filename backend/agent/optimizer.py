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
    """Fetch top N processes by CPU usage."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            # Fetch info ass a dict
            p_info = proc.info
            # Filter out idle/system processes if they have 0% usage to keep the list relevant
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
#def clear_temp_files(path="C:/Windows/Temp"):
def clear_temp_files(path=None):
    if path is None:
        path = os.environ.get("TEMP")

    try:
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)

            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)

                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)

            except PermissionError:
                pass

            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

        return True

    except Exception as e:
        print(f"Error during temp file cleanup: {e}")
        return False

# -------------------------------
# DISK CLEANUP
# -------------------------------
def disk_cleanup():

    try:
        subprocess.run("cleanmgr /sagerun:1", shell=True)
        return True

    except Exception:
        return False


# -------------------------------
# MEMORY CLEANUP
# -------------------------------
def memory_cleanup():

    try:
        subprocess.run("powershell.exe -Command Clear-RecycleBin -Force", shell=True)
        return True

    except Exception:
        return False


# -------------------------------
# STARTUP APPS CLEANUP
# -------------------------------
def startup_cleanup():

    try:
        startup_folder = os.path.expandvars(
            r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
        )

        for file in os.listdir(startup_folder):
            file_path = os.path.join(startup_folder, file)

            try:
                os.remove(file_path)
            except Exception:
                pass

        return True

    except Exception:
        return False


# -------------------------------
# TASK EXECUTOR
# -------------------------------
def execute_task(task, system_id):
    # 1. FORCE DICTIONARY CHECK
    if isinstance(task, str):
        # If it's a string, we treat the string as the action name
        action = task
        payload = {}
    elif isinstance(task, dict):
        # If it's a dict, we extract action and payload safely
        action = task.get("action") or task.get("action_type")
        payload = task.get("payload", {}) or {}

        if not isinstance(payload, dict):
            payload = {"path": payload}
    else:
        print(f"Unknown task format: {type(task)}")
        return False

    print(f"--- Processing: {action} ---")

    # 2. MATCH ACTIONS
    if action in ["fetch_processes", "fetch_top_processes"]:
        process_list = fetch_top_processes()
        # Ensure your api_client has this function
        from api_client import send_process_report
        return send_process_report(system_id, process_list)
    
    elif action == "clear_temp":
        # payload is now guaranteed to be a dict, so .get() works
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
        os.system("shutdown /r /t 0")

        
    print(f"Unknown action: {action}")
    return False
    
