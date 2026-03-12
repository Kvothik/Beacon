# repo_map.md

Complete repository tree (excluding `.git/`):

```text
.
├── .gitignore
├── README.md
├── agents/
│   ├── builder_agent.md
│   ├── overseer_agent.md
│   ├── planner_agent.md
│   └── verifier_agent.md
├── backend/
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── 20260311_0001_mvp_schema.py
│   ├── alembic.ini
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── db.py
│   │   │   └── security.py
│   │   ├── main.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── document.py
│   │   │   ├── notification_subscription.py
│   │   │   ├── offender.py
│   │   │   ├── packet.py
│   │   │   ├── parole_board.py
│   │   │   └── user.py
│   │   ├── routers/
│   │   │   ├── auth_router.py
│   │   │   ├── offender_router.py
│   │   │   ├── packet_router.py
│   │   │   ├── parole_board_router.py
│   │   │   ├── pdf_router.py
│   │   │   └── upload_router.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── offender.py
│   │   │   ├── packet.py
│   │   │   └── pdf.py
│   │   ├── services/
│   │   │   ├── packet_service.py
│   │   │   ├── parole_board_service.py
│   │   │   ├── pdf_service.py
│   │   │   ├── tdcj_lookup_service.py
│   │   │   └── upload_service.py
│   │   └── tests/
│   │       ├── test_auth.py
│   │       ├── test_offender.py
│   │       ├── test_packet.py
│   │       └── test_parole_board.py
│   ├── requirements.txt
│   └── tools/
│       ├── build_parole_board_datasets.py
│       ├── discord_bridge.py
│       └── seed_parole_board_data.py
├── datasets/
│   ├── parole_board_offices.json
│   └── parole_board_unit_mappings.json
├── docs/
│   ├── agent_architecture.md
│   ├── agent_execution_rules.md
│   ├── agent_workflow.md
│   ├── ai_engineering_rules.md
│   ├── api_contracts.md
│   ├── approval_gated_supervisor.md
│   ├── database_schema.md
│   ├── error_policy.md
│   ├── feature_priority.md
│   ├── github_issue_board_plan.md
│   ├── northstar.md
│   ├── orchestrator_context.md
│   ├── pdf_spec.md
│   ├── qa_review_model.md
│   ├── execution_router.md
│   ├── repo_map.md
│   ├── scanner_implementation.md
│   ├── sentinel_context.md
│   ├── system_invariants.md
│   ├── task_queue.md
│   ├── tdcj_html_parser_spec.md
│   └── tdcj_lookup_adapter.md
├── infra/
│   ├── deployment/
│   │   └── README.md
│   └── docker/
│       └── Dockerfile.backend
├── mobile/
│   ├── App.tsx
│   ├── app.json
│   ├── package-lock.json
│   ├── package.json
│   ├── src/
│   │   ├── components/
│   │   │   ├── DocumentUploader.tsx
│   │   │   ├── ErrorState.tsx
│   │   │   ├── LoadingState.tsx
│   │   │   ├── ProgressBanner.tsx
│   │   │   └── SectionCard.tsx
│   │   ├── navigation/
│   │   │   └── AppNavigator.tsx
│   │   ├── screens/
│   │   │   ├── HomeScreen.tsx
│   │   │   ├── LoginScreen.tsx
│   │   │   ├── PacketBuilderScreen.tsx
│   │   │   ├── PdfPreviewScreen.tsx
│   │   │   ├── RegisterScreen.tsx
│   │   │   ├── ReviewScreen.tsx
│   │   │   ├── ScannerScreen.tsx
│   │   │   └── SectionDetailScreen.tsx
│   │   ├── services/
│   │   │   ├── apiClient.ts
│   │   │   ├── authService.ts
│   │   │   ├── notificationService.ts
│   │   │   ├── offenderService.ts
│   │   │   ├── packetService.ts
│   │   │   └── uploadService.ts
│   │   ├── store/
│   │   │   ├── authStore.ts
│   │   │   ├── offenderStore.ts
│   │   │   └── packetStore.ts
│   │   └── types/
│   │       ├── api.ts
│   │       ├── auth.ts
│   │       ├── offender.ts
│   │       └── packet.ts
│   └── tsconfig.json
└── repo_map.md
```
