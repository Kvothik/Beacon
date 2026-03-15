# Execution Router

This document defines how Sixx determines the next issue and routes execution across agents.

The router does not store a static issue list.
Actual issue state should come from:
- the GitHub board
- `docs/task_queue.md`
- issue labels and status

## 1. Primary Routing Rule

Sixx determines the next issue using this priority order:

1. highest valid backlog issue
2. unblocked by dependencies
3. safe within architecture and scope
4. smallest unresolved risk
5. appropriate ownership lane

Execution proceeds one issue at a time unless explicitly authorized otherwise.

## 2. Ownership Routing

Ownership routing rules:

Backend work → Forge  
Mobile work → Atlas  
Docs / orchestration → Sixx  

Sentinel does not implement issues by default.

Sentinel is used for:
- QA checks
- regression review
- drift detection
- queue stall detection

## 3. Completion Protocol

Workers must report one of:

DONE <task-id> success

BLOCKED <task-id> <reason>

Sixx uses this result to determine the next step.

Queue progression continues automatically when:
- the issue is complete
- verification passed
- no blocker exists
- no explicit human hold exists

Queue progression stops when:
- an issue is blocked
- verification failed
- edit failure occurred
- runtime/tooling dependency is missing
- explicit human hold exists

## 4. Sentinel Review Policy

Sentinel review is REQUIRED when a change touches:

- backend API endpoints
- database schema
- TDCJ parser logic
- upload/storage orchestration
- scanner capture behavior
- PDF generation or assembly
- orchestration or queue logic

Sentinel review is OPTIONAL when a change is:

- mobile UI only
- layout adjustments
- styling changes
- screen-level refactors

Sentinel review may also be triggered manually.

## 5. Review Outcomes

Sentinel may return one of:

ACCEPT  
CONCERNS  
REJECT  

### ACCEPT

Implementation is healthy.

Sixx may:
- update issue metadata
- synchronize board state
- continue the queue automatically

### CONCERNS

Implementation is usable but has uncertainty.

Sixx may:
- continue queue
- create follow-up issue if needed

### REJECT

Implementation is not acceptable.

Sixx must:
- keep issue open
- record rejection reason
- route corrective work
- stop queue progression until resolved

## 6. Acceptance Flow

When an issue is accepted:

1. verification must be confirmed
2. issue metadata must be updated
3. board state must be synchronized
4. Sixx determines the next issue
5. Sixx continues queue automatically unless approval is required

Acceptance must occur before the kanban card moves to Done/Accepted.

## 7. Rejection Flow

When Sentinel rejects an issue:

1. issue remains open
2. rejection reason is recorded
3. corrective work is identified
4. Sixx routes the repair issue
5. queue progression pauses until repair succeeds

## 8. Default Status Message

Execution updates should remain compact.

Default completion message:

- issue number
- files changed
- verification result
- final issue status
- next recommended issue or blocker

Avoid repeating board summaries unless state changed.

## 9. Model Routing

Current intended model assignments:

Sixx → cheap coordinator model  
Forge → GPT-5.3  
Atlas → GPT-5.3  
Sentinel → cheap watchdog / QA model  

Rules:

- orchestration should remain cheap
- implementation uses stronger models only when needed
- fallback models should remain enabled

## 10. Queue Continuation

Queue progression should continue automatically when safe.

Stop conditions include:

- blocker
- failed verification
- edit failure
- missing dependency
- human hold

Sixx must not allow the queue to stall silently.

## 11. Maestro QA Status

Current QA reality:

Android Maestro harness: working  
Android smoke flow: passing  

Expected launch path:

Expo Go home  
→ Beacon  
→ dismiss Continue if shown  
→ Beacon sign-in screen

iOS Maestro remains blocked until full Xcode and `simctl` are installed.

Sentinel must not claim iOS QA coverage until this tooling exists.