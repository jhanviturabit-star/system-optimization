import requests

BASE_URL = "http://localhost:8000"

def get_systems():
    response = requests.get(f"{BASE_URL}/system")
    return response.json()

def get_metrics(system_id):
    response = requests.get(f"{BASE_URL}/system/metrics/{system_id}")
    return response.json()

def create_task(system_id, task_type):
    payload = {
        "system_id": system_id,
        "task_type": task_type
    }

    response = requests.post(f"{BASE_URL}/tasks/create", json=payload)
    return response.json()