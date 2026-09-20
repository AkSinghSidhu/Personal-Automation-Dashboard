from pathlib import Path
from datetime import datetime, timedelta
import hashlib, shutil

def validate_directory(path):
    directory = Path(path).resolve()

    if not directory.exists():
        raise FileNotFoundError("Path does not exist")

    if not directory.is_dir():
        raise NotADirectoryError("Path is not a directory")

    return directory

def validate_file_path(path):
    file = Path(path).resolve()

    if not file.exists():
        raise FileNotFoundError("File does not exist")

    if not file.is_file():
        raise ValueError("Given Path is not a file")

    return file

def get_folder_size(path):
    directory = validate_directory(path)
    
    total_size = 0
    for file in directory.rglob("*"):
        try:
            if file.is_file():
                total_size += get_file_size(file)
        except OSError:
            pass

    return total_size

def get_file_size(path):
    file = validate_file_path(path)

    file_size = file.stat().st_size

    return file_size

def build_directory_tree(path):
    total_folder_size = 0
    children = []

    for content in path.glob("*"):
        try:
            if content.is_dir():
                child_folder = build_directory_tree(content)
                total_folder_size += child_folder["size"]
                children.append(child_folder)
            elif content.is_file():
                curr_file_size = get_file_size(content)
                total_folder_size += curr_file_size
                child_file = {
                    "name": content.name,
                    "size": curr_file_size
                }
                children.append(child_file)
            else:
                continue
        except OSError:
            continue

    return {
        "name": path.name,
        "size": total_folder_size,
        "children": children
    }

def move_file(source, destination):
    source = Path(source).resolve()
    destination = Path(destination).resolve()

    if destination.exists():
        raise FileExistsError(f"Destination already exists: {destination}")
    if not source.exists():
        raise FileNotFoundError(f"Source file does not exist: {source}")
    if not source.is_file():
        raise ValueError(f"Source is not a file: {source}")

    destination.parent.mkdir(parents=True, exist_ok=True)

    shutil.move(str(source), str(destination))

def rename_file(path, new_name):
    file = validate_file_path(path)
    new_path = file.with_name(new_name)
    if new_path.exists():
        raise FileExistsError(f"Destination already exists: {new_path}")
    file.rename(new_path)
    return new_path


def format_size(size):
    for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} YB"

def get_folder_count(path):
    directory = validate_directory(path)

    count = sum(1 for folder in directory.rglob("*") if folder.is_dir())

    return count

def get_file_count(path):
    directory = validate_directory(path)

    count = sum(1 for file in directory.rglob("*") if file.is_file())

    return count

def get_creation_time(path):
    file = validate_file_path(path)

    try:
        create_time = datetime.fromtimestamp(file.stat().st_birthtime)
    except AttributeError:
        create_time = datetime.fromtimestamp(file.stat().st_ctime)

    return create_time

def get_modification_time(path):
    file = validate_file_path(path)

    modification_time = datetime.fromtimestamp(file.stat().st_mtime)

    return modification_time

def get_file_info(path):
    file = validate_file_path(path)

    file_info = {
        "name": file.name,
        "size": get_file_size(file),
        "extension": file.suffix,
        "creation_time": get_creation_time(file),
        "modification_time": get_modification_time(file)
    }

    return file_info

def get_contents_sorted_by_size(path, descending = True):
    directory = validate_directory(path)

    content_size = []
    for content in directory.glob("*"):
        try:
            if content.is_dir():
                size = get_folder_size(content)
            elif content.is_file():
                size = get_file_size(content)
            else:
                continue

            content_info = {
                "path": content,
                "size": size
            }
            content_size.append(content_info)
        except OSError:
            continue

    sorted_by_size = sorted(content_size, key = lambda x: x["size"], reverse = descending)

    return sorted_by_size

def get_directory_stats(path):
    directory = validate_directory(path)

    file_count = 0
    folder_count = 0
    total_size = 0

    for content in directory.rglob("*"):
        if content.is_dir():
            folder_count += 1
        elif content.is_file():
            file_count += 1
            try:
                total_size += get_file_size(content)
            except OSError:
                continue
        else:
            continue

    return {
        "files": file_count,
        "folders": folder_count,
        "total size": total_size
    }

def get_file_hash(file):
    file = validate_file_path(file)

    with open(file, "rb") as f:
        digest = hashlib.file_digest(f, "sha256")

    return digest.hexdigest()

def get_partial_file_hash(path, chunk_size = 65536):
    file = validate_file_path(path)

    with open(file, "rb") as f:
        data = f.read(chunk_size)

    return hashlib.sha256(data).hexdigest()

