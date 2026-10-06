from flask import Blueprint, request, jsonify
from .automations.file_tools import get_file_size, format_size
from .automations.file_categories import create_organization_plan, execute_organization_plan
from .automations.file_inspector import inspect_path
from .automations.storage_analysis import get_category_distribution
from .automations.duplicate_finder import find_duplicate_files
from .automations.logger import read_logs

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
