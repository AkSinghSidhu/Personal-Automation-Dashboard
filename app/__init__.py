from flask import render_template
from flask import Flask, jsonify
from .routes import api

def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("index.html")
    
    app.register_blueprint(api)
    return app