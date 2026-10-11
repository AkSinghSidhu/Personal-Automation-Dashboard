from pathlib import Path
from .file_tools import get_empty_directories, get_old_files
from .file_tools import get_file_size, format_size
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

def select_original(files: list[Path], strategy: str = "oldest") -> tuple[Path, list[Path]]:
    if not files:
        raise ValueError("Cannot select from an empty file list.")

    if len(files) == 1:
        return files[0], []

    if strategy == "oldest":
        original = min(files, key=lambda f: f.stat().st_mtime)
    elif strategy == "newest":
        original = max(files, key=lambda f: f.stat().st_mtime)
    elif strategy == "shortest_path":
        original = min(files, key=lambda f: (len(f.parts), len(str(f))))
    else:
        original = files[0]

    duplicates_to_delete = [f for f in files if f != original]
    return original, duplicates_to_delete

def create_duplicate_cleanup_plan(duplicate_groups: dict, strategy: str = "oldest") -> dict:

    plan = {
        "strategy": strategy,
        "groups": [],
        "total_files_to_delete": 0,
        "total_bytes_freed": 0,
        "formatted_bytes_freed": "0 B"
    }

    for file_hash, files in duplicate_groups.items():
        if len(files) < 2:
            continue

        original, duplicates = select_original(files, strategy=strategy)
        file_size = get_file_size(original)
        wasted_for_group = file_size * len(duplicates)

        plan["groups"].append({
            "hash": file_hash,
            "original": original,
            "duplicates_to_delete": duplicates,
            "file_size": file_size,
            "formatted_size": format_size(file_size),
            "wasted_bytes": wasted_for_group,
            "formatted_wasted": format_size(wasted_for_group)
        })

        plan["total_files_to_delete"] += len(duplicates)
        plan["total_bytes_freed"] += wasted_for_group

    plan["formatted_bytes_freed"] = format_size(plan["total_bytes_freed"])
    return plan

def preview_duplicate_cleanup_plan(plan):
    width = 60
    title = f"DUPLICATE CLEANUP PLAN ({plan['strategy'].upper()})"

    print("=" * width)
    print(title.center(width))
    print("=" * width)

    if not plan["groups"]:
        print("  (No duplicate files found to clean up)")
        print("=" * width)
        return

    for idx, group in enumerate(plan["groups"], 1):
        print(f"\n[Group {idx}] - {group['formatted_size']} each:")
        print(f"  • [KEEP]   {group['original']}")
        for dup in group["duplicates_to_delete"]:
            print(f"  • [DELETE] {dup}")

    print("\n" + "-" * width)
    print(f"  Duplicate Groups:    {len(plan['groups'])}")
    print(f"  Files to Delete:     {plan['total_files_to_delete']}")
    print(f"  Reclaimable Storage: {plan['formatted_bytes_freed']}")
    print("=" * width)

def execute_duplicate_cleanup(plan: dict) -> dict:
    deleted_files = []
    failed_files = []

    for group in plan["groups"]:
        original = group["original"]

        if not original.exists():
            continue

        for dup_path in group["duplicates_to_delete"]:
            try:
                if dup_path.exists() and dup_path != original:
                    dup_path.unlink()
                    deleted_files.append(dup_path)
                    log_operation(dup_path, "delete_duplicate", "success")
            except OSError as e:
                failed_files.append({"file": str(dup_path), "error": str(e)})
                log_operation(dup_path, "delete_duplicate", "failed", error=str(e))

    return {
        "status": "success",
        "deleted_count": len(deleted_files),
        "deleted_files": [str(f) for f in deleted_files],
        "failed_count": len(failed_files),
        "failed_files": failed_files
    }

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