from .extensions import db


class Person(db.Model):
    __tablename__ = "persons"

    id = db.Column(
        db.String(36),
        primary_key=True
    )

    family_id = db.Column(
        db.String(36),
        db.ForeignKey("families.id"),
        nullable=True
    )

    first_name = db.Column(
        db.String(100),
        nullable=False
    )

    last_name = db.Column(
        db.String(100)
    )

    birthday = db.Column(
        db.String(20)
    )

    avatar = db.Column(
        db.Text
    )

    gender = db.Column(
        db.String(1)
    )


class Relationship(db.Model):

    __tablename__ = "relationships"

    id = db.Column(
        db.String(36),
        primary_key=True
    )

    person_id = db.Column(
        db.String,
        db.ForeignKey("persons.id"),
        nullable=False
    )

    related_person_id = db.Column(
        db.String,
        db.ForeignKey("persons.id"),
        nullable=False
    )

    relation_type = db.Column(
        db.String(20),
        nullable=False
    )

class Family(db.Model):
    __tablename__ = "families"

    id = db.Column(
        db.String(36),
        primary_key=True
    )

    # Tên dòng họ
    name = db.Column(
        db.String(100),
        nullable=False
    )

    # Năm bắt đầu / lập họ / đời thủy tổ
    founded_year = db.Column(
        db.Integer
    )

    # Số chi nhánh
    branch_number = db.Column(
        db.Integer
    )

    ancestral_house_address = db.Column(
        db.Text
    )

    # Dùng cho Google Map
    latitude = db.Column(
        db.Numeric(10, 8)
    )

    longitude = db.Column(
        db.Numeric(11, 8)
    )

    # Mô tả thêm
    description = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )