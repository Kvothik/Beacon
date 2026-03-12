AI Engineering Rules
Audited build documentation for the Texas Parole Packet Builder
1. Purpose
These rules exist to keep the build modular, prevent hallucinations, and reduce token usage during autonomous development runs.
2. Architectural Rules
Follow northstar.md as the product and architecture source of truth.
Follow api_contracts.md for all endpoint names, request shapes, and response shapes.
Follow database_schema.md for all persistent models.
Follow pdf_spec.md for final packet ordering and formatting behavior.
Follow scanner_implementation.md for scanner technology choices.
Follow system_invariants.md as non-negotiable behavior.
3. Change Management Rules
Only work on one task at a time.
Only read files required for the current task.
Only modify files required for the current task.
Do not rewrite a working module unless the current task requires a bug fix or explicit refactor.
Do not rename endpoints, table names, or packet sections without updating the supporting docs first.
4. Output Rules
Return concise implementation output.
Prefer code diffs or file-level updates over broad narrative explanations.
Update repo_map.md whenever file structure changes.
Add or update tests for backend business logic when practical within the task.
5. Anti-Hallucination Rules
Never invent a public TDCJ JSON API.
Never invent a new packet section not listed in northstar.md.
Never invent new database tables outside database_schema.md without documenting them first.
Never change the generated PDF order outside pdf_spec.md.
Never bypass error_policy.md for API error format.
6. Token Efficiency Rules
Use docs as stable context and avoid loading unrelated source files.
Summarize logs instead of replaying long outputs into prompts.
Stop after configured task, token, or blocker limits.