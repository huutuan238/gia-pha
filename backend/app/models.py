import uuid
from .extensions import db
from werkzeug.security import check_password_hash, generate_password_hash

class Person(db.Model):
    __tablename__ = "persons"

    id = db.Column(db.String(36), primary_key=True)
    family_id = db.Column(db.String(36), db.ForeignKey("families.id"), nullable=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True)
    full_name = db.Column(db.String(100), nullable=True)
    birthday = db.Column(db.Date)
    hometown = db.Column(db.String(255))
    current_address = db.Column(db.String(255))
    death_date = db.Column(db.Date)
    avatar = db.Column(db.Text)
    gender = db.Column(db.String(1))
    education = db.Column(db.String(255))
    notes = db.Column(db.Text)
    sibling_index = db.Column(db.Integer)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )
    def to_dict(self):
        return {
            "id": self.id,
            "family_id": self.family_id,
            "userId": self.user_id,
            "fullName": self.full_name,
            "birthday": self.birthday.isoformat() if self.birthday else None,
            "death_date": self.death_date.isoformat() if self.death_date else None,
            "avatar": self.avatar,
            "hometown": self.hometown,
            "currentAddress": self.current_address,
            "gender": self.gender,
            "education": self.education,
            "notes": self.notes,
            "siblingIndex": self.sibling_index,
        }


class Relationship(db.Model):
    __tablename__ = "relationships"

    id = db.Column(db.String(36), primary_key=True)
    person_id = db.Column(db.String, db.ForeignKey("persons.id"), nullable=False)
    related_person_id = db.Column(
        db.String, db.ForeignKey("persons.id"), nullable=False
    )
    relation_type = db.Column(db.String(20), nullable=False)


class Family(db.Model):
    __tablename__ = "families"

    id = db.Column(db.String(36), primary_key=True)
    # Tên dòng họ
    name = db.Column(db.String(100), nullable=False)
    # Năm bắt đầu / lập họ / đời thủy tổ
    founded_year = db.Column(db.Integer)
    # Số chi nhánh
    branch_number = db.Column(db.Integer)
    ancestral_house_address = db.Column(db.Text)
    # Dùng cho Google Map
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))

    # Mô tả thêm
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Event(db.Model):

    __tablename__ = "events"

    id = db.Column(
        db.String(36),
        primary_key=True
    )
    family_id = db.Column(
        db.String(36),
        db.ForeignKey("families.id"),
        nullable=False
    )
    event_datetime = db.Column(
        db.DateTime,
        nullable=False
    )
    event_type = db.Column(
        db.String(50),
        nullable=False
    )
    title = db.Column(
        db.String(255),
        nullable=False
    )
    location = db.Column(
        db.String(255)
    )
    description = db.Column(
        db.Text
    )
    notified = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )
    recipient_count = db.Column(
        db.Integer,
        default=0
    )
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )
    def to_dict(self):
        return {
            "id": self.id,
            "family_id": self.family_id,
            "datetime": self.event_datetime.isoformat(sep=" ") if self.event_datetime else None,
            "type": self.event_type,
            "title": self.title,
            "location": self.location,
            "description": self.description,
            "notified": self.notified,
            "recipients": self.recipient_count,
        }

def _gen_uuid():
    return str(uuid.uuid4())
 
 
class Album(db.Model):
    __tablename__ = "albums"
 
    id = db.Column(db.String(36), primary_key=True, default=_gen_uuid)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    cover_photo_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
        )
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )
 
    photos = db.relationship(
        "Photo",
        backref="album",
        cascade="all, delete-orphan",  # xoá album -> tự xoá hết ảnh trong album
        order_by="Photo.uploaded_at.desc()",
    )
 
    def to_dict(self, include_photos=False):
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "coverPhotoUrl": self.cover_photo_url,
            "photoCount": len(self.photos),
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
        if include_photos:
            data["photos"] = [p.to_dict() for p in self.photos]
        return data
 
 
class Photo(db.Model):
    __tablename__ = "photos"
 
    id = db.Column(db.String(36), primary_key=True, default=_gen_uuid)
    album_id = db.Column(
        db.String(36),
        db.ForeignKey("albums.id", ondelete="CASCADE"),
        nullable=False,
    )
    url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(500), nullable=True)
    taken_date = db.Column(db.Date, nullable=True)
    uploaded_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
        )

    def to_dict(self):
        return {
            "id": self.id,
            "albumId": self.album_id,
            "url": self.url,
            "caption": self.caption,
            "takenDate": self.taken_date.isoformat() if self.taken_date else None,
            "uploadedAt": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }
    
class User(db.Model):
    __tablename__ = "users"
 
    id = db.Column(db.String(36), primary_key=True, default=_gen_uuid)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="member", nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
 
    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)
 
    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)
 
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }