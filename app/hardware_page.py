"""Static shell for the 硬件洞察 page (monthly edge-hardware industry analysis).

Reuses the WAIC insight shell (marked.js + auto TOC from h2 + KaTeX) and points
it at site/hardware/hardware-insight.md.
"""
from app.waic_page import WAIC_HTML


def _swap(html: str, old: str, new: str) -> str:
    if old not in html:
        raise RuntimeError(f"waic_page shell changed; cannot derive hardware page ({old!r})")
    return html.replace(old, new)


HARDWARE_HTML = WAIC_HTML
for _old, _new in (
    ("<title>RADAR · WAIC 洞察</title>", "<title>RADAR · 硬件洞察</title>"),
    ("WAIC 洞察 · 世界人工智能大会 2026", "硬件洞察 · 移动芯片 / 低功耗 / 存内计算"),
    ("var MD_URL = 'waic/WAIC-insight.md';", "var MD_URL = 'hardware/hardware-insight.md';"),
):
    HARDWARE_HTML = _swap(HARDWARE_HTML, _old, _new)
