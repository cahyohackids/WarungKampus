import subprocess
import time
proc = subprocess.Popen(["./venv/bin/python3", "main.py"])
time.sleep(10)
proc.terminate()
