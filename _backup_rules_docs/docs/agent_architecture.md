# Agent Architecture

Autonomous development in this repository is coordinated through a role-based agent system designed to keep implementation deterministic, auditable, and aligned with documented product constraints.

## 1. Purpose

This architecture separates planning, implementation, verification, and workflow control so no single agent silently invents product behavior, schema, or architecture.

## 2. Agent Roles

### Overseer Agent

Responsibilities:
- read GitHub issues
- maintain the execution queue
- assign work to other agents
- stop execution if ambiguity or rule violations occur
- enforce sequential issue execution
- ensure completed work is committed, pushed, and reflected in GitHub + repo docs

### Planner Agent

Responsibilities:
- read issue requirements
- break work into implementation steps
- identify schema, dependency, or documentation changes
- produce an execution plan before implementation starts

### Builder Agent

Responsibilities:
- write code
- update schema
- implement APIs and services
- create migrations
- follow planner instructions only

Constraints:
- cannot invent schema or business logic
- cannot skip verification
- cannot redefine issue scope without escalation

### Verifier Agent

Responsibilities:
- run tests
- check for lint or static analysis issues when configured
- validate migrations
- confirm issue requirements were satisfied
- reject incomplete implementations

### Documentation Agent (optional)

Responsibilities:
- update docs
- maintain architecture and schema references
- keep repo maps and workflow docs in sync with implementation changes

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
