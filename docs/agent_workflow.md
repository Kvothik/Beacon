# Agent Workflow
Audited build documentation for the Texas Parole Packet Builder

## 1. Purpose

This document defines the required execution order for autonomous implementation work so agents build the MVP predictably, validate the right things, and stop before scope drift.

## 2. Global Working Rules

- Work on one task at a time.
- Prefer P0 scope until the MVP is complete.
- Read only the docs and source files required for the current task.
- Do not create endpoints, tables, packet sections, or PDF behaviors not documented in the specs.
- If file structure changes, update `docs/repo_map.md` in the same change set.
- If a requested change conflicts with `system_invariants.md`, stop and ask.

## 3. Required Build Order

### Phase 0 — Documentation Baseline

Complete and stabilize these docs before application code expands:

- `northstar.md`
- `api_contracts.md`
- `database_schema.md`
- `pdf_spec.md`
- `scanner_implementation.md`
- `error_policy.md`
- `system_invariants.md`
- `repo_map.md`

Exit criteria:
- endpoint names are documented
- table names are documented
- packet ordering is documented
- scanner approach is documented
- error format is documented

### Phase 1 — Repository and Runtime Scaffolding

Create only the minimum structure needed for implementation:

- mobile Expo app shell
- backend FastAPI app shell
- backend config and database wiring
- initial test structure

Exit criteria:
- mobile app boots
- backend app boots
- health check endpoint responds
- no undocumented files or modules are introduced

### Phase 2 — Authentication

Implement:

- user registration
- user login
- authenticated session/token flow
- mobile login/register screens wired to backend

Exit criteria:
- user can register
- user can sign in
- protected endpoints reject unauthenticated access
- authentication responses match `api_contracts.md`

### Phase 3 — Offender Lookup

Implement:

- backend TDCJ adapter
- offender search endpoint
- offender detail endpoint
- mobile search and selection flow

Exit criteria:
- backend can submit TDCJ search requests
- search results normalize correctly
- user can select one offender
- no direct mobile scraping exists

### Phase 4 — Parole Board Mapping

Implement:

- backend board office mapping based on unit/facility
- endpoint returning office name, mailing address, and contact fields
- mobile display for selected offender

Exit criteria:
- selected offender shows a board office result
- mapping logic remains in backend services

### Phase 5 — Packet Builder Core

Implement:

- packet creation and retrieval
- section progress model
- section detail flows for all documented packet sections
- text entry for section-specific content

Exit criteria:
- user can create a packet tied to an offender
- user can save data into each packet section
- review state can determine populated vs incomplete sections

### Phase 6 — Uploads and Scanner v1

Implement:

- upload initiation and completion flow
- section-linked document records
- mobile document picker/upload
- mobile scanner flow per `scanner_implementation.md`

Exit criteria:
- user can attach uploaded or scanned documents to a packet section
- backend stores metadata and file location
- failed uploads return structured errors

### Phase 7 — Cover Letter and PDF Generation

Implement:

- cover letter generation
- packet assembly in required order
- divider page insertion for populated sections
- final PDF export endpoint
- mobile review and export trigger

Exit criteria:
- backend generates one print-ready PDF
- packet order matches `pdf_spec.md`
- PDF includes cover letter and divider pages as required

### Phase 8 — Final Review and MVP Hardening

Implement:

- review screen completion states
- clearer loading/error states
- retry behavior for network failures
- focused test coverage for critical backend logic

Exit criteria:
- user can review packet completeness
- major backend flows have targeted tests
- critical API failures are recoverable and understandable

## 4. Task Selection Rule

When multiple tasks are available, select the highest-priority unfinished item that:

1. is in P0 scope
2. is unblocked by documentation
3. has the fewest dependencies

Prefer foundational backend and contract work before UI polish.

## 5. Validation Rules

### For documentation-only changes
- check cross-document consistency
- ensure names match `repo_map.md`
- ensure no conflicting endpoint or table names were introduced

### For backend changes
- run targeted tests for touched routers/services
- run linting or static checks if configured
- verify response shapes match `api_contracts.md`

### For mobile changes
- run TypeScript checks if configured
- validate touched screens and flows only
- ensure mobile logic does not absorb backend business rules

## 6. Stop Conditions

Stop and report a blocker when:

- a required spec is missing or contradictory
- a task would require inventing an API or schema
- TDCJ HTML no longer matches the parser spec
- a change would violate `system_invariants.md`
- the current task exceeds configured time/token limits without stable progress

## 7. Out of Scope Until Explicitly Reprioritized

Do not implement before P0 completion:

- AI-assisted packet drafting
- packet scoring
- analytics dashboards
- collaboration
- advanced notifications beyond documented MVP needs
