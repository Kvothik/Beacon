# Agent Architecture

Autonomous development in this repository is coordinated through a role-based agent system designed to keep implementation deterministic, auditable, and aligned with documented product constraints.

## 1. Purpose

This architecture separates planning, implementation, verification, and workflow control so no single agent silently invents product behavior, schema, or architecture.

## 2. Agent Roles

### Sixx (orchestrator)

Responsibilities:
- manage queue
- assign tasks
- spawn workers
- update GitHub board
- send Telegram updates
- enforce worker lifecycle

### Aegis (strategist / proposal engine)

Responsibilities:
- analyze repository structure
- detect architectural drift
- detect technical debt
- propose improvements
- create GitHub issues in Sandbox column
- send proposal to Telegram
- wait for approval before moving issue to backlog
 Rules:
- may not execute code
- may only create proposals

### Forge (backend implementation)

Responsibilities:
- write code
- update schema
- implement backend services
- create migrations
- follow strategy from Aegis

### Atlas (frontend/mobile implementation)

Responsibilities:
- write code for user interface
- implement frontend and mobile features
- collaborate with Forge for API integration

### Sentinel (QA / verification)

Responsibilities:
- run builds
- run lint and typechecks
- run tests
- verify acceptance criteria
- PASS → move issue to Accepted
- FAIL → move issue to In Progress

### Pulse (runtime monitor)

Responsibilities:
- verify main session responsiveness
- verify queue integrity
- detect stalled workers
- restart system if frozen
- send Telegram alert

## 3. Execution Model

The Overseer Agent coordinates a strict handoff model:
1. Overseer selects the next issue
2. Planner interprets the issue and produces the execution plan
3. Builder implements only the planned scope
4. Verifier validates the result
5. Documentation Agent updates docs when needed
6. Overseer commits, pushes, updates GitHub, and advances the queue

## 4. Why This Exists

This architecture exists to:
- reduce hallucinated code and undocumented assumptions
- keep issue execution deterministic
- enforce sequential development
- isolate planning from implementation
- make failures and ambiguities explicit before code lands

## 5. Stop Principle

If ambiguity, undocumented schema changes, or rule violations appear at any stage, the Overseer must stop execution and surface the blocker rather than allow silent drift.
