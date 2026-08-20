from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from uuid import uuid4

from app.config import settings


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip()).strip("-").lower()
    return cleaned[:50] or "reference"


def create_agent_task(reference: dict, task_type: str = "analyze_reference") -> dict:
    settings.agent_outbox.mkdir(parents=True, exist_ok=True)
    task_id = f"di-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}"
    filename = f"{task_id}_{_slug(reference.get('title') or str(reference.get('id')))}.md"
    path = settings.agent_outbox / filename
    payload = {
        "task_id": task_id,
        "task_type": task_type,
        "reference_id": reference.get("id"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input": reference,
        "expected_output": {
            "theme": "string",
            "hook_analysis": "string",
            "format_analysis": "string",
            "audience": "string",
            "original_content_angles": ["string"],
            "monetization_options": ["string"],
            "recommended_score_adjustments": {"hook_strength": "0-10", "recreation_ease": "0-10", "monetization_potential": "0-10"},
            "risks": ["string"]
        }
    }
    markdown = f"""# DEADinternet Agent Task\n\n```json\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```\n\n## Instruções\n\n- Analise padrões, sem copiar o conteúdo original.\n- Proponha conteúdo transformativo e original.\n- Não publique, baixe mídia, envie mensagens ou execute transações.\n- Salve o resultado em `agent_workspace/inbox/{task_id}.json`.\n- Preserve `task_id` e `reference_id`.\n"""
    path.write_text(markdown, encoding="utf-8")
    return {"task_id": task_id, "path": str(path), "status": "queued_for_supercodex"}
