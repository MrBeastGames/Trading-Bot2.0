import threading
import os

# START BOT
def run_bot():
    os.system("python main.py")

# START DASHBOARD
def run_dashboard():
    os.system(
        "streamlit run dashboard.py --server.port $PORT --server.address 0.0.0.0"
    )

bot_thread = threading.Thread(target=run_bot)
bot_thread.start()

run_dashboard()