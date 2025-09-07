import os
import json
from datetime import datetime

# Files to store data by type
WARNINGS_FILE = "data/warnings.json"
MUTES_FILE = "data/mutes.json"
BANS_FILE = "data/bans.json"

# Function to save moderation_commands to JSON File
def save_moderation_json(SAVE_TYPE, TYPE, CASE, USER, MODERATOR, REASON, DURATION):
    # Check which type of moderation action should be saved
    # Choose the correct file to save the data
    # Options: warning, mute, ban
    if (TYPE == "WARNING"):
        FILE = WARNINGS_FILE
    elif (TYPE == "MUTE"):
        FILE = MUTES_FILE
    elif (TYPE == "BAN"):
        FILE = BANS_FILE

    # Check if the file exists, otherwise create a new File with "[]"
    if not os.path.exists(FILE):
        with open(FILE, "w") as f:
            json.dump([], f)
    
    with open(FILE, "r") as f:
        DATA = json.load(f)

    # Save data to JSON & check the save type (add/remove) and append it to the JSON data
    DATA.append({
        "TYPE": "add" if SAVE_TYPE == "ADD" else "remove",
        "CASE": CASE,
        "USER_ID": USER.id,
        "MODERATOR_ID": MODERATOR.id,
        "REASON": REASON,
        "TIMESTAMP": datetime.now().isoformat()
    })


    # If the type is "MUTE", also save the duration
    if (TYPE == "MUTE"):
        DATA.append({
            "DURATION": DURATION,
        })
    
    # Add all changes to the JSON file
    with open(FILE, "w") as f:
        json.dump(DATA, f, indent=4)