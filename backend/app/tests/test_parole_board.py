from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

DB_FILE = Path(tempfile.gettempdir()) / "beacon_issue11_test.db"
os.environ["BEACON_DATABASE_URL"] = f"sqlite+pysqlite:///{DB_FILE}"

from backend.app.core.security import ApiError  # noqa: E402
from backend.app.main import app  # noqa: E402
from backend.app.services.parole_board_service import lookup_parole_board_office, normalize_unit_name  # noqa: E402


def register_and_get_token(client: TestClient) -> str:
    email = f"parole-board-{uuid4().hex[:8]}@example.com"
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secret123", "full_name": "Jane Doe"},
    )
    assert response.status_code == 201
    return response.json()["access_token"]


class ParoleBoardServiceTests(unittest.TestCase):
    def test_normalize_unit_name_collapses_spacing_and_case(self) -> None:
        self.assertEqual(normalize_unit_name("  Ellis   Unit * "), "ELLIS UNIT")

    def test_lookup_parole_board_office_resolves_facility_alias_without_unit_suffix(self) -> None:
        office = lookup_parole_board_office("ELLIS")
        self.assertEqual(office["office_code"], "HUNTSVILLE")
        self.assertEqual(office["office_name"], "Huntsville Board Office")

    def test_lookup_parole_board_office_raises_for_unknown_unit(self) -> None:
        with self.assertRaises(ApiError) as context:
            lookup_parole_board_office("UNKNOWN UNIT")
        self.assertEqual(context.exception.code, "not_found")


class ParoleBoardRouterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if DB_FILE.exists():
            DB_FILE.unlink()
        config = Config(str(Path("backend/alembic.ini")))
        command.upgrade(config, "head")
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        if DB_FILE.exists():
            DB_FILE.unlink()

    def test_get_parole_board_office_returns_normalized_office(self) -> None:
        token = register_and_get_token(self.client)
        response = self.client.get(
            "/api/v1/parole-board-office",
            params={"unit": "ELLIS"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["office_code"], "HUNTSVILLE")
        self.assertEqual(body["office_name"], "Huntsville Board Office")
        self.assertEqual(body["city"], "Huntsville")
        self.assertEqual(body["state"], "TX")
        self.assertIn("address_lines", body)

    def test_get_parole_board_office_returns_structured_not_found_for_unknown_unit(self) -> None:
        token = register_and_get_token(self.client)
        response = self.client.get(
            "/api/v1/parole-board-office",
            params={"unit": "UNKNOWN UNIT"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "not_found")

    def test_get_parole_board_office_returns_structured_validation_error_for_blank_unit(self) -> None:
        token = register_and_get_token(self.client)
        response = self.client.get(
            "/api/v1/parole-board-office",
            params={"unit": "   "},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "validation_error")

    def test_get_parole_board_office_requires_authentication(self) -> None:
        response = self.client.get("/api/v1/parole-board-office", params={"unit": "ELLIS"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth_unauthorized")


if __name__ == "__main__":
    unittest.main()
