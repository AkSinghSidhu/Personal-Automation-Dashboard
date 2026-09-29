from pathlib import Path
from .file_tools import get_empty_directories, get_old_files
from .logger import log_operation

def preview_empty_directories(empty_dirs):
    width = 60
    title = "EMPTY FOLDERS"

    print("=" * width)
    print(title.center(width))
    print("=" * width)

    if not empty_dirs:
        print("  (No empty folders found)")
        print("=" * width)
        return

    total_folders = 0
    for folder in empty_dirs:
        print(f"  • {folder}")
        total_folders += 1

    print("-" * width)
    print(f"  Total Empty Folders: {total_folders}")
    print("=" * width)

def delete_empty_directories(empty_dirs):
    deleted_folders = []

    sorted_dirs = sorted(empty_dirs, key=lambda d: len(Path(d).parts), reverse=True)

    for dir_path in sorted_dirs:
        folder = Path(dir_path).resolve()
        try:
            if folder.exists() and folder.is_dir():
                folder.rmdir()
                deleted_folders.append(folder)
                log_operation(folder, "delete_directory", "success")
        except OSError as e:
            log_operation(folder, "delete_directory", "failed", error=str(e))
            continue

    return deleted_folders

def preview_old_files(old_files, days):
    width = 60
    title = f"OLD FILES (OLDER THAN {days} DAYS)"

    print("=" * width)
    print(title.center(width))
    print("=" * width)

    if not old_files:
        print("  (No old files found)")
        print("=" * width)
        return

    total_files = 0
    for idx, file in enumerate(old_files, 1):
        print(f"  [{idx}] {file['file']}")
        total_files += 1

    print("-" * width)
    print(f"  Total old files found: {total_files}")
    print("=" * width)

def select_files_by_index(files_list, indices_str):
    selected = []
    for part in indices_str.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(files_list):
                selected.append(files_list[idx])
    return selected

def delete_selected_files(selected_files):
    deleted_files = []
    for item in selected_files:
        file_path = item["file"] if isinstance(item, dict) else Path(item)
        try:
            file_path.unlink(missing_ok=True)
            deleted_files.append(file_path)
            log_operation(file_path, "delete_file", "success")
        except OSError as e:
            log_operation(file_path, "delete_file", "failed", error=str(e))
    return deleted_files

if __name__ == "__main__":
    empty_dirs = get_empty_directories(".")
    preview_empty_directories(empty_dirs)
    delete_empty_directories(empty_dirs)
    print("\nCleanup Complete!")

    folder = input("Enter folder path: ")
    days = int(input("Enter the number of days: "))
    old_files = get_old_files(folder, days)
    preview_old_files(old_files, days)
    
    if old_files:
        choice = input("\nEnter file numbers to delete (e.g. 1, 3) or 'all': ")
        if choice.strip().lower() == "all":
            selected = old_files
        else:
            selected = select_files_by_index(old_files, choice)
        if selected:
            deleted = delete_selected_files(selected)
            print(f"Deleted {len(deleted)} file(s).")