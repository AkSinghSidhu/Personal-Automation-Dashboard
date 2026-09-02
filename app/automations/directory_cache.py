from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional
from .file_tools import validate_directory, validate_file_path, get_modification_time, build_directory_tree

db = SQLAlchemy()

class DirectorySizeCache(db.Model):
    __tablename__ = "cache"

    full_path: Mapped[str] = mapped_column(primary_key = True)
    name: Mapped[str]
    size: Mapped[int]
    mtime: Mapped[Optional[datetime]]
    is_dir: Mapped[bool]
    parent_path: Mapped[str]

def traverse_directory_tree(tree, current_path, results):
    
    for content in tree["children"]:
        if "children" in content:
            results.append({
                "full_path": str(current_path / content["name"]),
                "size": content["size"],
                "name": content["name"],
                "mtime": None,
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
        "mtime": None,
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

def get_cached_entry(path):
    path = str(path)
    result = db.session.execute(
        select(DirectorySizeCache).where(
            DirectorySizeCache.full_path == path
        )
    )

    cache = result.scalar_one_or_none()

    return cache

def get_all_cached_entries(path):
    path = str(path)
    if not path.endswith("/"):
        path = f"{path}{"/"}"

    result = db.session.execute(
        select(DirectorySizeCache).where(
            DirectorySizeCache.full_path.startswith(path)
        )
    )

    cache = result.scalars().all()

    return cache   
    
def delete_cached_entry(path):
    cached_entry = get_cached_entry(path)
    if cached_entry:
        db.session.delete(cached_entry)
        db.session.commit()
    else:
        raise Exception("Cached entry not found")