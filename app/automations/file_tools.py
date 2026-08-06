from pathlib import Path

def validate_directory(path):
    directory = Path(path).resolve()

    if not directory.exists():
        raise FileNotFoundError("Path does not exist")

    if not directory.is_dir():
        raise NotADirectoryError("Path is not a directory")

    return directory

def get_folder_size(path):
    directory = validate_directory(path)
    
    total_size = 0
    for file in directory.rglob("*"):
        if file.is_file():
            total_size += file.stat().st_size

    return total_size

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

if __name__ == "__main__":
    folder_path = input("Enter folder path: ")
    size = get_folder_size(folder_path)
    folder_total = get_folder_count(folder_path)
    file_total = get_file_count(folder_path)
    print(f"Size of Folder is: {format_size(size)}")
    print(f"Number of folders in Current directory: {folder_total}")
    print(f"Number of files in Current directory: {file_total}")