#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
command -v python3 >/dev/null || { echo "Erro: python3 não encontrado."; exit 1; }
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -e '.[dev]'
mkdir -p data backups agent_workspace/outbox agent_workspace/inbox
[ -f .env ] || cp .env.example .env
.venv/bin/python -c 'from app.database import init_db; init_db(); print("Banco inicializado.")'
echo "Instalação concluída. Execute: ./scripts/run.sh"
