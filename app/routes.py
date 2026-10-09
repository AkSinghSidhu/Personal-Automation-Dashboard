from flask import Blueprint, request, jsonify
from .automations.file_tools import get_file_size, format_size, get_empty_directories, get_old_files
from .automations.file_categories import create_organization_plan, execute_organization_plan
from .automations.file_inspector import inspect_path
from .automations.storage_analysis import get_category_distribution
from .automations.duplicate_finder import find_duplicate_files
from .automations.logger import read_logs, read_last_change
from .automations.undo import undo_move, undo_rename
from .automations.cleanup import delete_empty_directories, delete_selected_files

api = Blueprint("api", __name__, url_prefix="/api")

@api.route("/inspect")
def inspect():
    file_path = request.args.get("path")

    if not file_path:
        return jsonify({"error": "Missing 'path' query parameter"}), 400
    
    try:
        result = inspect_path(file_path)
        return jsonify(result)
    except FileNotFoundError:
        return jsonify({"error": f"Path not found: {file_path}"}), 404

@api.route("/storage")
def storage():
    folder_path = request.args.get("path")

    if not folder_path:
        return jsonify({"error": "Missing 'path' query parameter"}), 400
    
    try:
        distribution = get_category_distribution(folder_path)
        total_files = sum(d["count"] for d in distribution.values())
        total_size = sum(d["size"] for d in distribution.values())

        return jsonify({ "distribution": distribution, "total_files": total_files, "total_size": total_size, "formatted_total_size": format_size(total_size) })

    except FileNotFoundError:
        return jsonify({"error": f"Path not found: {folder_path}"}), 404
    except NotADirectoryError:
        return jsonify({"error": f"Path is not a directory: {folder_path}"}), 400

@api.route("/duplicates")
def duplicates():
    folder_path = request.args.get("path")

    if not folder_path:
        return jsonify({"error": "Missing 'path' query parameter"}), 400
    
    try:
        duplicate_files = find_duplicate_files(folder_path)

        groups = []
        for file_hash, files in duplicate_files.items():
            file_size = get_file_size(files[0])
            groups.append({
                "hash": file_hash,
                "size": file_size,
                "formatted_size": format_size(file_size),
                "files": [str(f) for f in files]
            })

        return jsonify({
            "total_groups": len(groups),
            "groups": groups
        })

    except FileNotFoundError:
        return jsonify({"error": f"Path not found: {folder_path}"}), 404
    except NotADirectoryError:
        return jsonify({"error": f"Path is not a directory: {folder_path}"}), 400

@api.route("/organise/create")
def organise():
    folder_path = request.args.get("path")

    if not folder_path:
        return jsonify({"error": "Missing 'path' query parameter"}), 400
    
    try:
        organization_plan = create_organization_plan(folder_path)
        
        serialized_plan = [
            {
                "file": str(item["file"]),
                "filename": item["file"].name,
                "category": item["category"],
                "destination": str(item["destination"])
            }
            for item in organization_plan
        ]
        return jsonify(serialized_plan)

    except FileNotFoundError:
        return jsonify({"error": f"Path not found: {folder_path}"}), 404
    except NotADirectoryError:
        return jsonify({"error": f"Path is not a directory: {folder_path}"}), 400

@api.route("/organise/execute", methods=["POST"])
def execute_organise():
    data = request.get_json() or {}
    folder_path = data.get("path")

    if not folder_path:
        return jsonify({"error": "Missing 'path' in request body"}), 400

    try:
        plan = create_organization_plan(folder_path)
        execute_organization_plan(plan)
        return jsonify({"status": "success", "message": "Files organized successfully"})
    except FileNotFoundError:
        return jsonify({"error": f"Path not found: {folder_path}"}), 404
    except NotADirectoryError:
        return jsonify({"error": f"Path is not a directory: {folder_path}"}), 400

@api.route("/logs")
def logs():
    all_logs = read_logs()

    limit = request.args.get("limit", default=50, type=int)
    recent_logs = all_logs[-limit:][::-1]
    
    return jsonify({
        "total": len(all_logs),
        "logs": recent_logs
    })

@api.route("/undo", methods=["POST"])
def undo():
    last_change = read_last_change()

    if not last_change:
        return jsonify({"error": f"No operations in log to undo."}), 400
    
    try:
        if last_change["operation"] in ("move", "rename_and_move"):
            undo_move(last_change)
            return jsonify({"status": "success", "message": "Undo complete"})
        elif last_change["operation"] == "rename":
            undo_rename(last_change)
            return jsonify({"status": "success", "message": "Undo complete"})
        else:
            return jsonify({"error": f"Operation '{last_change['operation']}' cannot be undone"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route("/cleanup/preview")
def cleanup_preview():
    folder_path = request.args.get("path")
    days = request.args.get("days", default=30, type=int)

    if not folder_path:
        return jsonify({"error": "Missing 'path' query parameter"}), 400
    
    try:
        empty_dirs = [str(d) for d in get_empty_directories(folder_path)]
        old_files_list = [
            {
                "file": str(item["file"]),
                "filename": item["file"].name,
                "modified_on": item["modified_on"].strftime("%Y-%m-%d %H:%M:%S")
            }
            for item in get_old_files(folder_path, days)
        ]
        return jsonify({
            "empty_dirs": empty_dirs,
            "total_empty_dirs": len(empty_dirs),
            "old_files": old_files_list,
            "total_old_files": len(old_files_list)
        })
    except FileNotFoundError:
        return jsonify({"error": f"Path not found: {folder_path}"}), 404
    except NotADirectoryError:
        return jsonify({"error": f"Path is not a directory: {folder_path}"}), 400

@api.route("/cleanup/delete", methods=["POST"])
def execute_cleanup():
    data = request.get_json() or {}
    folder_path = data.get("path")
    empty_dirs = data.get("empty_dirs")
    files = data.get("files", [])

    if folder_path and empty_dirs is None and data.get("delete_empty_dirs"):
        try:
            empty_dirs = [str(d) for d in get_empty_directories(folder_path)]
        except (FileNotFoundError, NotADirectoryError) as e:
            return jsonify({"error": str(e)}), 400

    if not empty_dirs and not files:
        return jsonify({"error": "No empty directories or files specified for deletion"}), 400

    deleted_dirs = []
    if empty_dirs:
        deleted_dirs = [str(d) for d in delete_empty_directories(empty_dirs)]

    deleted_files = []
    if files:
        deleted_files = [str(f) for f in delete_selected_files(files)]

    return jsonify({
        "status": "success",
        "deleted_empty_directories": deleted_dirs,
        "total_deleted_directories": len(deleted_dirs),
        "deleted_files": deleted_files,
        "total_deleted_files": len(deleted_files)
    })