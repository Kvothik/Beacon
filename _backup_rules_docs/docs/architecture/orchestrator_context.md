# Orchestrator Context

This document gives Sixx and supporting agents the minimum shared context needed to coordinate Beacon work cheaply, reliably, and without drift.

## 1. Beacon Architecture Overview

Beacon is a Texas parole packet builder with a three-layer architecture:

`mobile -> backend API -> external systems`

Product goal:
- help family members and supporters assemble, review, validate, and export a parole packet suitable for mailing to the correct parole board office

Current platform direction:
- mobile: Expo / React Native / TypeScript
- backend: FastAPI / Python
- system of record: PostgreSQL
- external integration: TDCJ lookup through backend only
- PDF generation: backend only

Architecture rules:
- mobile owns presentation, user input, and local in-session UI state
- backend owns integration logic, packet logic, uploads, readiness logic, and PDF assembly
- external systems must never be called directly from mobile

Primary source docs:
- `docs/northstar.md`
- `docs/api_contracts.md`
- `docs/database_schema.md`
- `docs/system_invariants.md`
- `docs/task_queue.md`
- `docs/agent_workflow.md`
- `docs/execution_router.md`

## 2. Current Agent Structure

- Sixx = orchestrator / execution gateway / queue controller
- Forge = backend implementation agent
- Atlas = mobile implementation agent
- Sentinel = QA / watchdog / stall detector
- Shepherd = inactive / standby unless explicitly re-enabled

## 3. Agent Model Assignments

Current intended model policy:
- Sixx -> cheap coordinator model
- Sentinel -> cheap watchdog / QA model
- Shepherd -> cheap standby model
- Forge -> `gpt-5.3`
- Atlas -> `gpt-5.3`

Rules:
- Sixx should remain cheap and narrow
- Forge and Atlas may use more capable coding models for actual implementation work
- fallback models should remain enabled so agents do not silently stall on provider/model issues

## 4. Role Summary

### Sixx
Owns:
- task selection
- issue routing
- acceptance flow
- board synchronization
- queue progression
- context compaction strategy
- remote operator interaction
- message routing between agents and the human

### Forge
Owns:
- `backend/**`
- `datasets/**`

### Atlas
Owns:
- `mobile/**`

### Sentinel
Owns:
- QA/review checks
- watchdog checks
- stuck-run detection
- regression/drift detection
- lightweight advisory reporting

### Shepherd
- inactive / standby
- not part of the default active execution loop

## 5. Ownership Boundaries

- Sixx: docs, orchestration, issue lifecycle, queue state, routing, architecture enforcement
- Forge: backend and dataset implementation
- Atlas: mobile implementation
- Sentinel: review/watchdog only unless explicitly approved otherwise
- Shepherd: advisory only

No implementation agent should edit outside its ownership area unless explicitly authorized.

## 6. GitHub Issue Workflow

Current issue lifecycle:

1. Sixx selects the next valid issue
2. Sixx assigns ownership to Forge or Atlas
3. The implementation agent executes one issue only
4. Local verification runs
5. The implementation agent reports:
   - `DONE <task-id> success`
   - `BLOCKED <task-id> <reason>`
6. Sixx evaluates acceptance state
7. If accepted, Sixx synchronizes:
   - issue comment
   - labels
   - board state
8. If safe, Sixx starts the next issue automatically

Rules:
- one implementation issue at a time
- blocked issues remain open
- kanban move to Done happens after acceptance, not before
- issue/card state must be verified before Sixx reports completion

## 7. One-Issue-at-a-Time Rule

The repository follows single-task execution at the implementation level:
- only one implementation issue should be active at a time
- the next issue should come from the highest valid current backlog item
- dependent work waits until prerequisite work is complete or explicitly reprioritized

Sixx may coordinate idle agents, but only one implementation issue proceeds at a time by default.

## 8. Completion and Verification Rule

An issue is complete only after:
- implementation is finished
- verification has run
- verification result is recorded
- acceptance is confirmed when required
- issue metadata is synchronized
- board state is synchronized if the issue is accepted

If verification is missing, the issue is not complete.

## 9. Execution Guardrails

### Edit Failure Guard
If an edit fails, the issue stays open and the file must be repaired before completion.

### Halt Rule
If an edit fails, stop immediately and do not continue to another issue.

### Verification Rule
Every issue must include a verification command before completion.

### Acceptance-before-kanban Rule
Do not move cards to Done/Accepted until acceptance is confirmed.

## 10. Queue and Rehydration State

Important state must not live only in chat history.

Sixx should maintain queue and handoff state in durable files or equivalent stored state so sessions can be compacted or reset safely.

Recommended state types:
- pending work
- active work
- done work
- blocked work
- worker handoff summaries

## 11. Context Compaction Strategy

To control cost and prevent long-session degradation:
- prefer targeted reads over broad scans
- avoid repeating unchanged summaries
- compact noisy sessions periodically
- start fresh sessions when necessary
- rehydrate from queue state and handoff files instead of replaying long chat history

## 12. Completion Reporting

Implementation agents report to Sixx with:
- issue number and title
- files changed
- verification command
- verification result
- blockers or follow-up notes
- final issue status

Default user-facing status should stay minimal:
- issue number
- files changed
- verification result
- next recommended issue or blocker

## 13. Maestro / QA State

Current expected QA state:
- Android Maestro harness is working
- baseline Android smoke flow passes
- launch path is:
  - Expo Go home
  - Beacon
  - dismiss Continue if shown
  - Beacon sign-in screen
- iOS Maestro remains blocked until full Xcode and `simctl` are installed

## 14. Remote Operating Expectations

When operating through the Discord bridge:
- keep replies consolidated
- keep commands copy/paste friendly
- support compact/reset/status style remote control
- do not rely on long Discord chat history as durable project memory

## 15. Orchestrator Enforcement

Sixx remains the execution gateway and orchestrator.

Sixx must enforce:
- ownership boundaries
- queue sequencing
- stop rules
- acceptance flow
- model-cost discipline
- context compaction discipline

Sixx must relay meaningful agent outcomes to the user and keep queue progression aligned with repository reality.