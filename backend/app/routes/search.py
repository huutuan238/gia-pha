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

    children_map = {}  # parent_id -> [child_id, ...] (dùng để duyệt chi)
    parent_of = {}  # child_id -> [parent_id, ...] (dùng để lấy tên bố/mẹ, tránh N+1)
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
            return jsonify(
                {"error": f"Không tìm thấy người gốc chi '{chi_person_id}'."}
            ), 404

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
    needed_parent_ids = {parent_of[p.id][0] for p in persons if parent_of.get(p.id)}
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
        result.append(
            {
                "id": p.id,
                "fullName": p.full_name,
                "gender": p.gender,
                "birthYear": p.birth_year,
                "hasSpouse": p.id in married_ids,
                "parent": parent_names.get(first_parent_id, ""),
            }
        )

    return jsonify(result), 200


from collections import deque

from app.extensions import db
from app.models import Person, Relationship


def _build_relationship_maps():
    relationships = Relationship.query.filter(
        Relationship.relation_type.in_(["PARENT", "SPOUSE"])
    ).all()

    parents_map = {}  # child_id -> [parent_id, ...]
    spouses_map = {}  # person_id -> [spouse_id, ...] (2 chiều)

    for rel in relationships:
        if rel.relation_type == "PARENT":
            parents_map.setdefault(rel.related_person_id, []).append(rel.person_id)
        elif rel.relation_type == "SPOUSE":
            spouses_map.setdefault(rel.person_id, []).append(rel.related_person_id)
            spouses_map.setdefault(rel.related_person_id, []).append(rel.person_id)

    return parents_map, spouses_map


def _get_all_ancestors(person_id, parents_map):
    """
    BFS ngược lên qua TẤT CẢ cha lẫn mẹ (không chỉ 1 nhánh cố định) để biết
    chính xác đường đi (bên nội hay bên ngoại) tới từng tổ tiên.
    Trả về: { ancestor_id: (distance, path) }
    path = [person_id, ..., ancestor_id] — đường đi thực tế đã dùng.
    """
    result = {person_id: (0, [person_id])}
    queue = deque([person_id])
    while queue:
        current_id = queue.popleft()
        current_dist, current_path = result[current_id]
        for parent_id in parents_map.get(current_id, []):
            if parent_id in result:
                continue  # BFS đảm bảo lần thăm đầu tiên là đường ngắn nhất
            result[parent_id] = (current_dist + 1, current_path + [parent_id])
            queue.append(parent_id)
    return result


def _find_nearest_common_ancestor(ancestors1, ancestors2):
    """Chọn tổ tiên chung có tổng khoảng cách (dist1+dist2) nhỏ nhất — tức gần nhất."""
    common_ids = set(ancestors1) & set(ancestors2)
    if not common_ids:
        # FIX: thiếu guard này gây ValueError: min() iterable argument is
        # empty khi 2 người không có tổ tiên chung nào (VD: vợ mới cưới về,
        # không có huyết thống chung với gia đình bên chồng).
        return None

    min_dist = min(ancestors1[cid][0] + ancestors2[cid][0] for cid in common_ids)
    candidates = [
        cid for cid in common_ids if ancestors1[cid][0] + ancestors2[cid][0] == min_dist
    ]

    best_id = next((cid for cid in candidates if _gender(cid) == "M"), candidates[0])
    dist1, path1 = ancestors1[best_id]
    dist2, path2 = ancestors2[best_id]
    return best_id, dist1, path1, dist2, path2


def _sibling_rank(person_id):
    person = db.session.get(Person, person_id)
    return person.sibling_index if person and person.sibling_index is not None else 999


def _gender(person_id):
    person = db.session.get(Person, person_id)
    return person.gender if person else None


def _full_name(person_id):
    person = db.session.get(Person, person_id)
    return person.full_name if person else None


