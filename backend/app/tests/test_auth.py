from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

DB_FILE = Path(tempfile.gettempdir()) / "beacon_issue6_test.db"
os.environ["BEACON_DATABASE_URL"] = f"sqlite+pysqlite:///{DB_FILE}"

from backend.app.main import app  # noqa: E402


class AuthRouterTests(unittest.TestCase):
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

    def test_register_login_and_me_flow(self) -> None:
        email = f"user-{uuid4().hex[:8]}@example.com"
        register = self.client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "secret123", "full_name": "Jane Doe"},
        )
        self.assertEqual(register.status_code, 201)
        register_body = register.json()
        self.assertEqual(register_body["user"]["email"], email)
        self.assertEqual(register_body["token_type"], "bearer")
        self.assertTrue(register_body["access_token"])

        login = self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "secret123"},
        )
        self.assertEqual(login.status_code, 200)
        token = login.json()["access_token"]

        me = self.client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["email"], email)

    def test_registration_conflict_returns_structured_error(self) -> None:
        email = f"dup-{uuid4().hex[:8]}@example.com"
        payload = {"email": email, "password": "secret123", "full_name": "Jane Doe"}
        first = self.client.post("/api/v1/auth/register", json=payload)
        self.assertEqual(first.status_code, 201)

        second = self.client.post("/api/v1/auth/register", json=payload)
        self.assertEqual(second.status_code, 409)
        self.assertEqual(second.json()["error"]["code"], "auth_registration_conflict")

    def test_invalid_login_returns_structured_error(self) -> None:
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": "missing@example.com", "password": "wrongpass"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth_invalid_credentials")

    def test_me_requires_authentication(self) -> None:
        response = self.client.get("/api/v1/auth/me")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "auth_unauthorized")


if __name__ == "__main__":
    unittest.main()
