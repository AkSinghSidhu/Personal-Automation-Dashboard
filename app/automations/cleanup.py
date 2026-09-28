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
    for file in old_files:
        print(f"  • {file["file"]}")
        total_files += 1

    print("-" * width)
    print(f"  Total old files found: {total_files}")
    print("=" * width)

def delete_old_files(old_files):
    deleted_files = []
    for item in old_files:
        file_path = item["file"]
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
