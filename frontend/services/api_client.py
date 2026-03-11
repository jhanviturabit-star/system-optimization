import requests

BASE_URL = "http://localhost:8000"

def get_system():
    url = f"{BASE_URL}/system"
    response = requests.get(url)

    try:
        return response.json()
    except:
        return []
    

def get_metrics(system_id):
    url = f"{BASE_URL}/system/metrics/{system_id}"
    response = requests.get(url)

    try:
        return response.json()
    except:
        return []

    
def get_tasks(system_id):
    url = f"{BASE_URL}/tasks/{system_id}"
    response = requests.get(url)

    try:
        return response.json()
    except:
        return []