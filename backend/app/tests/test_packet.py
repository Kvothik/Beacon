from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from uuid import UUID, uuid4

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import select

DB_FILE = Path(tempfile.gettempdir()) / "beacon_issue13_test.db"
os.environ["BEACON_DATABASE_URL"] = f"sqlite+pysqlite:///{DB_FILE}"

from backend.app.core.db import create_session  # noqa: E402
from backend.app.main import app  # noqa: E402
from backend.app.models.document import Document  # noqa: E402
from backend.app.models.packet import Packet, PacketSection  # noqa: E402
from backend.app.services.parole_board_service import seed_parole_board_reference_data  # noqa: E402


def register_and_get_token(client: TestClient, *, prefix: str = "packet") -> str:
    email = f"{prefix}-{uuid4().hex[:8]}@example.com"
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secret123", "full_name": "Jane Doe"},
    )
    assert response.status_code == 201
    return response.json()["access_token"]


def create_packet(client: TestClient, token: str, *, sid: str = "05192675") -> dict:
    response = client.post(
        "/api/v1/packets",
        json={
            "offender_sid": sid,
            "offender_name": "SMITH,J C",
            "offender_tdcj_number": "02394240",
            "current_facility": "ELLIS",
            "parole_board_office_code": "HUNTSVILLE",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    return response.json()


def create_cover_letter(client: TestClient, token: str, packet_id: str) -> dict:
    response = client.post(
        f"/api/v1/packets/{packet_id}/cover-letter",
        json={
            "sender_name": "Jane Doe",
            "sender_phone": "512-555-0100",
            "sender_email": "jane@example.com",
            "sender_relationship": "sister",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    return response.json()


class PacketRouterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if DB_FILE.exists():
            DB_FILE.unlink()
        config = Config(str(Path("backend/alembic.ini")))
        command.upgrade(config, "head")
        with create_session() as session:
            seed_parole_board_reference_data(session)
            session.commit()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        if DB_FILE.exists():
            DB_FILE.unlink()

    def test_create_packet_returns_documented_response_shape(self) -> None:
        token = register_and_get_token(self.client)
        body = create_packet(self.client, token)
        UUID(body["id"])
        self.assertEqual(body["status"], "draft")
        self.assertEqual(body["offender_sid"], "05192675")
        self.assertEqual(body["offender_name"], "SMITH,J C")
        self.assertEqual(body["parole_board_office_code"], "HUNTSVILLE")
        self.assertIn("created_at", body)
        self.assertIn("updated_at", body)

    def test_create_packet_initializes_all_sections_in_pdf_order(self) -> None:
        token = register_and_get_token(self.client)
        body = create_packet(self.client, token, sid="99999999")
        packet_id = UUID(body["id"])

        with create_session() as session:
            packet = session.scalar(select(Packet).where(Packet.id == packet_id))
            self.assertIsNotNone(packet)
            sections = session.scalars(
                select(PacketSection).where(PacketSection.packet_id == packet_id).order_by(PacketSection.sort_order)
            ).all()

        self.assertEqual(
            [(section.section_key, section.title, section.sort_order) for section in sections],
            [
                ("photos", "Photos", 1),
                ("support_letters", "Support Letters", 2),
                ("reflection_letter", "Reflection Letter", 3),
                ("certificates_and_education", "Certificates and Education", 4),
                ("future_employment", "Future Employment", 5),
                ("parole_plan", "Parole Plan", 6),
                ("court_and_case_documents", "Court and Case Documents", 7),
                ("other_miscellaneous", "Other or Miscellaneous", 8),
            ],
        )

    def test_create_packet_returns_structured_error_for_unknown_office_code(self) -> None:
        token = register_and_get_token(self.client)
        response = self.client.post(
            "/api/v1/packets",
            json={
                "offender_sid": "05192675",
                "offender_name": "SMITH,J C",
                "parole_board_office_code": "UNKNOWN",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "not_found")

    def test_create_packet_requires_authentication(self) -> None:
        response = self.client.post(
            "/api/v1/packets",
            json={"offender_sid": "05192675", "offender_name": "SMITH,J C"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth_unauthorized")

    def test_get_packet_returns_metadata_sections_and_document_counts(self) -> None:
        token = register_and_get_token(self.client)
        body = create_packet(self.client, token, sid="11111111")
        packet_id = UUID(body["id"])

        with create_session() as session:
            photos_section = session.scalar(
                select(PacketSection).where(PacketSection.packet_id == packet_id, PacketSection.section_key == "photos")
            )
            photos_section.is_populated = True
            photos_section.notes_text = "Two photos attached"
            session.add(
                Document(
                    packet_id=packet_id,
                    packet_section_id=photos_section.id,
                    filename="photo1.jpg",
                    content_type="image/jpeg",
                    source="upload",
                    upload_status="uploaded",
                )
            )
            session.add(
                Document(
                    packet_id=packet_id,
                    packet_section_id=photos_section.id,
                    filename="photo2.jpg",
                    content_type="image/jpeg",
                    source="upload",
                    upload_status="uploaded",
                )
            )
            session.commit()

        response = self.client.get(
            f"/api/v1/packets/{packet_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        detail = response.json()
        self.assertEqual(detail["id"], str(packet_id))
        self.assertEqual(detail["offender"]["sid"], "11111111")
        self.assertEqual(detail["parole_board_office_code"], "HUNTSVILLE")
        self.assertEqual(len(detail["sections"]), 8)
        photos = next(section for section in detail["sections"] if section["section_key"] == "photos")
        self.assertTrue(photos["is_populated"])
        self.assertEqual(photos["notes_text"], "Two photos attached")
        self.assertEqual(photos["document_count"], 2)

    def test_get_packet_returns_packet_not_found_for_missing_id(self) -> None:
        token = register_and_get_token(self.client)
        response = self.client.get(
            f"/api/v1/packets/{uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "packet_not_found")

    def test_get_packet_enforces_ownership(self) -> None:
        owner_token = register_and_get_token(self.client, prefix="owner")
        other_token = register_and_get_token(self.client, prefix="other")
        body = create_packet(self.client, owner_token, sid="22222222")

        response = self.client.get(
            f"/api/v1/packets/{body['id']}",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "forbidden")

    def test_patch_packet_section_updates_notes_and_population_state(self) -> None:
        token = register_and_get_token(self.client)
        body = create_packet(self.client, token, sid="33333333")

        response = self.client.patch(
            f"/api/v1/packets/{body['id']}/sections/reflection_letter",
            json={"notes_text": "I take responsibility for my actions.", "is_populated": True},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        section = response.json()
        self.assertEqual(section["section_key"], "reflection_letter")
        self.assertEqual(section["notes_text"], "I take responsibility for my actions.")
        self.assertTrue(section["is_populated"])
        self.assertEqual(section["document_count"], 0)
        self.assertIn("updated_at", section)

    def test_patch_packet_section_rejects_invalid_section_key(self) -> None:
        token = register_and_get_token(self.client)
        body = create_packet(self.client, token, sid="44444444")

        response = self.client.patch(
            f"/api/v1/packets/{body['id']}/sections/not_a_real_section",
            json={"notes_text": "x", "is_populated": True},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "validation_error")

    def test_patch_packet_section_enforces_ownership(self) -> None:
        owner_token = register_and_get_token(self.client, prefix="ownerpatch")
        other_token = register_and_get_token(self.client, prefix="otherpatch")
        body = create_packet(self.client, owner_token, sid="55555555")

        response = self.client.patch(
            f"/api/v1/packets/{body['id']}/sections/photos",
            json={"notes_text": "private", "is_populated": True},
            headers={"Authorization": f"Bearer {other_token}"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "forbidden")

    def test_post_packet_upload_creates_pending_document_record(self) -> None:
        token = register_and_get_token(self.client)
        body = create_packet(self.client, token, sid="66666666")

        response = self.client.post(
            f"/api/v1/packets/{body['id']}/uploads",
            json={
                "section_key": "photos",
                "filename": "image1.jpg",
                "content_type": "image/jpeg",
                "source": "scanner",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 201)
        upload = response.json()
        self.assertEqual(upload["packet_id"], body["id"])
        self.assertEqual(upload["section_key"], "photos")
        self.assertEqual(upload["upload_status"], "pending")
        self.assertIn("upload_url", upload)
        self.assertIn("storage_key", upload)

    def test_post_packet_upload_rejects_invalid_section_key(self) -> None:
        token = register_and_get_token(self.client)
        body = create_packet(self.client, token, sid="77777777")

        response = self.client.post(
            f"/api/v1/packets/{body['id']}/uploads",
            json={
                "section_key": "bad_section",
                "filename": "image1.jpg",
                "content_type": "image/jpeg",
                "source": "scanner",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "validation_error")

    def test_post_packet_upload_enforces_ownership(self) -> None:
        owner_token = register_and_get_token(self.client, prefix="ownerupload")
        other_token = register_and_get_token(self.client, prefix="otherupload")
        body = create_packet(self.client, owner_token, sid="88888888")

        response = self.client.post(
            f"/api/v1/packets/{body['id']}/uploads",
            json={
                "section_key": "photos",
                "filename": "image1.jpg",
                "content_type": "image/jpeg",
                "source": "upload",
            },
            headers={"Authorization": f"Bearer {other_token}"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "forbidden")

    def test_post_cover_letter_generates_respectful_template(self) -> None:
        token = register_and_get_token(self.client)
        body = create_packet(self.client, token, sid="99999998")

        letter = create_cover_letter(self.client, token, body["id"])
        self.assertEqual(letter["packet_id"], body["id"])
        self.assertIn("Jane Doe", letter["cover_letter_text"])
        self.assertIn("SMITH,J C", letter["cover_letter_text"])
        self.assertIn("Huntsville Board Office", letter["cover_letter_text"])
        self.assertIn("respectfully support this parole packet", letter["cover_letter_text"])
        self.assertIn("accountability", letter["cover_letter_text"])
        self.assertIn("updated_at", letter)

    def test_post_cover_letter_requires_associated_board_office(self) -> None:
        token = register_and_get_token(self.client)
        response = self.client.post(
            "/api/v1/packets",
            json={
                "offender_sid": "12312312",
                "offender_name": "SMITH,J C",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        packet_id = response.json()["id"]

        cover = self.client.post(
            f"/api/v1/packets/{packet_id}/cover-letter",
            json={
                "sender_name": "Jane Doe",
                "sender_phone": "512-555-0100",
                "sender_email": "jane@example.com",
                "sender_relationship": "sister",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(cover.status_code, 404)
        self.assertEqual(cover.json()["error"]["code"], "not_found")

    def test_post_cover_letter_enforces_ownership(self) -> None:
        owner_token = register_and_get_token(self.client, prefix="ownercover")
        other_token = register_and_get_token(self.client, prefix="othercover")
        body = create_packet(self.client, owner_token, sid="99999997")

        response = self.client.post(
            f"/api/v1/packets/{body['id']}/cover-letter",
            json={
                "sender_name": "Jane Doe",
                "sender_phone": "512-555-0100",
                "sender_email": "jane@example.com",
                "sender_relationship": "sister",
            },
            headers={"Authorization": f"Bearer {other_token}"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "forbidden")

    def test_get_readiness_reports_missing_items_before_packet_is_ready(self) -> None:
        token = register_and_get_token(self.client)
        body = create_packet(self.client, token, sid="99999996")

        response = self.client.get(
            f"/api/v1/packets/{body['id']}/readiness",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        readiness = response.json()
        self.assertFalse(readiness["is_ready"])
        self.assertIn("cover_letter", readiness["missing_items"])
        self.assertIn("section:photos", readiness["missing_items"])

    def test_post_pdf_generates_pdf_url_when_packet_ready(self) -> None:
        token = register_and_get_token(self.client)
        body = create_packet(self.client, token, sid="99999996")
        create_cover_letter(self.client, token, body["id"])

        for section_key in (
            "photos",
            "support_letters",
            "reflection_letter",
            "certificates_and_education",
            "future_employment",
            "parole_plan",
            "court_and_case_documents",
            "other_miscellaneous",
        ):
            self.client.patch(
                f"/api/v1/packets/{body['id']}/sections/{section_key}",
                json={"notes_text": f"{section_key} complete", "is_populated": True},
                headers={"Authorization": f"Bearer {token}"},
            )
            self.client.post(
                f"/api/v1/packets/{body['id']}/uploads",
                json={
                    "section_key": section_key,
                    "filename": f"{section_key}.jpg",
                    "content_type": "image/jpeg",
                    "source": "upload",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        response = self.client.post(
            f"/api/v1/packets/{body['id']}/pdf",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        pdf = response.json()
        self.assertEqual(pdf["packet_id"], body["id"])
        self.assertEqual(pdf["status"], "ready")
        self.assertIn("/final-packet.pdf", pdf["pdf_url"])
        self.assertIn("generated_at", pdf)

    def test_post_pdf_requires_ready_packet_state(self) -> None:
        token = register_and_get_token(self.client)
        body = create_packet(self.client, token, sid="99999995")
        self.client.patch(
            f"/api/v1/packets/{body['id']}/sections/reflection_letter",
            json={"notes_text": "Ready for review.", "is_populated": True},
            headers={"Authorization": f"Bearer {token}"},
        )

        response = self.client.post(
            f"/api/v1/packets/{body['id']}/pdf",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "validation_error")
        self.assertIn("missing_items", response.json()["error"]["details"])

    def test_get_readiness_enforces_ownership(self) -> None:
        owner_token = register_and_get_token(self.client, prefix="ownerready")
        other_token = register_and_get_token(self.client, prefix="otherready")
        body = create_packet(self.client, owner_token, sid="99999993")

        response = self.client.get(
            f"/api/v1/packets/{body['id']}/readiness",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "forbidden")

    def test_post_pdf_enforces_ownership(self) -> None:
        owner_token = register_and_get_token(self.client, prefix="ownerpdf")
        other_token = register_and_get_token(self.client, prefix="otherpdf")
        body = create_packet(self.client, owner_token, sid="99999994")
        create_cover_letter(self.client, owner_token, body["id"])
        self.client.patch(
            f"/api/v1/packets/{body['id']}/sections/reflection_letter",
            json={"notes_text": "Ready for review.", "is_populated": True},
            headers={"Authorization": f"Bearer {owner_token}"},
        )

        response = self.client.post(
            f"/api/v1/packets/{body['id']}/pdf",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "forbidden")


if __name__ == "__main__":
    unittest.main()
