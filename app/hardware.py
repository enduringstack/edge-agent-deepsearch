"""Validation and loading for the weekly hardware radar (端侧硬件雷达).

The hardware radar is an editorial module that sits beside the formal paper
run: mobile SoCs, PC chips, NPUs, low-power / wearable silicon, PIM/CIM and
memory. It has its own contract so the paper pipeline's rules (7-day arXiv
window, candidate attestation) do not apply, but every item still needs a
dated, openable source and readable Chinese copy.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

CATEGORIES = (
    "移动SoC",
    "PC芯片",
    "NPU/AI加速器",
    "低功耗/可穿戴/IoT",
    "存内计算/PIM",
    "存储与内存",
    "车载/机器人",
    "数据中心(对端侧有参考)",
    "软件栈/工具链",
    "产业动态",
    "学术研究",
)
SOURCE_TYPES = {"官方", "媒体", "论文"}
CONFIDENCE = {"high", "medium", "low"}
SPEC_KEYS = ("process", "cpu", "gpu", "npu", "memory", "power", "other")
_CJK_RE = re.compile(r"[㐀-鿿]")


class HardwareValidationError(ValueError):
    pass


def _http_url(value) -> bool:
    try:
        parsed = urlparse(value)
    except Exception:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _chinese(value) -> bool:
    return isinstance(value, str) and bool(_CJK_RE.search(value))


def empty_hardware(note: str = "") -> dict:
    return {"window": {}, "overview": note, "items": []}


def validate_hardware(payload: dict) -> dict:
    """Return a normalised copy of ``payload`` or raise HardwareValidationError."""
    if not isinstance(payload, dict):
        raise HardwareValidationError("hardware radar 必须是 JSON object")
    window = payload.get("window") or {}
    try:
        start = date.fromisoformat(window["start"])
        end = date.fromisoformat(window["end"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HardwareValidationError("window.start/end 必须是 ISO 日期") from exc
    if end < start:
        raise HardwareValidationError("window.end 早于 window.start")
    overview = payload.get("overview") or ""
    if not _chinese(overview):
        raise HardwareValidationError("overview 必须是可读中文")
    takeaways = payload.get("takeaways_zh") or []
    if not (isinstance(takeaways, list) and all(_chinese(x) for x in takeaways)):
        raise HardwareValidationError("takeaways_zh 必须是中文字符串数组")

    items = payload.get("items")
    if not isinstance(items, list):
        raise HardwareValidationError("items 必须是数组")
    seen = set()
    out = []
    for i, item in enumerate(items):
        where = f"items[{i}]"
        if not isinstance(item, dict):
            raise HardwareValidationError(f"{where} 必须是 object")
        try:
            day = date.fromisoformat(item.get("date") or "")
        except ValueError as exc:
            raise HardwareValidationError(f"{where}.date 不是 ISO 日期") from exc
        if not (start <= day <= end):
            raise HardwareValidationError(f"{where}.date {day} 不在窗口 {start}~{end} 内")
        if item.get("category") not in CATEGORIES:
            raise HardwareValidationError(f"{where}.category 非法：{item.get('category')!r}")
        if item.get("source_type") not in SOURCE_TYPES:
            raise HardwareValidationError(f"{where}.source_type 非法：{item.get('source_type')!r}")
        url = item.get("url")
        if not _http_url(url):
            raise HardwareValidationError(f"{where}.url 不是 http(s) 链接")
        if url in seen:
            raise HardwareValidationError(f"{where}.url 重复：{url}")
        seen.add(url)
        for key in ("vendor", "title"):
            if not (isinstance(item.get(key), str) and item[key].strip()):
                raise HardwareValidationError(f"{where}.{key} 不能为空")
        for key in ("title_zh", "summary_zh", "edge_ai_impact_zh"):
            if not _chinese(item.get(key)):
                raise HardwareValidationError(f"{where}.{key} 必须是可读中文")
        whats_new = item.get("whats_new_zh") or []
        if not (isinstance(whats_new, list) and all(_chinese(x) for x in whats_new)):
            raise HardwareValidationError(f"{where}.whats_new_zh 必须是中文字符串数组")
        specs = item.get("key_specs") or {}
        if not isinstance(specs, dict) or any(k not in SPEC_KEYS for k in specs):
            raise HardwareValidationError(f"{where}.key_specs 只允许 {SPEC_KEYS}")
        evidence = item.get("evidence_urls") or []
        if not (isinstance(evidence, list) and all(_http_url(u) for u in evidence)):
            raise HardwareValidationError(f"{where}.evidence_urls 必须是链接数组")
        confidence = item.get("confidence") or "high"
        if confidence not in CONFIDENCE:
            raise HardwareValidationError(f"{where}.confidence 非法：{confidence!r}")
        capacity = item.get("model_capacity_zh") or ""
        if capacity and not _chinese(capacity):
            raise HardwareValidationError(f"{where}.model_capacity_zh 必须是可读中文")
        deep = item.get("deep_dive_zh") or []
        if not isinstance(deep, list) or not all(
                isinstance(d, dict) and _chinese(d.get("heading"))
                and isinstance(d.get("points"), list) and d["points"]
                and all(isinstance(x, str) and x.strip() for x in d["points"])
                for d in deep):
            raise HardwareValidationError(
                f"{where}.deep_dive_zh 必须是 [{{heading, points[]}}] 且标题为中文")
        for key in ("venue", "affiliation", "authors"):
            if key in item and not isinstance(item[key], str):
                raise HardwareValidationError(f"{where}.{key} 必须是字符串")
        if item["category"] == "学术研究" and not (item.get("venue") or "").strip():
            raise HardwareValidationError(f"{where}.venue 学术研究条目必须注明发表处")
        out.append({
            **item,
            "deep_dive_zh": deep,
            "whats_new_zh": whats_new,
            "key_specs": {k: v for k, v in specs.items() if v},
            "evidence_urls": evidence,
            "confidence": confidence,
        })
    # within a category: first-party and well-sourced items lead, then newest first
    order = {c: n for n, c in enumerate(CATEGORIES)}
    trust = {"high": 0, "medium": 1, "low": 2}
    out.sort(key=lambda x: (
        order[x["category"]], x["source_type"] != "官方", trust[x["confidence"]],
        -date.fromisoformat(x["date"]).toordinal()))
    return {**payload, "takeaways_zh": takeaways, "items": out}


def load_hardware(path: Path) -> dict:
    if not path.exists():
        return empty_hardware()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HardwareValidationError(f"hardware radar 不是合法 JSON：{exc}") from exc
    return validate_hardware(raw)
