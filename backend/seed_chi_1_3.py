import uuid
import json
from pathlib import Path

from app import create_app
from app.extensions import db
from app.models import Person, Relationship


app = create_app()


def seed_gia_pha():
    with app.app_context():
        file_path = Path(__file__).parent / "data" / "data_chi_1_3.json"

        with open(file_path, encoding="utf-8") as f:
            persons = json.load(f)
        try:
            # 1. Seed persons
            for body in persons:
                data = body.get("data", {})

                person = Person(
                    id=body["id"],
                    family_id="8b6c4f0e-7f3a-4d8e-9a61-2e7b5c9d1f20",
                    user_id=data.get("userId", 1),
                    full_name=data.get("fullName", ""),
                    # birthday=data.get("birthday") or None,
                    avatar=(
                        "/male.png" if data.get("gender") == "M" else "/female.png"
                    ),
                    gender=data.get("gender", ""),
                    hometown=data.get("hometown", ""),
                    current_address=data.get("currentAddress", ""),
                    # death_date=data.get("death_date") or None,
                    education=data.get("education", ""),
                    notes=data.get("notes", ""),
                    sibling_index=data.get("siblingIndex", 0),
                )

                db.session.add(person)

            # đảm bảo tất cả Person đã có trong DB
            db.session.flush()

            # 2. Seed relationships
            for body in persons:
                rels = body.get("rels", {})
                person_id = body["id"]

                # add parent for u_nguyenhuuhuan_195
                if person_id in ["anc_tientohuuthong", "anc_tientohuuthong_vo1"]:
                    db.session.add(
                        Relationship(
                            id=str(uuid.uuid4()),
                            person_id=person_id,
                            related_person_id="u_nguyenhuuhuan_195",
                            relation_type="PARENT",
                        )
                    )

                for parent_id in rels.get("parents", []):
                    if not db.session.get(Person, parent_id):
                        raise Exception(f"Parent {parent_id} not found")

                    db.session.add(
                        Relationship(
                            id=str(uuid.uuid4()),
                            person_id=parent_id,
                            related_person_id=person_id,
                            relation_type="PARENT",
                        )
                    )

                for spouse_id in rels.get("spouses", []):
                    if not db.session.get(Person, spouse_id):
                        raise Exception(f"Spouse {spouse_id} not found")

                    db.session.add(
                        Relationship(
                            id=str(uuid.uuid4()),
                            person_id=person_id,
                            related_person_id=spouse_id,
                            relation_type="SPOUSE",
                        )
                    )

            db.session.commit()

            print("Seed gia pha completed")

        except Exception as e:
            db.session.rollback()
            print(f"Seed failed: {e}")
            raise


if __name__ == "__main__":
    seed_gia_pha()
