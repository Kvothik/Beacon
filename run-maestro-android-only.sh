#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export JAVA_HOME=/opt/homebrew/opt/openjdk
export ANDROID_SDK_ROOT=/opt/homebrew/share/android-commandlinetools
export ANDROID_HOME=$ANDROID_SDK_ROOT
export PATH="$JAVA_HOME/bin:$ANDROID_SDK_ROOT/emulator:$ANDROID_SDK_ROOT/platform-tools:$HOME/.maestro/bin:/opt/homebrew/bin:$PATH"

if ! command -v adb >/dev/null 2>&1 || ! command -v emulator >/dev/null 2>&1 || ! command -v avdmanager >/dev/null 2>&1; then
  echo "ERROR: Android tooling is incomplete. Expected adb, emulator, and avdmanager on PATH." >&2
  exit 1
fi

avd_name="$(emulator -list-avds | head -n1)"
if [[ -z "$avd_name" ]]; then
  echo "ERROR: No Android AVD exists. Create one before running Maestro on Android." >&2
  exit 1
fi

if ! adb devices | grep -q '^emulator-'; then
  nohup emulator -avd "$avd_name" >/tmp/beacon-maestro-android.log 2>&1 &
fi

adb wait-for-device >/dev/null 2>&1
cd "$ROOT_DIR"
maestro test mobile/.maestro
