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


from collections import deque


def _is_deceased(p):
    return bool(p.death_day or p.death_month or p.death_year)


@search_bp.route("/person", methods=["GET"])
@admin_required
def search_persons():
    chi_person_id = request.args.get("chi")
    metric = request.args.get("metric", "all")
    age_from = request.args.get("age_from", type=int)
    age_to = request.args.get("age_to", type=int)

    # ================== 1 QUERY DUY NHẤT CHO TOÀN BỘ QUAN HỆ CẦN DÙNG ==================
    relationships = Relationship.query.filter(
        Relationship.relation_type.in_(["PARENT", "SPOUSE"])
    ).all()

    children_map = {}   # parent_id -> [child_id, ...] (dùng để duyệt chi)
    parent_of = {}       # child_id -> [parent_id, ...] (dùng để lấy tên bố/mẹ, tránh N+1)
    married_ids = set()

    for rel in relationships:
        if rel.relation_type == "PARENT":
            children_map.setdefault(rel.person_id, []).append(rel.related_person_id)
            parent_of.setdefault(rel.related_person_id, []).append(rel.person_id)
        elif rel.relation_type == "SPOUSE":
            married_ids.add(rel.person_id)
            married_ids.add(rel.related_person_id)

    # ================== LỌC THEO CHI (BFS trong bộ nhớ, không query thêm) ==================
    if chi_person_id and chi_person_id != "all":
        if not Person.query.get(chi_person_id):
            return jsonify({"error": f"Không tìm thấy người gốc chi '{chi_person_id}'."}), 404

        descendant_ids = {chi_person_id}
        queue = deque([chi_person_id])
        while queue:
            current_id = queue.popleft()
            for child_id in children_map.get(current_id, []):
                if child_id not in descendant_ids:
                    descendant_ids.add(child_id)
                    queue.append(child_id)

        persons = Person.query.filter(Person.id.in_(descendant_ids)).all()
    else:
        persons = Person.query.all()

    # ================== BATCH TRUY VẤN TÊN BỐ/MẸ (thay vì query từng người) ==================
    needed_parent_ids = {
        parent_of[p.id][0] for p in persons if parent_of.get(p.id)
    }
    parent_names = {}
    if needed_parent_ids:
        parent_names = {
            pp.id: pp.full_name
            for pp in Person.query.filter(Person.id.in_(needed_parent_ids)).all()
        }

    # ================== LỌC ĐIỀU KIỆN + DỰNG KẾT QUẢ TRONG 1 VÒNG LẶP ==================
    current_year = datetime.now().year

    def matches_age(p):
        if age_from is None and age_to is None:
            return True
        if not p.birth_year:
            return False
        age = current_year - p.birth_year
        if age_from is not None and age < age_from:
            return False
        if age_to is not None and age > age_to:
            return False
        return True

    result = []
    for p in persons:
        if _is_deceased(p):
            continue
        if metric == "dinh" and p.gender != "M":
            continue
        if metric == "ho" and not (p.gender == "M" and p.id in married_ids):
            continue
        if not matches_age(p):
            continue

        first_parent_id = parent_of.get(p.id, [None])[0]
        result.append({
            "id": p.id,
            "fullName": p.full_name,
            "gender": p.gender,
            "birthYear": p.birth_year,
            "hasSpouse": p.id in married_ids,
            "parent": parent_names.get(first_parent_id, ""),
        })

    return jsonify(result), 200