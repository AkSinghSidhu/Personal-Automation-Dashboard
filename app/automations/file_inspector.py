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

def preview_inspection(metadata):
    width = 60
    title = "FILE/FOLDER METADATA PREVIEW"

    print("=" * width)
    print(title.center(width))
    print("=" * width)

    if not metadata:
        print("  (No metadata found)")
        print("=" * width)
        return

    print(f"  • {'name':<16} -> {metadata['name']}")
    print(f"  • {'path':<16} -> {metadata['path']}")
    print(f"  • {'type':<16} -> {metadata['type']}")
    print(f"  • {'category':<16} -> {metadata['category']}")
    print(f"  • {'size':<16} -> {metadata['formatted_size']}")
    print(f"  • {'extension':<16} -> {metadata['extension'] or 'N/A'}")
    print(f"  • {'mime_type':<16} -> {metadata['mime_type'] or 'N/A'}")
    print(f"  • {'permissions':<16} -> {metadata['permissions']}")
    print(f"  • {'created_on':<16} -> {metadata['created_time']}")
    print(f"  • {'modified_on':<16} -> {metadata['modified_time']}")
    print(f"  • {'hidden':<16} -> {'Yes' if metadata['is_hidden'] else 'No'}")

    print("=" * width)


if __name__ == "__main__":
    path = input("Enter path (file or folder): ")
    metadata = inspect_path(path)
    preview_inspection(metadata)

