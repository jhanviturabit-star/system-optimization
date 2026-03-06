#collects system data

import psutil

def collect_metrics():
    cpu_usage = psutil.cpu_percent(interval=1)

    ram = psutil.virtual_memory()
    ram_usage = ram.percent

    disk = psutil.disk_usage()
    disk_usage = disk.percent

    #temperature (may not work in every systems)
    try:
        temps = psutil.sensors_battery()
        if temps:
            temp = list(temps.values())[0][0].current
        else:
            temp = 0
    except:
        temp = 0

    #startup apps placeholder
    startup_apps = 10

    return {
        "cpu": cpu_usage,
        "ram": ram_usage,
        "disk": disk_usage,
        "temp": temp,
        "startup": startup_apps
    }