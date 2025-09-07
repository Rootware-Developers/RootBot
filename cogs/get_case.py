import json
import os

CASES_FILE = "data/cases.json" # File to save the current case number

def get_case():
    # Increments the case number stored in the file and returns the new value (+1)
    if not os.path.exists(CASES_FILE):
        with open(CASES_FILE, "w") as f:
            json.dump({"CASE": 0}, f)

    with open(CASES_FILE, "r") as f:
        data = json.load(f)

    data["CASE"] += 1
    NEXT_CASE = data["CASE"]

    with open(CASES_FILE, "w") as f:
        json.dump(data, f, indent=4)

    return NEXT_CASE