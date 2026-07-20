import uuid
from datetime import datetime

from app.decorators import admin_required
from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Event


event_bp = Blueprint(
    "events",
    __name__,
    url_prefix="/api/events"
)


@event_bp.route("", methods=["GET"])
def get_events():
    events = (
        Event.query.order_by(
            Event.event_datetime.asc()
        ).all()
    )
    return jsonify([
        event.to_dict()
        for event in events
    ])


@event_bp.route("/<string:event_id>", methods=["GET"])
def get_event(event_id):
    event = db.session.get(
        Event,
        event_id
    )
    if event is None:
        return jsonify({
            "message": "Event not found"
        }), 404

    return jsonify(
        event.to_dict()
    )


@event_bp.route("", methods=["POST"])
@admin_required
def create_event():
    body = request.get_json()

    event = Event(
        id=str(uuid.uuid4()),
        family_id="8b6c4f0e-7f3a-4d8e-9a61-2e7b5c9d1f20",
        event_datetime=datetime.fromisoformat(body["datetime"]),
        event_type=body["type"],
        title=body["title"],
        location=body.get("location"),
        description=body.get("description"),
        notified=body.get("notified", False),
        recipient_count=body.get("recipients", 0),
    )

    db.session.add(event)
    db.session.commit()

    return jsonify(
        event.to_dict()
    ), 201


@event_bp.route("/<string:event_id>", methods=["PUT"])
@admin_required
def update_event(event_id):
    body = request.get_json()

    event = db.session.get(
        Event,
        event_id
    )
    if event is None:
        return jsonify({
            "message": "Event not found"
        }), 404
    event.family_id = body.get(
        "family_id",
        event.family_id
    )
    if body.get("datetime"):
        event.event_datetime = datetime.fromisoformat(
            body["datetime"]
        )
    event.event_type = body.get(
        "type",
        event.event_type
    )
    event.title = body.get(
        "title",
        event.title
    )
    event.location = body.get(
        "location",
        event.location
    )
    event.description = body.get(
        "description",
        event.description
    )
    event.notified = body.get(
        "notified",
        event.notified
    )
    event.recipient_count = body.get(
        "recipients",
        event.recipient_count
    )
    db.session.commit()

    return jsonify(
        event.to_dict()
    )


@event_bp.route("/<string:event_id>", methods=["DELETE"])
@admin_required
def delete_event(event_id):
    event = db.session.get(
        Event,
        event_id
    )

    if event is None:
        return jsonify({
            "message": "Event not found"
        }), 404

    db.session.delete(event)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Event deleted"
    })