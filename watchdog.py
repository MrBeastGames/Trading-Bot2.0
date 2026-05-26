import time
import subprocess


while True:

    try:

        subprocess.run([
            "python",
            "main.py"
        ])

    except Exception:
        pass

    time.sleep(5)