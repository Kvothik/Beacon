# Error Policy
Audited build documentation for the Texas Parole Packet Builder

## 1. Purpose

This document defines the required backend error format and the expected client handling behavior for the MVP.

## 2. Core Rule

All backend endpoints must return structured JSON errors.

The mobile app must never depend on raw Python exceptions, HTML responses, or undocumented error strings.

## 3. Error Response Shape

All non-2xx API responses must use:

```json
{
  "error": {
    "code": "machine_readable_code",
    "message": "Human-readable explanation.",
    "details": null,
    "retryable": false
  }
}
```

Fields:
- `code`: stable programmatic identifier
- `message`: user-safe message or operator-safe summary
- `details`: optional structured object or null
- `retryable`: whether the client may offer retry behavior

## 4. Common Error Codes

### Authentication
- `auth_invalid_credentials`
- `auth_unauthorized`
- `auth_token_expired`
- `auth_registration_conflict`

### Validation
- `validation_error`
- `invalid_section_key`
- `invalid_search_request`

### Offender Lookup / TDCJ
- `tdcj_network_error`
- `tdcj_parser_error`
- `tdcj_invalid_sid`
- `tdcj_unavailable`

### Packet / Upload / PDF
- `packet_not_found`
- `document_not_found`
- `upload_failed`
- `pdf_generation_failed`
- `resource_conflict`

### Generic
- `not_found`
- `forbidden`
- `internal_error`

## 5. Recommended HTTP Mapping

- `400` validation errors
- `401` authentication required or invalid token
- `403` forbidden resource access
- `404` missing resource
- `409` conflicts such as duplicate registration
- `422` semantically invalid request payloads when distinct from basic validation
- `502` upstream TDCJ or integration failures
- `500` internal backend errors

## 6. Examples

### Validation error
```json
{
  "error": {
    "code": "invalid_search_request",
    "message": "Provide last name and first initial, TDCJ number, or SID.",
    "details": {
      "fields": ["last_name", "first_name_initial", "tdcj_number", "sid"]
    },
    "retryable": false
  }
}
```

### Retryable upstream error
```json
{
  "error": {
    "code": "tdcj_network_error",
    "message": "Offender lookup is temporarily unavailable.",
    "details": null,
    "retryable": true
  }
}
```

## 7. Logging Rules

- log full internal exception details on the backend only
- do not expose stack traces to mobile clients
- when parser mismatches occur, log enough context for diagnosis without inventing fallback fields

## 8. Mobile Handling Rules

- display the `message` field to users when appropriate
- use `code` for conditional UI behaviors
- show retry controls only when `retryable=true`
- do not parse backend HTML or raw text failures

## 9. Anti-Hallucination Rules

- do not return ad hoc error shapes
- do not silently swallow integration failures
- do not fake successful PDF generation or upload completion after an error
