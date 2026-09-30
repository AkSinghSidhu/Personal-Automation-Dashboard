from flask import Flask, jsonify

def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return jsonify({
            "status": "online",
            "name": "Personal Automation Dashboard"
        })

    return app