from flask import Flask, jsonify
from .routes import api

def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return jsonify({
            "status": "online",
            "name": "Personal Automation Dashboard"
        })
    
    app.register_blueprint(api)
    return app