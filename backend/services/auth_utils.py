from functools import wraps
from flask import session, jsonify
from models import db, User


def current_user():
    uid = session.get("user_id")
    return db.session.get(User, uid) if uid else None


def role_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            u = current_user()
            if not u:
                return jsonify(error="Sila login"), 401
            if roles and u.role not in roles:
                return jsonify(error="Tiada kebenaran"), 403
            return fn(u, *a, **kw)
        return wrapper
    return deco
