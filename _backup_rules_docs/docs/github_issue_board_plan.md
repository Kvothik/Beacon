# GitHub Issue Board Plan
Audited build documentation for the Texas Parole Packet Builder

## 1. Purpose

This document defines a documentation-backed GitHub issue structure for implementing the MVP in the order required by `docs/task_queue.md`.

It keeps P0 separate from later work and avoids inventing product scope beyond the existing documentation.

## 2. Recommended GitHub Labels

### Priority labels
- `priority:P0`
- `priority:P1`
- `priority:P2`

### Area labels
- `area:docs`
- `area:backend`
- `area:mobile`
- `area:data`
- `area:pdf`
- `area:testing`
- `area:infra`

### Workflow / type labels
- `type:epic`
- `type:task`
- `type:bug`
- `type:hardening`
- `type:qa`
- `type:scaffolding`
- `type:seed-data`

### Domain labels
- `domain:auth`
- `domain:offender-lookup`
- `domain:tdcj-parser`
- `domain:parole-board`
- `domain:packets`
- `domain:uploads`
- `domain:scanner`
- `domain:review`
- `domain:pdf-export`
- `domain:notifications`

### Status helper labels
- `status:blocked`
- `status:ready`
- `status:in-progress`
- `status:needs-docs`
- `status:needs-review`

## 3. Recommended Milestones

### Milestone 1 — P0 Foundation
Includes:
- documentation lock
- backend scaffolding
- mobile scaffolding
- database migrations
- seed/data preparation

Maps to task queue:
- P0-01 through P0-05

### Milestone 2 — P0 Auth + Offender Lookup
Includes:
- auth backend/mobile
- TDCJ adapter and parser
- offender search/detail API
- offender search/detail mobile flow
- parole board lookup backend/mobile

Maps to task queue:
- P0-06 through P0-12

### Milestone 3 — P0 Packet Builder Core
Includes:
- packet creation
- packet detail and section update
- review endpoint
- mobile packet builder and section detail flows

Maps to task queue:
- P0-13 through P0-15

### Milestone 4 — P0 Documents + Scanner + PDF
Includes:
- upload backend/mobile
- scanner v1
- cover letter generation
- final PDF generation
- mobile review/export flow

Maps to task queue:
- P0-16 through P0-21

### Milestone 5 — P0 Hardening + Validation
Includes:
- backend auth tests
- parser/lookup tests
- packet/upload/PDF tests
- mobile hardening
- end-to-end MVP validation

Maps to task queue:
- P0-22 through P0-26

### Milestone 6 — P1 Post-MVP Improvements
Includes:
- notification work
- PDF preview enhancements
- completion scoring improvements
- richer retry/progress UX
- document-template refinements

### Milestone 7 — P2 Deferred Features
Includes:
- AI-assisted drafting
- scoring
- photo enhancement suggestions
- analytics/admin
- collaboration

## 4. Recommended Issue Categories

Use these categories in issue titles, templates, or project views:
- Docs / Spec Alignment
- Scaffolding / Runtime Setup
- Database / Persistence
- Seed Data / Datasets
- Authentication
- TDCJ Adapter / Parser
- Offender Lookup API
- Mobile Lookup UX
- Parole Board Mapping
- Packet Builder
- Uploads / Storage
- Scanner
- Cover Letter / PDF Export
- Testing / QA
- Hardening / Reliability

## 5. Initial Board Columns

Recommended project board columns/statuses:
- `Backlog`
- `Ready`
- `In Progress`
- `Blocked`
- `In Review`
- `Done`

Column intent:
- `Backlog`: documented but not yet the next task
- `Ready`: unblocked and ready to start now
- `In Progress`: exactly one primary implementation issue at a time when possible
- `Blocked`: waiting on dependency, docs clarification, or upstream constraint
- `In Review`: implementation complete, awaiting review/validation
- `Done`: merged/accepted

## 6. Recommended Epics

Create these epics first:

### Epic A — Documentation and Foundation
Covers:
- P0-01 through P0-05

### Epic B — Authentication and Guided Offender Discovery
Covers:
- P0-06 through P0-12

### Epic C — Packet Builder Core
Covers:
- P0-13 through P0-15

### Epic D — Documents, Scanner, and PDF Export
Covers:
- P0-16 through P0-21

### Epic E — MVP Hardening and Validation
Covers:
- P0-22 through P0-26

### Epic F — Post-MVP Improvements (P1)
Covers:
- all P1 items

### Epic G — Deferred Strategic Features (P2)
Covers:
- all P2 items

## 7. How `docs/task_queue.md` Maps to GitHub Issues

### Default mapping rule
- one `P0-XX` queue item = one GitHub issue by default
- if a queue item is too large, split it into a parent issue plus tightly scoped child issues
- do not merge unrelated backend and mobile work into one issue unless the queue item explicitly describes a single end-to-end slice