# Có thể tuỳ chỉnh thang bậc này theo vùng miền của bạn (một số nơi dùng
# "Cố" thay "Cụ", hoặc chèn thêm "Can" trước "Kỵ")
DIRECT_ANCESTOR_TERMS = {
    1: {"M": "Cha", "F": "Mẹ"},
    2: {"M": "Ông", "F": "Bà"},
    3: {"M": "Cố Ông", "F": "Cố Bà"},
}
DIRECT_DESCENDANT_TERMS = {1: "Con", 2: "Cháu", 3: "Chắt"}


def _collateral_term(senior_path, junior_path, dist_senior, junior_direct_parent_id):
    """
    Xưng hô khi lệch đúng 1 đời (senior là anh/chị/em RUỘT hoặc HỌ của bố/mẹ junior).

    - branch_senior / branch_junior = 2 người CON TRỰC TIẾP của commonAncestor
      trên mỗi nhánh -> dùng để so sibling_index, xác định nhánh nào trưởng.
    - junior_direct_parent_id = cha/mẹ THẬT của junior (bước 1 từ junior đi lên)
      -> chỉ dùng để xác định bên nội hay ngoại (giới tính), KHÔNG dùng để so
      sibling_index.
    """
    senior_gender = _gender(senior_path[0])  # senior_path[0] luôn là chính senior
    parent_gender = _gender(junior_direct_parent_id)  # M -> bên nội, F -> bên ngoại
    is_close = dist_senior == 1

    branch_senior_id = senior_path[dist_senior - 1]
    branch_junior_id = junior_path[dist_senior]

    if parent_gender == "M":  # bên nội
        if senior_gender == "M":
            base = (
                "Bác"
                if _sibling_rank(branch_senior_id) < _sibling_rank(branch_junior_id)
                else "Chú"
            )
        else:
            base = "O"
    elif parent_gender == "F":  # bên ngoại
        base = "Cậu" if senior_gender == "M" else "Dì"
    else:
        base = "Cô/Chú/Bác/Cậu/Dì"

    return base if is_close else f"{base} họ"


def _affinal_term(blood_term, spouse_gender):
    """
    Vợ/chồng của 1 người họ hàng máu mủ thì gọi là gì.

    Nguyên tắc: ưu tiên DÙNG LẠI đúng từ đã gọi người máu mủ (VD: gọi
    người kia là "Bác" thì vợ/chồng của họ cũng gọi là "Bác") — chỉ đổi
    từ khi có cặp tương ứng rõ ràng theo giới tính (VD: "Anh" -> "Chị").
    """
    # Chồng được gọi là X (key) -> vợ của X được gọi là gì (value)
    MAP_IS_WIFE = {
        "Anh": "Chị",
        "Em": "Em",
        "Chú": "Thím",
        "Cậu": "Mợ",
        "Bác": "Bác",
        "Ông": "Bà",
    }
    # Vợ được gọi là X (key) -> chồng của X được gọi là gì (value)
    MAP_IS_HUSBAND = {
        "Chị": "Anh",
        "Em": "Em",
        "Cô": "Dượng",
        "Dì": "Dượng",
        "Bác": "Bác",
        "Bà": "Ông",
    }
    table = MAP_IS_WIFE if spouse_gender == "F" else MAP_IS_HUSBAND
    suffix = " họ" if blood_term.endswith(" họ") else ""
    mapped = table.get(blood_term.replace(" họ", ""))
    return f"{mapped}{suffix}" if mapped else None


