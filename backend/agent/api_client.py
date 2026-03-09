#connects to FastAPI server

import requests

BASE_URL = 'http://127.0.0.1:8000/'

def register_system(hostname, os):

    url = f"{BASE_URL}/system/register"

    data = {
        "hostname": hostname,
        "os": os
    }

    response = requests.post(url, json=data)

    return response.json()


def send_metrics(system_id, metrics):

    url = f"{BASE_URL}/system/report"

    data = {
        "system_id": system_id,
        "cpu_usage": metrics["cpu_usage"],
        "disk_usage": metrics["disk_usage"],
        "ram_usage": metrics["ram_usage"],
        "temperature": metrics["temperature"],
        "startup_time": metrics["startup_time"]
    }

    response = requests.post(url, json=data)

    return response.json()


def fetch_tasks(system_id):

    url = f"{BASE_URL}/tasks/{system_id}"

    response = requests.get(url)

    return response.json()


def update_task_status(task_id, status):

    url = f"{BASE_URL}/tasks/update_status"

    data = {
        "task_id": task_id,
        "status": status
    }

    response = requests.post(url, json=data)

    return response.json()