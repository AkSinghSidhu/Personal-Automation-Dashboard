from pathlib import Path
from datetime import datetime
import mimetypes
from .file_tools import get_file_size, get_folder_size, format_size, get_creation_time, get_modification_time
from .file_categories import get_file_category

def inspect_path(path):
    content = Path(path).resolve()
    if not content.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    stat = content.stat()

    if content.is_dir():
        item_type = "directory"
        category = "Folder"
        size = get_folder_size(content)
        extension = None
        mime_type = None
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        try:
            created_time = datetime.fromtimestamp(stat.st_birthtime)
        except AttributeError:
            created_time = datetime.fromtimestamp(stat.st_ctime)
    else:
        item_type = "file"
        category = get_file_category(content) or "Uncategorized"
        size = get_file_size(content)
        extension = content.suffix.lower() if content.suffix else None
        mime_type = mimetypes.guess_type(str(content))[0]
        created_time = get_creation_time(content)
        modified_time = get_modification_time(content)

    return {
        "name": content.name,
        "path": str(content),
        "type": item_type,
        "category": category,
        "size": size,
        "formatted_size": format_size(size),
        "extension": extension,
        "mime_type": mime_type,
        "permissions": oct(stat.st_mode & 0o777),
        "created_time": created_time.strftime("%Y-%m-%d %H:%M:%S"),
        "modified_time": modified_time.strftime("%Y-%m-%d %H:%M:%S"),
        "is_hidden": content.name.startswith(".")
    }

if __name__ == "__main__":
    path = input("Enter path (file or folder): ")
    print(inspect_path(path))
