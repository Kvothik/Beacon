# Execution Router

## Issue Routing

Use this as the primary next-step routing source for the active P0 sequence.

- `#16` -> Atlas
- `#17` -> Forge
- `#18` -> Atlas
- `#19` -> Forge
- `#20` -> Atlas
- `#21` -> Forge
- `#22` -> Forge
- `#23` -> Forge

## Sentinel Review Policy

Sentinel review is REQUIRED for:
- backend API endpoint changes
- database schema changes
- TDCJ parser changes
- upload/storage system changes
- scanner implementation
- PDF generation

Sentinel review is OPTIONAL for:
- mobile UI-only issues
- layout changes
- screen-level refactors

## ACCEPT FLOW

When Sentinel returns ACCEPT:
1. Sixx moves the issue card to `ACCEPTED`
2. Sixx determines the next issue using `docs/execution_router.md`
3. Sixx sends a concise summary message
4. Sixx sends the approval command message
5. No work begins until user approval

## REJECT FLOW

When Sentinel returns REJECT:
1. Sixx moves the issue card back to `IN PROGRESS`
2. Sixx applies label: `rejected`
3. Sixx posts Sentinel rejection reason as a GitHub comment
4. Sixx sends rejection summary via Discord
5. Sixx sends the fix command message

## DISCORD MESSAGE TEMPLATE

Message 1 — Summary

STATE
- issue reviewed: `#<number>`
- review result: `ACCEPT` or `REJECT`
- concise change summary

WAITING
- execution will not begin until approval

Message 2 — Command

`Approve issue #<number>. Owner: <Forge or Atlas>.`
