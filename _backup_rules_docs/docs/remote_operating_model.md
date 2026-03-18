# Beacon Remote Operating Model

## Purpose

This document defines the stable remote development model for Beacon.

Goals:
- reduce token usage
- keep development moving when workers fail
- avoid orchestration dead ends
- preserve clear ownership and predictable execution

## Core Model

### Sixx is the control plane

Sixx always owns:
- issue routing
- execution decisions
- repo and project tracking
- verification
- user-facing updates
- fallback implementation when workers are unavailable

Sixx must not block development waiting on perfect worker recovery.

### Workers are disposable implementation lanes

Forge, Atlas, and any Codex/App implementation sessions are helpers, not continuity anchors.

Rules:
- one implementation lane per issue
- workers may be replaced without blocking progress
- workers do not directly own the overall workflow
- if a worker stalls, Sixx either restores it from a valid surface or takes over directly

## Valid vs Invalid Worker Surfaces

### Valid surface for persistent worker sessions

Persistent worker sessions are allowed only from a real Discord thread-bound orchestration session.

Use this surface for:
- `thread=true`
- `mode="session"`
- persistent Forge/Atlas restoration
- focused thread-bound follow-up work
- Discord thread session controls such as `/agents`, `/focus`, `/unfocus`, `/session idle`, and `/session max-age`

### Invalid surface for persistent worker restoration

Do not attempt persistent worker restoration from:
- webchat fallback sessions
- non-thread-bound remote sessions
- any surface where thread binding is unavailable

If the active surface is invalid, Sixx must not keep retrying worker restore.

## Fallback Mode

If a worker fails, stalls, or cannot be restored:

1. inspect once
2. retry once only if the active surface is valid for persistent workers
3. if still blocked, enter single-agent fallback mode immediately
4. continue the issue directly as Sixx
5. do not attempt further worker restoration from the invalid surface

Single-agent fallback mode means:
- Sixx is the active implementer
- Sixx is the orchestrator
- Sixx is the message gateway
- Forge and Atlas remain inactive until restoration is possible from a valid Discord thread-bound session

## Implementation Session Policy

For implementation work, prefer issue-scoped isolated sessions.

Recommended order:
1. Sixx routes the issue
2. one isolated implementation lane performs the work
3. Sixx verifies the change
4. Sixx updates issue/project tracking
5. Sixx reports completion
6. Sixx compacts or resets context before the next issue

Use Codex/App or valid worker sessions for longer implementation tasks when available.

## Visible Work State

When Sixx receives work, Sixx must make state obvious in chat.

Required pattern:
- `Seen. Starting now.` when work begins
- `Status: in progress` while actively working
- `Last thing done: ...` with one short concrete action
- `Status: blocked` when blocked
- `Status: complete` when finished
- `Status: paused` when not actively continuing

Do not leave the human guessing whether work is active or idle.

## Token Reduction Rules

### Keep sessions short-lived

- prefer one issue per session or thread when practical
- compact after delivery
- compact before switching topics
- avoid giant long-lived sessions carrying unrelated issues

### Read only what is needed

- read only the docs required for the current issue
- avoid broad repo rehydration unless context is actually lost
- avoid repeatedly re-reading the same docs in the same issue
- use targeted file reads instead of repo-wide scans

### Keep messages compact

Default status updates should include only:
- issue number
- files changed
- verification result
- next recommended issue

Use one single consolidated reply whenever reasonably possible.

### Separate model roles

Use a cheaper/default orchestration model for:
- planning
- routing
- issue tracking
- status updates

Use stronger models only for:
- implementation turns that need them
- difficult debugging
- high-complexity code changes

### Minimize prompt overhead

- keep bundled skills trimmed to what is actually used
- avoid verbose mode unless debugging
- avoid unnecessary repeated system/context expansion
- compact between issues to prevent runaway context growth

## Ownership Rules

Backend/mobile ownership remains logically separated:
- backend issues map to backend implementation lanes
- mobile issues map to mobile implementation lanes
- Sixx preserves the ownership boundary in planning and reporting even in fallback mode

One issue at a time.

## Recovery Rules

### Worker recovery

If remote and a worker is unavailable:
- do not loop on restoration attempts
- switch to fallback mode if the surface is invalid
- resume worker orchestration only after returning to a valid Discord thread-bound session

### Host/runtime repair

Do not rely on broad remote admin.

Preferred model:
- narrow repair capability only
- enough to inspect and recover gateway/runtime health
- no blanket privileged shell for normal remote development

## Review Policy

Sentinel review is only required when the routing or execution policy says it is required.

Do not block normal issue progress on Sentinel when the issue does not require Sentinel review.

## Beacon Remote Workflow

For each issue:

1. identify the current issue from routing docs
2. choose the correct execution lane
3. confirm whether the current surface is valid for workers
4. implement in one lane only
5. run targeted verification
6. update issue/project tracking
7. send one concise completion update
8. compact or reset context before the next issue

## Quick Operating Checklist

For each remote Beacon issue:

1. announce `Seen. Starting now.`
2. confirm the active issue
3. decide whether the current surface is valid for workers
4. if invalid, use single-agent fallback immediately
5. read only the docs/files required for that issue
6. implement in one lane only
7. run targeted verification only
8. update issue/project tracking when complete
9. send one concise completion message
10. compact before the next issue

## Success Criteria

This model is working when:
- worker failures do not stop issue progress
- remote sessions stop wasting time on invalid worker restoration
- token usage per issue drops materially
- issue updates are short and consistent
- context size stays bounded
- Sixx remains predictable and stable across remote work
