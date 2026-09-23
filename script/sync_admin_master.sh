#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_DIR="$ROOT_DIR/external/comoros-admin-master"

mkdir -p "$ROOT_DIR/external"

if [ -d "$TARGET_DIR/.git" ]; then
  echo "Updating admin master dependency..."
  git -C "$TARGET_DIR" pull --ff-only
else
  echo "Cloning admin master dependency..."
  git clone https://github.com/hhousni/comoros-admin-master.git "$TARGET_DIR"
fi

echo "Admin master available at $TARGET_DIR"
