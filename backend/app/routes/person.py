from flask import Blueprint, jsonify, request

from app.models import Person, Relationship
from app.extensions import db


person_bp = Blueprint(
    "person",
    __name__,
    url_prefix="/api/persons"
)


@person_bp.route("", methods=["GET"])
def get_persons():
    persons = Person.query.all()

    result = []

    for person in persons:

        rels = {
            "spouses": [],
            "children": [],
            "parents": []
        }


        # person -> spouse / children
        relationships = Relationship.query.filter(
            Relationship.person_id == person.id
        ).all()


        for rel in relationships:

            if rel.relation_type == "SPOUSE":

                rels["spouses"].append(
                    str(rel.related_person_id)
                )


            elif rel.relation_type == "PARENT":

                # person là cha/mẹ
                rels["children"].append(
                    str(rel.related_person_id)
                )


        # lấy parents của person
        parent_relationships = Relationship.query.filter(
            Relationship.related_person_id == person.id,
            Relationship.relation_type == "PARENT"
        ).all()


        for rel in parent_relationships:

            rels["parents"].append(
                str(rel.person_id)
            )


        result.append(
            {
                "id": str(person.id),

                "data": {
                    "first name": person.first_name,
                    "last name": person.last_name or "",
                    "birthday": person.birthday or "",
                    "avatar": person.avatar or "",
                    "gender": person.gender or ""
                },

                "rels": rels
            }
        )


    return jsonify(result)
