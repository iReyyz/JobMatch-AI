from flask import Blueprint, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from services.auth_utils import current_user

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    d = request.get_json() or {}
    if not all(d.get(k) for k in ("name", "email", "password")):
        return jsonify(error="Nama, email & password wajib"), 400
    if User.query.filter_by(email=d["email"].lower()).first():
        return jsonify(error="Email sudah digunakan"), 409
    role = d.get("role", "student")
    if role not in ("student", "company"):  # admin hanya boleh diset manual di DB
        role = "student"
    u = User(name=d["name"], email=d["email"].lower(), role=role, skills=d.get("skills", ""),
             password_hash=generate_password_hash(d["password"]))
    db.session.add(u)
    db.session.commit()
    session["user_id"] = u.id
    return jsonify(u.to_dict()), 201


@auth_bp.post("/login")
def login():
    d = request.get_json() or {}
    u = User.query.filter_by(email=(d.get("email") or "").lower()).first()
    if not u or not check_password_hash(u.password_hash, d.get("password", "")):
        return jsonify(error="Email atau password salah"), 401
    session["user_id"] = u.id
    return jsonify(u.to_dict())


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify(ok=True)


@auth_bp.get("/me")
def me():
    u = current_user()
    return jsonify(u.to_dict()) if u else (jsonify(error="Belum login"), 401)


@auth_bp.patch("/skills")
def update_skills():
    u = current_user()
    if not u:
        return jsonify(error="Sila login"), 401
    u.skills = (request.get_json() or {}).get("skills", "")
    db.session.commit()
    return jsonify(u.to_dict())
