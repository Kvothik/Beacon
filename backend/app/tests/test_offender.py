from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from uuid import uuid4

import httpx
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

DB_FILE = Path(tempfile.gettempdir()) / "beacon_issue9_test.db"
os.environ["BEACON_DATABASE_URL"] = f"sqlite+pysqlite:///{DB_FILE}"

from backend.app.core.security import ApiError  # noqa: E402
from backend.app.main import app  # noqa: E402
from backend.app.routers.offender_router import get_tdcj_lookup_service  # noqa: E402
from backend.app.services.tdcj_lookup_service import SearchRequest, TdcjLookupService  # noqa: E402


SEARCH_RESULTS_HTML = """
<!doctype html>
<html>
  <head>
    <title>TDCJ Inmate Search -  Search Result Listing</title>
  </head>
  <body>
    <h1>Inmate Information Search Result(s)</h1>
    <table class="tdcj_table">
      <thead>
        <tr>
          <th>Name</th>
          <th>TDCJ Number</th>
          <th>Race</th>
          <th>Gender</th>
          <th>Projected Release Date</th>
          <th>Unit of Assignment</th>
          <th>Age</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th class='rowHeader'><a href="/InmateSearch/viewDetail.action?sid=05192675">SMITH,J C</a></th>
          <td>02394240</td>
          <td>W</td>
          <td>M</td>
          <td>2041-12-10</td>
          <td>ELLIS</td>
          <td>52</td>
        </tr>
      </tbody>
    </table>
    <form id="form_paginate" action="/InmateSearch/search.action" method="POST">
      <input type="hidden" name="lastSearch" value='{"lastName":"Smith","firstName":"J"}' />
      <input type="hidden" name="currentPage" value="1" />
      <input type="hidden" name="totalPageCount" value="5" />
    </form>
  </body>
</html>
"""

DETAIL_HTML = """
<!doctype html>
<html>
  <head>
    <title>TDCJ Inmate Search - Inmate Details</title>
  </head>
  <body>
    <h1>Inmate Information Details</h1>
    <p>
      <font class="bold">SID Number:</font> 05192675 <br />
      <font class="bold">TDCJ Number:</font> 02394240 <br />
      <font class="bold">Name:</font> SMITH,J C <br />
      <font class="bold">Race:</font> W <br />
      <font class="bold">Gender:</font> M <br />
      <font class="bold">Age:</font> 52 <br />
      <font class="bold">Maximum Sentence Date:</font> 2041-12-10 <br />
      <font class="bold">Current Facility:</font>
      <a href="http://www.tdcj.texas.gov/unit_directory/unit_information.html">ELLIS</a><br />
      <font class="bold">Projected Release Date:</font>
      <a href="http://www.tdcj.texas.gov/definitions/index.html#Projected">2041-12-10</a><br />
      <font class="bold">Parole Eligibility Date:</font>
      <a href="http://www.tdcj.texas.gov/definitions/index.html#Eligibility">2031-12-10</a><br />
      <font class="bold">Inmate Visitation Eligible:</font>
      <a href="http://www.tdcj.texas.gov/visitation/index.html">YES</a>
    </p>
    <p>
      <b>Scheduled Release Date:</b><br/>
      Inmate is not scheduled for release at this time.
    </p>
    <p>
      <b>Scheduled Release Type:</b><br/>
      Will be determined when release date is scheduled.
    </p>
    <p>
      <b>Scheduled Release Location:</b><br/>
      Will be determined when release date is scheduled.
    </p>
    <p>
      <a href="/InmateSearch/reviewDetail.action?sid=05192675&amp;tdcj=02394240&amp;fullName=SMITH%2CJ+C">Parole Review Information</a>
    </p>
    <h2>Offense History:</h2>
    <table class="tdcj_table">
      <tr>
        <th scope="col">Offense Date</th>
        <th scope="col">Offense</th>
        <th scope="col">Sentence Date</th>
        <th scope="col">County</th>
        <th scope="col">Case No.</th>
        <th scope="col">Sentence (YY-MM-DD)</th>
      </tr>
      <tr valign="middle">
        <th class='rowHeader'> 1993-11-03 </c:out></th>
        <td> INDECENCY W/CHILD </c:out></td>
        <td> 1997-07-08 </c:out></td>
        <td> VAN ZANDT </c:out></td>
        <td> 14,732 </c:out></td>
        <td> 8-00-00 </c:out></td>
      </tr>
    </table>
  </body>
</html>
"""