def get_empty_directories(path):
    directory = validate_directory(path)

    empty_directories = []
    for content in directory.rglob("*"):
        try:
            if content.is_dir():
                if next(content.iterdir(), None) is None:
                    empty_directories.append(content)
        except OSError:
            continue

    return empty_directories

def search(path, query, filter_type = None):
    directory = validate_directory(path)

    search_results = []

    if filter_type is None:
        type_check = lambda content: True
    elif filter_type == "files":
        type_check = lambda content: content.is_file()
    elif filter_type == "folders":
        type_check = lambda content: content.is_dir()
    else:
        raise ValueError(f"Invalid filter_type: '{filter_type}'")


    for content in directory.rglob("*"):
        if type_check(content) and query.lower() in content.name.lower():
            result = {
                "name": content.name,
                "path": content
                }
            search_results.append(result)

    return search_results

def get_files_by_extension(path, extension):
    directory = validate_directory(path)
    extension = extension.lower()

    if not extension.startswith("."):
        extension = "." + extension

    files_with_extension = []
    for file in directory.rglob("*"):
        if file.is_file():
            if file.suffix.lower() == extension:
                files_with_extension.append({
                    "file": file
                })

    return files_with_extension

def get_recently_modified_files(path, days):
    directory = validate_directory(path)
    now = datetime.now()
    days_ago = now - timedelta(days = days)

    modified_files = []
    for file in directory.rglob("*"):
        try:
            if file.is_file():
                modification_time = get_modification_time(file)
                if modification_time >= days_ago:
                    modified_files.append({
                        "file": file,
                        "modified_on": modification_time
                    })
        except OSError:
            continue

    return modified_files

def get_recently_created_files(path, days):
    directory = validate_directory(path)
    now = datetime.now()
    days_ago = now - timedelta(days = days)

    created_files = []
    for file in directory.rglob("*"):
        try:
            if file.is_file():
                create_time = get_creation_time(file)
                if create_time >= days_ago:
                    created_files.append({
                        "file": file,
                        "created_on": create_time
                    })
        except OSError:
            continue

    return created_files

def get_old_files(path, days):
    directory = validate_directory(path)
    now = datetime.now()
    days_ago = now - timedelta(days = days)

    old_files = []
    for file in directory.rglob("*"):
        try:
            if file.is_file():
                modification_time = get_modification_time(file)
                if modification_time <= days_ago:
                    old_files.append({
                        "file": file,
                        "modified_on": modification_time
                    })
        except OSError:
            continue

    return old_files

def sort_files_by_modified_time(modified_files, descending=True):
    sorted_by_modification_time = sorted(modified_files, key = lambda x: x["modified_on"], reverse = descending)
    
    return sorted_by_modification_time

def get_large_files(path, min_size):
    directory = validate_directory(path)
    large_files = []

    for file in directory.rglob("*"):
        try:
            if file.is_file():
                size = get_file_size(file)
                if size >= min_size:
                    large_files.append({
                        "file": file,
                        "size": size
                    })
        except OSError:
            continue

    return large_files

def sort_files_by_created_time(files, descending=True):
    sorted_by_created_time = sorted(files, key = lambda x: x["created_on"], reverse = descending)

    return sorted_by_created_time


if __name__ == "__main__":
    folder_path = input("Enter folder path: ")
    file_size_tree = build_directory_tree(validate_directory(folder_path))
    print(file_size_tree)
    size = get_folder_size(folder_path)
    folder_total = get_folder_count(folder_path)
    file_total = get_file_count(folder_path)
    sorted_files = get_contents_sorted_by_size(folder_path)
    print(f"Size of Folder is: {format_size(size)}")
    print(f"Number of folders in Current directory: {folder_total}")
    print(f"Number of files in Current directory: {file_total}")
    for content in sorted_files:
        print(f"{content['path'].name}: {format_size(content['size'])}")

    file = input("Enter File path: ")
    file_size = get_file_size(file)
    print(format_size(file_size))

    file1 = input("Enter File_1 path for its HASH: ")
    file2 = input("Enter File_2 path for its HASH: ")
    print(f"HASH of File_1: {get_file_hash(file1)}")
    print(f"HASH of File_2: {get_file_hash(file2)}")

    test_folder = input("Enter folder path: ")
    search_results = search(test_folder, "file")
    print(search_results)

    print(get_recently_modified_files(test_folder, 7))
    print(get_recently_created_files(test_folder, 7))