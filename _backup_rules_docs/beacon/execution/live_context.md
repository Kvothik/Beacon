# Live Context

This is the minimal rehydration surface for Beacon autonomous execution.

Read this first after any compact, reset, or fresh session.
Do not reread large docs unless the current issue specifically requires them.

## Project

Beacon mobile parole packet builder

Repo path:
- `~/dev/Beacon`

## Current Agent Roles

- Sixx = cheap coordinator / queue controller / message router
- Forge = backend implementation
- Atlas = mobile implementation
- Sentinel = cheap watchdog / QA
- Shepherd = inactive / standby

## Model Policy

Target model usage:
- Sixx -> cheapest safe coordinator model
- Forge -> preferred coding model
- Atlas -> preferred coding model
- Sentinel -> cheapest safe watchdog / QA model

If preferred coding model is unavailable:
- use the cheapest working coding-capable fallback
- do not leave Sixx on an expensive coding model

## Core Execution Rules

- one implementation issue at a time
- if an edit fails, stop immediately
- issue stays open until repaired
- do not mark complete without verification
- do not move kanban to Done before acceptance when acceptance is required
- workers must report:
  - `DONE <task-id> success`
  - `BLOCKED <task-id> <reason>`

## Queue State

Source of truth:
- GitHub board
- queue files
- current issue metadata

Queue files:
- `queue/pending.json`
- `queue/active.json`
- `queue/done.json`
- `queue/blocked.json`
- `queue/handoffs/*.md`

## Current Project State

Core guided packet workflow exists.

Recently completed:
- #33 Maestro harness (Android passing; iOS blocked pending Xcode)
- #39 workflow event logging
- #41 attachment visibility
- #42 scan quality guidance
- #43 offender search filtering
- #44 offender selection clarity
- #45 packet builder progress indicators
- #46 improved error handling
- #48 packet readiness review

## Maestro Status

Android:
- working
- smoke flow passes

Launch path:
- Expo Go home
- tap Beacon
- dismiss Continue if shown
- Beacon sign-in screen

iOS:
- blocked until full Xcode and `simctl` exist

## Compaction Rule

After compaction or fresh session:
1. read this file
2. read queue files
3. read only the files needed for the current issue
4. do not reread full historical docs unless required

## When To Read More

Read additional docs only if needed:
- `docs/api_contracts.md` for endpoint/response work
- `docs/database_schema.md` for schema/migration work
- `docs/repo_map.md` if structure changed
- `docs/execution_router.md` for routing rules
- `docs/error_policy.md` for error behavior
- issue-specific source files for implementation

## Default Status Report

Return only:
- issue number
- files changed
- verification result
- final issue state
- next recommended issue or blocker