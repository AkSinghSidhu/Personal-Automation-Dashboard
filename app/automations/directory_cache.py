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

    try:
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
    except Exception:
        db.session.rollback()
        raise

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

def get_direct_cached_children(path):
    path = str(path)
    path = path.rstrip("/")

    result = db.session.execute(
        select(DirectorySizeCache).where(
            DirectorySizeCache.parent_path == path
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

def update_cached_folder_size(path, size, commit=True):
    cached_entry = get_cached_entry(path)
    if cached_entry:
        cached_entry.size = size
        if commit:
            db.session.commit()
    else:
        raise KeyError("Cached entry not found")

def add_cached_entry(path, commit=True):
    item = Path(path)

    if item.is_dir():
        cache = DirectorySizeCache(
            full_path=str(item),
            name=item.name,
            size=0,
            mtime=None,
            is_dir=True,
            parent_path=str(item.parent)
        )
    else:
        item = validate_file_path(item)

        cache = DirectorySizeCache(
            full_path=str(item),
            name=item.name,
            size=get_file_size(item),
            mtime=get_modification_time(item),
            is_dir=False,
            parent_path=str(item.parent)
        )

    db.session.add(cache)

    if commit:
        db.session.commit()

def rescan(path):
    directory = validate_directory(path)

    rescanned_entries = {}
    for item in directory.rglob("*"):
        try:
            rescanned_entries[str(item)] = {
                "is_dir": item.is_dir(),
                "mtime": get_modification_time(item) if item.is_file() else None,
                "parent": str(item.parent)
            }
        except OSError:
            continue

    return rescanned_entries

def get_file_changes(path):
    directory = validate_directory(path)
    rescanned_items = rescan(directory)
    rescanned_set = set(rescanned_items.keys())

    cached_entries = get_all_cached_entries(directory)
    cached_set = {entry.full_path for entry in cached_entries}

    new_files = rescanned_set - cached_set
    deleted_files = cached_set - rescanned_set

    cached_file_mtimes = {entry.full_path: entry.mtime for entry in cached_entries if not entry.is_dir}
    modified_files = {
        p for p in (rescanned_set & cached_set)
        if p in cached_file_mtimes and rescanned_items[p]["mtime"] != cached_file_mtimes[p]
    }

    return {
        "new_files": new_files,
        "deleted_files": deleted_files,
        "modified_files": modified_files
    }

def propagate_changes_upwards(path):
    direct_children = get_direct_cached_children(path)
    total_folder_size = 0

    for content in direct_children:
        if content.is_dir:
            total_folder_size += propagate_changes_upwards(content.full_path)
        else:
            total_folder_size += content.size

    update_cached_folder_size(path, total_folder_size, commit=False)
    return total_folder_size

def apply_changes(changes, path):
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
    try:
        propagate_changes_upwards(path)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise