import schedule
import time

from telegram_utils import (
    send_daily_report
)

schedule.every().day.at(
    "23:59"
).do(
    send_daily_report
)

while True:

    schedule.run_pending()

    time.sleep(30)