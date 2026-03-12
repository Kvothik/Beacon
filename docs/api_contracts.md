# API Contracts
Audited build documentation for the Texas Parole Packet Builder

## 1. Purpose

This document defines the backend HTTP API surface for the MVP. Agents must not invent endpoints, request shapes, or response shapes outside this file.

## 2. Conventions

- Base path: `/api/v1`
- Content type: `application/json`
- Authentication: Bearer token for protected endpoints
- Time format: ISO 8601 UTC timestamps
- IDs: UUID strings unless otherwise stated
- Error responses must follow `docs/error_policy.md`

## 2A. TDCJ Data Authority and Persistence Rules

- offender search and offender detail data retrieved from TDCJ are **transient integration data**
- TDCJ responses are used to guide user workflow and packet creation, but they are **not authoritative application-owned records**
- offense history and parole review data are **not persisted in the database** for MVP
- the backend may cache offender search/detail responses temporarily for performance or retry behavior, but cached responses remain non-authoritative and time-limited
- any persisted offender snapshot in the database is limited to the documented packet-supporting fields in `docs/database_schema.md`

## 3. Authentication Endpoints

### POST `/api/v1/auth/register`

Create a user account.

Request:
```json
{
  "email": "user@example.com",
  "password": "string",
  "full_name": "Jane Doe"
}
```

Response `201`:
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "Jane Doe",
    "created_at": "2026-03-11T21:00:00Z"
  },
  "access_token": "jwt-or-session-token",
  "token_type": "bearer"
}
```

### POST `/api/v1/auth/login`

Authenticate an existing user.

Request:
```json
{
  "email": "user@example.com",
  "password": "string"
}
```

Response `200`:
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "Jane Doe",
    "created_at": "2026-03-11T21:00:00Z"
  },
  "access_token": "jwt-or-session-token",
  "token_type": "bearer"
}
```

### GET `/api/v1/auth/me`

Return the authenticated user.

