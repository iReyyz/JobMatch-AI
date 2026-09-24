from flask import Blueprint, jsonify
from models import db, User
from services.auth_utils import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/users")
@role_required("admin")
def users(user):
    return jsonify([u.to_dict() for u in User.query.order_by(User.id).all()])


@admin_bp.delete("/users/<int:uid>")
@role_required("admin")
def delete_user(user, uid):
    if uid == user.id:
        return jsonify(error="Tak boleh padam diri sendiri"), 400
    db.session.delete(db.get_or_404(User, uid))
    db.session.commit()
    return jsonify(ok=True)
