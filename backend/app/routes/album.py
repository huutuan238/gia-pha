"""
API cho tính năng Album ảnh.

Endpoints:
  GET    /api/albums                -> danh sách album (không kèm full photos, chỉ cover + count)
  GET    /api/albums/<album_id>     -> chi tiết 1 album kèm toàn bộ ảnh
  POST   /api/albums                -> tạo album mới          body: { title, description }
  PUT    /api/albums/<album_id>     -> sửa thông tin album     body: { title, description }
  DELETE /api/albums/<album_id>     -> xoá album (cascade xoá luôn ảnh trong album)

  POST   /api/albums/<album_id>/photos  -> upload ảnh vào album (multipart/form-data, field "file")
  DELETE /api/photos/<photo_id>         -> xoá 1 ảnh

Giả định:
- Flask app đã có `db = SQLAlchemy()` khởi tạo trong extensions.py (đổi lại cho khớp project bạn).
- Đăng ký blueprint này trong app chính: app.register_blueprint(album_bp)
- Ảnh được lưu trực tiếp trên server (thư mục UPLOAD_FOLDER), phục vụ qua route static.
  Nếu bạn dùng cloud storage (S3, Cloudinary...) thay vì lưu local, báo mình viết lại phần upload_photo.
"""

import os
import uuid
from datetime import datetime

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Album, Photo

album_bp = Blueprint("albums", __name__, url_prefix="/api")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
UPLOAD_SUBDIR = "uploads/albums"  # nằm trong thư mục static/


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _upload_folder():
    folder = os.path.join(current_app.static_folder, UPLOAD_SUBDIR)
    os.makedirs(folder, exist_ok=True)
    return folder


# ---------------------------------------------------------------------------
# Albums
# ---------------------------------------------------------------------------


@album_bp.route("/albums", methods=["GET"])
def get_albums():
    albums = Album.query.order_by(Album.created_at.desc()).all()
    return jsonify([a.to_dict() for a in albums]), 200


@album_bp.route("/albums/<album_id>", methods=["GET"])
def get_album_detail(album_id):
    album = Album.query.get(album_id)
    if not album:
        return jsonify({"message": "Không tìm thấy album"}), 404
    return jsonify(album.to_dict(include_photos=True)), 200


@album_bp.route("/albums", methods=["POST"])
def create_album():
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    if not title:
        return jsonify({"message": "Thiếu tiêu đề album"}), 400

    album = Album(title=title, description=payload.get("description"))
    db.session.add(album)
    db.session.commit()
    return jsonify(album.to_dict()), 201


@album_bp.route("/albums/<album_id>", methods=["PUT"])
def update_album(album_id):
    album = Album.query.get(album_id)
    if not album:
        return jsonify({"message": "Không tìm thấy album"}), 404

    payload = request.get_json(silent=True) or {}
    if "title" in payload:
        title = (payload.get("title") or "").strip()
        if not title:
            return jsonify({"message": "Tiêu đề không được để trống"}), 400
        album.title = title
    if "description" in payload:
        album.description = payload.get("description")

    db.session.commit()
    return jsonify(album.to_dict()), 200


@album_bp.route("/albums/<album_id>", methods=["DELETE"])
def delete_album(album_id):
    album = Album.query.get(album_id)
    if not album:
        return jsonify({"message": "Không tìm thấy album"}), 404

    # Xoá luôn file ảnh vật lý trên disk trước khi xoá record
    for photo in album.photos:
        _delete_photo_file(photo.url)

    db.session.delete(album)  # cascade xoá hết Photo nhờ relationship ở model
    db.session.commit()
    return jsonify({"message": "Đã xoá album"}), 200


# ---------------------------------------------------------------------------
# Photos
# ---------------------------------------------------------------------------


@album_bp.route("/albums/<album_id>/photos", methods=["POST"])
def upload_photo(album_id):
    album = Album.query.get(album_id)
    if not album:
        return jsonify({"message": "Không tìm thấy album"}), 404

    if "file" not in request.files:
        return jsonify({"message": "Thiếu file ảnh"}), 400

    file = request.files["file"]
    if file.filename == "" or not _allowed_file(file.filename):
        return jsonify(
            {"message": "File không hợp lệ (chỉ nhận png/jpg/jpeg/gif/webp)"}
        ), 400

    ext = file.filename.rsplit(".", 1)[1].lower()
    stored_name = f"{uuid.uuid4()}.{ext}"
    file.save(os.path.join(_upload_folder(), secure_filename(stored_name)))

    photo_url = f"/static/{UPLOAD_SUBDIR}/{stored_name}"

    photo = Photo(
        album_id=album.id,
        url=photo_url,
        caption=request.form.get("caption"),
    )
    taken_date_str = request.form.get("takenDate")
    if taken_date_str:
        try:
            photo.taken_date = datetime.strptime(taken_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass  # bỏ qua nếu format ngày không hợp lệ, không chặn upload

    db.session.add(photo)

    # Nếu album chưa có ảnh bìa, lấy luôn ảnh đầu tiên làm bìa
    if not album.cover_photo_url:
        album.cover_photo_url = photo_url

    db.session.commit()
    return jsonify(photo.to_dict()), 201


@album_bp.route("/photos/<photo_id>", methods=["DELETE"])
def delete_photo(photo_id):
    photo = Photo.query.get(photo_id)
    if not photo:
        return jsonify({"message": "Không tìm thấy ảnh"}), 404

    album = photo.album
    was_cover = album.cover_photo_url == photo.url

    _delete_photo_file(photo.url)
    db.session.delete(photo)
    db.session.flush()

    # Nếu ảnh vừa xoá là ảnh bìa, tự chọn ảnh còn lại (mới nhất) làm bìa mới
    if was_cover:
        remaining = (
            Photo.query.filter_by(album_id=album.id)
            .order_by(Photo.uploaded_at.desc())
            .first()
        )
        album.cover_photo_url = remaining.url if remaining else None

    db.session.commit()
    return jsonify({"message": "Đã xoá ảnh"}), 200


def _delete_photo_file(photo_url):
    """Xoá file vật lý trên disk tương ứng với photo_url (bỏ qua nếu không tìm thấy)."""
    if not photo_url or not photo_url.startswith(f"/static/{UPLOAD_SUBDIR}/"):
        return
    filename = photo_url.rsplit("/", 1)[-1]
    filepath = os.path.join(_upload_folder(), filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass
