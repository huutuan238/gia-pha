"""
Decorator dùng chung: chặn API chỉ cho user có role "admin" (lấy từ JWT claims).

Cách dùng:
    from ..decorators import admin_required

    @events_bp.post("")
    @admin_required
    def create_event():
        ...

Lưu ý: role được nhúng vào token lúc login/register
(xem create_access_token(..., additional_claims={"role": user.role})
trong routes/auth.py) — nếu role của user đổi sau khi đăng nhập,
họ cần đăng nhập lại để token có role mới.
"""

from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()  # báo lỗi 401 nếu thiếu/token không hợp lệ
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"error": f"{claims}"}), 403
        return fn(*args, **kwargs)

    return wrapper
