# Beacon Remote Operating Model

## Purpose

This document defines the stable remote operating model for Beacon.

Goals:
- keep token usage low
- keep execution moving when workers fail
- avoid orchestration dead ends
- preserve clear ownership and predictable issue flow
- allow long-running autonomous work without relying on long-lived chat history

## 1. Core Model

### Sixx is the coordinator

Sixx always owns:
- issue routing
- execution decisions
- queue progression
- issue/board synchronization
- verification enforcement
- user-facing updates
- fallback implementation when workers are unavailable

Sixx is the control plane, not the long-running expensive implementer.

### Workers are disposable execution lanes

Forge, Atlas, Sentinel, and any other helper lanes are disposable.

Rules:
- one implementation lane per issue
- workers may be replaced without stopping progress
- workers do not own overall continuity
- durable state must live outside chat history

## 2. Model Policy

Current intended model usage:
- Sixx -> cheap coordinator model
- Forge -> `gpt-5.3`
- Atlas -> `gpt-5.3`
- Sentinel -> cheap watchdog / QA model
- fallback models remain enabled

Rules:
- do not run Sixx all day on an expensive coding model
- reserve stronger models for actual implementation or difficult debugging
- planning, routing, tracking, and queue control should stay cheap

## 3. Durable State Rule

Important operating state must not live only in remote chat.

State must be written to durable queue or handoff files, such as:
- active task
- pending work
- blocked work
- done work
- worker handoff summary
- current board snapshot

This allows:
- session compaction
- session reset
- fresh-session rehydration
- worker replacement without losing continuity

## 4. Worker Validity and Fallback

### Preferred worker mode
Use isolated or focused worker sessions when they are functioning normally.

### Fallback mode
If a worker fails, stalls, or cannot be restored:

1. inspect once
2. retry once if a clean recovery path exists
3. if still blocked, enter fallback mode immediately
4. continue the issue directly as Sixx
5. do not loop on recovery attempts

Fallback mode means:
- Sixx becomes the active implementer for the issue
- Sixx remains the coordinator and message gateway
- worker restoration is deferred until a clean recovery path exists

Do not let worker restoration loops block issue progress.

## 5. One-Issue-at-a-Time Rule

Only one implementation issue may be active at a time unless a human explicitly authorizes parallel work.

Rules:
- one issue
- one active lane
- one clear owner
- next issue begins only after the current issue is verified and resolved

## 6. Completion Protocol

Workers must report completion in a structured form:

- `DONE <task-id> success`
- `BLOCKED <task-id> <reason>`

Sixx uses this result to:
- update queue state
- decide whether to continue automatically
- decide whether human approval is needed
- decide whether to pause

Do not rely on vague completion language.

## 7. Verification and Acceptance Rules

An issue is not complete until:
- implementation is finished
- verification has run
- verification result is recorded
- acceptance is confirmed when required
- issue metadata is synchronized
- board state is synchronized if accepted

Rules:
- if an edit fails, stop immediately
- do not continue to another issue after an edit failure
- do not mark complete without verification
- do not move the kanban card to Done before acceptance is confirmed

## 8. Visible Work State

Remote work state should stay obvious but compact.

Use short status updates such as:
- `Seen. Starting now.`
- `Status: in progress`
- `Last thing done: ...`
- `Status: blocked`
- `Status: complete`
- `Status: paused`

Do not flood the operator with repetitive updates.

Default completion update:
- issue number
- files changed
- verification result
- final issue state
- next recommended issue or blocker

## 9. Token Control Rules

### Keep sessions short
- prefer one issue per isolated run when practical
- compact after meaningful work batches
- compact before switching topics
- avoid giant multi-issue remote threads as the only memory source

### Read only what is needed
- read only the docs/files needed for the current issue
- use targeted reads
- avoid repeated repo-wide scans
- avoid repeated doc summarization

### Keep prompts narrow
- avoid verbose planning unless needed
- avoid unnecessary repeated system context
- avoid repeating queue and board summaries unless state changed

## 10. Compaction and Rehydration

To support all-day operation at controlled cost:

- compact after several completed tasks or when session noise grows
- start a fresh session when context becomes bloated
- rehydrate only from:
  - current active task
  - pending queue
  - blocked tasks
  - durable handoff summaries
  - current operating rules

Do not rehydrate from large chat history unless absolutely necessary.

## 11. Remote Control Commands

The remote operating model must support simple recovery commands.

Expected commands:
- status
- compact
- reset current session
- reset all worker sessions
- continue queue

These commands should not depend on reconstructing long chat history.

## 12. Reset-All Recovery Rule

If the system gets stuck, the operator must be able to reset worker activity without losing queue state.

Reset-all should:
- stop active worker sessions
- preserve durable queue and handoff files
- clear stale session state if needed
- allow Sixx to resume from the latest saved queue state

Reset-all must not destroy the queue.

## 13. Sentinel / Watchdog Role

Sentinel is not the primary implementer.

Sentinel should be used for:
- lightweight QA checks
- stall detection
- missing-verification detection
- queue-stuck detection
- model/runtime failure detection

Sentinel should not block normal execution unless a configured policy requires it.

## 14. Remote Workflow

For each issue:

1. identify the current issue
2. choose the correct execution lane
3. confirm whether the worker path is healthy
4. if unhealthy, use fallback mode quickly
5. implement in one lane only
6. run targeted verification
7. update issue/queue/board state
8. report one concise completion message
9. compact or reset context when needed
10. continue the queue if safe

## 15. Success Criteria

This model is working when:
- worker failures do not stop issue progress
- token usage stays bounded
- long-running coordination remains cheap
- workers can be replaced without losing continuity
- queue progression continues automatically
- reset-all recovery works without losing state