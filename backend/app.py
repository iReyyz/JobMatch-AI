import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from config.settings import Config
from models import db
from routes.auth import auth_bp
from routes.jobs import jobs_bp
from routes.admin import admin_bp

FRONTEND = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))


def create_app():
    # Flask hidang folder frontend/ terus sebagai static files
    app = Flask(__name__, static_folder=FRONTEND, static_url_path="")
    app.config.from_object(Config)
    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        raise RuntimeError("DATABASE_URL belum diset. Salin .env.example -> .env")
    CORS(app)
    db.init_app(app)
    for bp in (auth_bp, jobs_bp, admin_bp):
        app.register_blueprint(bp)

    @app.get("/")
    def index():
        return send_from_directory(FRONTEND, "index.html")

    @app.get("/api/health")
    def health():
        db.session.execute(db.text("SELECT 1"))
        return {"status": "ok", "db": "connected"}

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
