#!/usr/bin/env python3
"""Meme Radar: coleta pública, deduplicação e ranking de candidatos do Reddit.

O módulo não publica conteúdo e não chama IA automaticamente. A saída serve para
revisão humana e, opcionalmente, para análise posterior dos finalistas por um agente.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

DEFAULT_USER_AGENT = "MemeRadar/0.1 (+local research; contact: owner)"
VALID_LISTINGS = {"hot", "new", "top", "rising"}


@dataclass(frozen=True)
class Candidate:
    source: str
    source_id: str
    title: str
    url: str
    permalink: str
    community: str
    author: str
    created_utc: float
    score: int
    comments: int
    upvote_ratio: float
    is_nsfw: bool
    is_video: bool
    ranking_score: float = 0.0


def normalize_text(value: str) -> str:
    """Normalize text for deterministic duplicate detection."""

    decomposed = unicodedata.normalize("NFKD", value or "")
    ascii_text = "".join(char for char in decomposed if not unicodedata.combining(char))
    lowered = ascii_text.casefold()
    return re.sub(r"[^a-z0-9]+", " ", lowered).strip()


def canonical_url(value: str) -> str:
    """Remove fragments and common tracking parameters from a URL."""

    try:
        parsed = urllib.parse.urlsplit(value)
    except ValueError:
        return value.strip()
    ignored = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"}
    query = [
        (key, item)
        for key, item in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        if key.casefold() not in ignored
    ]
    return urllib.parse.urlunsplit(
        (
            parsed.scheme.casefold(),
            parsed.netloc.casefold(),
            parsed.path.rstrip("/"),
            urllib.parse.urlencode(query),
            "",
        )
    )


def duplicate_key(candidate: Candidate) -> str:
    canonical = canonical_url(candidate.url)
    material = canonical if canonical.startswith(("http://", "https://")) else normalize_text(candidate.title)
    if not material:
        material = candidate.source_id
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def rank_candidate(candidate: Candidate, now: float | None = None) -> float:
    """Return a deterministic opportunity score based only on public metrics."""

    current = time.time() if now is None else now
    age_hours = max(0.0, (current - candidate.created_utc) / 3600.0)
    engagement = math.log1p(max(candidate.score, 0)) + 1.45 * math.log1p(max(candidate.comments, 0))
    approval = max(0.0, min(candidate.upvote_ratio, 1.0)) * 3.0
    freshness = max(0.0, 1.0 - age_hours / (24.0 * 7.0)) * 2.0
    return round(engagement + approval + freshness, 4)


def deduplicate(candidates: Iterable[Candidate]) -> list[Candidate]:
    """Keep the strongest version of each candidate."""

    selected: dict[str, Candidate] = {}
    for candidate in candidates:
        key = duplicate_key(candidate)
        previous = selected.get(key)
        if previous is None or candidate.ranking_score > previous.ranking_score:
            selected[key] = candidate
    return list(selected.values())


def parse_reddit_listing(
    payload: dict[str, Any],
    *,
    allow_nsfw: bool = False,
    now: float | None = None,
) -> list[Candidate]:
    children = payload.get("data", {}).get("children", [])
    results: list[Candidate] = []
    for child in children:
        data = child.get("data", {}) if isinstance(child, dict) else {}
        is_nsfw = bool(data.get("over_18", False))
        if is_nsfw and not allow_nsfw:
            continue
        candidate = Candidate(
            source="reddit",
            source_id=str(data.get("name") or data.get("id") or ""),
            title=str(data.get("title") or "").strip(),
            url=str(data.get("url_overridden_by_dest") or data.get("url") or "").strip(),
            permalink="https://www.reddit.com" + str(data.get("permalink") or ""),
            community=str(data.get("subreddit") or ""),
            author=str(data.get("author") or "[deleted]"),
            created_utc=float(data.get("created_utc") or 0.0),
            score=int(data.get("score") or 0),
            comments=int(data.get("num_comments") or 0),
            upvote_ratio=float(data.get("upvote_ratio") or 0.0),
            is_nsfw=is_nsfw,
            is_video=bool(data.get("is_video", False)),
        )
        if not candidate.title or not candidate.source_id:
            continue
        results.append(
            Candidate(**{**asdict(candidate), "ranking_score": rank_candidate(candidate, now=now)})
        )
    return results


def fetch_reddit(
    community: str,
    *,
    listing: str,
    limit: int,
    timeout: float,
    user_agent: str,
    allow_nsfw: bool,
) -> list[Candidate]:
    if listing not in VALID_LISTINGS:
        raise ValueError(f"listagem inválida: {listing}")
    safe_community = re.sub(r"[^A-Za-z0-9_]+", "", community)
    if not safe_community:
        raise ValueError("comunidade inválida")
    query = urllib.parse.urlencode({"limit": max(1, min(limit, 100)), "raw_json": 1})
    url = f"https://www.reddit.com/r/{safe_community}/{listing}.json?{query}"
    request = urllib.request.Request(url, headers={"User-Agent": user_agent, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"Reddit respondeu HTTP {error.code} para r/{safe_community}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"falha de rede ao consultar r/{safe_community}: {error.reason}") from error
    return parse_reddit_listing(payload, allow_nsfw=allow_nsfw)


def load_config(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"configuração inválida em {path}: {error}") from error
    if not isinstance(content, dict):
        raise RuntimeError("a configuração precisa ser um objeto JSON")
    return content


def write_report(path: Path, candidates: list[Candidate], metadata: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    document = {
        "metadata": metadata,
        "candidates": [asdict(candidate) for candidate in candidates],
    }
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Coleta, deduplica e ranqueia candidatos públicos do Reddit.")
    parser.add_argument("--config", type=Path, help="arquivo JSON opcional")
    parser.add_argument("--subreddit", action="append", dest="subreddits", help="comunidade, repetível")
    parser.add_argument("--listing", choices=sorted(VALID_LISTINGS), default=None)
    parser.add_argument("--limit", type=int, default=None, help="itens por comunidade, máximo 100")
    parser.add_argument("--top", type=int, default=None, help="quantidade final após deduplicação")
    parser.add_argument("--timeout", type=float, default=None)
    parser.add_argument("--allow-nsfw", action="store_true", help="inclui posts marcados como adultos")
    parser.add_argument("--output", type=Path, default=Path("data/meme-radar/latest.json"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
        subreddits = args.subreddits or config.get("subreddits") or []
        if not isinstance(subreddits, list) or not subreddits:
            raise RuntimeError("informe ao menos um --subreddit ou configure subreddits")
        listing = args.listing or str(config.get("listing") or "hot")
        limit = args.limit or int(config.get("limit") or 25)
        top = args.top or int(config.get("top") or 30)
        timeout = args.timeout or float(config.get("timeout") or 15.0)
        allow_nsfw = bool(args.allow_nsfw or config.get("allow_nsfw", False))
        user_agent = os.environ.get("MEME_RADAR_USER_AGENT", DEFAULT_USER_AGENT).strip()

        collected: list[Candidate] = []
        failures: list[str] = []
        for community in subreddits:
            try:
                collected.extend(
                    fetch_reddit(
                        str(community),
                        listing=listing,
                        limit=limit,
                        timeout=timeout,
                        user_agent=user_agent,
                        allow_nsfw=allow_nsfw,
                    )
                )
            except (RuntimeError, ValueError) as error:
                failures.append(str(error))

        ranked = sorted(deduplicate(collected), key=lambda item: item.ranking_score, reverse=True)[:top]
        metadata = {
            "project": "Meme Radar",
            "collected_at": datetime.now(UTC).isoformat(),
            "source": "reddit",
            "communities": [str(item) for item in subreddits],
            "listing": listing,
            "raw_count": len(collected),
            "final_count": len(ranked),
            "failures": failures,
            "ai_used": False,
            "automatic_publication": False,
        }
        write_report(args.output, ranked, metadata)
        print(f"Relatório salvo em {args.output} com {len(ranked)} candidatos.")
        for failure in failures:
            print(f"AVISO: {failure}", file=sys.stderr)
        return 0 if ranked or not failures else 2
    except (RuntimeError, ValueError) as error:
        print(f"ERRO: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
