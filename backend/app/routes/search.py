import uuid

from app.services.family_tree_service import count_generation, get_person_lineage_info
from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Person, Relationship


search_bp = Blueprint("search", __name__, url_prefix="/api/search")


@search_bp.route("/person-info/", methods=["POST"])
def search():  # thong tin tu thuy to
    id = request.get_json()
    max_generation = count_generation(id)
    person_lineage_info = get_person_lineage_info(id)
    person_lineage_info["max_generation"] = max_generation
    return jsonify(person_lineage_info)
