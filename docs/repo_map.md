# Repository Map
Audited build documentation for the Texas Parole Packet Builder

---

# 1. Purpose

This file defines the **target repository structure** for implementation.

It is a planning and architecture map, not a literal snapshot of the current filesystem at every moment.

AI agents must use it to avoid hallucinating file and folder names while building toward the documented structure.

If new files are created, renamed, or removed as part of implementation, this map **must be updated in the same task**.

---

# 2. Repo Layout

```
.gitignore
README.md
repo_map.md

agents/
  overseer_agent.md
  planner_agent.md
  builder_agent.md
  verifier_agent.md

docs/
  northstar.md
  repo_map.md
  ai_engineering_rules.md
  agent_architecture.md
  agent_execution_rules.md
  agent_workflow.md
  feature_priority.md
  api_contracts.md
  database_schema.md
  pdf_spec.md
  scanner_implementation.md
  error_policy.md
  system_invariants.md
  task_queue.md
  github_issue_board_plan.md
  tdcj_lookup_adapter.md
  tdcj_html_parser_spec.md

mobile/
  App.tsx
  app.json
  package.json
  package-lock.json
  tsconfig.json
  src/
    navigation/
      AppNavigator.tsx

    screens/
      LoginScreen.tsx
      RegisterScreen.tsx
      HomeScreen.tsx
      PacketBuilderScreen.tsx
      SectionDetailScreen.tsx
      ScannerScreen.tsx
      ReviewScreen.tsx
      PdfPreviewScreen.tsx

    components/
      SectionCard.tsx
      ProgressBanner.tsx
      DocumentUploader.tsx
      LoadingState.tsx
      ErrorState.tsx

    services/
      apiClient.ts
      authService.ts
      offenderService.ts
      packetService.ts
      uploadService.ts
      notificationService.ts

    store/
      authStore.ts
      packetStore.ts
      offenderStore.ts

    types/
      api.ts
      auth.ts
      packet.ts
      offender.ts

backend/
  alembic.ini
  requirements.txt
  alembic/
    env.py
    script.py.mako
    versions/
      20260311_0001_mvp_schema.py
  tools/
    build_parole_board_datasets.py
    discord_bridge.py
    seed_parole_board_data.py
  app/
    main.py

    core/
      config.py
      security.py
      db.py

    routers/
      auth_router.py
      offender_router.py
      parole_board_router.py
      packet_router.py
      upload_router.py
      pdf_router.py

    services/
      tdcj_lookup_service.py
      parole_board_service.py
      packet_service.py
      upload_service.py
      pdf_service.py

    models/
      __init__.py
      base.py
      user.py
      offender.py
      parole_board.py
      packet.py
      document.py
      notification_subscription.py

    schemas/
      auth.py
      offender.py
      packet.py
      pdf.py

    tests/
      test_auth.py
      test_offender.py
      test_packet.py

infra/
  docker/
    Dockerfile.backend

  deployment/
    README.md

datasets/
  parole_board_offices.json
  parole_board_unit_mappings.json
```

---

# 3. File Ownership Guidance

**Mobile**

Mobile screens own **presentation and user interaction only**.

Mobile services wrap **API calls** and do not contain backend business rules.

**Backend**

Backend routers define **endpoints** and delegate logic to services.

Backend services contain **integration and business logic**.

Models and schemas must follow:

- `database_schema.md`
- `api_contracts.md`

---

# 4. Update Rule

Whenever a task **creates, renames, or removes a file**, `repo_map.md` must be updated in the **same change set**.

The map should remain **concrete** and not drift into abstract folder-only descriptions.