### Recommended issue structure
Each issue should include:
- objective
- in-scope work only
- explicit dependencies from `docs/task_queue.md`
- acceptance criteria pulled from the source docs
- labels for priority, area, type, and domain
- milestone assignment
- epic link/reference

### Parent/child guidance
Use parent issues or epics when a task spans multiple files or layers, but keep implementation tickets concrete enough to finish in one focused work session.

### Blocker handling
If a queue item is blocked:
- leave the issue open
- add `status:blocked`
- link the blocking issue(s)
- do not move lower-priority P1/P2 issues ahead of blocked P0 work unless explicitly reprioritized

## 8. First 10 GitHub Issues to Create

These should be created first because they represent the top of the documented MVP queue.

### 1. Audit and lock MVP documentation baseline
Labels:
- `priority:P0`
- `area:docs`
- `type:task`
- `status:ready`

Milestone:
- Milestone 1 — P0 Foundation

Maps to:
- P0-01

### 2. Scaffold backend FastAPI app shell and runtime wiring
Labels:
- `priority:P0`
- `area:backend`
- `type:scaffolding`
- `status:ready`

Milestone:
- Milestone 1 — P0 Foundation

Maps to:
- P0-02

Dependencies:
- Issue 1

### 3. Scaffold mobile Expo app shell and navigation structure
Labels:
- `priority:P0`
- `area:mobile`
- `type:scaffolding`
- `status:ready`

Milestone:
- Milestone 1 — P0 Foundation

Maps to:
- P0-03

Dependencies:
- Issue 1

### 4. Implement MVP database schema migrations and persistence wiring
Labels:
- `priority:P0`
- `area:backend`
- `type:task`
- `domain:packets`
- `status:ready`

Milestone:
- Milestone 1 — P0 Foundation

Maps to:
- P0-04

Dependencies:
- Issue 1
- Issue 2

### 5. Create parole board office seed datasets and import strategy
Labels:
- `priority:P0`
- `area:data`
- `area:backend`
- `type:seed-data`
- `domain:parole-board`
- `status:ready`

Milestone:
- Milestone 1 — P0 Foundation

Maps to:
- P0-05

Dependencies:
- Issue 1
- Issue 4

### 6. Implement authentication API endpoints and protected access enforcement
Labels:
- `priority:P0`
- `area:backend`
- `type:task`
- `domain:auth`
- `status:ready`

Milestone:
- Milestone 2 — P0 Auth + Offender Lookup

Maps to:
- P0-06

Dependencies:
- Issue 2
- Issue 4

### 7. Implement mobile login and registration flow
Labels:
- `priority:P0`
- `area:mobile`
- `type:task`
- `domain:auth`
- `status:ready`

Milestone:
- Milestone 2 — P0 Auth + Offender Lookup

Maps to:
- P0-07

Dependencies:
- Issue 3
- Issue 6

### 8. Implement TDCJ lookup adapter and HTML parser core
Labels:
- `priority:P0`
- `area:backend`
- `type:task`
- `domain:tdcj-parser`
- `domain:offender-lookup`
- `status:ready`

Milestone:
- Milestone 2 — P0 Auth + Offender Lookup

Maps to:
- P0-08

Dependencies:
- Issue 2

### 9. Implement offender search/detail API endpoints using normalized TDCJ adapter output
Labels:
- `priority:P0`
- `area:backend`
- `type:task`
- `domain:offender-lookup`
- `status:ready`

Milestone:
- Milestone 2 — P0 Auth + Offender Lookup

Maps to:
- P0-09

Dependencies:
- Issue 2
- Issue 8

### 10. Implement mobile offender search, selection, and offender detail flow
Labels:
- `priority:P0`
- `area:mobile`
- `type:task`
- `domain:offender-lookup`
- `status:ready`

Milestone:
- Milestone 2 — P0 Auth + Offender Lookup

Maps to:
- P0-10

Dependencies:
- Issue 3
- Issue 9

## 9. Issue Title Style Guide

Recommended format:
- `[P0][Backend] Implement authentication API endpoints`
- `[P0][Mobile] Build offender search and selection flow`
- `[P0][Data] Seed parole board offices and unit mappings`

Keep titles:
- short
- imperative
- scoped to one deliverable
- aligned with task queue terminology

## 10. Board Operating Rules

- Always pull the next issue from the top-most unblocked P0 queue item.
- Keep backend/data prerequisites ahead of dependent mobile work.
- Use epics for grouping, not to hide missing acceptance criteria.
- Do not create P1/P2 implementation issues as active work until P0 is validated.
- If docs change in a way that affects implementation order, update `docs/task_queue.md` and this plan together.
- When implementation for an issue is finished, push the committed changes to GitHub, update the issue/PR with completion context, and move the project/kanban item to `Done` (or the correct review/completion column) before starting the next queued issue.
- If task completion changes repository execution state, update the repo-tracked docs that reflect progress so future rehydration shows the completed step.
