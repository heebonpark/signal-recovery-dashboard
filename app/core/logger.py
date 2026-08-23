import json
import os
import datetime
import threading

LOG_FILE_PATH = os.path.expanduser("~/.dataintelligence_pro/activity_logs.json")
MAX_LOG_ENTRIES = 5000

_log_lock = threading.Lock()

def ensure_log_file():
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    if not os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump([], f)

def add_log(user_id, action, details=""):
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "user_id": user_id,
        "action": action,
        "details": details
    }
    with _log_lock:
        ensure_log_file()
        try:
            with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, OSError):
            logs = []

        logs.append(log_entry)
        logs = logs[-MAX_LOG_ENTRIES:]

        with open(LOG_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

def get_logs():
    ensure_log_file()
    try:
        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []
