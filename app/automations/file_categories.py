from pathlib import Path
from .file_tools import validate_directory, get_file_size, get_file_hash
from .logger import log_operation
import shutil

FILE_CATEGORIES = {
    "Images": {
        ".jpg", ".jpeg", ".jpe", ".jfif",
        ".png", ".gif", ".bmp", ".webp",
        ".tif", ".tiff", ".ico", ".svg",
        ".heic", ".heif", ".avif",
        ".raw", ".cr2", ".cr3", ".nef",
        ".arw", ".dng", ".orf", ".rw2",
        ".psd", ".xcf", ".ai", ".eps"
    },

    "Videos": {
        ".mp4", ".m4v", ".mkv", ".mov",
        ".avi", ".wmv", ".flv", ".webm",
        ".mpeg", ".mpg", ".mpe", ".m2v",
        ".mts", ".m2ts", ".3gp",
        ".3g2", ".vob", ".ogv", ".rm",
        ".rmvb", ".asf"
    },

    "Audio": {
        ".mp3", ".wav", ".flac", ".aac",
        ".m4a", ".ogg", ".oga", ".opus",
        ".wma", ".aiff", ".aif", ".aifc",
        ".alac", ".ape", ".mid", ".midi",
        ".amr", ".ac3", ".dts", ".mka"
    },

    "Documents": {
        ".pdf",
        ".doc", ".docx", ".docm", ".dot", ".dotx",
        ".odt", ".ott", ".rtf", ".txt",
        ".tex", ".wpd", ".pages",
        ".epub", ".mobi", ".azw", ".azw3",
        ".fb2", ".djvu",
        ".eml", ".msg"
    },

    "Spreadsheets": {
        ".xls", ".xlsx", ".xlsm", ".xlsb",
        ".xlt", ".xltx", ".ods", ".ots",
        ".csv", ".tsv", ".numbers"
    },

    "Presentations": {
        ".ppt", ".pptx", ".pptm",
        ".pot", ".potx", ".pps", ".ppsx",
        ".odp", ".otp", ".key"
    },

    "Archives": {
        ".zip", ".rar", ".7z", ".tar",
        ".gz", ".bz2", ".xz", ".zst",
        ".lz", ".lz4", ".lzma",
        ".tgz", ".tbz", ".txz",
        ".cab", ".arj", ".ace",
        ".war", ".ear"
    },

    "Disk Images": {
        ".iso", ".img", ".dmg", ".vhd",
        ".vhdx", ".vmdk", ".vdi", ".qcow",
        ".qcow2", ".ova", ".ovf", ".bin",
        ".cue", ".nrg", ".mdf", ".mds"
    },

    "Executables": {
        ".exe", ".msi", ".msix", ".appx",
        ".deb", ".rpm", ".appimage",
        ".run", ".com", ".bat", ".cmd",
        ".sh", ".bash", ".zsh",
        ".dll", ".so", ".dylib"
    },

    "Code": {
        ".py", ".pyw",
        ".js", ".jsx", ".mjs", ".cjs",
        ".ts", ".tsx",
        ".java", ".class", ".jar",
        ".c", ".h", ".cc", ".cpp", ".cxx",
        ".hpp", ".cs",
        ".go", ".rs", ".swift", ".kt", ".kts",
        ".php", ".rb", ".pl", ".pm",
        ".lua", ".r", ".R",
        ".dart", ".scala", ".groovy",
        ".hs", ".fs", ".fsx", ".vb",
        ".asm", ".s",
        ".sql",
        ".html", ".htm", ".css", ".scss", ".sass", ".less",
        ".vue", ".svelte"
    },

    "Data": {
        ".json", ".jsonl",
        ".xml", ".yaml", ".yml",
        ".toml", ".ini", ".cfg", ".conf",
        ".env",
        ".db", ".sqlite", ".sqlite3",
        ".mdb", ".accdb",
        ".dbf", ".dat"
    },

    "Fonts": {
        ".ttf", ".otf", ".woff", ".woff2",
        ".eot"
    },

    "Subtitles": {
        ".srt", ".vtt", ".ass", ".ssa",
        ".sub", ".sbv"
    },

    "3D": {
        ".obj", ".fbx", ".gltf", ".glb",
        ".stl", ".3ds", ".blend",
        ".dae", ".abc", ".ply",
        ".max", ".ma", ".mb"
    },

    "Design": {
        ".fig", ".sketch", ".xd",
        ".indd", ".indt",
        ".cdr", ".afdesign", ".afphoto",
        ".kra", ".ora"
    },

    "Game Files": {
        ".pak", ".pk3", ".pk4",
        ".wad", ".bsp",
        ".rom", ".nes", ".sfc", ".smc",
        ".gba", ".gb", ".gbc",
        ".nds", ".n64", ".z64",
        ".sav"
    },

    "Torrents": {
        ".torrent"
    },

    "Backups": {
        ".bak", ".backup", ".old",
        ".tmp", ".temp",
        ".swp", ".swo"
    }
}

