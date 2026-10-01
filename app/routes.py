from flask import Blueprint, request, jsonify
from .automations.file_inspector import inspect_path

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
