import uuid

from app.services.family_tree_service import count_generation, get_person_lineage_info
from app.decorators import admin_required
from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Person, Relationship
from datetime import datetime

search_bp = Blueprint("search", __name__, url_prefix="/api/search")


@search_bp.route("/person-info/", methods=["POST"])
def search():  # thong tin tu thuy to
    id = request.get_json()
    max_generation = count_generation(id)
    person_lineage_info = get_person_lineage_info(id)
    person_lineage_info["max_generation"] = max_generation
    return jsonify(person_lineage_info)

def get_descendant_ids(root_id):
    visited = set()
    queue = [root_id]
    result = set()

    while queue:
        current = queue.pop(0)
        children = Relationship.query.filter_by(
            person_id=current, relation_type="PARENT"
        ).all()
        for rel in children:
            child_id = rel.related_person_id
            if child_id not in visited:
                visited.add(child_id)
                result.add(child_id)
                queue.append(child_id)

    return result


def _is_deceased(p):
    return bool(
        getattr(p, "death_day", None)
        or getattr(p, "death_month", None)
        or getattr(p, "death_year", None)
    )


@search_bp.route("/person", methods=["GET"])
@admin_required
def search_persons():
    chi_person_id = request.args.get("chi")
    metric = request.args.get("metric", "all")
    age_from = request.args.get("age_from", type=int)
    age_to = request.args.get("age_to", type=int)

    query = Person.query

    # ---- Lọc theo chi (con cháu của 1 person_id gốc) ----
    if chi_person_id and chi_person_id != "all":
        root_person = Person.query.get(chi_person_id)
        if not root_person:
            return jsonify({"error": f"Không tìm thấy người gốc chi '{chi_person_id}'."}), 404

        descendant_ids = get_descendant_ids(chi_person_id)
        descendant_ids.add(chi_person_id)  # tính luôn người gốc chi
        query = query.filter(Person.id.in_(descendant_ids))

    persons = query.all()

    # ---- Chỉ tính người còn sống ----
    alive = [p for p in persons if not _is_deceased(p)]

    # ---- Tính sẵn tập id đã có vợ/chồng (dùng cho metric "ho" và cột hasSpouse) ----
    spouse_relations = Relationship.query.filter_by(relation_type="SPOUSE").all()
    married_ids = set()
    for rel in spouse_relations:
        married_ids.add(rel.person_id)
        married_ids.add(rel.related_person_id)

    # ---- Lọc theo metric (đinh / hộ / tất cả) ----
    if metric == "dinh":
        alive = [p for p in alive if p.gender == "M"]
    elif metric == "ho":
        alive = [p for p in alive if p.gender == "M" and p.id in married_ids]
    # metric == "all" -> không lọc thêm

    # ---- Lọc theo độ tuổi (dựa vào birth_year) ----
    current_year = datetime.now().year

    def matches_age(p):
        if age_from is None and age_to is None:
            return True
        birth_year = getattr(p, "birth_year", None)
        if not birth_year:
            return False  # không rõ năm sinh -> loại khi có lọc tuổi
        age = current_year - birth_year
        if age_from is not None and age < age_from:
            return False
        if age_to is not None and age > age_to:
            return False
        return True

    filtered = [p for p in alive if matches_age(p)]

    result = [
        {
            "id": p.id,
            "fullName": p.full_name,
            "gender": p.gender,
            "birthYear": getattr(p, "birth_year", None),
            "hasSpouse": p.id in married_ids,
            "parent": p.parents[0].full_name if len(p.parents) else '',
        }
        for p in filtered
    ]

    return jsonify(result), 200