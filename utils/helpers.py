import os
import json
from typing import Dict, Any

def load_json_file(filepath: str) -> Dict[str, Any]:
    """Loads a JSON file robustly."""
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_json_file(filepath: str, data: Any) -> bool:
    """Saves data to a JSON file, creating parent folders if needed."""
    try:
        dir_name = os.path.dirname(filepath)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False

def format_compiler_logs(logs: list) -> str:
    """Formats logs for terminal or UI stream prints."""
    return "\n".join(f"[COMPILE LOG] {log}" for log in logs)
