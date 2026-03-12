# System Invariants
Audited build documentation for the Texas Parole Packet Builder

Non-negotiable architectural rules for the Texas Parole Packet Builder.

These invariants must never be violated by implementation tasks.

If a change requires breaking an invariant, the task must stop and request human approval.

---

## 1. Architecture Layers

The system consists of three layers:

`mobile → backend API → external systems`

Rules:
- mobile clients must never communicate directly with TDCJ or other external data systems
- all external integrations must occur through backend services
- the backend is the only layer allowed to own business logic and integration logic

## 2. Mobile Responsibilities

The mobile app may own only:
- navigation
- presentation
- user input
- local in-session UI state
- document capture and upload initiation
- rendering backend data

The mobile app must never own:
- parole board mapping rules
- offender parsing rules
- packet composition rules
- final PDF generation
- long-term storage policy

## 3. Backend Responsibilities

The backend must own:
- authentication
- TDCJ integration
- parole board lookup
- packet persistence
- upload orchestration
- PDF generation
- structured API error responses

Routers define endpoints and delegate.

Services implement business logic.

## 4. TDCJ Integration Boundary

All TDCJ communication must occur through:

`backend/app/services/tdcj_lookup_service.py`

Rules:
- there is no assumed public JSON API
- mobile code must never scrape TDCJ
- no other backend module may bypass the adapter contract documented in `tdcj_lookup_adapter.md` and `tdcj_html_parser_spec.md`

## 5. Source-of-Truth Documents

The following docs are authoritative:

- product and architecture: `docs/northstar.md`
- API surface: `docs/api_contracts.md`
- persistent models: `docs/database_schema.md`
- PDF ordering and rendering behavior: `docs/pdf_spec.md`
- scanner behavior: `docs/scanner_implementation.md`
- API errors: `docs/error_policy.md`
- file structure: `docs/repo_map.md`

Implementation must conform to these docs exactly.

## 6. Packet Section Invariant

Only these packet sections exist in the MVP:
- Photos
- Support Letters
- Reflection Letter
- Certificates and Education
- Future Employment
- Parole Plan
- Court and Case Documents
- Other or Miscellaneous

No implementation may introduce additional packet sections without updating the documentation first.

## 7. PDF Invariant

- final packet PDFs are generated on the backend only
- packet ordering must follow `docs/pdf_spec.md`
- divider pages are required only for populated sections
- the system must not represent a partial or failed PDF as ready

## 8. Authentication Invariant

Protected endpoints require authenticated users except documented registration and login endpoints.

Users may access only their own packet data and notification subscriptions.

## 9. Error Handling Invariant

All backend errors must conform to `docs/error_policy.md`.

The system must never expose raw stack traces or parser internals to the mobile client.

## 10. Repository Invariant

Files and modules must remain within the documented repository structure in `docs/repo_map.md` unless the docs are updated first.

## 11. Safety Invariant

The system must guide users toward respectful, accountability-oriented packet content.

The system must not generate content that argues innocence in the Court and Case Documents section.

## 12. Uncertainty Rule

If an agent is uncertain whether a change violates one of these invariants, the agent must:
1. stop
2. identify the possible conflict
3. ask for clarification before proceeding

## 13. Temporary Ambiguity Rule

If real-world source data is ambiguous but development must continue, the agent may implement a temporary deterministic `TEMP_RULE` only if:
- the rule is clearly marked in code and documentation as temporary
- the temporary rule does not invent new product scope beyond the existing docs
- a follow-up GitHub issue is created to replace the temporary rule with the real logic
- the temporary rule is treated as a placeholder, not a final business rule
