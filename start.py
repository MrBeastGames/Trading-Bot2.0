
import os
import sys
import time
import signal
import logging
import subprocess
import threading

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

processes = []
shutdown_flag = False

def run_bot():

    global shutdown_flag

    while not shutdown_flag:

        try:

            logging.info("Starting trading bot...")

            bot = subprocess.Popen(
                [sys.executable, "main.py"]
            )

            processes.append(bot)

            bot.wait()

            if shutdown_flag:
                break

            logging.warning(
                "Bot crashed. Restarting in 5 seconds..."
            )

            time.sleep(5)

        except Exception as e:

            logging.error(
                f"Bot process error: {e}"
            )

            time.sleep(5)

def run_dashboard():

    global shutdown_flag

    port = os.environ.get("PORT", "8080")

    while not shutdown_flag:

        try:

            logging.info(
                f"Starting dashboard on port {port}"
            )

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

            if shutdown_flag:
                break

            logging.warning(
                "Dashboard crashed. Restarting..."
            )

            time.sleep(5)

        except Exception as e:

            logging.error(
                f"Dashboard error: {e}"
            )

            time.sleep(5)

def shutdown(*args):

    global shutdown_flag

    shutdown_flag = True

    logging.info(
        "Shutting down services..."
    )

    for proc in processes:

        try:
            proc.terminate()
        except Exception:
            pass

    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

bot_thread = threading.Thread(
    target=run_bot,
    daemon=True
)

bot_thread.start()

run_dashboard()
