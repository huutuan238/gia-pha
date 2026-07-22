from app.models import Family, Relationship
from collections import deque
from app.extensions import db


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


def count_person(root_id: str) -> int:
    relationships = Relationship.query.filter(
        Relationship.relation_type == "PARENT"
    ).all()

    # parent -> children
    children_map = {}

    for rel in relationships:
        children_map.setdefault(rel.person_id, []).append(rel.related_person_id)

    total = 0

    visited = set()

    queue = deque([root_id])

    while queue:
        person_id = queue.popleft()

        if person_id in visited:
            continue

        visited.add(person_id)

        # count current person
        total += 1

        # add children
        for child_id in children_map.get(person_id, []):
            queue.append(child_id)

    return total
