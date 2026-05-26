import os
import sys
import time
import signal
import subprocess
import threading

processes = []

def run_bot():
    bot = subprocess.Popen([sys.executable, "main.py"])
    processes.append(bot)
    bot.wait()

def run_dashboard():
    port = os.environ.get("PORT", "8501")

    dashboard = subprocess.Popen([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "dashboard.py",
        "--server.port",
        str(port),
        "--server.address",
        "0.0.0.0",
        "--server.headless",
        "true"
    ])

    processes.append(dashboard)
    dashboard.wait()

def shutdown(*args):
    for proc in processes:
        try:
            proc.terminate()
        except Exception:
            pass
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

while True:
    try:
        run_dashboard()
    except Exception as e:
        print(f"Dashboard crashed: {e}")
        time.sleep(5)