"""
API quản lý user — chỉ admin mới gọi được.

Đăng ký vào app:
    from .routes.users import users_bp
    app.register_blueprint(users_bp)
"""

from flask import Blueprint, jsonify, request

from ..decorators import admin_required
from ..extensions import db
from ..models import User

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.get("")
@admin_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users]), 200


@users_bp.put("/<string:user_id>/role")
@admin_required
def update_user_role(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Không tìm thấy người dùng."}), 404

    payload = request.get_json(silent=True) or {}
    role = payload.get("role")
    if role not in ("admin", "member"):
        return jsonify({"errors": ["role phải là 'admin' hoặc 'member'."]}), 400

    user.role = role
    db.session.commit()
    return jsonify(user.to_dict()), 200
