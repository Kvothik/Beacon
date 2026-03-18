# Agent Execution Rules

These rules govern autonomous agent execution in the beacon repository.

## 1. Sequential Issue Execution

Issues must be executed sequentially.

The active executor must not skip ahead unless a human explicitly reprioritizes or a blocker is documented and surfaced.

## 2. Maximum Issues Per Run

Maximum of 3 issues may be completed in a single run unless a human explicitly overrides that limit.

## 3. Ambiguity Stop Rule

If a domain ambiguity occurs, the agent must stop and surface the ambiguity.

The agent must not invent undocumented domain behavior, schema, or routing rules on its own.

## 4. TEMP_RULE Exception

A `TEMP_RULE` may be implemented only if:
- it is clearly labeled in code as temporary
- it is documented in repository docs
- a follow-up GitHub issue is created for the real logic

A `TEMP_RULE` is a development placeholder only, not a final business rule.

## 5. Builder Restrictions

Builder agents cannot invent schema or domain logic.

Builder work must stay inside:
- the current issue scope
- the planner output
- the documented repository contracts

## 6. Verification Requirement

No issue is complete until verification has run and confirmed:
- implementation matches issue scope
- tests or targeted validation passed
- migrations or data changes behave as expected
- documentation is updated when file structure or rules changed

## 7. Completion Requirement

Before moving to the next issue, the active executor must:
- commit changes
- push changes
- comment on the GitHub issue with summary and verification
- apply the correct status label
- close the issue if complete


## 8. Next Task Recommendation Rule

After completing any task, the system must:
1. Read the canonical task queue:
   - `pentarch-runtime/planner/planner_tasks.json`
2. Identify the next task in sequence or priority
3. Recommend that next task explicitly in the report
4. If no next task exists, report that the queue is empty

## 9. Runtime Reporting Behavior

After every task execution, the system output must include:
- `current_task_completed`
- `next_recommended_task_from_queue`
- `github_issue_updated_yes_or_no`


## 10. Repository Boundaries

- Beacon is the only product repository
- pentarch-runtime contains runtime, orchestrator only
- NEVER write product code outside Beacon

