"""Weekly recall audit (漏检对账): an independent list of the week's big edge-AI
events, each reconciled against what the report actually contains.

Collection proves which sources were *checked*; it cannot show what those
sources *missed*. This audit is the outside view: a separate subagent lists the
week's important events from independent media, aggregators and community front
pages, and every one must be either found in the report (已收录), added to it
(补收), or deliberately left out with a reason (不收).
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from app.clock import report_today

STATUSES = {"已收录", "补收", "不收"}
PLACES = {"正式周报", "本周判断", "社区雷达", "硬件雷达"}
MIN_ITEMS = 10
_CJK_RE = re.compile(r"[㐀-鿿]")


class RecallAuditError(ValueError):
    pass


def _http_url(value) -> bool:
    try:
        parsed = urlparse(str(value or ""))
    except Exception:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _chinese(value, minimum: int = 4) -> bool:
    return len(_CJK_RE.findall(str(value or ""))) >= minimum


def validate_recall_audit(payload: dict, *, today: date | None = None) -> dict:
    today = today or report_today()
    if not isinstance(payload, dict):
        raise RecallAuditError("recall audit 必须是 JSON object")
    window = payload.get("window") or {}
    try:
        start = date.fromisoformat(window["start"])
        end = date.fromisoformat(window["end"])
    except (KeyError, TypeError, ValueError) as exc:
        raise RecallAuditError("window.start/end 必须是 ISO 日期") from exc
    if end != today or (end - start).days != 6:
        raise RecallAuditError("漏检对账必须覆盖截至 today 的 7 个自然日")
    if not _chinese(payload.get("method"), 10):
        raise RecallAuditError("method 必须用中文说明查了哪些独立来源")
    items = payload.get("items")
    if not isinstance(items, list) or len(items) < MIN_ITEMS:
        raise RecallAuditError(f"items 至少 {MIN_ITEMS} 条本周大事")
    out = []
    for i, raw in enumerate(items):
        item = dict(raw or {})
        where = f"items[{i}]"
        if not _chinese(item.get("headline")):
            raise RecallAuditError(f"{where}.headline 必须是可读中文")
        if not _http_url(item.get("url")):
            raise RecallAuditError(f"{where}.url 必须是报道或原文直达链接")
        status = item.get("status")
        if status not in STATUSES:
            raise RecallAuditError(f"{where}.status 必须是 {sorted(STATUSES)} 之一")
        if status == "不收":
            if not _chinese(item.get("reason"), 6):
                raise RecallAuditError(f"{where}: 不收 必须写中文理由")
        else:
            if item.get("place") not in PLACES:
                raise RecallAuditError(f"{where}.place 必须是 {sorted(PLACES)} 之一")
            if not str(item.get("match") or "").strip():
                raise RecallAuditError(f"{where}.match 必须写对应条目的 id 或 URL")
        out.append(item)
    return {**payload, "items": out}


def load_recall_audit(path: Path, *, today: date | None = None) -> dict:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RecallAuditError(f"无法读取漏检对账：{exc}") from exc
    return validate_recall_audit(payload, today=today)


def report_keys(papers: list, weekly: dict, community: dict, hardware: dict) -> dict:
    """place -> set of ids/URLs the built report actually contains."""
    def norm(u):
        return str(u or "").strip().rstrip("/")
    return {
        "正式周报": {norm(p.get(k)) for p in papers for k in ("id", "paper_url") if p.get(k)},
        "本周判断": {norm(h.get("url")) for h in (weekly or {}).get("highlights") or []},
        "社区雷达": {norm(c.get(k)) for c in (community or {}).get("items") or [] for k in ("id", "url") if c.get(k)},
        "硬件雷达": {norm(h.get("url")) for h in (hardware or {}).get("items") or []},
    }


def unmatched(audit: dict, keys: dict) -> list:
    """Audit items claimed as included whose match is not in the named place."""
    bad = []
    for item in audit["items"]:
        if item["status"] == "不收":
            continue
        if str(item["match"]).strip().rstrip("/") not in keys.get(item["place"], set()):
            bad.append(f"{item['headline']}：{item['place']} 里找不到 {item['match']}")
    return bad
