#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
STAMP="$(date +%Y-%m-%d_%H%M%S)"; DEST="backups/$STAMP"; mkdir -p "$DEST"
[ -f data/deadinternet.db ] && cp data/deadinternet.db "$DEST/"
tar -czf "$DEST/agent_workspace.tar.gz" agent_workspace 2>/dev/null || true
find backups -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' | sort -nr | awk 'NR>7{$1="";sub(/^ /,"");print}' | xargs -r rm -rf
echo "Backup criado em $DEST"
