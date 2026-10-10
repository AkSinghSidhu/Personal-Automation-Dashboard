from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.automations.file_tools import get_file_size, format_size, get_empty_directories, get_old_files
from app.automations.file_categories import create_organization_plan, execute_organization_plan
from app.automations.file_inspector import inspect_path
from app.automations.storage_analysis import get_category_distribution
from app.automations.duplicate_finder import find_duplicate_files
from app.automations.logger import read_logs, read_last_change
from app.automations.undo import undo_move, undo_rename
from app.automations.cleanup import delete_empty_directories, delete_selected_files

app = FastAPI()


class CleanupRequest(BaseModel):
    path: Optional[str] = None
    empty_dirs: Optional[list[str]] = None
    files: Optional[list[str]] = None
    delete_empty_dirs: Optional[bool] = False

@app.get("/api/inspect")
def inspect(path: str):
    try:
        return inspect_path(path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Path not found: {path}")

@app.get("/api/storage")
def storage(path: str):
    try:
        distribution = get_category_distribution(path)
        total_files = sum(d["count"] for d in distribution.values())
        total_size = sum(d["size"] for d in distribution.values())

        return {
            "distribution": distribution,
            "total_files": total_files,
            "total_size": total_size,
            "formatted_total_size": format_size(total_size)
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Path not found: {path}")
    except NotADirectoryError:
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {path}")

@app.get("/api/duplicates")
def duplicates(path: str):
    try:
        duplicate_files = find_duplicate_files(path)

        groups = []
        for file_hash, files in duplicate_files.items():
            file_size = get_file_size(files[0])
            groups.append({
                "hash": file_hash,
                "size": file_size,
                "formatted_size": format_size(file_size),
                "files": [str(f) for f in files]
            })

        return {
            "total_groups": len(groups),
            "groups": groups
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Path not found: {path}")
    except NotADirectoryError:
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {path}")

@app.get("/api/organise/create")
def organise(path: str):
    try:
        organization_plan = create_organization_plan(path)
    
        return [
                    {
                        "file": str(item["file"]),
                        "filename": item["file"].name,
                        "category": item["category"],
                        "destination": str(item["destination"])
                    }
                    for item in organization_plan
                ]

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Path not found: {path}")
    except NotADirectoryError:
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {path}")

@app.post("/api/organise/execute")
def execute_organise(path: str):
    try:
        plan = create_organization_plan(path)
        execute_organization_plan(plan)
        return {"status": "success", "message": "Files organized successfully"}
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Path not found: {path}")
    except NotADirectoryError:
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {path}")

@app.get("/api/logs")
def logs(limit: int = 50):
    all_logs = read_logs()
    recent_logs = all_logs[-limit:][::-1]
    
    return {
        "total": len(all_logs),
        "logs": recent_logs
    }

@app.post("/api/undo")
def undo():
    last_change = read_last_change()

    if not last_change:
        raise HTTPException(status_code=400, detail="No operations in log to undo.")

    if last_change["operation"] not in ("move", "rename_and_move", "rename"):
        raise HTTPException(status_code=400, detail=f"Operation '{last_change['operation']}' cannot be undone")

    try:
        if last_change["operation"] in ("move", "rename_and_move"):
            undo_move(last_change)
        elif last_change["operation"] == "rename":
            undo_rename(last_change)
        return {"status": "success", "message": "Undo complete"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error: {str(e)}")

@app.get("/api/cleanup/preview")
def cleanup_preview(path: str, days: int = 30):
    try:
        empty_dirs = [str(d) for d in get_empty_directories(path)]
        old_files_list = [
            {
                "file": str(item["file"]),
                "filename": item["file"].name,
                "modified_on": item["modified_on"].strftime("%Y-%m-%d %H:%M:%S")
            }
            for item in get_old_files(path, days)
        ]
        return {
            "empty_dirs": empty_dirs,
            "total_empty_dirs": len(empty_dirs),
            "old_files": old_files_list,
            "total_old_files": len(old_files_list)
        }
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Path not found: {path}")
    except NotADirectoryError:
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {path}")

@app.post("/api/cleanup/delete")
def execute_cleanup(payload: CleanupRequest):
    path = payload.path
    empty_dirs = payload.empty_dirs
    files = payload.files

    if path and empty_dirs is None and payload.delete_empty_dirs:
        try:
            empty_dirs = [str(d) for d in get_empty_directories(path)]

        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"Path not found: {path}")
        except NotADirectoryError:
            raise HTTPException(status_code=400, detail=f"Path is not a directory: {path}")

    if not empty_dirs and not files:
        raise HTTPException(status_code=400, detail="No empty directories or files specified for deletion")

    deleted_dirs = []
    if empty_dirs:
        deleted_dirs = [str(d) for d in delete_empty_directories(empty_dirs)]

    deleted_files = []
    if files:
        deleted_files = [str(f) for f in delete_selected_files(files)]

    return {
        "status": "success",
        "deleted_empty_directories": deleted_dirs,
        "total_deleted_directories": len(deleted_dirs),
        "deleted_files": deleted_files,
        "total_deleted_files": len(deleted_files)
    }