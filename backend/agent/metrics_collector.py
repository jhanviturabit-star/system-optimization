#collects system data

import psutil

def collect_metrics():
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('C:/').percent

        try:
            temps = psutil.sensors_temperatures()
            temp = list(temps.values())[0][0].current if temps else 0
        except Exception:
            temp = 0

        startup_apps = 10

        return {
            "cpu_usage": cpu_usage,
            "ram_usage": ram,
            "disk_usage": disk,
            "temperature": temp,
            "startup_time": startup_apps
        }

    except Exception:   
        return {
            "cpu_usage": 0,
            "ram_usage": 0,
            "disk_usage": 0,
            "temperature": 0,
            "startup_time": 0
        }