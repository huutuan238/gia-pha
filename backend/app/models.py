from .extensions import db


class Person(db.Model):

    __tablename__ = "persons"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    full_name = db.Column(
        db.String(100),
        nullable=False
    )

    birth_year = db.Column(
        db.Integer
    )

    parent_id = db.Column(
        db.Integer,
        db.ForeignKey("persons.id")
    )

    children = db.relationship(
        "Person",
        backref=db.backref(
            "parent",
            remote_side=[id]
        )
    )