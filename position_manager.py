import json
import os


POSITION_FILE = "positions.json"


# =====================================================
# SAVE POSITION
# =====================================================
def save_position(position):

    try:

        with open(
            POSITION_FILE,
            "w"
        ) as f:

            json.dump(
                position,
                f,
                indent=4
            )

    except Exception as e:

        print(
            f"Save position error: {e}"
        )


# =====================================================
# LOAD POSITION
# =====================================================
def load_position():

    try:

        if not os.path.exists(
            POSITION_FILE
        ):

            return None

        with open(
            POSITION_FILE,
            "r"
        ) as f:

            position = json.load(f)

        return position

    except Exception as e:

        print(
            f"Load position error: {e}"
        )

        return None


# =====================================================
# CLEAR POSITION
# =====================================================
def clear_position():

    try:

        if os.path.exists(
            POSITION_FILE
        ):

            os.remove(
                POSITION_FILE
            )

    except Exception as e:

        print(
            f"Clear position error: {e}"
        )