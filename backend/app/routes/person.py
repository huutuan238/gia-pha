import uuid

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Person, Relationship


person_bp = Blueprint(
    "person",
    __name__,
    url_prefix="/api/persons"
)


@person_bp.route("", methods=["POST"])
def add_person():

    body = request.get_json()

    if not body:
        return jsonify({"message": "Request body is required"}), 400

    data = body.get("data", {})
    rels = body.get("rels", {})

    # Kiểm tra trùng id
    if Person.query.get(body["id"]):
        return jsonify({"message": "Person already exists"}), 409

    person = Person(
        id=body["id"],
        first_name=data.get("first name", ""),
        last_name=data.get("last name", ""),
        birthday=data.get("birthday", ""),
        avatar=data.get("avatar", ""),
        gender=data.get("gender", "")
    )

    try:

        db.session.add(person)

        # Parent -> Child
        for parent_id in rels.get("parents", []):

            if not Person.query.get(parent_id):
                db.session.rollback()
                return jsonify({
                    "message": f"Parent '{parent_id}' not found"
                }), 404

            db.session.add(
                Relationship(
                    id=str(uuid.uuid4()),
                    person_id=parent_id,
                    related_person_id=person.id,
                    relation_type="PARENT"
                )
            )

        # Spouse
        for spouse_id in rels.get("spouses", []):

            if not Person.query.get(spouse_id):
                db.session.rollback()
                return jsonify({
                    "message": f"Spouse '{spouse_id}' not found"
                }), 404

            db.session.add(
                Relationship(
                    id=str(uuid.uuid4()),
                    person_id=person.id,
                    related_person_id=spouse_id,
                    relation_type="SPOUSE"
                )
            )

        db.session.commit()

        return jsonify({
            "success": True,
            "id": person.id
        }), 201

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500