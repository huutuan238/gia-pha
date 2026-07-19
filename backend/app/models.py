from .extensions import db


class Person(db.Model):
    __tablename__ = "persons"

    id = db.Column(db.String(36), primary_key=True)
    family_id = db.Column(db.String(36), db.ForeignKey("families.id"), nullable=True)
    full_name = db.Column(db.String(100), nullable=True)
    birthday = db.Column(db.Date)
    hometown = db.Column(db.String(255))
    current_address = db.Column(db.String(255))
    death_date = db.Column(db.Date)
    avatar = db.Column(db.Text)
    gender = db.Column(db.String(1))
    education = db.Column(db.String(255))
    note = db.Column(db.Text)
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
            "full_name": self.full_name,
            "birthday": self.birthday.isoformat() if self.birthday else None,
            "death_date": self.death_date.isoformat() if self.death_date else None,
            "avatar": self.avatar,
            "hometown": self.hometown,
            "current_address": self.current_address,
            "gender": self.gender,
            "education": self.education,
            "note": self.note,
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
