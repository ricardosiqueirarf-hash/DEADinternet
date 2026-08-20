#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
[ -x .venv/bin/uvicorn ] || { echo "Execute ./scripts/install.sh primeiro."; exit 1; }
set -a; [ -f .env ] && source .env; set +a
HOST="${DEADINTERNET_HOST:-127.0.0.1}"
PORT="${DEADINTERNET_PORT:-4750}"
if command -v ss >/dev/null && ss -ltn "sport = :$PORT" | grep -q LISTEN; then echo "A porta $PORT já está em uso."; exit 1; fi
exec .venv/bin/uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
