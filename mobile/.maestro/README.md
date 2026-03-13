# Maestro Test Harness

Baseline mobile UI test flows for Beacon live in this directory.

## Prerequisites

- Maestro CLI installed and on `PATH`
- Expo app running on a simulator or device
- App already authenticated for the baseline smoke flow
- Backend/API reachable from the running mobile preview

## Run the baseline flow

```bash
maestro test mobile/.maestro
```

The baseline flow covers:
- search offender by SID
- select offender
- create packet
- open packet builder
- open review screen

## Notes

- The baseline smoke flow assumes a stable offender SID and an already-authenticated app session.
- Login automation is tracked separately in issue #34.
