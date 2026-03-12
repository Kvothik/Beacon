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
from backend.app.models.packet import Packet, PacketSection  # noqa: E402
from backend.app.services.parole_board_service import seed_parole_board_reference_data  # noqa: E402


def register_and_get_token(client: TestClient) -> str:
    email = f"packet-{uuid4().hex[:8]}@example.com"
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secret123", "full_name": "Jane Doe"},
    )
    assert response.status_code == 201
    return response.json()["access_token"]


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
        response = self.client.post(
            "/api/v1/packets",
            json={
                "offender_sid": "05192675",
                "offender_name": "SMITH,J C",
                "offender_tdcj_number": "02394240",
                "current_facility": "ELLIS",
                "parole_board_office_code": "HUNTSVILLE",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 201)
        body = response.json()
        UUID(body["id"])
        self.assertEqual(body["status"], "draft")
        self.assertEqual(body["offender_sid"], "05192675")
        self.assertEqual(body["offender_name"], "SMITH,J C")
        self.assertEqual(body["parole_board_office_code"], "HUNTSVILLE")
        self.assertIn("created_at", body)
        self.assertIn("updated_at", body)

    def test_create_packet_initializes_all_sections_in_pdf_order(self) -> None:
        token = register_and_get_token(self.client)
        response = self.client.post(
            "/api/v1/packets",
            json={
                "offender_sid": "99999999",
                "offender_name": "DOE,JANE",
                "offender_tdcj_number": "12345678",
                "current_facility": "ELLIS",
                "parole_board_office_code": "HUNTSVILLE",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 201)
        packet_id = UUID(response.json()["id"])

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
