# Agent Workflow

Audited build and execution workflow for the Beacon parole packet builder.

## 1. Purpose

This document defines the required operating model for autonomous work so the Beacon system can run predictably, cheaply, and safely across long sessions.

## 2. Global Working Rules

Canonical local repository path:
- `~/dev/Beacon`

Core rules:
- work one implementation issue at a time
- prefer highest-value MVP-safe work unless explicitly reprioritized
- read only the docs and files required for the current task
- do not invent endpoints, tables, packet sections, or PDF behaviors not documented in the specs
- if file structure changes, update `docs/repo_map.md`
- do not move a card to Done until acceptance is confirmed
- do not start the next issue if the current issue is unverified or blocked

## 3. Agent Model Assignments

Current intended model policy:

- Sixx = orchestrator
- Aegis = strategist / proposal engine
- Forge = backend implementation
- Atlas = frontend / mobile implementation
- Sentinel = watchdog / QA
- Pulse = runtime monitor

Rules:
- Sixx should not run all day on an expensive implementation model
- expensive models should be reserved for actual implementation and review work
- fallback models should remain enabled so temporary model issues do not halt the system

## 4. Agent Roles

- Sixx = orchestrator, execution gateway, queue controller, and message router
- Aegis = strategist and proposal creation
- Forge = backend implementation agent
- Atlas = frontend and mobile implementation agent
- Sentinel = watchdog, QA, regression review, stall detection
- Pulse = runtime monitor

Sixx owns:
- task selection
- issue routing
- acceptance coordination
- queue progression
- board synchronization
- context compaction strategy
- remote control behavior

## 5. Current Execution Loop

The active execution loop is:

1. Sixx selects the next valid issue
2. Sixx assigns it to the correct implementation agent
3. The implementation agent performs only the scoped work
4. Verification is run
5. The agent reports either:
   - `DONE <task-id> success`
   - `BLOCKED <task-id> <reason>`
6. Sixx evaluates the result
7. If accepted, Sixx synchronizes issue metadata and board state
8. If safe, Sixx starts the next queued issue automatically

## 6. Required Runtime Rules

### Execution Guard
If an edit fails, the issue stays open and must be repaired before completion.

### Execution Halt Rule
If an edit fails, stop immediately and do not continue to the next issue.

### Verification Rule
Every issue must include a verification command before completion.

### Acceptance-before-kanban Rule
Do not move the kanban card to Done/Accepted until acceptance is confirmed.

## 7. Current Build State

Beacon has completed the core guided packet workflow and major stabilization work.

Recently completed:
- #33 Maestro test harness (Android path passing; iOS blocked pending Xcode)
- #39 workflow event logging
- #41 attachment visibility
- #42 scan quality / rescan guidance
- #43 offender search filtering
- #44 offender selection clarity
- #45 packet builder progress indicators
- #46 improved error handling
- #48 packet readiness review

Current board state should be tracked in GitHub / queue files, not assumed from this document.

## 8. Task Selection Rule

When multiple tasks are available, select the highest-value unfinished item that:
1. is unblocked
2. is safe within current architecture
3. has the fewest unresolved dependencies
4. materially improves MVP reliability, usability, or automation confidence

Prefer:
- broken or blocked workflow fixes
- regression-prevention work
- high-value QA/automation
- clear MVP-enabling features

## 9. Queue Continuation Rule

Queue processing should continue automatically when:
- the current task reports `DONE`
- verification passed
- the issue is accepted or acceptance is already implied by the operating mode
- no explicit human hold is active

Queue processing should stop when:
- the issue is blocked
- a stop rule triggers
- a human reprioritizes
- the system detects a tooling or model failure

## 10. Token Optimization Rule

Reduce token usage aggressively.

Rules:
- do not repeatedly reread the full repository
- prefer targeted file reads
- store important state in queue/handoff files
- compact sessions after several completed tasks
- use fresh sessions when needed, then rehydrate from saved state
- do not keep long Discord history as the only memory source
- do not repeat board summaries unless state changed
- default reports should stay short

Default status report:
- issue number
- files changed
- verification result
- final issue status
- next recommended issue or blocker

## 11. Context Compaction and Rehydration

To support all-day autonomous execution at controlled cost:

- important queue state must be saved outside chat
- worker state must be recoverable from handoff files
- Sixx should compact noisy sessions periodically
- if a session becomes too bloated, start a fresh session and rehydrate from queue state and handoff files

Recommended behavior:
- compact after several completed tasks
- use a fresh session after larger execution batches
- rehydrate only the current queue state, active task, blockers, and operating rules

## 12. Verification Rules

### Documentation changes
- verify cross-doc consistency
- update naming references
- update `repo_map.md` if structure changed

### Backend changes
- run targeted tests/checks for touched services/routes
- validate response shapes against `api_contracts.md`

### Mobile changes
- run TypeScript verification
- validate touched screens/flows only
- do not move backend logic into mobile

### QA / Maestro changes
- verify Android Maestro flows on emulator when possible
- document platform-specific blockers clearly
- do not claim iOS Maestro coverage until full Xcode/simctl is available

## 13. Maestro Status

Current expected QA reality:
- Android Maestro path is working
- Android smoke flow passes
- current launch path is:
  - Expo Go home
  - tap Beacon
  - dismiss Continue if shown
  - land on Beacon sign-in screen
- iOS Maestro remains blocked until full Xcode and `simctl` are installed

## 14. Remote Discord Operating Rule

When operating through the Discord bridge:
- prefer one consolidated response when possible
- keep messages copy/paste friendly
- allow remote operator commands for compact/reset/status flows
- do not rely on giant Discord threads as durable task memory

## 15. Stop Conditions

Stop and report a blocker when:
- a required spec is missing or contradictory
- a task would require inventing undocumented behavior
- a tool/runtime dependency is missing
- a change would violate `system_invariants.md`
- context degradation or cost pressure makes continued execution unreliable