def _term_used_by(blood, caller_id, target_id):
    """
    Trả về từ mà caller_id dùng để gọi target_id, dựa vào kết quả
    _resolve_blood_relationship — đọc đúng cho cả 3 kiểu type.

    FIX: bản cũ chỉ đọc key "senior"/"junior", nên bỏ sót hoàn toàn
    trường hợp SAME_GENERATION (dict đó dùng key "elder"/"younger"),
    khiến case "chồng gọi Anh -> vợ phải gọi Chị" luôn rơi vào UNRELATED.
    """
    if blood["type"] == "SAME_GENERATION":
        elder = blood.get("elder") or {}
        elder_id = elder.get("id")
        if elder_id is None:
            return None  # không rõ ai lớn hơn (thiếu sibling_index)
        return (
            blood.get("elderCallsYounger")
            if caller_id == elder_id
            else blood.get("youngerCallsElder")
        )

    # DIRECT_LINE / DIFFERENT_GENERATION đều dùng key "senior"/"junior"
    senior = blood.get("senior") or {}
    senior_id = senior.get("id")
    return (
        blood.get("seniorCallsJunior")
        if caller_id == senior_id
        else blood.get("juniorCallsSenior")
    )


def _resolve_blood_relationship(person1_id, person2_id, parents_map, spouses_map):
    """Trả về dict mô tả quan hệ huyết thống, hoặc None nếu không tìm thấy tổ tiên chung."""
    ancestors1 = _get_all_ancestors(person1_id, parents_map)
    ancestors2 = _get_all_ancestors(person2_id, parents_map)

    lca_result = _find_nearest_common_ancestor(ancestors1, ancestors2)
    if not lca_result:
        return None

    lca_id, dist1, path1, dist2, path2 = lca_result

    # ---- 1 người là tổ tiên trực hệ của người kia ----
    if dist1 == 0 or dist2 == 0:
        ancestor_id, descendant_id, gap = (
            (person1_id, person2_id, dist2)
            if dist1 == 0
            else (person2_id, person1_id, dist1)
        )
        ancestor_gender = _gender(ancestor_id)
        term_ladder = DIRECT_ANCESTOR_TERMS.get(gap)

        if term_ladder:
            term = term_ladder.get(ancestor_gender, "Tổ tiên")
        else:
            term = (
                "Can Ông"
                if ancestor_gender == "M"
                else ("Can Bà" if ancestor_gender == "F" else "Can")
            )

        reciprocal = DIRECT_DESCENDANT_TERMS.get(gap, "Chút")

        return {
            "type": "DIRECT_LINE",
            "generationGap": gap,
            "senior": {"id": ancestor_id, "fullName": _full_name(ancestor_id)},
            "junior": {"id": descendant_id, "fullName": _full_name(descendant_id)},
            "juniorCallsSenior": term,
            "seniorCallsJunior": reciprocal,
        }

    gap = abs(dist1 - dist2)
    senior_id, junior_id, dist_senior = (
        (person1_id, person2_id, dist1)
        if dist1 < dist2
        else (person2_id, person1_id, dist2)
    )
    senior_path = path1 if senior_id == person1_id else path2
    junior_path = path2 if senior_id == person1_id else path1

    # ---- Cùng đời ----
    if gap == 0:
        branch1_id = path1[dist1 - 1]
        branch2_id = path2[dist2 - 1]
        same_parent = branch1_id == branch2_id  # true nếu là anh em RUỘT

        if same_parent:
            rank1, rank2 = _sibling_rank(person1_id), _sibling_rank(person2_id)
        else:
            rank1, rank2 = _sibling_rank(branch1_id), _sibling_rank(branch2_id)

        if rank1 == rank2:
            elder_id, younger_id = None, None
        elif rank1 < rank2:
            elder_id, younger_id = person1_id, person2_id
        else:
            elder_id, younger_id = person2_id, person1_id

        elder_term = (
            "Anh"
            if elder_id and _gender(elder_id) == "M"
            else ("Chị" if elder_id else None)
        )

        return {
            "type": "SAME_GENERATION",
            "closeness": "ruột" if same_parent else "họ",
            "commonAncestor": {"id": lca_id, "fullName": _full_name(lca_id)},
            "elder": {"id": elder_id, "fullName": _full_name(elder_id)}
            if elder_id
            else None,
            "younger": {"id": younger_id, "fullName": _full_name(younger_id)}
            if younger_id
            else None,
            "youngerCallsElder": elder_term,
            "elderCallsYounger": "Em" if elder_id else None,
        }

    # ---- Lệch đúng 1 đời: chú/bác/cô/cậu/dì <-> cháu ----
    if gap == 1:
        junior_direct_parent_id = junior_path[1]
        term = _collateral_term(
            senior_path, junior_path, dist_senior, junior_direct_parent_id
        )
        return {
            "type": "DIFFERENT_GENERATION",
            "generationGap": gap,
            "commonAncestor": {"id": lca_id, "fullName": _full_name(lca_id)},
            "senior": {"id": senior_id, "fullName": _full_name(senior_id)},
            "junior": {"id": junior_id, "fullName": _full_name(junior_id)},
            "juniorCallsSenior": term,
            "seniorCallsJunior": "Cháu",
        }

    # ---- Lệch 2 đời trở lên: dùng gần đúng Ông/Bà (+"trẻ"/"họ" nếu là quan hệ xa) ----
    senior_gender = _gender(senior_id)
    term_ladder = DIRECT_ANCESTOR_TERMS.get(gap)

    if term_ladder:
        base_term = term_ladder.get(senior_gender, "Tổ tiên")
    else:
        base_term = (
            "Can Ông"
            if senior_gender == "M"
            else ("Can Bà" if senior_gender == "F" else "Can")
        )

    is_close = dist_senior == gap
    term = base_term if is_close else f"{base_term} họ"

    reciprocal = DIRECT_DESCENDANT_TERMS.get(gap, "Chút")

    return {
        "type": "DIFFERENT_GENERATION",
        "generationGap": gap,
        "commonAncestor": {"id": lca_id, "fullName": _full_name(lca_id)},
        "senior": {"id": senior_id, "fullName": _full_name(senior_id)},
        "junior": {"id": junior_id, "fullName": _full_name(junior_id)},
        "juniorCallsSenior": term,
        "seniorCallsJunior": reciprocal,
        "note": "Từ đời cách nhau >= 2, cách xưng hô mang tính ước lệ, có thể khác theo vùng miền.",
    }


