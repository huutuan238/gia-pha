from collections import defaultdict

from app.services.family_tree_service import (
    get_family_info,
)
from flask import Blueprint, jsonify

from app.models import Person, Relationship


family_tree = Blueprint("tree", __name__, url_prefix="/api/family-tree")


@family_tree.route("/info/<string:family_id>", methods=["GET"])
def get_info(family_id):
    person_id = "u_nguyenhuuhuan_195"
    result = get_family_info(family_id, person_id)
    return jsonify(result)


@family_tree.route("", methods=["GET"])
def get_persons():
    persons = Person.query.all()
    relationships = Relationship.query.all()

    person_map = {p.id: p for p in persons}

    rel_map = defaultdict(
        lambda: {
            "spouses": [],
            "children": [],
            "parents": [],
        }
    )

    for rel in relationships:
        if rel.relation_type == "PARENT":
            rel_map[rel.person_id]["children"].append(rel.related_person_id)
            rel_map[rel.related_person_id]["parents"].append(rel.person_id)

        elif rel.relation_type == "SPOUSE":
            if rel.related_person_id not in rel_map[rel.person_id]["spouses"]:
                rel_map[rel.person_id]["spouses"].append(rel.related_person_id)
            if rel.person_id not in rel_map[rel.related_person_id]["spouses"]:
                rel_map[rel.related_person_id]["spouses"].append(rel.person_id)

    # Sort children theo sibling_index
    for rels in rel_map.values():
        rels["children"].sort(
            key=lambda child_id: (
                person_map[child_id].sibling_index
                if person_map[child_id].sibling_index is not None
                else 999999
            )
        )

    result = []

    for person in persons:
        data = person.to_dict()

        # Tạo search_label
        parent_ids = rel_map[person.id]["parents"]

        if parent_ids:
            father = person_map[parent_ids[0]]
            father_last_name = father.full_name.split()[-1]
            data["search_label"] = f"{person.full_name}({father_last_name})"
        else:
            spouses = rel_map[person.id]["spouses"]
            if len(spouses):
                spouse = person_map[spouses[0]]
                spouse_last_name = spouse.full_name.split()[-1]
                data["search_label"] = f"{person.full_name}({spouse_last_name})"
            else:
                data["search_label"] = f"{person.full_name}"

        result.append(
            {
                "id": person.id,
                "data": data,
                "rels": rel_map[person.id],
            }
        )

    return jsonify(result)
