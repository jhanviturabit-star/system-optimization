#connects to FastAPI server

import requests

BASE_URL = 'http://127.0.0.1:8000'

def register_system(hostname, os):

    url = f"{BASE_URL}/system/register"

    data = {
        "hostname": hostname,
        "os": os
    }

    response = requests.post(url, json=data)

    try:
        return response.json()
    except:
        return response.text


def send_metrics(system_id, metrics):

    url = f"{BASE_URL}/system/report"

    data = {
        "system_id": system_id,
        "cpu_usage": metrics["cpu_usage"],
        "disk_usage": metrics["disk_usage"],
        "ram_usage": metrics["ram_usage"],
        "temp_size_mb": metrics["temp_size_mb"],
        "startup_files": metrics["startup_files"]
    }

    response = requests.post(url, json=data)

    try:
        return response.json()
    except:
        return response.text


def fetch_tasks(system_id):

    url = f"{BASE_URL}/tasks/{system_id}"

    try:
        response = requests.get(url)
        # Only return JSON if the request was successful
        if response.status_code == 200:
            return response.json()
        return {"tasks": []} # Return empty tasks on error
    except Exception as e:
        print(f"Connection error: {e}")
        return {"tasks": []}

def update_task_status(task_id):

    url = f"{BASE_URL}/tasks/{task_id}/complete"

    try:
        response = requests.post(url)
        if response.status_code == 200:
            return response.json()
        return {"status": "error"}
    except Exception as e:
        return {"status": "connection_failed"}
    
def send_process_report(system_id, processes):

    url = f"{BASE_URL}/system/report-processes/{system_id}"

    try:
        response = requests.post(url, json=processes)
        if response.status_code == 200:
            return response.json()
        return {"status": "error"}
    except Exception as e:
        return {"status": "connection_failed"}

        return response.text
