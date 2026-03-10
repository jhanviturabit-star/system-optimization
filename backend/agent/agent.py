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

from metrics_collector import collect_metrics
from api_client import register_system, send_metrics, fetch_tasks, update_task_status
from optimizer import execute_task

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
            tasks = tasks_response.get("tasks", [])

            for task in tasks:

                task_id = task["task_id"]

                print(f"Executing task {task_id}: {task['action']}")

                success = execute_task(task)

                print("TASK RECEIVED:", task)
                print("TYPE OF PAYLOAD:", type(task.get("payload")))

                if success:
                    update_task_status(task_id, "completed")
                    print(f"Task {task_id} completed")

                else:
                    update_task_status(task_id, "failed")
                    print(f"Task {task_id} failed")

        except Exception as e:

            print("Agent error:", e)

        # wait before next cycle
        time.sleep(100)


if __name__ == "__main__":
    main()