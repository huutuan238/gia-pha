from .extensions import db


class Person(db.Model):

    __tablename__ = "persons"

    id = db.Column(
        db.Integer,
        primary_key=True
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
        db.Integer,
        primary_key=True
    )

    person_id = db.Column(
        db.Integer,
        db.ForeignKey("persons.id"),
        nullable=False
    )

    related_person_id = db.Column(
        db.Integer,
        db.ForeignKey("persons.id"),
        nullable=False
    )

    relation_type = db.Column(
        db.String(20),
        nullable=False
    )