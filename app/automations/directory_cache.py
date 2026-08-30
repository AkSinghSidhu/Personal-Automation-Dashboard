from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from .file_tools import validate_directory, get_modification_time, build_directory_tree

db = SQLAlchemy()

class DirectorySizeCache(db.Model):
    __tablename__ = "cache"

    full_path: Mapped[str] = mapped_column(primary_key = True)
    name: Mapped[str]
    size: Mapped[int]
    mtime: Mapped[datetime]
    is_dir: Mapped[bool]
    parent_path: Mapped[str]

def traverse_directory_tree(tree, current_path, results):
    
    for content in tree["children"]:
        if "children" in content:
            results.append({
                "full_path": str(current_path / content["name"]),
                "size": content["size"],
                "name": content["name"],
                "mtime": get_modification_time(current_path / content["name"]),
                "is_dir": True,
                "parent_path": str(current_path)
            })
            traverse_directory_tree(content, current_path / content["name"], results)
        else:
            results.append({
                "full_path": str(current_path / content["name"]),
                "name": content["name"],
                "size": content["size"],
                "mtime": get_modification_time(current_path / content["name"]),
                "is_dir": False,
                "parent_path": str(current_path)
            })

    return results

def build_cache(path):
    directory = validate_directory(path)
    directory_tree = build_directory_tree(directory)
    results = [{
        "full_path": str(directory),
        "name": directory.name,
        "size": directory_tree["size"],
        "mtime": get_modification_time(directory),
        "is_dir": True,
        "parent_path": str(directory.parent)
    }]

    result = traverse_directory_tree(directory_tree, directory, results)

    for content_metadata in result:
        cache = DirectorySizeCache(
            full_path = content_metadata["full_path"],
            name = content_metadata["name"],
            size = content_metadata["size"],
            mtime = content_metadata["mtime"],
            is_dir = content_metadata["is_dir"],
            parent_path = content_metadata["parent_path"]
        )
        db.session.add(cache)
    db.session.commit()
