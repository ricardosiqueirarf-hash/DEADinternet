from __future__ import annotations

import sqlite3
from contextlib import asynccontextmanager
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, HttpUrl

from app.agent_bridge import create_agent_task
from app.config import ROOT_DIR, settings
from app.database import db_session, init_db
from app.scoring import calculate_score

Platform = Literal["instagram", "tiktok", "youtube", "other"]
Status = Literal["captured", "enriched", "scored", "selected", "discarded"]


class ReferenceInput(BaseModel):
    platform: Platform
    url: HttpUrl
    creator_name: str = ""
    title: str = ""
    caption: str = ""
    views: int = Field(default=0, ge=0)
    likes: int = Field(default=0, ge=0)
    comments: int = Field(default=0, ge=0)
    topic: str = ""
    hook: str = ""
    format_type: str = ""
    monetization_path: str = ""
    source_notes: str = ""
    status: Status = "captured"
    hook_strength: float = Field(default=0, ge=0, le=10)
    recreation_ease: float = Field(default=0, ge=0, le=10)
    monetization_potential: float = Field(default=0, ge=0, le=10)


class ReferencePatch(BaseModel):
    platform: Platform | None = None
    url: HttpUrl | None = None
    creator_name: str | None = None
    title: str | None = None
    caption: str | None = None
    views: int | None = Field(default=None, ge=0)
    likes: int | None = Field(default=None, ge=0)
    comments: int | None = Field(default=None, ge=0)
    topic: str | None = None
    hook: str | None = None
    format_type: str | None = None
    monetization_path: str | None = None
    source_notes: str | None = None
    status: Status | None = None
    hook_strength: float | None = Field(default=None, ge=0, le=10)
    recreation_ease: float | None = Field(default=None, ge=0, le=10)
    monetization_potential: float | None = Field(default=None, ge=0, le=10)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    settings.agent_outbox.mkdir(parents=True, exist_ok=True)
    settings.agent_inbox.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="DEADinternet", version="0.1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=ROOT_DIR / "app/static"), name="static")
templates = Jinja2Templates(directory=ROOT_DIR / "app/templates")


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def get_reference_or_404(reference_id: int) -> dict[str, Any]:
    with db_session() as conn:
        row = conn.execute("SELECT * FROM references WHERE id = ?", (reference_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Referência não encontrada")
    return row_to_dict(row)


def score_values(values: dict[str, Any]) -> float:
    return calculate_score(views=values.get("views", 0), likes=values.get("likes", 0), comments=values.get("comments", 0), hook_strength=values.get("hook_strength", 0), recreation_ease=values.get("recreation_ease", 0), monetization_potential=values.get("monetization_potential", 0))


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"port": settings.port})


@app.get("/health")
def health():
    return {"status": "ok", "host": settings.host, "port": settings.port, "database": str(settings.db_path)}


@app.get("/api/references")
def list_references(platform: Platform | None = None, status: Status | None = None, min_score: float = 0):
    query = "SELECT * FROM references WHERE score >= ?"
    params: list[Any] = [min_score]
    if platform:
        query += " AND platform = ?"; params.append(platform)
    if status:
        query += " AND status = ?"; params.append(status)
    query += " ORDER BY score DESC, id DESC"
    with db_session() as conn:
        rows = conn.execute(query, params).fetchall()
    return [row_to_dict(row) for row in rows]


@app.post("/api/references", status_code=201)
def create_reference(payload: ReferenceInput):
    values = payload.model_dump(mode="json")
    values["url"] = str(payload.url)
    values["score"] = score_values(values)
    if values["score"] > 0 and values["status"] == "captured":
        values["status"] = "scored"
    columns = ",".join(values.keys())
    placeholders = ",".join("?" for _ in values)
    try:
        with db_session() as conn:
            cursor = conn.execute(f"INSERT INTO references ({columns}) VALUES ({placeholders})", tuple(values.values()))
            reference_id = cursor.lastrowid
    except sqlite3.IntegrityError as exc:
        if "url" in str(exc).lower() or "unique" in str(exc).lower():
            raise HTTPException(status_code=409, detail="Esta URL já foi cadastrada") from exc
        raise HTTPException(status_code=400, detail="Dados inválidos") from exc
    return get_reference_or_404(int(reference_id))


@app.get("/api/references/{reference_id}")
def get_reference(reference_id: int):
    return get_reference_or_404(reference_id)


@app.patch("/api/references/{reference_id}")
def update_reference(reference_id: int, payload: ReferencePatch):
    current = get_reference_or_404(reference_id)
    changes = payload.model_dump(exclude_none=True, mode="json")
    if "url" in changes:
        changes["url"] = str(changes["url"])
    merged = {**current, **changes}
    changes["score"] = score_values(merged)
    assignments = ", ".join(f"{key} = ?" for key in changes) + ", updated_at = CURRENT_TIMESTAMP"
    try:
        with db_session() as conn:
            conn.execute(f"UPDATE references SET {assignments} WHERE id = ?", (*changes.values(), reference_id))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="URL duplicada ou dados inválidos") from exc
    return get_reference_or_404(reference_id)


@app.delete("/api/references/{reference_id}", status_code=204)
def delete_reference(reference_id: int):
    get_reference_or_404(reference_id)
    with db_session() as conn:
        conn.execute("DELETE FROM references WHERE id = ?", (reference_id,))


@app.post("/api/references/{reference_id}/score")
def rescore_reference(reference_id: int):
    reference = get_reference_or_404(reference_id)
    score = score_values(reference)
    with db_session() as conn:
        conn.execute("UPDATE references SET score = ?, status = CASE WHEN status='captured' THEN 'scored' ELSE status END, updated_at=CURRENT_TIMESTAMP WHERE id=?", (score, reference_id))
    return get_reference_or_404(reference_id)


@app.post("/api/references/{reference_id}/agent-task", status_code=201)
def queue_agent_task(reference_id: int):
    return create_agent_task(get_reference_or_404(reference_id))


@app.get("/api/stats")
def stats():
    with db_session() as conn:
        total = conn.execute("SELECT COUNT(*) FROM references").fetchone()[0]
        average = conn.execute("SELECT COALESCE(AVG(score), 0) FROM references").fetchone()[0]
        by_platform = {row[0]: row[1] for row in conn.execute("SELECT platform, COUNT(*) FROM references GROUP BY platform")}
        by_status = {row[0]: row[1] for row in conn.execute("SELECT status, COUNT(*) FROM references GROUP BY status")}
    return {"total": total, "average_score": round(float(average), 2), "by_platform": by_platform, "by_status": by_status}
