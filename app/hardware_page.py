"""Static shell for the 硬件洞察 page (monthly edge-hardware industry analysis).

Reuses the WAIC insight shell (marked.js + auto TOC from h2 + KaTeX) and adds a
month switcher: ``?m=YYYY-MM`` loads site/hardware/insight-YYYY-MM.md, no
parameter loads the newest month (site/hardware/hardware-insight.md). The
month list comes from site/hardware/index.json, written by
agent/build_hardware.py.
"""
from app.waic_page import WAIC_HTML

_MONTH_JS = r"""var MONTH = (location.search.match(/[?&]m=(\d{4}-\d{2})/) || [])[1] || '';
    var MD_URL = MONTH ? 'hardware/insight-' + MONTH + '.md' : 'hardware/hardware-insight.md';
    fetch('hardware/index.json').then(function(r){return r.ok ? r.json() : [];}).then(function(months){
      var el = document.getElementById('months');
      if(!el || !months.length) return;
      var current = MONTH || months[0].month;
      el.innerHTML = months.map(function(m, i){
        var href = i === 0 ? 'hardware.html' : 'hardware.html?m=' + m.month;
        return '<a class="month' + (m.month === current ? ' on' : '') + '" href="' + href + '" title="' + m.title + '">' + m.month + '</a>';
      }).join('');
    }).catch(function(){});"""


def _swap(html: str, old: str, new: str) -> str:
    if old not in html:
        raise RuntimeError(f"waic_page shell changed; cannot derive hardware page ({old!r})")
    return html.replace(old, new)


HARDWARE_HTML = WAIC_HTML
for _old, _new in (
    ("<title>RADAR · WAIC 洞察</title>", "<title>RADAR · 硬件洞察</title>"),
    ("WAIC 洞察 · 世界人工智能大会 2026", "硬件洞察 · 移动芯片 / 低功耗 / 存内计算"),
    ('<a class="back" href="index.html">← 返回雷达</a>',
     '<nav class="months" id="months" aria-label="切换月份"></nav><a class="back" href="index.html">← 返回雷达</a>'),
    ("    .back{",
     "    .months{display:flex;gap:6px;flex-wrap:wrap}"
     ".month{font-family:\"IBM Plex Mono\",monospace;font-size:11px;padding:2px 8px;border:1px solid var(--rule);border-radius:3px;color:var(--muted)}"
     ".month.on{background:var(--amber);border-color:var(--amber);color:#fff}\n    .back{"),
    ("var MD_URL = 'waic/WAIC-insight.md';", _MONTH_JS),
):
    HARDWARE_HTML = _swap(HARDWARE_HTML, _old, _new)
