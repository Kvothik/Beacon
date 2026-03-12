# Task Queue
Audited build documentation for the Texas Parole Packet Builder

## 1. Purpose

This document defines the repository-backed implementation queue for autonomous work.

It is ordered for MVP-first delivery, keeps P0 separate from later work, and is written so each task can be converted into one or more GitHub issues.

## 2. Queue Rules

- Work from top to bottom unless a human explicitly reprioritizes.
- Keep only one implementation task actively in progress at a time.
- Do not start P1 or P2 work until P0 is complete or explicitly reprioritized.
- If a task would require inventing an endpoint, schema, packet section, or PDF behavior, stop and update docs first.
- If file structure changes, update `docs/repo_map.md` in the same change set.
- When a queued task is completed, update the corresponding GitHub issue/PR, move the GitHub project/kanban item to its completion state, and update repository tracking docs so the completed status is visible from repo context.
- Treat blockers and dependencies listed here as part of the implementation contract.

## 3. MVP Build Order (P0)

### Execution State

- completed: `P0-01`, `P0-02`, `P0-03`, `P0-04`, `P0-05`, `P0-06`, `P0-07`, `P0-08`, `P0-09`, `P0-10`, `P0-11`, `P0-12`, `P0-13`, `P0-14`, `P0-15`, `P0-16`, `P0-17`, `P0-18`, `P0-19`, `P0-20`, `P0-22`, `P0-23`, `P0-24`, `P0-25`, `P0-26`
- current: `P0-27`

### P0-01. Lock documentation baseline and cross-document consistency

Status:
- completed

Scope:
- verify `northstar.md`, `agent_workflow.md`, `feature_priority.md`, `api_contracts.md`, `database_schema.md`, `pdf_spec.md`, `scanner_implementation.md`, `error_policy.md`, `system_invariants.md`, `tdcj_lookup_adapter.md`, and `tdcj_html_parser_spec.md`
- resolve doc-level naming drift that would block implementation sequencing
- confirm packet section names, endpoint names, table names, and PDF ordering are aligned

Why first:
- `agent_workflow.md` requires the documentation baseline before application code expands

Dependencies:
- none

Blocks:
- all implementation work

Issue shape:
- docs-only

### P0-02. Define backend app shell and runtime scaffolding

Status:
- completed

Scope:
- create the minimum FastAPI application shell
- define config, security, database wiring, and router registration layout consistent with `docs/repo_map.md`
- add a health check endpoint within documented backend structure

Dependencies:
- P0-01

Blocks:
- auth endpoints
- lookup endpoints
- packet endpoints
- upload endpoints
- PDF endpoints
- backend tests

Issue shape:
- backend
- scaffolding

### P0-03. Define mobile app shell and navigation scaffolding

Status:
- completed

Scope:
- create the minimum Expo/React Native shell
- define app navigation and base screen structure from `docs/repo_map.md`
- establish API client wiring and basic loading/error presentation primitives

Dependencies:
- P0-01

Blocks:
- auth UI
- offender lookup UI
- packet builder UI
- scanner UI
- review/export UI

Issue shape:
- mobile
- scaffolding

### P0-04. Define database schema migrations and seed strategy

Status:
- completed

Scope:
- implement MVP database tables from `database_schema.md`
- define migrations for users, offenders, parole board offices, parole board unit mappings, packets, packet sections, documents, and notification subscriptions
- define seed strategy for packet sections, parole board offices, and unit mappings

Dependencies:
- P0-01
- P0-02

Blocks:
- auth persistence
- packet creation
- parole board lookup
- uploads
- notification subscription endpoint

Issue shape:
- backend
- database
- seeds

### P0-05. Prepare parole board seed datasets and import path

Status:
- completed

Scope:
- create repository-backed datasets for parole board offices and unit-to-office mappings under `datasets/`
- define import/seed path used by backend services
- ensure backend lookup logic depends on seeded data, not hardcoded mobile logic

Dependencies:
- P0-01
- P0-04

Blocks:
- parole board lookup endpoint
- packet creation with office association
- cover letter generation requiring office address data

Issue shape:
- data
- backend

### P0-06. Implement authentication backend

Status:
- completed

Scope:
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- protected-route authentication enforcement
- structured auth errors per `error_policy.md`

Dependencies:
- P0-02
- P0-04

Blocks:
- all protected packet, upload, PDF, and notification flows
- authenticated mobile flows

Issue shape:
- backend
- auth

### P0-07. Implement mobile authentication flow

Status:
- completed

Scope:
- login screen
- registration screen
- authenticated session/token handling
- auth bootstrap to home screen
- structured error display for auth failures

Dependencies:
- P0-03
- P0-06

Blocks:
- authenticated user workflow in mobile

Issue shape:
- mobile
- auth

### P0-08. Implement TDCJ lookup adapter and parser core

Status:
- completed

Scope:
- implement backend adapter boundary in `backend/app/services/tdcj_lookup_service.py`
- implement search request submission per `tdcj_lookup_adapter.md`
- implement results-page parsing, SID extraction, pagination support, and detail-page parsing per `tdcj_html_parser_spec.md`
- normalize transient integration data to API-facing shapes
- return structured parser/network errors per `error_policy.md`

