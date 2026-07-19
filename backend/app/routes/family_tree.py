from collections import defaultdict

from app.services.family_tree_service import (
    get_family_info,
)
from flask import Blueprint, jsonify

from app.models import Person, Relationship


family_tree = Blueprint("tree", __name__, url_prefix="/api/family-tree")


@family_tree.route("/info/<string:family_id>", methods=["GET"])
def get_info(family_id):
    person_id = "12a9bddf-855a-4583-a695-c73fa8c0e9b2"
    result = get_family_info(family_id, person_id)
    return jsonify(result)


@family_tree.route("", methods=["GET"])
def get_persons():
    persons = Person.query.all()
    relationships = Relationship.query.all()

    # Map person_id -> rels
    rel_map = defaultdict(lambda: {"spouses": [], "children": [], "parents": []})

    for rel in relationships:
        if rel.relation_type == "PARENT":
            # parent -> child
            rel_map[rel.person_id]["children"].append(rel.related_person_id)
            rel_map[rel.related_person_id]["parents"].append(rel.person_id)

        elif rel.relation_type == "SPOUSE":
            # chỉ lưu 1 chiều trong DB nhưng trả về 2 chiều
            rel_map[rel.person_id]["spouses"].append(rel.related_person_id)
            rel_map[rel.related_person_id]["spouses"].append(rel.person_id)

    result = []

    for person in persons:
        result.append(
            {
                "id": person.id,
                "data": person.to_dict(),
                "rels": rel_map[person.id],
            }
        )

    return jsonify(result)
