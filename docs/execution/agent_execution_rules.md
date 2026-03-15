# Agent Execution Rules

These rules govern autonomous execution in the Beacon repository.

## 1. Primary Execution Model

- Sixx is the execution gateway, coordinator, and message router.
- Forge implements backend tasks.
- Atlas implements mobile tasks.
- Sentinel performs lightweight QA/watchdog/review tasks and stall detection.
- Only one implementation issue may be actively executed at a time unless a human explicitly authorizes parallel work.

## 2. Sequential Issue Execution

Issues must be executed sequentially.

The active executor must not skip ahead unless:
- a human explicitly reprioritizes, or
- a blocker is documented and surfaced.

If the current issue is blocked, it remains open until the blocker is resolved or the human explicitly changes priority.

## 3. Automatic Queue Continuation

When an issue is complete and verified, Sixx should automatically assign the next valid queued issue unless:
- the issue requires explicit human approval,
- the issue is blocked,
- or a stop rule has been triggered.

Workers must report completion in a structured form:
- `DONE <task-id> success`
- `BLOCKED <task-id> <reason>`

Sixx must use these structured outcomes to update queue state and determine the next action.

## 4. Ambiguity Stop Rule

If a domain ambiguity occurs, the agent must stop and surface the ambiguity.

The agent must not invent undocumented:
- domain behavior
- schema
- routing logic
- packet rules
- PDF behavior
- parole board mapping logic

## 5. TEMP_RULE Exception

A `TEMP_RULE` may be implemented only if:
- it is clearly labeled in code as temporary
- it is documented in repository docs
- a follow-up GitHub issue is created for the real logic

A `TEMP_RULE` is a development placeholder only, not a final business rule.

## 6. Scope Restriction Rule

Implementation must stay inside:
- the current issue scope
- documented repository contracts
- the assigned ownership boundary
- the current execution plan

Agents may not widen scope without explicit approval.

## 7. Ownership Boundaries

- Sixx owns orchestration, docs, issue coordination, review flow, queue flow, and message routing.
- Forge owns backend and dataset implementation.
- Atlas owns mobile implementation.
- Sentinel owns QA/watchdog/review behavior only unless explicitly approved otherwise.

No implementation agent may edit outside its ownership area unless Sixx explicitly authorizes it.

## 8. Execution Guard

If any edit operation reports `Edit failed`:
- the current issue remains OPEN
- the failing file must be re-opened
- the intended change must be applied manually
- the file must be re-verified
- verification must be rerun before the issue may be considered complete

An issue with an unresolved edit failure must never be reported as complete.

## 9. Execution Halt Rule

If an edit fails:
- stop execution immediately
- do not continue implementation
- do not start another issue
- resume only after repair is complete and verification passes

## 10. Verification Rule

No issue is complete until verification has run and confirmed that:
- implementation matches issue scope
- targeted validation passed
- relevant tests/typechecks passed
- data/schema/migration behavior is valid when applicable
- documentation is updated when behavior, structure, or operating rules changed

Every completion report must include:
- files changed
- verification command run
- verification result
- final issue status

If verification is missing, the issue cannot be marked complete.

## 11. Acceptance and Kanban Rule

Implementation completion does not automatically mean accepted.

Before moving a kanban card to Done/Accepted:
- the implementation must be verified
- acceptance must be confirmed
- issue metadata must be updated
- completion comment must be present
- required labels must be present

Do not move the card to Done before acceptance is confirmed.

## 12. GitHub Closeout Rule

Before the next issue begins, the active executor must ensure the current issue has the required closeout state:
- summary comment added or updated
- verification recorded
- correct status label applied
- board state synchronized when accepted

Commit/push behavior should remain consistent with the current repo workflow, but no issue may be reported as fully complete if the repository and issue state are out of sync.

## 13. Context Preservation Rule

Important operational state must not live only in chat history.

Queue state, handoff state, and recovery state must be written to repository-backed or workspace-backed files so sessions can be compacted or reset safely.

## 14. Compaction and Rehydration Rule

To control token usage and prevent context bloat:
- agents should prefer targeted reads over broad repo scans
- important state must be written to queue/handoff files
- active sessions should compact after several completed tasks or when context becomes noisy
- fresh sessions may be started when needed, then rehydrated from queue/handoff files

## 15. Stop Conditions

Stop and report a blocker when:
- a required spec is missing or contradictory
- a task would require inventing an API, schema, packet rule, or PDF behavior
- a required runtime/tooling dependency is unavailable
- the current task exceeds configured time/token limits without stable progress
- a change would violate `system_invariants.md`

## 16. Default Status Reporting

Default status reports should be minimal and include only:
- issue number
- files changed
- verification result
- final issue state
- next recommended issue or blocker