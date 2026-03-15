# Execution Router

## Canonical Agents

- Sixx (orchestrator): assigns tasks, manages queue, updates GitHub board, sends Telegram alerts, enforces worker lifecycle
- Aegis (strategist / proposal engine): analyzes repo for architectural drift, proposes improvements, creates GitHub issues, sends Telegram proposals
- Forge (backend): implements backend logic, updates schema, creates migrations
- Atlas (frontend/mobile): implements UI and mobile features, collaborates with backend
- Sentinel (QA / verification): runs tests, verifies acceptance criteria, flags regressions and stalls
- Pulse (runtime monitor): monitors runtime system health, queue integrity, and worker stalls; triggers restarts and alerts

## Routing Priority

Sixx prioritizes issues based on:

1. highest valid backlog issue
2. unblocked dependencies
3. architectural and scope safety
4. risk minimization
5. ownership matching

## Execution Model

- Only one active implementation issue at a time unless human overrides.
- Workers spawn isolated sessions for execution.
- Completion reports must be structured: DONE or BLOCKED.
- Sentinels review required for backend, schema, parsing, upload, scanning, PDF, orchestration.

## Issue Outcomes

- ACCEPT: move issue forward, sync board, continue queue.
- CONCERNS: allow continued work with uncertainty.
- REJECT: keep issue open, log reason, route work, pause queue.

## Acceptance & Rejection Process

- Acceptance requires verification, metadata update, and board sync.
- Rejections pause queue and require corrective routing.

## Status and Routing

- Execution status messages should be concise.
- Avoid repetitive board summaries.

## Model Assignments

- Sixx runs cheap coordination models.
- Forge and Atlas run GPT-5.3 models for implementation.
- Sentinel runs a cheap QA/watchdog model.

## Queue Progression

- Continue automatically on safe completion.
- Halt on blockers, verification failures, edit errors, dependencies, or human holds.
- Sixx ensures queue never stalls silently.

## Platform QA Status

- Android Maestro flows pass successfully.
- iOS testing pending tooling support.
- Sentinel does not claim iOS QA coverage until tooling is available.
