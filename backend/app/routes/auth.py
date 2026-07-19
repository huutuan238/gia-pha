"""
API đăng ký / đăng nhập, dùng JWT (flask-jwt-extended).

Cài đặt:
    pip install flask-jwt-extended --break-system-packages

Đăng ký vào app (trong app/__init__.py hoặc nơi tạo Flask app):

    from flask_jwt_extended import JWTManager
    from .routes.auth import auth_bp

    app.config["JWT_SECRET_KEY"] = "đổi-thành-chuỗi-bí-mật-that-dai-va-kho-doan"
    JWTManager(app)
    app.register_blueprint(auth_bp)

Trước khi dùng, nhớ đã gộp class User (xem models_user_addon.py) vào
app/models.py, và đã chạy migration để tạo bảng "users".
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from ..extensions import db
from ..models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    errors = []
    if not username:
        errors.append("Tên đăng nhập là bắt buộc.")
    if not email:
        errors.append("Email là bắt buộc.")
    if len(password) < 6:
        errors.append("Mật khẩu phải có ít nhất 6 ký tự.")

    if not errors:
        if User.query.filter_by(username=username).first():
            errors.append("Tên đăng nhập đã được sử dụng.")
        if User.query.filter_by(email=email).first():
            errors.append("Email đã được đăng ký.")

    if errors:
        return jsonify({"errors": errors}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    identifier = (payload.get("identifier") or "").strip()
    password = payload.get("password") or ""

    if not identifier or not password:
        return jsonify({"error": "Vui lòng nhập đầy đủ tên đăng nhập/email và mật khẩu."}), 400

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier.lower())
    ).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Tên đăng nhập hoặc mật khẩu không đúng."}), 401

    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Không tìm thấy người dùng."}), 404
    return jsonify(user.to_dict()), 200