#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
[ -x .venv/bin/pytest ] || { echo "Execute ./scripts/install.sh primeiro."; exit 1; }
exec .venv/bin/pytest -q