def _resolve_affinal_relationship(root_id, spouse_id, target_id):
    """
    Xử lý trường hợp AFFINAL theo 1 chiều: root_id <-> spouse_id (là vợ/chồng
    của target_id, người có quan hệ máu mủ với root_id).

    Trả về (root_calls_spouse, spouse_calls_root) hoặc None nếu không áp dụng
    được (VD: target_id không phải "vai trên" so với spouse_id, hoặc không
    map được sang từ AFFINAL tương ứng).
    """
    blood = _resolve_blood_relationship(root_id, target_id, *_build_relationship_maps())
    if not blood:
        return None

    root_term_for_target = _term_used_by(blood, root_id, target_id)
    if not root_term_for_target:
        return None

    target_person = db.session.get(Person, target_id)
    spouse_person = db.session.get(Person, spouse_id)
    if not target_person or not spouse_person:
        return None

    affinal = _affinal_term(root_term_for_target, spouse_person.gender)
    if not affinal:
        return None

    reciprocal_term = _term_used_by(blood, target_id, root_id)
    return affinal, (reciprocal_term or "Cháu")


# ---------------------------------------------------------------------------
# API: quan hệ giữa 2 người
# ---------------------------------------------------------------------------
@search_bp.route("/relationship", methods=["GET"])
def get_relationship_between():
    person1_id = request.args.get("person1_id")
    person2_id = request.args.get("person2_id")

    if not person1_id or not person2_id:
        return jsonify({"error": "Thiếu person1_id hoặc person2_id"}), 400
    if person1_id == person2_id:
        return jsonify({"error": "Hai ID trùng nhau, không thể so sánh"}), 400

    person1 = db.session.get(Person, person1_id)
    person2 = db.session.get(Person, person2_id)
    if not person1 or not person2:
        return jsonify({"error": "Không tìm thấy 1 hoặc cả 2 người"}), 404

    parents_map, spouses_map = _build_relationship_maps()

    # ---- Trực tiếp là vợ chồng ----
    if person2_id in spouses_map.get(person1_id, []):
        return jsonify(
            {
                "type": "SPOUSE",
                "person1CallsPerson2": "Chồng" if person2.gender == "M" else "Vợ",
                "person2CallsPerson1": "Chồng" if person1.gender == "M" else "Vợ",
            }
        ), 200

    # ---- Thử quan hệ máu mủ trực tiếp trước ----
    blood = _resolve_blood_relationship(
        person1_id, person2_id, parents_map, spouses_map
    )

    if blood:
        p1_calls_p2, p2_calls_p1 = _normalize_direction(blood, person1_id, person2_id)
        return jsonify(
            {
                **blood,
                "person1CallsPerson2": p1_calls_p2,
                "person2CallsPerson1": p2_calls_p1,
            }
        ), 200

    # ---- Không cùng huyết thống trực tiếp -> thử qua vợ/chồng của bà con máu mủ ----
    # Xét cả 2 CHIỀU: person2 có thể là dâu/rể mới về (vợ/chồng của người máu
    # mủ với person1), HOẶC ngược lại person1 mới là dâu/rể (vợ/chồng của
    # người máu mủ với person2). Bản cũ chỉ xét 1 chiều nên bỏ sót nửa số case.

    # Chiều 1: person2 là vợ/chồng của ai đó có quan hệ máu mủ với person1
    for target_id in spouses_map.get(person2_id, []):
        result = _resolve_affinal_relationship(person1_id, person2_id, target_id)
        if result:
            p1_calls_p2, p2_calls_p1 = result
            return jsonify(
                {
                    "type": "AFFINAL",
                    "note": f"{person2.full_name} là vợ/chồng của người có quan hệ máu mủ với {person1.full_name}",
                    "person1CallsPerson2": p1_calls_p2,
                    "person2CallsPerson1": p2_calls_p1,
                }
            ), 200

    # Chiều 2: person1 là vợ/chồng của ai đó có quan hệ máu mủ với person2
    for target_id in spouses_map.get(person1_id, []):
        result = _resolve_affinal_relationship(person2_id, person1_id, target_id)
        if result:
            p2_calls_p1, p1_calls_p2 = result
            return jsonify(
                {
                    "type": "AFFINAL",
                    "note": f"{person1.full_name} là vợ/chồng của người có quan hệ máu mủ với {person2.full_name}",
                    "person1CallsPerson2": p1_calls_p2,
                    "person2CallsPerson1": p2_calls_p1,
                }
            ), 200

    return jsonify(
        {
            "type": "UNRELATED",
            "note": "Không tìm thấy quan hệ huyết thống hoặc hôn nhân giữa 2 người trong dữ liệu.",
        }
    ), 200


def _normalize_direction(blood, person1_id, person2_id):
    """
    Từ kết quả _resolve_blood_relationship (vốn không biết ai là person1/person2),
    suy ra đúng chiều: person1 gọi person2 là gì, và ngược lại.
    """
    if blood["type"] == "SAME_GENERATION":
        elder = blood.get("elder") or {}
        elder_id = elder.get("id")

        if elder_id == person1_id:
            return blood.get("elderCallsYounger"), blood.get("youngerCallsElder")
        if elder_id == person2_id:
            return blood.get("youngerCallsElder"), blood.get("elderCallsYounger")

        fallback = "Anh/Chị/Em (không rõ ai lớn hơn)"
        return fallback, fallback

    senior = blood.get("senior") or {}
    senior_id = senior.get("id")

    if senior_id == person1_id:
        return blood.get("seniorCallsJunior"), blood.get("juniorCallsSenior")
    if senior_id == person2_id:
        return blood.get("juniorCallsSenior"), blood.get("seniorCallsJunior")

    return None, None
