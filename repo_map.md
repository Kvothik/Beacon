# repo_map.md

Complete repository tree (excluding `.git/`):

```text
.
├── .gitignore
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── db.py
│   │   │   └── security.py
│   │   ├── main.py
│   │   ├── models/
│   │   │   ├── document.py
│   │   │   ├── notification_subscription.py
│   │   │   ├── offender.py
│   │   │   ├── packet.py
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
│   │       └── test_packet.py
│   └── tools/
│       └── discord_bridge.py
├── datasets/
├── docs/
│   ├── agent_workflow.md
│   ├── ai_engineering_rules.md
│   ├── api_contracts.md
│   ├── database_schema.md
│   ├── error_policy.md
│   ├── feature_priority.md
│   ├── northstar.md
│   ├── pdf_spec.md
│   ├── repo_map.md
│   ├── scanner_implementation.md
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
│   ├── app.json
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
│   │       ├── offender.ts
│   │       └── packet.ts
│   └── tsconfig.json
└── repo_map.md
```
