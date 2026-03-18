import pytest
import requests
import os
import json

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="module")
def auth_token():
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"email": "test@example.com", "password": "password"})
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture(scope="module")
def offender_id():
    return "05192675"

@pytest.fixture(scope="module")
def sample_upload_file():
    return "tests/e2e/sample_doc.pdf"


def test_api_packet_workflow(auth_token, offender_id, sample_upload_file):
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Step 1: login - already done in fixture

    # Step 2: offender lookup
    r = requests.get(f"{BASE_URL}/api/v1/offenders/{offender_id}", headers=headers)
    assert r.status_code == 200

    # Step 3: packet builder
    artifacts_path = "tests/e2e/artifacts"
    os.makedirs(artifacts_path, exist_ok=True)
    request_payload = {"offender_id": offender_id, "offender_name": "John Doe", "offender_sid": "SID-1234"}
    with open(os.path.join(artifacts_path, "packet_builder_request.json"), "w") as f:
        json.dump(request_payload, f, indent=2)

    r = requests.post(f"{BASE_URL}/api/v1/packets", json=request_payload, headers=headers)

    with open(os.path.join(artifacts_path, "packet_builder_response.json"), "w") as f:
        f.write(f"Status code: {r.status_code}\n")
        f.write(r.text)

    assert r.status_code == 201

    # Step 4: document upload
    upload_artifacts_path = "tests/e2e/artifacts"
    os.makedirs(upload_artifacts_path, exist_ok=True)
    upload_url = f"{BASE_URL}/api/v1/packets/{r.json()['id']}/documents"
    upload_request_info = {
        "upload_url": upload_url,
        "request_method": "POST",
        "packet_id": r.json()['id'],
        "filename": os.path.basename(sample_upload_file),
        "content_type": "application/pdf"
    }
    with open(os.path.join(upload_artifacts_path, "document_upload_request.json"), "w") as f:
        json.dump(upload_request_info, f, indent=2)

    with open(sample_upload_file, "rb") as f:
        files = {"file": f}
        r = requests.post(upload_url, headers=headers, files=files)

    upload_response_info = {
        "status_code": r.status_code,
        "response_body": r.text
    }
    with open(os.path.join(upload_artifacts_path, "document_upload_response.json"), "w") as f:
        json.dump(upload_response_info, f, indent=2)

    assert r.status_code == 200

    # Step 5: review readiness
    r = requests.get(f"{BASE_URL}/api/v1/packets/{upload_request_info['packet_id']}/review", headers=headers)
    assert r.status_code == 200
    review_data = r.json()
    assert review_data.get("complete") is True

    # Step 6: PDF generation
    r = requests.post(f"{BASE_URL}/api/v1/packets/{upload_request_info['packet_id']}/generate-pdf", headers=headers)
    assert r.status_code == 200
    pdf_url = r.json().get("pdf_url")
    assert pdf_url and pdf_url.endswith(".pdf")

    print(f"Validation test completed. PDF URL: {pdf_url}")
