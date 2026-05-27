import os
import sys
import time
import signal
import subprocess
import threading
import logging

logging.basicConfig(level=logging.INFO)

processes = []

# =====================================================
# RUN BOT
# =====================================================
def run_bot():

    logging.info("Starting trading bot...")

    bot = subprocess.Popen(
        [sys.executable, "main.py"]
    )

    processes.append(bot)

    bot.wait()

# =====================================================
# RUN DASHBOARD
# =====================================================
def run_dashboard():

    port = os.environ.get("PORT", "8080")

    logging.info(f"Starting dashboard on port {port}")

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
        "true",
        "--browser.gatherUsageStats",
        "false"
    ])

    processes.append(dashboard)

    dashboard.wait()

# =====================================================
# SHUTDOWN
# =====================================================
def shutdown(*args):

    logging.info("Shutting down services...")

    for proc in processes:

        try:
            proc.terminate()
        except Exception:
            pass

    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

# =====================================================
# START BOT THREAD
# =====================================================
bot_thread = threading.Thread(
    target=run_bot,
    daemon=True
)

bot_thread.start()

# =====================================================
# START DASHBOARD
# =====================================================
while True:

    try:

        run_dashboard()

    except Exception as e:

        logging.error(
            f"Dashboard crashed: {e}"
        )

        time.sleep(5)