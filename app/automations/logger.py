from datetime import datetime
import json
from pathlib import Path

LOG_FILE = Path(__file__).parent.parent / "logs" / "operations.jsonl"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def log_operation(original_path, operation_type, result, new_path=None, error=None):
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'operation': operation_type,
        'original_path': str(original_path),
        'new_path': str(new_path) if new_path is not None else None,
        'result': result,
        'error': str(error) if error is not None else None
    }

    with open(LOG_FILE, 'a', encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + '\n')

def read_logs():
    if not LOG_FILE.exists():
        return []

    logs = []
    with open(LOG_FILE, 'r', encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                logs.append(json.loads(line))
    return logs

def read_last_change():
    if not LOG_FILE.exists():
        return []
    
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        if lines:
            last_change = json.loads(lines[-1])
    return last_change

if __name__ == "__main__":
    log_operation("original_path", "operation_type", "result", "new_path", "error")
    for log in read_logs():
        print(log)