def create_organization_plan(path):
    directory = validate_directory(path)
    organization_plan = []
    for content in directory.glob("*"):
        if content.is_file():
            file_category = get_file_category(content)
            destination_path = get_file_destination(content, file_category)

            file_info = {
                "file": content,
                "category": file_category,
                "destination": destination_path
            }
            organization_plan.append(file_info)

    return organization_plan
    

def get_file_category(file):
    extension = file.suffix.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category

    return None

def get_file_destination(file, category):
    if category is None:
        destination_path = file.parent / file.name
    else:
        destination_path = file.parent / category / file.name

    return destination_path

def ensure_destination_directory(destination_directory):
    destination_directory.mkdir(parents=True, exist_ok=True)

def auto_rename_content(destination):
    number = 1

    while destination.exists():
        new_name = destination.stem + "_" + str(number) + destination.suffix
        candidate = destination.parent / new_name

        if not candidate.exists():
            return candidate

        number += 1

    return destination

def collision_detection(destination, curr_file):
    same_file = False
    if destination.exists():
        size_of_destination = get_file_size(destination)
        size_of_curr_file = get_file_size(curr_file)
        if size_of_destination == size_of_curr_file:
            hash_of_destination = get_file_hash(destination)
            hash_of_curr_file = get_file_hash(curr_file)
            if hash_of_destination == hash_of_curr_file:
                same_file = True
                return (destination, same_file)
            else:
                new_destination = auto_rename_content(destination)

        else:
            new_destination = auto_rename_content(destination)

    else:
        return (destination, same_file)

    return (new_destination, same_file)

def execute_organization_plan(organization_plan):
    for item in organization_plan:
        source = item["file"]
        planned_destination = item["destination"]
        try:
            destination, same_file = collision_detection(planned_destination, source)
            op_type = "rename_and_move" if destination != planned_destination else "move"
        except OSError:
            continue

        if same_file:
            log_operation(source, "skip_duplicate", "success")
            continue

        try:
            ensure_destination_directory(item["destination"].parent)
            shutil.move(source, destination)
            log_operation(source, op_type, "success", destination)
        except FileNotFoundError:
            log_operation(source, op_type, "failed", destination, "File not found")
            continue
        except PermissionError:
            log_operation(source, op_type, "failed", destination, "Permission denied")
            continue
        except shutil.Error as e:
            log_operation(source, op_type, "failed", destination, str(e))
            continue

def preview_organization_plan(plan):
    width = 50
    title = "ORGANIZATION PLAN PREVIEW"

    print("=" * width)
    print(title.center(width))
    print("=" * width)

    if not plan:
        print("  (No files found in folder to organize)")
        print("=" * width)
        return

    source_folder = plan[0]["file"].parent
    print(f"Source Folder: {source_folder}\n")

    print("Planned Moves:")
    move_file_count = 0
    for item in plan:
        if item["category"] is not None:
            move_file_count += 1
            file_name = item["file"].name
            dest = f"{item['category']}/{file_name}"
            print(f"  • {file_name.ljust(20)} -> {dest}")

    if move_file_count == 0:
        print("  (None)")

    print("\nSkipped (No category / Stays in place):")
    skip_file_count = 0
    for item in plan:
        if item["category"] is None:
            skip_file_count += 1
            print(f"  • {item['file'].name}")

    if skip_file_count == 0:
        print("  (None)")

    print("-" * width)
    print(f"Total: {move_file_count + skip_file_count} | To move: {move_file_count} | To skip: {skip_file_count}")
    print("=" * width)



if __name__ == "__main__":
    folder_path = input("Enter folder path: ")
    organization_plan = create_organization_plan(folder_path)
    print(organization_plan)

    execution_test = execute_organization_plan(organization_plan)