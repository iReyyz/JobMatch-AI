import os
from dotenv import load_dotenv

# Load .env dari root project
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "connect_args": {"sslmode": "require"}}
