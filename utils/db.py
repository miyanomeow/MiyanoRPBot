import json
import os

DB_PATH = "rp_commands.json"

def load_commands():
    if not os.path.exists(DB_PATH):
        # Базовые команды при первом запуске
        return {
            "ударить": "ударил(а)",
            "обнять": "обнял(а)",
            "поцеловать": "поцеловал(а)"
        }
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_command(name, action):
    commands = load_commands()
    commands[name.lower()] = action
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(commands, f, ensure_ascii=False, indent=4)

def delete_command(name):
    commands = load_commands()
    if name.lower() in commands:
        del commands[name.lower()]
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(commands, f, ensure_ascii=False, indent=4)
        return True
    return False