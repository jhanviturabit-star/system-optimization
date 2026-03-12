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

    response = requests.get(url)

    try:
        return response.json()
    except:
        return response.text


def update_task_status(task_id):

    url = f"{BASE_URL}/tasks/{task_id}/complete"

    response = requests.post(url)

    try:
        return response.json()
    except:
        return response.text