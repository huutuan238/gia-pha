from app.models import Family, Person, Relationship
from collections import deque
from app.extensions import db
from collections import deque


def get_family_info(family_id, person_id):
    family_info: Family = db.session.get(Family, family_id)
    max_generation = count_generation(person_id)
    count = count_person(person_id)
    result = {
        "max_generation": max_generation,
        "count_person": count,
        "start_year": family_info.founded_year,
        "description": family_info.description,
        "branch_number": family_info.branch_number,
    }

    return result


def count_generation(root_id):
    # lấy tất cả quan hệ PARENT
    relationships = Relationship.query.filter(
        Relationship.relation_type == "PARENT"
    ).all()

    # map parent -> children
    children_map = {}

    for rel in relationships:
        children_map.setdefault(rel.person_id, []).append(rel.related_person_id)

    max_generation = 1

    def dfs(person_id, generation):
        nonlocal max_generation

        max_generation = max(max_generation, generation)

        for child_id in children_map.get(person_id, []):
            dfs(child_id, generation + 1)

    dfs(root_id, 1)
    return max_generation


def count_person(root_id: str) -> dict:
    relationships = Relationship.query.filter(
        Relationship.relation_type.in_(["PARENT", "SPOUSE"])
    ).all()

    # parent_id -> [child_id, ...]
    children_map = {}
    # child_id -> [parent_id, ...]  (thường có 2: cha + mẹ)
    parents_map = {}
    # person_id -> [spouse_id, ...] (2 chiều, vì Relationship SPOUSE không phân
    # biệt ai là person_id/related_person_id)
    spouses_map = {}

    for rel in relationships:
        if rel.relation_type == "PARENT":
            children_map.setdefault(rel.person_id, []).append(rel.related_person_id)
            parents_map.setdefault(rel.related_person_id, []).append(rel.person_id)
        elif rel.relation_type == "SPOUSE":
            spouses_map.setdefault(rel.person_id, []).append(rel.related_person_id)
            spouses_map.setdefault(rel.related_person_id, []).append(rel.person_id)

    # ================== SỐ CON / CHÁU / CHẮT (BFS xuôi xuống) ==================
    children_count = 0
    grandchildren_count = 0
    great_grandchildren_count = 0

    visited = {root_id}
    queue = deque([(root_id, 0)])

    while queue:
        person_id, depth = queue.popleft()

        for child_id in children_map.get(person_id, []):
            if child_id in visited:
                continue
            visited.add(child_id)

            child_depth = depth + 1
            if child_depth == 1:
                children_count += 1
            elif child_depth == 2:
                grandchildren_count += 1
            else:  # gộp chung chắt/chút/chít... từ đời thứ 4 trở đi
                great_grandchildren_count += 1

            queue.append((child_id, child_depth))

    # ================== SỐ ĐỜI (đi ngược lên theo cha/mẹ) ==================
    generation = 1
    current_id = root_id
    ancestors_visited = {root_id}

    while parents_map.get(current_id):
        current_id = parents_map[current_id][
            0
        ]  # đi theo 1 nhánh là đủ, cha/mẹ luôn cùng đời
        if current_id in ancestors_visited:
            break  # tránh vòng lặp vô hạn nếu dữ liệu quan hệ bị lỗi
        ancestors_visited.add(current_id)
        generation += 1

    # ================== BỐ / MẸ / VỢ (CHỒNG) ==================
    def person_summary(person):
        if not person:
            return None
        return {
            "id": person.id,
            "full_name": person.full_name,
            "gender": person.gender,
        }

    parent_ids = parents_map.get(root_id, [])
    parents = Person.query.filter(Person.id.in_(parent_ids)).all() if parent_ids else []
    father = next((p for p in parents if p.gender == "M"), None)
    mother = next((p for p in parents if p.gender == "F"), None)

    spouse_ids = spouses_map.get(root_id, [])
    spouses = Person.query.filter(Person.id.in_(spouse_ids)).all() if spouse_ids else []

    return {
        "generation": generation,
        "children_count": children_count,
        "grandchildren_count": grandchildren_count,
        "great_grandchildren_count": great_grandchildren_count,
        "total_descendants": children_count
        + grandchildren_count
        + great_grandchildren_count,
        "father": person_summary(father),
        "mother": person_summary(mother),
        "spouses": [person_summary(s) for s in spouses],
    }