Response `200`:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "Jane Doe",
  "created_at": "2026-03-11T21:00:00Z"
}
```

## 4. Offender Lookup Endpoints

### POST `/api/v1/offenders/search`

Search TDCJ by last name + first initial, TDCJ number, or SID.

Request:
```json
{
  "last_name": "Smith",
  "first_name_initial": "J",
  "tdcj_number": null,
  "sid": null,
  "page": 1
}
```

Rules:
- at least one valid search mode is required
- supported modes are:
  - `last_name` + `first_name_initial`
  - `tdcj_number`
  - `sid`

Response `200`:
```json
{
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
      "detail_url": "https://inmate.tdcj.texas.gov/InmateSearch/viewDetail.action?sid=05192675"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "has_more": false
  },
  "source": "Texas Department of Criminal Justice",
  "retrieved_at": "2026-03-11T21:00:00Z"
}
```

### GET `/api/v1/offenders/{sid}`

Return normalized offender detail for a selected SID.

Response `200`:
```json
{
  "sid": "05192675",
  "tdcj_number": "02394240",
  "name": "SMITH,J C",
  "race": "W",
  "gender": "M",
  "age": 52,
  "maximum_sentence_date": "2041-12-10",
  "current_facility": "ELLIS",
  "projected_release_date": "2041-12-10",
  "parole_eligibility_date": "2031-12-10",
  "visitation_eligible": true,
  "visitation_eligible_raw": "YES",
  "scheduled_release_date_text": "Inmate is not scheduled for release at this time.",
  "scheduled_release_type_text": "Will be determined when release date is scheduled.",
  "scheduled_release_location_text": "Will be determined when release date is scheduled.",
  "parole_review_url": "https://inmate.tdcj.texas.gov/InmateSearch/reviewDetail.action?...",
  "offense_history": [],
  "source": "Texas Department of Criminal Justice",
  "retrieved_at": "2026-03-11T21:00:00Z",
  "source_note": "Information provided is updated once daily during weekdays and may not reflect the true current status or location."
}
```

## 5. Parole Board Endpoint

### GET `/api/v1/parole-board-office`

Resolve the correct parole board office from the offender's current unit/facility.

Query parameters:
- `unit` (required)
- `sid` (optional)

Temporary development routing rule:
- if the same unit appears under multiple upstream board offices, resolve to the first office in alphabetical order of `office_name`
- this is a temporary placeholder rule only, until real TDCJ routing logic is implemented

Response `200`:
```json
{
  "office_code": "REGION_01",
  "office_name": "Texas Board of Pardons and Paroles Office",
  "address_lines": ["Line 1", "Line 2"],
  "city": "Austin",
  "state": "TX",
  "postal_code": "78701",
  "phone": "512-555-0100",
  "notes": "Mail parole packet to this office for review."
}
```

## 6. Packet Endpoints

### POST `/api/v1/packets`

Create a packet draft for a selected offender.

Request:
```json
{
  "offender_sid": "05192675",
  "offender_name": "SMITH,J C",
  "offender_tdcj_number": "02394240",
  "current_facility": "ELLIS",
  "parole_board_office_code": "REGION_01"
}
```

Response `201`:
```json
{
  "id": "uuid",
  "status": "draft",
  "offender_sid": "05192675",
  "offender_name": "SMITH,J C",
  "offender_tdcj_number": "02394240",
  "current_facility": "ELLIS",
  "parole_board_office_code": "REGION_01",
  "created_at": "2026-03-11T21:00:00Z",
  "updated_at": "2026-03-11T21:00:00Z"
}
```

### GET `/api/v1/packets/{packet_id}`

Return packet metadata, section states, and attached documents.

Response `200`:
```json
{
  "id": "uuid",
  "status": "draft",
  "offender": {
    "sid": "05192675",
    "name": "SMITH,J C",
    "tdcj_number": "02394240",
    "current_facility": "ELLIS"
  },
  "parole_board_office_code": "REGION_01",
  "sections": [
    {
      "section_key": "photos",
      "title": "Photos",
      "is_populated": false,
      "notes_text": null,
      "document_count": 0
    }
  ],
  "created_at": "2026-03-11T21:00:00Z",
  "updated_at": "2026-03-11T21:00:00Z"
}
```

### PATCH `/api/v1/packets/{packet_id}/sections/{section_key}`

Update a single packet section.

Allowed `section_key` values:
- `photos`
- `support_letters`
- `reflection_letter`
- `certificates_and_education`
- `future_employment`
- `parole_plan`
- `court_and_case_documents`
- `other_miscellaneous`

Request:
```json
{
  "notes_text": "Section-specific user-entered content",
  "is_populated": true
}
```

Response `200`:
```json
{
  "section_key": "reflection_letter",
  "title": "Reflection Letter",
  "notes_text": "Section-specific user-entered content",
  "is_populated": true,
  "document_count": 0,
  "updated_at": "2026-03-11T21:00:00Z"
}
```

### GET `/api/v1/packets/{packet_id}/review`

Return review-ready packet completeness data.

Response `200`:
```json
{
  "packet_id": "uuid",
  "status": "draft",
  "sections": [
    {
      "section_key": "photos",
      "title": "Photos",
      "is_populated": true,
      "document_count": 2
    }
  ],
  "ready_for_pdf": true
}
```

## 7. Upload Endpoints

### POST `/api/v1/packets/{packet_id}/uploads`

Create a document record and return upload target metadata.

Request:
```json
{
  "section_key": "photos",
  "filename": "image1.jpg",
  "content_type": "image/jpeg",
  "source": "scanner"
}
```

Response `201`:
```json
{
  "document_id": "uuid",
  "packet_id": "uuid",
  "section_key": "photos",
  "filename": "image1.jpg",
  "content_type": "image/jpeg",
  "upload_status": "pending",
  "upload_url": "https://object-storage.example/upload",
  "storage_key": "packets/uuid/documents/uuid-image1.jpg",
  "created_at": "2026-03-11T21:00:00Z"
}
```

### POST `/api/v1/packets/{packet_id}/uploads/{document_id}/complete`

Mark upload complete after storage succeeds.

Request:
```json
{
  "storage_key": "packets/uuid/documents/uuid-image1.jpg",
  "file_size_bytes": 123456,
  "page_count": 1
}
```

Response `200`:
```json
{
  "document_id": "uuid",
  "upload_status": "uploaded",
  "file_size_bytes": 123456,
  "page_count": 1,
  "updated_at": "2026-03-11T21:00:00Z"
}
```

## 8. PDF Endpoints

### POST `/api/v1/packets/{packet_id}/cover-letter`

Generate or refresh the packet cover letter content.

Request:
```json
{
  "sender_name": "Jane Doe",
  "sender_phone": "512-555-0100",
  "sender_email": "user@example.com",
  "sender_relationship": "Sister"
}
```

Response `200`:
```json
{
  "packet_id": "uuid",
  "cover_letter_text": "Formal letter body...",
  "updated_at": "2026-03-11T21:00:00Z"
}
```

### POST `/api/v1/packets/{packet_id}/pdf`

Generate the final print-ready PDF.

Response `202`:
```json
{
  "packet_id": "uuid",
  "status": "generating",
  "message": "PDF generation started."
}
```

### GET `/api/v1/packets/{packet_id}/pdf`

Return PDF generation status and final file metadata.

Response `200` when ready:
```json
{
  "packet_id": "uuid",
  "status": "ready",
  "pdf_filename": "parole-packet.pdf",
  "download_url": "https://object-storage.example/download",
  "generated_at": "2026-03-11T21:10:00Z"
}
```

## 9. Notifications Endpoint

### POST `/api/v1/notifications/subscriptions`

Register a device token for push notifications.

Request:
```json
{
  "platform": "ios",
  "device_token": "expo-push-token"
}
```

Response `201`:
```json
{
  "id": "uuid",
  "platform": "ios",
  "device_token": "expo-push-token",
  "created_at": "2026-03-11T21:00:00Z"
}
```

## 10. Notes

- All protected endpoints require a valid bearer token.
- The API returns structured errors only.
- TDCJ-facing metadata must remain normalized and backend-owned.
