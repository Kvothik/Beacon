# Agent Workflow
Audited build documentation for the Texas Parole Packet Builder

## 1. Purpose

This document defines the required execution order for autonomous implementation work so agents build the MVP predictably, validate the right things, and stop before scope drift.

## 2. Global Working Rules

Agent model assignments:
- Sixx -> `gpt-5-mini`
- Sentinel -> `gpt-5-mini`
- Shepherd -> `gpt-5-mini` (inactive / standby)
- Forge -> `gpt-5.4`
- Atlas -> `gpt-5.4`

- Canonical local repository path: `~/dev/beacon`.
- Work on one task at a time.
- Prefer P0 scope until the MVP is complete.
- Read only the docs and source files required for the current task.
- Do not create endpoints, tables, packet sections, or PDF behaviors not documented in the specs.
- If file structure changes, update `docs/repo_map.md` in the same change set.
- After completing work for an issue, push the corresponding committed changes to GitHub before starting the next issue.
- Sixx must not report an issue as fully completed to the user until the relevant commits have been pushed to the GitHub repository.
- After completing work for a queued task or GitHub issue, update the corresponding GitHub issue/PR status and move the GitHub project/kanban card to the appropriate completion state before starting the next task.
- On every completed story, update `docs/task_queue.md` so issue status and current execution state stay accurate before starting the next task.
- If real-world data ambiguity exists, the agent may implement a `TEMP_RULE` to keep development moving only when the rule is clearly marked in code/docs as temporary and a follow-up GitHub issue is created for the real logic.
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
- `execution_router.md`

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

## 5. Discord Remote Response Rule

When operating through the developer Discord bridge:

- return the full answer as **one single consolidated message** whenever reasonably possible
- avoid fragmented follow-up messages for the same response unless the human explicitly asks for chunking
- prefer copy/paste-friendly formatting with short sections and bullets
- if the response would be very long, compress it rather than splitting it into multiple Discord messages

## 6. Token Optimization Rule

Reduce token usage.

Rules:
- do not repeatedly re-read the entire repository or docs unless required
- use cached context whenever possible
- only read files directly related to the current issue
- do not rehydrate the entire repo unless context is lost
- do not re-scan docs on every task
- prefer targeted file reads instead of directory scans
- read `docs/task_queue.md` only for next-task decisions
- read `docs/api_contracts.md` or `docs/database_schema.md` only when implementing endpoints or validating endpoint/schema behavior
- do not summarize unchanged documentation repeatedly
- do not produce long explanations when a short status is sufficient

Default status reports should include only:
- issue number
- files changed
- verification result
- next recommended issue

## 7. Validation Rules

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

## 7. Stop Conditions

Stop and report a blocker when:

- a required spec is missing or contradictory
- a task would require inventing an API or schema
- TDCJ HTML no longer matches the parser spec
- a change would violate `system_invariants.md`
- the current task exceeds configured time/token limits without stable progress

## 8. Out of Scope Until Explicitly Reprioritized

Do not implement before P0 completion:

- AI-assisted packet drafting
- packet scoring
- analytics dashboards
- collaboration
- advanced notifications beyond documented MVP needs

## 9. Multi-Agent Execution Model

Sixx orchestrates work and reviews outcomes.
Forge implements backend tasks.
Atlas implements mobile tasks.

Rules:
- one agent per issue
- no cross-ownership edits
- architecture changes route through Sixx
- no agent spawning

Execution model:
- Sixx assigns issues
- Forge handles backend issues
- Atlas handles mobile issues

Each issue completion requires:
1. implementation
2. local verification
3. GitHub issue comment with summary
4. label `status:complete`
5. close issue
6. commit referencing issue

Commit rules:
- Forge and Atlas may not commit directly to main
- all commits must reference the GitHub issue number
- all commits must be reviewed or finalized through Sixx
- commit message format: `type: description (#issue)`

Supervisor and QA behavior:
- Sixx performs next-step planning directly using `docs/execution_router.md`, GitHub issue state, and project board state
- Shepherd is inactive / standby and is not used in the active execution loop unless explicitly re-enabled
- Sentinel is approval-gated and reviews completed work for regressions, drift, missing verification, and acceptance-criteria compliance on high-risk issues
- Sentinel may prepare future GitHub issues only after explicit approval and does not assign them itself
- implementation completion flow is: implementation done -> Sixx verifies -> board/card to `DELIVERED` -> Sentinel review when required -> `ACCEPTED` or `IN PROGRESS`
- after any board move, Sixx must verify that the issue/card is actually present on the project board and in the expected status before reporting completion
- if Sentinel accepts, Sixx must relay the Sentinel result to the user immediately and then determine the next recommendation directly
- if Sentinel rejects, Sixx must relay the Sentinel rejection to the user immediately; no other issue may begin until the rejection is addressed or the human explicitly reprioritizes
- all agent-to-human messages and all human-to-agent execution instructions route through Sixx
- when an issue completes and the next routed issue is safe to start, Sixx should start it immediately instead of waiting for a separate approval ping
- Forge and Atlas do not message the user directly unless routed through Sixx
- if Sixx receives any agent message, Sixx must relay it to the user through Discord immediately
- Sixx remains the execution gateway, central orchestrator, and message router, and enforces agent scope boundaries
