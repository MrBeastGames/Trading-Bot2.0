import subprocess
import sys
import os
import time

# =====================================================
# START BOT
# =====================================================
bot_process = subprocess.Popen(
    [sys.executable, "main.py"]
)

print("Trading bot started.")

# =====================================================
# START DASHBOARD
# =====================================================
port = os.environ.get("PORT", "8080")

dashboard_process = subprocess.Popen(
    [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "dashboard.py",
    ]
)

print(f"Dashboard started on port {port}")

# =====================================================
# KEEP CONTAINER ALIVE
# =====================================================
while True:
    time.sleep(60)