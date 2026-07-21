import uuid

from app.services.family_tree_service import count_generation, count_person
from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Person, Relationship


search_bp = Blueprint("search", __name__, url_prefix="/api/search")


@search_bp.route("/", methods=["POST"])
def search(): # thong tin tu thuy to
    body = request.get_json()
    id = body.get("id")
    max_generation = count_generation(id)
    count = count_person(id)
    return jsonify(
        {
            'max_generation': max_generation,
            'count': count,
        }
    )
