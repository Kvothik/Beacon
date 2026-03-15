# Runtime State Model

This document defines the authoritative runtime state controller for the BEACON system.

## Canonical State Files

- `runtime/state/tasks.json`: Tracks all active, pending, blocked, and done tasks with linked worker IDs.
- `runtime/state/workers.json`: Tracks all active workers with linked task IDs and lifecycle status.
- `runtime/state/events.ndjson`: Stream of lifecycle events in NDJSON format capturing worker and task lifecycle.
- `runtime/state/pulse.json`: Health status of the Pulse runtime monitor.

## State Invariants

- Every active task must map to exactly one active worker.
- Every active worker must map to exactly one active task.
- No task may complete without the following lifecycle events recorded: `DONE`, Sentinel verification, `worker_terminated`, and `queue_cleanup`.
- No worker may disappear from the state unless finally classified (e.g., done, blocked, or terminated).

## State Transitions

### Task Lifecycle
- proposed → backlog → active → delivered → accepted / blocked

### Worker Lifecycle
- spawned → linked → executing → verifying → terminated / timeout / failure

## Validation Rules

A state controller enforces these to prevent illegal transitions:

- Tasks cannot skip states or transition backward (e.g., backlog → accepted or active → accepted are invalid).
- Workers cannot abruptly jump to terminal states without going through intermediate execution phases.
- All transitions require corresponding lifecycle events to be logged.

## Illegal Transitions

Examples of illegal transitions:

- backlog → accepted
- active → accepted
- spawned → executing (without linked)
- verifying → active

## Canonical Lifecycle Authority

This state transition matrix is the single source of truth for task and worker lifecycle management within BEACON.
It ensures deterministic and valid state changes monitored and enforced by the runtime state controller.

---

(This section supplements the earlier runtime state model definitions.)
