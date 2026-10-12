from pathlib import Path
from .file_tools import validate_directory, rename_file
from .logger import log_operation


def generate_new_name(
    file_path,
    prefix="",
    suffix="",
    find_str="",
    replace_str="",
    base_name=None,
    index=None,
    digits=3,
    case=None,
    new_extension=None
):
    path = Path(file_path)
    stem = path.stem
    ext = path.suffix

    name = base_name if base_name is not None else stem

    if find_str:
        name = name.replace(find_str, replace_str)

    if index is not None:
        num_str = str(index).zfill(digits)
        name = f"{name}_{num_str}"

    if prefix:
        name = f"{prefix}{name}"

    if suffix:
        name = f"{name}{suffix}"

    if case == "lower":
        name = name.lower()
    elif case == "upper":
        name = name.upper()
    elif case == "title":
        name = name.title()

    if new_extension:
        if not new_extension.startswith("."):
            new_extension = f".{new_extension}"
        ext = new_extension

    return f"{name}{ext}"


def create_rename_plan(
    path,
    prefix="",
    suffix="",
    find_str="",
    replace_str="",
    base_name=None,
    numbering=False,
    start_num=1,
    digits=3,
    case=None,
    new_extension=None,
    filter_ext=None
):
    directory = validate_directory(path)
    files = sorted([f for f in directory.iterdir() if f.is_file()])

    if filter_ext:
        if not filter_ext.startswith("."):
            filter_ext = f".{filter_ext}"
        files = [f for f in files if f.suffix.lower() == filter_ext.lower()]

    plan = []
    seen_destinations = set()
    current_index = start_num

    for file in files:
        idx = current_index if numbering else None
        new_name = generate_new_name(
            file,
            prefix=prefix,
            suffix=suffix,
            find_str=find_str,
            replace_str=replace_str,
            base_name=base_name,
            index=idx,
            digits=digits,
            case=case,
            new_extension=new_extension
        )
        new_path = file.with_name(new_name)

        collision_reason = None
        if new_name == file.name:
            status = "unchanged"
        elif new_path.exists() and new_path != file:
            status = "collision"
            collision_reason = "File already exists on disk"
        elif new_path in seen_destinations:
            status = "collision"
            collision_reason = "Conflict with another planned rename"
        else:
            status = "rename"
            seen_destinations.add(new_path)

        plan.append({
            "original_file": file,
            "original_name": file.name,
            "new_name": new_name,
            "new_path": new_path,
            "status": status,
            "collision_reason": collision_reason
        })

        if numbering:
            current_index += 1

    return plan


def preview_rename_plan(plan):
    width = 60
    title = "BATCH RENAME PLAN PREVIEW"

    print("=" * width)
    print(title.center(width))
    print("=" * width)

    if not plan:
        print("  (No files found to rename)")
        print("=" * width)
        return

    to_rename = [item for item in plan if item["status"] == "rename"]
    collisions = [item for item in plan if item["status"] == "collision"]
    unchanged = [item for item in plan if item["status"] == "unchanged"]

    if to_rename:
        print("\nPlanned Renames:")
        for item in to_rename:
            print(f"  • {item['original_name'].ljust(24)} -> {item['new_name']}")

    if collisions:
        print("\nCollisions / Conflicts (Skipped):")
        for item in collisions:
            print(f"  ✗ {item['original_name'].ljust(24)} -> {item['new_name']} ({item['collision_reason']})")

    if unchanged:
        print("\nUnchanged:")
        for item in unchanged:
            print(f"  - {item['original_name']}")

    print("\n" + "-" * width)
    print(f"  Total Files Evaluated: {len(plan)}")
    print(f"  To Rename:             {len(to_rename)}")
    print(f"  Collisions / Skipped:  {len(collisions)}")
    print(f"  Unchanged:             {len(unchanged)}")
    print("=" * width)


def execute_rename_plan(plan):
    results = {
        "status": "success",
        "renamed": [],
        "failed": [],
        "skipped": []
    }

    for item in plan:
        if item["status"] != "rename":
            results["skipped"].append({
                "file": str(item["original_file"]),
                "reason": item.get("collision_reason") or "No change needed"
            })
            continue

        source = item["original_file"]
        new_name = item["new_name"]

        try:
            new_path = rename_file(source, new_name)
            log_operation(source, "rename", "success", new_path)
            results["renamed"].append({
                "original": str(source),
                "new_path": str(new_path),
                "new_name": new_name
            })
        except OSError as e:
            log_operation(source, "rename", "failed", item["new_path"], error=str(e))
            results["failed"].append({
                "file": str(source),
                "error": str(e)
            })

    return results


if __name__ == "__main__":
    folder_path = input("Enter folder path: ")
    prefix_input = input("Enter prefix (or press enter to skip): ").strip()
    suffix_input = input("Enter suffix (or press enter to skip): ").strip()

    plan = create_rename_plan(
        folder_path,
        prefix=prefix_input,
        suffix=suffix_input
    )
    preview_rename_plan(plan)

    to_rename = [item for item in plan if item["status"] == "rename"]
    if to_rename:
        confirm = input("\nExecute rename plan? (y/n): ").strip().lower()
        if confirm == "y":
            result = execute_rename_plan(plan)
            print(f"\nSuccessfully renamed {len(result['renamed'])} files.")
