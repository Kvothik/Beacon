# Task Queue

## Purpose

This document tracks the live Beacon execution queue for autonomous work.

It is intentionally short.
Detailed historical task breakdown should live in GitHub issues, not in this file.

## Queue Rules

- Only one implementation issue may be active at a time.
- Work the highest valid backlog item unless a human reprioritizes.
- Do not start the next issue if the current issue is blocked, unverified, or awaiting required acceptance.
- Blocked issues remain open.
- Do not invent undocumented endpoints, schema, packet sections, or PDF behavior.
- Keep GitHub issue state, board state, and repo state aligned.

## Completion Protocol

Workers must report:
- `DONE <task-id> success`
- `BLOCKED <task-id> <reason>`

Every completion report must include:
- files changed
- verification command run
- verification result
- final issue status

## Current State

Board snapshot:
- Backlog: 7
- In Progress: 0
- Done/Accepted: 13

Recently completed:
- #33 Maestro harness (Android passing, iOS blocked pending Xcode)
- #39 workflow event logging
- #41 attachment visibility
- #42 scan quality / rescan guidance
- #43 offender search filtering
- #44 offender selection clarity
- #45 packet builder progress indicators
- #46 improved error handling
- #48 packet readiness review

Current active issue:
- none

Next issue:
- derive from current GitHub backlog analysis

## Queue Progression Rule

Sixx should automatically start the next valid issue when:
- the current issue is complete
- verification passed
- required acceptance is confirmed
- no blocker or human hold exists

Queue progression stops on:
- blocker
- verification failure
- edit failure
- explicit human hold
- missing runtime/tooling dependency

## Rehydration Rule

This file is part of the minimal rehydration surface.

After compaction or reset, the system should recover from:
- current board snapshot
- active issue
- blocked issue list
- recent completed issues
- durable worker handoff notes