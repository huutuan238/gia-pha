import os
import uuid
from datetime import datetime

import boto3
from botocore.exceptions import ClientError, BotoCoreError
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Album, Photo

album_bp = Blueprint("albums", __name__, url_prefix="/api")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
S3_KEY_PREFIX = "albums"  # tương đương UPLOAD_SUBDIR cũ, nhưng là "thư mục ảo" trong bucket


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _s3_client():
    return boto3.client(
        "s3",
        region_name=current_app.config["AWS_REGION"],
        aws_access_key_id=current_app.config.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=current_app.config.get("AWS_SECRET_ACCESS_KEY"),
    )


def _bucket_name():
    return current_app.config["S3_BUCKET_NAME"]


def _build_public_url(key):
    """Ưu tiên dùng CDN (CloudFront) nếu có cấu hình, không thì dùng URL S3 mặc định."""
    base = current_app.config.get("S3_PUBLIC_BASE_URL")  # ví dụ: https://cdn.giapha.com
    if base:
        return f"{base.rstrip('/')}/{key}"
    region = current_app.config["AWS_REGION"]
    return f"https://{_bucket_name()}.s3.{region}.amazonaws.com/{key}"


def _extract_s3_key(photo_url):
    """Lấy lại object key trong bucket từ URL đã lưu, để phục vụ xoá."""
    if not photo_url or f"/{S3_KEY_PREFIX}/" not in photo_url:
        return None
    return f"{S3_KEY_PREFIX}/{photo_url.split(f'/{S3_KEY_PREFIX}/', 1)[1]}"


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

    # Xoá luôn object trên S3 trước khi xoá record
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
    stored_name = secure_filename(f"{uuid.uuid4()}.{ext}")
    s3_key = f"{S3_KEY_PREFIX}/{stored_name}"

    try:
        _s3_client().upload_fileobj(
            file,
            _bucket_name(),
            s3_key,
            ExtraArgs={"ContentType": file.mimetype or "application/octet-stream"},
        )
    except (ClientError, BotoCoreError) as e:
        current_app.logger.error(f"Upload S3 thất bại: {e}")
        return jsonify({"message": "Không thể tải ảnh lên. Vui lòng thử lại."}), 500

    photo_url = _build_public_url(s3_key)

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
    """Xoá object trên S3 tương ứng với photo_url (bỏ qua nếu không parse được key)."""
    key = _extract_s3_key(photo_url)
    if not key:
        return
    try:
        _s3_client().delete_object(Bucket=_bucket_name(), Key=key)
    except (ClientError, BotoCoreError) as e:
        current_app.logger.warning(f"Xoá S3 object thất bại ({key}): {e}")