# Beacon

Texas parole packet builder.

## Autonomous Development System

This repository uses the BEACON agent system for AI-assisted development coordination.

The orchestration model separates work into explicit roles:
- Sixx (orchestrator)
- Aegis (strategist / proposal engine)
- Forge (backend implementation)
- Atlas (frontend / mobile implementation)
- Sentinel (QA / verification)
- Pulse (runtime monitor)

The goal is to keep development deterministic, reduce hallucinated code, and ensure issues follow a verified lifecycle before closure.

Documentation is organized under:
- `docs/architecture/`
- `docs/rules/`
- `docs/execution/`

Primary references:
- `docs/architecture/agent_architecture.md`
- `docs/execution/agent_execution_rules.md`
- `docs/execution/agent_workflow.md`

---

## Maestro Mobile Test Harness

Baseline Maestro flows live in `mobile/.maestro/`.

Run locally with:

```bash
maestro test mobile/.maestro
```

See `mobile/.maestro/README.md` for prerequisites and flow notes.

## Maestro Mobile Test Harness

Baseline Maestro flows live in `mobile/.maestro/`.

Run locally with:

```bash
maestro test mobile/.maestro
```

See `mobile/.maestro/README.md` for prerequisites and flow notes.
