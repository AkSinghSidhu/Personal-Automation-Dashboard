from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from pathlib import Path
from typing import Optional
from .file_tools import validate_directory, validate_file_path, get_modification_time, build_directory_tree, get_file_size

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
    
def delete_cached_entry(path, commit=True):
    cached_entry = get_cached_entry(path)
    if cached_entry:
        db.session.delete(cached_entry)
        if commit:
            db.session.commit()
    else:
        raise KeyError("Cached entry not found")

def update_cached_entry(path, commit=True):
    cached_entry = get_cached_entry(path)
    if cached_entry:
        cached_entry.size = get_file_size(path)
        cached_entry.mtime = get_modification_time(path)
        if commit:
            db.session.commit()
    else:
        raise KeyError("Cached entry not found")

def add_cached_entry(path, commit=True):
    file = validate_file_path(path)

    cache = DirectorySizeCache(
        full_path = str(file),
        name = file.name,
        size = get_file_size(file),
        mtime = get_modification_time(file),
        is_dir = False,
        parent_path = str(file.parent)
    )
    db.session.add(cache)
    if commit:
        db.session.commit()

def rescan(path):
    directory = validate_directory(path)

    rescanned_files = {}
    for file in directory.rglob("*"): 
        if file.is_file():
            rescanned_files[str(file)] = get_modification_time(file)            
    
    return rescanned_files

def get_file_changes(path):
    directory = validate_directory(path)
    rescanned_files = rescan(directory)
    rescanned_set = set(rescanned_files.keys())

    cached_entries = get_all_cached_entries(directory)
    cached_files_entries = [entry for entry in cached_entries if not entry.is_dir]
    cached_set = set(entry.full_path for entry in cached_files_entries)

    new_files = rescanned_set - cached_set
    deleted_files = cached_set - rescanned_set

    cached_mtime = {entry.full_path: entry.mtime for entry in cached_files_entries}
    modified_files = {path for path in rescanned_set & cached_set if rescanned_files[path] != cached_mtime[path]}

    changes = {
        "new_files": new_files,
        "deleted_files": deleted_files,
        "modified_files": modified_files
    }

    return changes

def apply_changes(changes):
    new_files = changes["new_files"]
    deleted_files = changes["deleted_files"]
    modified_files = changes["modified_files"]

    try:
        for new_file in new_files:
            add_cached_entry(new_file, commit=False)

        for deleted_file in deleted_files:
            delete_cached_entry(deleted_file, commit=False)

        for modified_file in modified_files:
            update_cached_entry(modified_file, commit=False)

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise