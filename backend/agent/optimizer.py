#executes optimization tasks recieved from server

import os
import shutil
import subprocess
# import json

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
def execute_task(task):

    action = task.get("action")
    payload = task.get("payload", {})

    if action == "clear_temp":

        path = payload.get("path")
        return clear_temp_files(path)

    elif action == "disk_cleanup":

        return disk_cleanup()

    elif action == "memory_cleanup":

        return memory_cleanup()

    elif action == "startup_cleanup":

        return startup_cleanup()
    
    
    else:

        print(f"Unknown optimization task: {action}")
        return False