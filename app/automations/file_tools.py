from pathlib import Path

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
        if file.is_file():
            total_size += file.stat().st_size

    return total_size

def get_file_size(path):
    file = validate_file_path(path)

    file_size = file.stat().st_size

    return file_size

def format_size(size):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

def get_folder_count(path):
    directory = validate_directory(path)

    count = sum(1 for folder in directory.rglob("*") if folder.is_dir())

    return count

def get_file_count(path):
    directory = validate_directory(path)

    count = sum(1 for file in directory.rglob("*") if file.is_file())

    return count

def get_contents_sorted_by_size(path, descending = True):
    directory = validate_directory(path)

    content_size = []
    for content in directory.glob("*"):
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

    if descending:
        sorted_by_size = sorted(content_size, key = lambda x: x["size"], reverse = True)
    else:
        sorted_by_size = sorted(content_size, key = lambda x: x["size"])

    return sorted_by_size

if __name__ == "__main__":
    folder_path = input("Enter folder path: ")
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