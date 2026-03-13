#main loop of agent

"""
while True:
    metrics = collect_metrics()

    send_metrics(system_id, metrics)

    tasks = fetch_tasks(system_id)

    for task in tasks:
        run_task(task)

    time.sleep(30)
"""

import time
import socket
import platform
import os
import sys

from metrics_collector import collect_metrics
from api_client import register_system, send_metrics, fetch_tasks, update_task_status, send_process_report
from optimizer import execute_task, fetch_top_processes

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

SYSTEM_ID_FILE = "system_id.txt"

def get_or_register_system():

    # check if system already registered
    if os.path.exists(SYSTEM_ID_FILE):

        with open(SYSTEM_ID_FILE, "r") as f:
            return int(f.read().strip())

    # register new system
    hostname = socket.gethostname()
    os_name = platform.system()

    response = register_system(hostname, os_name)

    system_id = response.get("system_id")

    # save system id locally
    with open(SYSTEM_ID_FILE, "w") as f:
        f.write(str(system_id))

    return system_id


def main():

    print("Starting System Optimization Agent...")

    system_id = get_or_register_system()

    print(f"System registered with ID: {system_id}")

    while True:

        try:

            # collect system metrics
            metrics = collect_metrics()
            print("Collected metrics:", metrics)

            # send metrics to server
            send_metrics(system_id, metrics)
            print("Metrics sent to server")

            # fetch optimization tasks
            tasks_response = fetch_tasks(system_id)
            
            if isinstance(tasks_response, dict):
                tasks = tasks_response.get("tasks", [])
            else:
                print("Invalid response for tasks:", tasks_response)
                tasks = []

            for task in tasks:

                if isinstance(task, dict):
                    task_id = task.get("task_id")
                    action = task.get("action") or task.get("action_type")
                else:
                    task_id = None
                    action = task

                print(f"Executing task {task_id}: {action}")

                success = execute_task({"action" : action} if isinstance(task, str) else task, system_id)
                print("Checking for tasks...")

                if success:
                    update_task_status(task_id)
                    print(f"Task {task_id} completed")
                else:
                    print(f"Task {task_id} failed")

        except Exception as e:

            print("Agent error:", e)

        # wait before next cycle
        time.sleep(10)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error occurred:", e)
        input("Press Enter to exit...")