NO_RESULTS_HTML = """
<!doctype html>
<html>
  <head><title>TDCJ Inmate Search -  Search Result Listing</title></head>
  <body>
    <h1>Inmate Information Search Result(s)</h1>
    <p>No records found for the requested search.</p>
  </body>
</html>
"""


def register_and_get_token(client: TestClient) -> str:
    email = f"offender-{uuid4().hex[:8]}@example.com"
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secret123", "full_name": "Jane Doe"},
    )
    assert response.status_code == 201
    return response.json()["access_token"]


class StubTdcjLookupService:
    def search_offenders(self, request: SearchRequest) -> dict:
        if not any([request.last_name and request.first_name_initial, request.tdcj_number, request.sid]):
            raise ApiError(
                400,
                "invalid_search_request",
                "Provide last name and first initial, TDCJ number, or SID.",
                details={"fields": ["last_name", "first_name_initial", "tdcj_number", "sid"]},
            )
        if request.last_name == "Nobody":
            return {
                "results": [],
                "pagination": {"current_page": 1, "total_pages": 1, "has_more": False},
                "source": "Texas Department of Criminal Justice",
                "retrieved_at": "2026-03-11T21:00:00Z",
            }
        return {
            "results": [
                {
                    "name": "SMITH,J C",
                    "sid": "05192675",
                    "tdcj_number": "02394240",
                    "race": "W",
                    "gender": "M",
                    "projected_release_date": "2041-12-10",
                    "unit": "ELLIS",
                    "age": 52,
                    "detail_url": "https://inmate.tdcj.texas.gov/InmateSearch/viewDetail.action?sid=05192675",
                }
            ],
            "pagination": {"current_page": 1, "total_pages": 1, "has_more": False},
            "source": "Texas Department of Criminal Justice",
            "retrieved_at": "2026-03-11T21:00:00Z",
        }

    def get_offender_detail(self, sid: str) -> dict:
        if sid == "bad-sid":
            raise ApiError(404, "tdcj_invalid_sid", "No offender was found for that SID.")
        return {
            "sid": sid,
            "tdcj_number": "02394240",
            "name": "SMITH,J C",
            "race": "W",
            "gender": "M",
            "age": 52,
            "maximum_sentence_date": "2041-12-10",
            "current_facility": "ELLIS",
            "projected_release_date": "2041-12-10",
            "parole_eligibility_date": "2031-12-10",
            "visitation_eligible": True,
            "visitation_eligible_raw": "YES",
            "scheduled_release_date_text": "Inmate is not scheduled for release at this time.",
            "scheduled_release_type_text": "Will be determined when release date is scheduled.",
            "scheduled_release_location_text": "Will be determined when release date is scheduled.",
            "parole_review_url": "https://inmate.tdcj.texas.gov/InmateSearch/reviewDetail.action?sid=05192675&tdcj=02394240&fullName=SMITH%2CJ+C",
            "offense_history": [],
            "source": "Texas Department of Criminal Justice",
            "retrieved_at": "2026-03-11T21:00:00Z",
            "source_note": "Information provided is updated once daily during weekdays and may not reflect the true current status or location.",
        }


class OffenderRouterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if DB_FILE.exists():
            DB_FILE.unlink()
        config = Config(str(Path("backend/alembic.ini")))
        command.upgrade(config, "head")
        app.dependency_overrides[get_tdcj_lookup_service] = lambda: StubTdcjLookupService()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        app.dependency_overrides.clear()
        if DB_FILE.exists():
            DB_FILE.unlink()

    def test_post_offender_search_returns_results(self) -> None:
        token = register_and_get_token(self.client)
        response = self.client.post(
            "/api/v1/offenders/search",
            json={"last_name": "Smith", "first_name_initial": "J", "page": 1},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["results"][0]["sid"], "05192675")
        self.assertEqual(body["pagination"]["current_page"], 1)

    def test_post_offender_search_returns_empty_results(self) -> None:
        token = register_and_get_token(self.client)
        response = self.client.post(
            "/api/v1/offenders/search",
            json={"last_name": "Nobody", "first_name_initial": "Z", "page": 1},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"], [])

    def test_post_offender_search_returns_structured_error_for_invalid_search(self) -> None:
        token = register_and_get_token(self.client)
        response = self.client.post(
            "/api/v1/offenders/search",
            json={"page": 1},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "invalid_search_request")

    def test_get_offender_detail_returns_normalized_detail(self) -> None:
        token = register_and_get_token(self.client)
        response = self.client.get(
            "/api/v1/offenders/05192675",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["sid"], "05192675")
        self.assertEqual(body["current_facility"], "ELLIS")

    def test_get_offender_detail_returns_structured_error_for_invalid_sid(self) -> None:
        token = register_and_get_token(self.client)
        response = self.client.get(
            "/api/v1/offenders/bad-sid",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "tdcj_invalid_sid")

    def test_offender_endpoints_require_authentication(self) -> None:
        search = self.client.post("/api/v1/offenders/search", json={"last_name": "Smith", "first_name_initial": "J"})
        self.assertEqual(search.status_code, 401)
        self.assertEqual(search.json()["error"]["code"], "auth_unauthorized")

        detail = self.client.get("/api/v1/offenders/05192675")
        self.assertEqual(detail.status_code, 401)
        self.assertEqual(detail.json()["error"]["code"], "auth_unauthorized")


class TdcjLookupServiceParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = TdcjLookupService(throttle_seconds=0)

    def test_parse_search_results_page_normalizes_row_and_pagination(self) -> None:
        parsed = self.service.parse_search_results_page(SEARCH_RESULTS_HTML)

        self.assertEqual(len(parsed["results"]), 1)
        self.assertEqual(parsed["results"][0]["sid"], "05192675")
        self.assertEqual(parsed["results"][0]["detail_url"], "https://inmate.tdcj.texas.gov/InmateSearch/viewDetail.action?sid=05192675")
        self.assertEqual(parsed["pagination"]["current_page"], 1)
        self.assertEqual(parsed["pagination"]["total_pages"], 5)
        self.assertTrue(parsed["pagination"]["has_more"])

    def test_parse_detail_page_normalizes_summary_fields_and_offense_history(self) -> None:
        parsed = self.service.parse_detail_page(DETAIL_HTML)

        self.assertEqual(parsed["sid"], "05192675")
        self.assertEqual(parsed["tdcj_number"], "02394240")
        self.assertEqual(parsed["current_facility"], "ELLIS")
        self.assertEqual(parsed["projected_release_date"], "2041-12-10")
        self.assertEqual(parsed["parole_eligibility_date"], "2031-12-10")
        self.assertTrue(parsed["visitation_eligible"])
        self.assertEqual(parsed["visitation_eligible_raw"], "YES")
        self.assertEqual(parsed["scheduled_release_date_text"], "Inmate is not scheduled for release at this time.")
        self.assertEqual(parsed["parole_review_url"], "https://inmate.tdcj.texas.gov/InmateSearch/reviewDetail.action?sid=05192675&tdcj=02394240&fullName=SMITH%2CJ+C")
        self.assertEqual(len(parsed["offense_history"]), 1)
        self.assertEqual(parsed["offense_history"][0]["offense"], "INDECENCY W/CHILD")
        self.assertEqual(parsed["offense_history"][0]["sentence_length"], "8-00-00")

    def test_parse_search_results_page_returns_empty_results_for_no_match_page(self) -> None:
        parsed = self.service.parse_search_results_page(NO_RESULTS_HTML)
        self.assertEqual(parsed["results"], [])
        self.assertEqual(parsed["pagination"]["current_page"], 1)
        self.assertEqual(parsed["pagination"]["total_pages"], 1)
        self.assertFalse(parsed["pagination"]["has_more"])

    def test_search_request_requires_supported_mode(self) -> None:
        with self.assertRaises(ApiError) as context:
            self.service.search_offenders(SearchRequest())
        self.assertEqual(context.exception.code, "invalid_search_request")

    def test_request_with_retry_falls_back_to_urllib_on_remote_protocol_error(self) -> None:
        with mock.patch("httpx.Client.request", side_effect=httpx.RemoteProtocolError("bad header")):
            with mock.patch.object(self.service, "_request_with_urllib", return_value=SEARCH_RESULTS_HTML) as fallback:
                response = self.service._request_with_retry(
                    "POST",
                    "https://inmate.tdcj.texas.gov/InmateSearch/search.action",
                    data={"lastName": "Smith", "firstName": "J"},
                )

        self.assertIn("Search Result Listing", response)
        fallback.assert_called_once()


if __name__ == "__main__":
    unittest.main()
