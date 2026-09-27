from pathlib import Path
from .file_tools import get_empty_directories
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

if __name__ == "__main__":
    empty_dirs = get_empty_directories(".")
    preview_empty_directories(empty_dirs)
    delete_empty_directories(empty_dirs)
    print("\nCleanup Complete!")