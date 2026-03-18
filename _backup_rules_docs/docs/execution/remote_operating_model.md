# Beacon Remote Operating Model

## Purpose

This document defines the stable remote operating model for the BEACON agent system.

## Canonical Agents

- Sixx (orchestrator): manages queue, assigns tasks, spawns workers, updates GitHub board, sends Telegram updates, enforces lifecycle
- Aegis (strategist / proposal engine): analyzes repository structure, detects architectural drift and technical debt, proposes improvements, creates GitHub issues, and sends Telegram proposals
- Forge (backend implementation): writes code, updates schema, implements backend services, and creates migrations
- Atlas (frontend/mobile implementation): writes user interface code, implements frontend and mobile features, collaborates with Forge
- Sentinel (QA / verification): runs builds, lint, tests, verifies acceptance criteria, moves issues on pass or fail
- Pulse (runtime monitor): monitors runtime system, verifies queue integrity, detects stalls, restarts system if frozen, and sends alerts

## Remote Execution Workflow

1. Sixx selects the next valid issue from the queue.
2. Sixx assigns the issue to the appropriate implementation agent based on ownership labels.
3. The assigned worker spawns an isolated execution session.
4. Worker reports lifecycle events: worker_spawned, worker_execution_start, worker_heartbeat, DONE or BLOCKED, worker_terminated, queue_cleanup.
5. Sixx monitors lifecycle events to advance the queue and trigger Telegram notifications.

## Worker Lifecycle Expectations

- Workers must only handle one active task at a time.
- Workers terminate cleanly after reporting DONE or BLOCKED.
- Silent or unexpected termination classifies as failure requiring manual intervention.
- Workers may enter fallback mode where Sixx assumes active implementation if workers stall or fail.

## Queue Interaction Rules

- Task progress is tracked through structured lifecycle events.
- Queue state updates are managed by Sixx based on worker reports.
- Only one active task allowed per worker session.
- Blocked tasks pause queue progression until resolution.

## Failure Handling and Blocking Conditions

- Workers must explicitly report BLOCKED with reason.
- Sixx stops queue advancement on incomplete or blocked tasks.
- Verification failures or missing specifications block task completion.
- Unexpected model or runtime failures must be detected and addressed.

## Sentinel Verification Role

- Sentinel runs verification builds, lint/typechecks, and tests.
- Sentinel confirms acceptance criteria before moving issues to Accepted.
- Sentinel marks tasks as In Progress if verification fails.
- Sentinel performs stall and failure detection to alert or pause the queue.

## Pulse Monitoring Responsibilities

- Pulse monitors main session responsiveness.
- Pulse verifies queue integrity and detects stalled workers.
- Pulse restarts the system if unresponsive or frozen.
- Pulse sends Telegram alerts for system health and events.
