import json
import os


STATE_FILE = "bot_state.json"


def save_state(data):

    with open(STATE_FILE, "w") as f:
        json.dump(data, f)


def load_state():

    if not os.path.exists(STATE_FILE):
        return {}

    with open(STATE_FILE, "r") as f:
        return json.load(f)