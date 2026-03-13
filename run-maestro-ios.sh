#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="/opt/homebrew/opt/openjdk/bin:$HOME/.maestro/bin:$PATH"

if ! xcrun simctl list devices >/dev/null 2>&1; then
  echo "ERROR: iOS simulator tooling is unavailable (xcrun simctl not found or no Xcode runtime installed)." >&2
  exit 1
fi

booted_udid="$(xcrun simctl list devices available | awk -F '[()]' '/Booted/ && /iPhone/ {print $(NF-1); exit}')"
if [[ -z "$booted_udid" ]]; then
  target_name="$(xcrun simctl list devices available | sed -n 's/^[[:space:]]*\(iPhone[^()]\+\) (.*/\1/p' | head -n1)"
  if [[ -z "$target_name" ]]; then
    echo "ERROR: No available iPhone simulator runtime is installed." >&2
    exit 1
  fi
  xcrun simctl boot "$target_name" || true
fi

open -a Simulator >/dev/null 2>&1 || true
xcrun simctl bootstatus booted -b
cd "$ROOT_DIR"
maestro test mobile/.maestro
