from pathlib import Path
from .file_tools import validate_directory, move_file, rename_file
from .logger import log_operation, read_last_change

def undo_move(log_entry):
    if log_entry["operation"] in ("move", "rename_and_move"):
        try:
            move_file(log_entry["new_path"], log_entry["original_path"])
            log_operation(log_entry["new_path"], "move", "success", log_entry["original_path"])
        except FileNotFoundError:
            log_operation(log_entry["new_path"], "move", "failed", log_entry["original_path"], "File not found")
        except PermissionError:
            log_operation(log_entry["new_path"], "move", "failed", log_entry["original_path"], "Permission denied")
        except (ValueError, OSError) as e:
            log_operation(log_entry["new_path"], "move", "failed", log_entry["original_path"], str(e))

def undo_rename(log_entry):
    if log_entry["operation"] == "rename":
        try:
            rename_file(log_entry["new_path"], Path(log_entry["original_path"]).name)
            log_operation(log_entry["new_path"], "rename", "success", log_entry["original_path"])
        except FileNotFoundError:
            log_operation(log_entry["new_path"], "rename", "failed", log_entry["original_path"], "File not found")
        except PermissionError:
            log_operation(log_entry["new_path"], "rename", "failed", log_entry["original_path"], "Permission denied")
        except (ValueError, OSError) as e:
            log_operation(log_entry["new_path"], "rename", "failed", log_entry["original_path"], str(e))

if __name__ == "__main__":
    last_change = read_last_change()
    if not last_change:
        print("No operations in log to undo.")
    elif last_change["operation"] in ("move", "rename_and_move"):
        undo_move(last_change)
    elif last_change["operation"] == "rename":
        undo_rename(last_change)
