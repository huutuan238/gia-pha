"""
CRUD API cho model Family (thông tin dòng họ).

Cách đăng ký vào app (trong app/__init__.py hoặc nơi tạo Flask app):

    from .routes.families import families_bp
    app.register_blueprint(families_bp)

Nếu frontend Vue chạy ở cổng khác (vd http://localhost:5173) và gọi API
qua http://localhost:5000, cần bật CORS:

    pip install flask-cors --break-system-packages

    from flask_cors import CORS
    CORS(app)  # hoặc CORS(app, origins=["http://localhost:5173"])
"""

import uuid

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Family

families_bp = Blueprint("families", __name__, url_prefix="/api/families")


# ============================================================
# Serialize: Family model -> dict trả về cho frontend
# ============================================================
def family_to_dict(family: Family) -> dict:
    return {
        "id": family.id,
        "name": family.name,
        "foundedYear": family.founded_year,
        "branchNumber": family.branch_number,
        "ancestralHouseAddress": family.ancestral_house_address,
        "latitude": float(family.latitude) if family.latitude is not None else None,
        "longitude": float(family.longitude) if family.longitude is not None else None,
        "description": family.description,
        "createdAt": family.created_at.isoformat() if family.created_at else None,
    }


# ============================================================
# Validate: dữ liệu JSON gửi lên -> dict field hợp lệ để gán vào model
# partial=True dùng cho PUT (chỉ validate field nào được gửi lên)
# ============================================================
def validate_payload(payload, partial=False):
    errors = []
    data = {}

    # --- name: bắt buộc khi tạo mới ---
    name = payload.get("name")
    if name is not None:
        name = str(name).strip()
    if not partial and not name:
        errors.append("Tên dòng họ (name) là bắt buộc.")
    if "name" in payload:
        data["name"] = name

    # --- các trường số nguyên ---
    for field in ("founded_year", "branch_number"):
        if field in payload and payload[field] not in (None, ""):
            try:
                data[field] = int(payload[field])
            except (TypeError, ValueError):
                errors.append(f"Trường '{field}' phải là số nguyên.")
        elif field in payload:
            data[field] = None

    # --- các trường số thực (toạ độ) ---
    for field in ("latitude", "longitude"):
        if field in payload and payload[field] not in (None, ""):
            try:
                data[field] = float(payload[field])
            except (TypeError, ValueError):
                errors.append(f"Trường '{field}' phải là số.")
        elif field in payload:
            data[field] = None

    # --- các trường text tự do ---
    for field in ("ancestral_house_address", "description"):
        if field in payload:
            data[field] = payload[field]

    return data, errors


# ============================================================
# Routes
# ============================================================
@families_bp.get("")
def list_families():
    families = Family.query.order_by(Family.created_at.desc()).all()
    return jsonify([family_to_dict(f) for f in families]), 200


@families_bp.get("/<string:family_id>")
def get_family(family_id):
    family = Family.query.get(family_id)
    if not family:
        return jsonify({"error": "Không tìm thấy dòng họ."}), 404
    return jsonify(family_to_dict(family)), 200


@families_bp.post("")
def create_family():
    payload = request.get_json(silent=True) or {}
    data, errors = validate_payload(payload, partial=False)
    if errors:
        return jsonify({"errors": errors}), 400

    family = Family(id=str(uuid.uuid4()), **data)
    db.session.add(family)
    db.session.commit()
    return jsonify(family_to_dict(family)), 201


@families_bp.put("/<string:family_id>")
def update_family(family_id):
    family = Family.query.get(family_id)
    if not family:
        return jsonify({"error": "Không tìm thấy dòng họ."}), 404

    payload = request.get_json(silent=True) or {}
    data, errors = validate_payload(payload, partial=True)
    if errors:
        return jsonify({"errors": errors}), 400

    for field, value in data.items():
        setattr(family, field, value)

    db.session.commit()
    return jsonify(family_to_dict(family)), 200


@families_bp.delete("/<string:family_id>")
def delete_family(family_id):
    family = Family.query.get(family_id)
    if not family:
        return jsonify({"error": "Không tìm thấy dòng họ."}), 404

    db.session.delete(family)
    db.session.commit()
    return "", 204
