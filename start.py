import subprocess
import sys
import os

bot_process = subprocess.Popen(
    [sys.executable, "bot/main.py"]
)

dashboard_process = subprocess.Popen(
    [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "dashboard/dashboard.py",
        "--server.port",
        os.environ.get("PORT", "8080"),
        "--server.address",
        "0.0.0.0",
    ]
)

bot_process.wait()
dashboard_process.wait()