Dependencies:
- P0-02

Blocks:
- offender search endpoint
- offender detail endpoint
- offender normalization tests

Issue shape:
- backend
- integration
- parser

### P0-09. Implement offender lookup API endpoints

Status:
- completed

Scope:
- `POST /api/v1/offenders/search`
- `GET /api/v1/offenders/{sid}`
- request validation for allowed search modes only
- normalized source metadata in responses
- no persistence beyond documented snapshot/caching rules

Dependencies:
- P0-02
- P0-08

Blocks:
- mobile offender search flow
- packet creation from selected offender

Issue shape:
- backend
- offenders

### P0-10. Implement mobile offender search and offender selection flow

Status:
- completed

Scope:
- search form for last name + first initial, TDCJ number, or SID
- results list and user selection flow
- offender detail display for selected SID
- clear retry/error UX for TDCJ/network failures

Dependencies:
- P0-03
- P0-09

Blocks:
- parole board lookup display
- packet creation flow

Issue shape:
- mobile
- offenders

### P0-11. Implement parole board lookup service and endpoint

Status:
- completed

Scope:
- backend mapping from offender unit/facility to seeded parole board office data
- `GET /api/v1/parole-board-office`
- response shape exactly matching `api_contracts.md`

Dependencies:
- P0-02
- P0-04
- P0-05

Blocks:
- packet creation with office association
- mobile office display
- cover letter generation using office mailing info

Issue shape:
- backend
- data
- parole-board

### P0-12. Implement mobile parole board office display

Status:
- completed

Scope:
- show office name, address, phone, and notes after offender selection
- keep all mapping logic in backend

Dependencies:
- P0-03
- P0-10
- P0-11

Blocks:
- end-to-end pre-packet workflow

Issue shape:
- mobile
- parole-board

### P0-13. Implement packet creation and section initialization backend

Status:
- completed

Scope:
- `POST /api/v1/packets`
- create offender snapshot record limited to documented fields
- associate parole board office
- initialize all eight packet sections in `pdf_spec.md` order with stored sort order

Dependencies:
- P0-04
- P0-09
- P0-11
- P0-06

Blocks:
- packet detail retrieval
- section editing
- review flow
- uploads tied to packet sections

Issue shape:
- backend
- packets

### P0-14. Implement packet detail, section update, and review backend

Status:
- completed

Scope:
- `GET /api/v1/packets/{packet_id}`
- `PATCH /api/v1/packets/{packet_id}/sections/{section_key}`
- `GET /api/v1/packets/{packet_id}/review`
- section completeness and document count reporting
- ownership enforcement and structured errors

Dependencies:
- P0-06
- P0-13

Blocks:
- mobile packet builder
- review screen
- cover letter and PDF workflows

Issue shape:
- backend
- packets
- review

### P0-15. Implement mobile packet builder and section detail flows

Scope:
- packet builder screen with section progress
- section detail screen for all documented packet sections
- notes entry and completion toggles per section
- guidance copy placeholders wired to each section screen without adding new sections

Dependencies:
- P0-03
- P0-13
- P0-14

Blocks:
- upload attachment workflow from sections
- review/export UX

Issue shape:
- mobile
- packets

### P0-16. Implement upload initiation/completion backend flow

Scope:
- `POST /api/v1/packets/{packet_id}/uploads`
- `POST /api/v1/packets/{packet_id}/uploads/{document_id}/complete`
- document record creation and packet-section association
- object-storage metadata handling
- upload failure handling per `error_policy.md`

Dependencies:
- P0-06
- P0-13
- P0-14

Blocks:
- mobile upload UI
- scanner upload completion
- PDF generation from attached files

Issue shape:
- backend
- uploads

### P0-17. Implement mobile document upload flow

Scope:
- document picker upload into selected packet section
- upload progress/loading states appropriate for MVP
- retry on structured retryable failures
- document list refresh after upload completion

Dependencies:
- P0-03
- P0-15
- P0-16

Blocks:
- full non-scanner attachment workflow

Issue shape:
- mobile
- uploads

### P0-18. Implement scanner v1 mobile flow

Scope:
- camera permission request
- capture, review, retake, and accept flow
- upload accepted captures into selected packet section using upload API
- temporary local retention only long enough for in-session retry

Dependencies:
- P0-03
- P0-15
- P0-16
- `scanner_implementation.md`

Blocks:
- mobile scan-to-section workflow

Issue shape:
- mobile
- scanner

### P0-19. Implement cover letter generation backend

Scope:
- `POST /api/v1/packets/{packet_id}/cover-letter`
- generate formal, respectful cover letter content using sender, offender, and board office data
- enforce safety rule against innocence-claim generation

Dependencies:
- P0-11
- P0-13
- P0-14
- P0-06

Blocks:
- final PDF generation
- review/export completion

Issue shape:
- backend
- pdf
- content

### P0-20. Implement final PDF generation backend

