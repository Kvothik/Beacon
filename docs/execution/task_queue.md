# Task Queue

## Purpose

This document tracks the live BEACON execution queue supporting autonomous implementation.

It is deliberately minimal. Historical breakdowns live in GitHub issues.

## Queue Rules

- Single active implementation issue at a time unless human overrides.
- Prioritize highest-value unblocked backlog item.
- Do not start next issue if current is blocked, unverified, or awaiting acceptance.
- Blocked issues remain open until resolved.
- No inventing undocumented APIs, schemas, rules, or behaviors.
- Maintain alignment of GitHub issue, board, and repository states.

## Completion Protocol

Workers must structurally report completion via:
- `DONE <task-id> success`
- `BLOCKED <task-id> <reason>`

Every report must include:
- files changed
- verification command
- verification result
- final task status

## Current Board State

Backlog: derived from GitHub
In Progress: managed live
Done/Accepted: managed live

## Queue Progression

Sixx should auto-assign next valid task when:
- current task verified complete
- acceptance confirmed
- no blockers or holds

Queue progression halts on:
- blockers
- failed verification
- failed edits
- explicit human holds
- tooling/runtime issues

## Rehydration

As part of minimal rehydration surface, system recovers after reset or compaction from:
- board snapshot
- active task
- blocked task list
- recent completed tasks
- durable worker handoff
