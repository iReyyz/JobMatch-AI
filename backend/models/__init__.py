from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .entities import User, Job, Application, Recommendation  # noqa: E402,F401