Scope:
- `POST /api/v1/packets/{packet_id}/pdf`
- `GET /api/v1/packets/{packet_id}/pdf`
- backend-only PDF assembly
- cover letter insertion
- populated-section divider pages only
- section ordering exactly per `pdf_spec.md`
- ready vs generating status handling without false success states

Dependencies:
- P0-16
- P0-19
- P0-14
- P0-06

Blocks:
- mobile export completion flow
- end-to-end MVP acceptance

Issue shape:
- backend
- pdf

### P0-21. Implement mobile review and export flow

Scope:
- review screen showing completeness by section
- export trigger for cover letter/PDF generation flow
- PDF-ready status polling or refresh UX consistent with API contract
- clear loading, error, and success states

Dependencies:
- P0-15
- P0-20
- P0-14

Blocks:
- end-to-end MVP validation

Issue shape:
- mobile
- review
- export

### P0-22. Implement backend cover letter generation

Status:
- completed

Scope:
- generate a deterministic cover letter for the packet using sender information plus offender and parole board office data
- keep language respectful, accountability-oriented, and safe for MVP use

Dependencies:
- P0-15

Issue shape:
- backend
- pdf

### P0-23. Implement backend packet PDF assembly

Status:
- completed

Scope:
- generate the final packet PDF including cover letter, section dividers, section content, and uploaded documents

Dependencies:
- P0-22

Issue shape:
- backend
- pdf


### P0-24. Implement mobile packet review screen

Status:
- completed

Scope:
- mobile packet review screen summarizing packet sections, uploads, and cover letter state
- clear read-only review before final validation/export

Dependencies:
- P0-18
- P0-19
- P0-22

Issue shape:
- mobile
- review

### P0-25. Implement backend packet readiness validation

Status:
- completed

Scope:
- packet readiness validation logic for required sections, uploads, and cover letter prerequisites
- structured readiness result for downstream review/export UX

Dependencies:
- P0-17
- P0-19
- P0-22
- P0-23

Issue shape:
- backend
- validation

### P0-26. Implement mobile completion validation messaging

Status:
- completed

Scope:
- user-facing validation messaging for incomplete packet state
- clear blocking vs non-blocking readiness feedback in the mobile flow

Dependencies:
- P0-24
- P0-25

Issue shape:
- mobile
- validation

### P0-27. Implement mobile PDF generation trigger

Scope:
- trigger final PDF generation from the mobile app
- reflect backend generation state and final readiness transitions

Dependencies:
- P0-23
- P0-24
- P0-25

Issue shape:
- mobile
- pdf

### P0-28. Implement backend error handling hardening

Scope:
- tighten structured error handling across MVP packet, upload, validation, and PDF flows
- ensure retryability and user-safe error behavior remain consistent with `error_policy.md`

Dependencies:
- P0-19
- P0-22
- P0-23

Issue shape:
- backend
- hardening

### P0-29. Implement upload size and file-type guardrails

Scope:
- enforce upload size and file-type guardrails
- return structured validation failures for unsupported uploads

Dependencies:
- P0-19

Issue shape:
- backend
- uploads

### P0-30. Implement packet completion UX improvements

Scope:
- improve final packet completion UX for review, readiness messaging, and handoff toward export
- stay within documented MVP scope only

Dependencies:
- P0-24
- P0-25
- P0-26
- P0-27

Issue shape:
- mobile
- ux

### P0-31. Execute end-to-end acceptance test pass

Scope:
- run end-to-end MVP acceptance validation across the documented packet flow
- capture any remaining MVP mismatches as follow-up docs/issues only

Dependencies:
- P0-24
- P0-25
- P0-26
- P0-27
- P0-28
- P0-29
- P0-30

Issue shape:
- qa
- acceptance

## 4. Later Work (Blocked Until P0 Completion)

### P1
- push notification subscription endpoint and delivery wiring
- PDF preview enhancements
- improved section completion scoring
- better upload progress and retry UX beyond MVP minimums
- template refinements for cover letter and divider pages

### P2
- AI-assisted support letter drafting
- packet quality scoring
- photo enhancement suggestions
- analytics or admin dashboards
- collaboration or shared editing

## 5. Dependency Notes

- Notification work is intentionally deferred even though `notification_subscriptions` exists in the schema and an endpoint is documented; `feature_priority.md` places meaningful notification delivery in P1.
- Mobile must never implement TDCJ scraping, parole board mapping rules, or PDF composition logic.
- Offender search/detail responses are transient integration data; packet creation may persist only the documented offender snapshot fields.
- PDF generation must not start before uploads, packet section state, cover letter content, and parole board data are available.

## 6. Task Selection Rule

When multiple P0 tasks are available, choose the highest unfinished task that:
1. is unblocked
2. has the smallest documentation risk
3. unlocks the largest number of downstream tasks

Prefer foundational backend/data tasks before dependent mobile UX tasks.

## 7. Blocker Rule

Stop and report a blocker when:
- a required source doc is contradictory
- a task would require inventing an undocumented endpoint, table, packet section, or PDF behavior
- TDCJ HTML no longer matches `tdcj_html_parser_spec.md`
- the change would violate `system_invariants.md`
- the next step would drift into P1/P2 before P0 completion
