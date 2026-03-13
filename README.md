# Beacon

Texas parole packet builder.

## Autonomous Development System

This repository uses an Overseer agent system to coordinate AI-assisted development.

The orchestration model separates work into explicit roles:
- Overseer Agent
- Planner Agent
- Builder Agent
- Verifier Agent
- Documentation Agent (optional)

The goal is to keep development deterministic, reduce hallucinated code, and ensure that issues are executed sequentially with verification before closure.

Primary references:
- `docs/agent_architecture.md`
- `docs/agent_execution_rules.md`
- `docs/agent_workflow.md`

## Maestro Mobile Test Harness

Baseline Maestro flows live in `mobile/.maestro/`.

Run locally with:

```bash
maestro test mobile/.maestro
```

See `mobile/.maestro/README.md` for prerequisites and flow notes.
