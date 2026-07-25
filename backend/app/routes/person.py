import uuid

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Person, Relationship


person_bp = Blueprint("person", __name__, url_prefix="/api/persons")


@person_bp.route("/", methods=["POST"])
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
        family_id="8b6c4f0e-7f3a-4d8e-9a61-2e7b5c9d1f20",
        user_id=data.get("userId", ""),
        full_name=data.get("fullName", ""),
        birthday=data.get("birthday", ""),
        avatar="",
        gender=data.get("gender", ""),
        hometown=data.get("hometown", ""),
        current_address=data.get("currentAddress", ""),
        death_date=data.get("deathDate") or None,
        education=data.get("education", ""),
        notes=data.get("notes", ""),
        sibling_index=data.get("siblingIndex", ""),
    )

    try:
        db.session.add(person)

        # Parent -> Child
        for parent_id in rels.get("parents", []):
            if not Person.query.get(parent_id):
                db.session.rollback()
                return jsonify({"message": f"Parent '{parent_id}' not found"}), 404

            db.session.add(
                Relationship(
                    id=str(uuid.uuid4()),
                    person_id=parent_id,
                    related_person_id=person.id,
                    relation_type="PARENT",
                )
            )

        # Spouse
        for spouse_id in rels.get("spouses", []):
            if not Person.query.get(spouse_id):
                db.session.rollback()
                return jsonify({"message": f"Spouse '{spouse_id}' not found"}), 404

            db.session.add(
                Relationship(
                    id=str(uuid.uuid4()),
                    person_id=person.id,
                    related_person_id=spouse_id,
                    relation_type="SPOUSE",
                )
            )

        db.session.commit()

        return jsonify({"success": True, "id": person.id}), 201

    except Exception as e:
        db.session.rollback()

        return jsonify({"success": False, "message": str(e)}), 500


@person_bp.route("/<string:person_id>", methods=["PUT"])
def update_person(person_id):
    body = request.get_json()
    person: Person = db.session.get(Person, person_id)
    if not person:
        return jsonify({"message": "Person not found"}), 404

    data = body.get("data", {})
    try:
        person.full_name = data.get("fullName", "")
        person.birthday = data.get("birthday", "")
        person.avatar = data.get("avatar", "")
        person.gender = data.get("gender", "")
        person.hometown = data.get("hometown", "")
        person.current_address = data.get("currentAddress", "")
        person.death_date = data.get("deathDate") or None
        person.education = data.get("education", "")
        person.notes = data.get("notes", "")
        person.sibling_index = data.get("siblingIndex", "")

        db.session.commit()

        return jsonify({"success": True, "id": person_id})

    except Exception as e:
        db.session.rollback()

        return jsonify({"message": str(e)}), 500


@person_bp.route("/<string:person_id>", methods=["DELETE"])
def delete_person(person_id):
    person = db.session.get(Person, person_id)
    if not person:
        return jsonify({"message": "Person not found"}), 404

    try:
        # xóa relationship trước->k xoa vi nhung nguoi k ket hon van co con
        Relationship.query.filter(
            db.or_(
                Relationship.person_id == person_id,
                Relationship.related_person_id == person_id,
            )
        ).delete()
        # xóa person
        db.session.delete(person)
        db.session.commit()
        return jsonify({"success": True, "id": person_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@person_bp.route("/update-relationships", methods=["POST"])
def update_relationship():
    body = request.get_json()
    if not body:
        return jsonify({"message": "Request body is required"}), 400
    parent_id = body.get("parentId")
    childrens = body.get("childrens")
    if not parent_id or not len(childrens):
        return jsonify({"message": "Person not found"}), 404

    try:
        for children_id in childrens:
            db.session.add(
                Relationship(
                    id=str(uuid.uuid4()),
                    person_id=parent_id,
                    related_person_id=children_id,
                    relation_type="PARENT",
                )
            )
        db.session.commit()
        return jsonify({"success": True, "id": parent_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500
