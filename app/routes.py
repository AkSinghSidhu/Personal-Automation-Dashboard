from flask import Blueprint, request, jsonify
from .automations.file_tools import format_size
from .automations.file_inspector import inspect_path
from .automations.storage_analysis import get_category_distribution, get_largest_files
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
