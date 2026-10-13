"""The report date used by every window check.

Publishing a week a day after it closes (e.g. a Monday run finished on Tuesday)
must still judge the 7-day windows against the week's last day, not the wall
clock. EDGE_TODAY=YYYY-MM-DD overrides today for the server, build-time gates
and validators alike — the same convention app/storage.py already uses.
"""
from __future__ import annotations

import os
from datetime import date


def report_today() -> date:
    raw = os.environ.get("EDGE_TODAY", "").strip()
    return date.fromisoformat(raw) if raw else date.today()
