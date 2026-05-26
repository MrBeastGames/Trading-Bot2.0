import json
import os
import logging

POSITION_FILE = "position.json"

def load_position():

    if os.path.exists(POSITION_FILE):

        try:

            with open(POSITION_FILE, "r") as f:

                position = json.load(f)

                return position

        except Exception as e:

            logging.error(
                f"Load Position Error: {e}"
            )

            return None

    return None