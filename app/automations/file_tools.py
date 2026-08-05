from pathlib import Path

def get_folder_size(path):
    
    folder = Path(path).resolve()

    if not folder.exists():
        raise FileNotFoundError("Folder does not exist")
    
    total_size = 0

    for file in folder.rglob("*"):
        if file.is_file():
            total_size += file.stat().st_size

    return total_size

def format_size(size):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

if __name__ == "__main__":
    folder_path = input("Enter folder path: ")
    size = get_folder_size(folder_path)
    print(f"Size of Folder is: {format_size(size)}")