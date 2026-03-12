# Task Queue
Audited build documentation for the Texas Parole Packet Builder

## 1. Purpose

This document defines the implementation queue for autonomous work. It is ordered to preserve P0 delivery and prevent low-value work from starting too early.

## 2. Queue Rules

- Work from top to bottom unless a human explicitly reprioritizes.
- Only one active implementation task should be in progress at a time.
- Documentation blockers should be cleared before code that depends on them.
- P1 and P2 work stays blocked until P0 is substantially complete.

## 3. Current Queue

### Ready Now
1. Finalize and cross-check documentation set
2. Scaffold backend FastAPI application structure
3. Scaffold mobile Expo application structure
4. Define parole board office seed dataset format

### Next After Scaffolding
5. Implement authentication backend endpoints
6. Implement mobile login and registration flow
7. Implement TDCJ offender search endpoint
8. Implement mobile offender search and result selection flow
9. Implement parole board office lookup endpoint
10. Implement packet creation endpoint and packet section initialization
11. Implement packet detail and section update endpoints
12. Implement mobile packet builder and section detail screens

### After Core Packet Flow
13. Implement upload initiation and completion flow
14. Implement mobile document upload UI
15. Implement scanner v1 capture and retry flow
16. Implement cover letter generation endpoint
17. Implement final PDF generation endpoint
18. Implement mobile review and export flow

### Hardening
19. Add focused backend tests for auth
20. Add focused backend tests for offender lookup normalization
21. Add focused backend tests for packet and PDF flows
22. Improve loading, retry, and error states in mobile

## 4. Deferred Queue

Do not start until explicitly reprioritized:
- push notification delivery flow
- PDF preview enhancements
- AI-assisted drafting
- packet quality scoring
- analytics/admin features
- collaboration/shared editing

## 5. Blocker Rule

If a queue item depends on undocumented behavior, pause that item and update the relevant documentation first.
