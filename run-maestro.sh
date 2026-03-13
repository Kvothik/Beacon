#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if "$ROOT_DIR/run-maestro-ios.sh"; then
  exit 0
fi

if "$ROOT_DIR/run-maestro-android.sh"; then
  exit 0
fi

echo "ERROR: Could not start a local iOS simulator or Android emulator for Maestro." >&2
exit 1
