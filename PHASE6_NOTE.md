# Phase 6 Note: Canonical Worker Contract and Audit Summary

## Canonical Worker Contract

- Worker input: `task_id` string specifying the work item
- Workers create a fresh `StateController` instance and reload state from disk to avoid stale data
- Worker reports success with `record_worker_done(worker_id)`
- Worker must NOT mutate task lifecycle directly (e.g. delivered, accepted states)
- Task lifecycle is owned by orchestrator and StateController

## Worker Module Audit

| Worker Module | Current Behavior | Matches Contract? | Required Changes |
|---------------|------------------|-------------------|------------------|
| forge.py      | Fresh state, calls record_worker_done, no direct task mutation | Yes | None needed |
| atlas.py      | Same as forge | Yes | None needed |
| aegis.py      | Same as forge | Yes | None needed |
| sentinel.py   | Same as forge | Yes | None needed |

## Recommended Implementation Order

1. Solidify and document canonical worker contract
2. Standardize worker modules fully to contract
3. Implement failure reporting enhancements if desired
4. Proceed with Phase 6 lifecycle expansions

---

This note accompanies the RUNTIME_CANONICAL_PATHS.md file specifying canonical runtime paths.

