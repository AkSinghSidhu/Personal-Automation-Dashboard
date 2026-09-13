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

    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
