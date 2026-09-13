"""Special Event Report pages — hub + individual event detail pages.

The hub (EVENTS_HUB_HTML) lists all special reports with cards.
Each event detail page (render_event_page) loads a markdown file client-side
via marked.js, with a sidebar TOC auto-built from h2 headings.

Usage:
    from app.event_page import EVENTS_HUB_HTML, render_event_page
    # Hub: write EVENTS_HUB_HTML to site/events.html
    # Detail: write render_event_page("apple-sep-2025") to site/events/apple-sep-2025.html
"""

EVENTS_HUB_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RADAR · 专项报告</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    *{box-sizing:border-box}
    :root{--bg:#eef1f3;--panel:#ffffff;--ink:#0b1a24;--muted:#5a6b78;--faint:#8a99a6;--rule:#d4dae0;--hair:#e3e8ec;--accent:#1d1d1f;--accent-light:#86868b;--highlight:#0071e3;--green:#15803d;--amber:#c2410c}
    body{margin:0;background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans","PingFang SC","Noto Sans SC",system-ui,sans-serif;font-size:14.5px;line-height:1.7}
    main{max-width:1180px;margin:0 auto;padding:18px 22px 80px}
    a{color:var(--highlight);text-decoration:none}
    a:hover{text-decoration:underline}
    .scope{background:var(--panel);border:1px solid var(--rule);border-radius:6px;padding:16px 20px;margin-bottom:18px}
    h1{margin:0;font-family:"IBM Plex Mono",monospace;font-size:20px;font-weight:600;letter-spacing:1.5px}
    h1 .sub{font-family:"IBM Plex Sans",sans-serif;font-weight:500;font-size:13px;color:var(--muted);letter-spacing:0;margin-left:8px}
    .back{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--faint)}
    .sweep{height:2px;margin:12px -20px -16px;background:linear-gradient(90deg,transparent,var(--hair) 20%,var(--hair) 80%,transparent);position:relative;overflow:hidden}
    .sweep::after{content:"";position:absolute;inset:0;width:30%;background:linear-gradient(90deg,transparent,var(--highlight),transparent);animation:sweep 3.2s linear infinite}
    @keyframes sweep{0%{transform:translateX(-100%)}100%{transform:translateX(400%)}}
    @media(prefers-reduced-motion:reduce){.sweep::after{animation:none;opacity:.5}}
    .hub-desc{margin:14px 0 0;color:var(--muted);font-size:13px;max-width:640px}
    .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px;margin-top:18px}
    .card{background:var(--panel);border:1px solid var(--rule);border-radius:8px;padding:22px 24px;transition:border-color .2s,box-shadow .2s;text-decoration:none;color:inherit;display:block}
    .card:hover{border-color:var(--highlight);box-shadow:0 2px 12px rgba(0,113,227,.08);text-decoration:none}
    .card-tag{font-family:"IBM Plex Mono",monospace;font-size:10px;font-weight:600;letter-spacing:.8px;text-transform:uppercase;color:var(--highlight);margin-bottom:8px}
    .card-title{font-size:19px;font-weight:700;letter-spacing:-.01em;line-height:1.3;margin:0 0 6px}
    .card-date{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--faint);margin-bottom:10px}
    .card-desc{color:var(--muted);font-size:13px;line-height:1.6;margin:0}
    .card-products{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}
    .card-product{font-family:"IBM Plex Mono",monospace;font-size:10px;color:var(--muted);background:var(--hair);padding:3px 8px;border-radius:3px}
    .empty{color:var(--faint);font-size:13px;padding:40px 0;text-align:center}
  </style>
</head>
<body>
  <main>
    <header class="scope">
      <h1>RADAR<span class="sub">专项报告 · Special Reports</span></h1>
      <a class="back" href="index.html">← 返回雷达</a>
      <div class="sweep"></div>
      <p class="hub-desc">重大发布会、行业事件、技术峰会的深度整理与解读。每期专项聚焦一个标志性事件，覆盖产品、场景、芯片与技术全景。</p>
    </header>
    <div class="grid">
      <a class="card" href="events/siri-ai-deep-dive.html">
        <div class="card-tag">技术深潜</div>
        <h2 class="card-title">Siri Recap 技术深潜 · 一只手表背后的 AI 全栈</h2>
        <div class="card-date">2026-09-11 · 从场景到技术全链路拆解</div>
        <p class="card-desc">以 Apple Watch 上的 Siri Recap 对话摘要为切入点，逐层展开 S11 芯片、Secure Exclave (cL4)、ANE 脉动阵列、AFM 3 MoE 模型、PCC 云端隐私——一个功能串联 Apple 13 年安全技术积累。</p>
        <div class="card-products">
          <span class="card-product">Foundation Models</span>
          <span class="card-product">Secure Exclave</span>
          <span class="card-product">ANE</span>
          <span class="card-product">PCC</span>
          <span class="card-product">S11</span>
        </div>
      </a>
      <a class="card" href="events/apple-sep-2026.html">
        <div class="card-tag">Apple Event</div>
        <h2 class="card-title">Apple 2026 秋季发布会</h2>
        <div class="card-date">2026-09-09 · "Surprise and Shine" · John Ternus 首秀</div>
        <p class="card-desc">iPhone Duo 折叠屏横空出世、iPhone 18 Pro 首款 2nm A20 Pro 芯片 + 可变光圈相机、全新 Siri AI 重构、Apple Watch Ultra 4 续航 84 小时——Ternus 时代的开篇之作。</p>
        <div class="card-products">
          <span class="card-product">iPhone Duo</span>
          <span class="card-product">iPhone 18 Pro</span>
          <span class="card-product">Apple Watch</span>
          <span class="card-product">AirPods 5</span>
          <span class="card-product">Siri AI</span>
        </div>
      </a>
    </div>
  </main>
</body>
</html>
"""


def render_event_page(slug: str) -> str:
    """Return the HTML shell for a single event report page.

    ``slug`` is the filename without extension, e.g. "apple-sep-2025".
    The page fetches ``events/{slug}.md`` client-side and renders it with
    marked.js, building a sidebar TOC from h2 headings.
    """
    return _EVENT_DETAIL_HTML.replace("__SLUG__", slug)


_EVENT_DETAIL_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RADAR · 专项报告</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    *{box-sizing:border-box}
    :root{
      --bg:#f5f5f7;--panel:#ffffff;--ink:#1d1d1f;--muted:#6e6e73;--faint:#86868b;
      --rule:#d2d2d7;--hair:#e8e8ed;--highlight:#0071e3;--accent:#1d1d1f;
      --green:#34c759;--amber:#ff9500;--red:#ff3b30;--purple:#af52de;
      --blue:#007aff;--teal:#5ac8fa;
    }
    body{margin:0;background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans","PingFang SC","Noto Sans SC",system-ui,sans-serif;font-size:14.5px;line-height:1.7}
    main{max-width:1240px;margin:0 auto;padding:18px 22px 80px}
    a{color:var(--highlight);text-decoration:none}
    a:hover{text-decoration:underline}

    /* Header */
    .scope{background:var(--panel);border:1px solid var(--rule);border-radius:8px;padding:16px 20px;margin-bottom:16px}
    h1{margin:0;font-family:"IBM Plex Mono",monospace;font-size:20px;font-weight:600;letter-spacing:1.5px}
    h1 .sub{font-family:"IBM Plex Sans",sans-serif;font-weight:500;font-size:13px;color:var(--muted);letter-spacing:0;margin-left:8px}
    .back{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--faint)}
    .sweep{height:2px;margin:12px -20px -16px;background:linear-gradient(90deg,transparent,var(--hair) 20%,var(--hair) 80%,transparent);position:relative;overflow:hidden}
    .sweep::after{content:"";position:absolute;inset:0;width:30%;background:linear-gradient(90deg,transparent,var(--highlight),transparent);animation:sweep 3.2s linear infinite}
    @keyframes sweep{0%{transform:translateX(-100%)}100%{transform:translateX(400%)}}
    @media(prefers-reduced-motion:reduce){.sweep::after{animation:none;opacity:.5}}

    /* Layout */
    .layout{display:grid;grid-template-columns:230px 1fr;gap:16px;align-items:start}
    .toc{background:var(--panel);border:1px solid var(--rule);border-radius:8px;padding:12px 10px;position:sticky;top:12px;max-height:calc(100vh - 24px);overflow:auto}
    .toc-title{font-family:"IBM Plex Mono",monospace;font-size:10px;color:var(--faint);text-transform:uppercase;letter-spacing:.5px;padding:4px 6px 8px;border-bottom:1px solid var(--hair);margin-bottom:6px}
    .toc a{display:block;padding:4px 8px;font-size:12.5px;color:var(--muted);border-radius:3px;line-height:1.4;transition:background .15s}
    .toc a:hover{background:var(--hair);color:var(--ink)}
    .toc a.active{background:#e8f0fe;color:var(--highlight);font-weight:600}

    /* Article */
    .art{background:var(--panel);border:1px solid var(--rule);border-radius:8px;padding:28px 34px;min-height:60vh}
    .art:empty::before{content:"loading…";color:var(--faint);font-family:"IBM Plex Mono",monospace}
    .art h1{font-family:"IBM Plex Sans",sans-serif;font-size:28px;letter-spacing:-.02em;margin:0 0 8px;border-bottom:2px solid var(--highlight);padding-bottom:10px;display:inline-block}
    .art h2{font-size:20px;margin:32px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--hair);scroll-margin-top:20px;color:var(--ink);font-weight:700;letter-spacing:-.01em}
    .art h3{font-size:16px;margin:22px 0 8px;color:var(--ink);font-weight:600}
    .art h4{font-size:14px;margin:16px 0 6px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.5px;font-family:"IBM Plex Mono",monospace}
    .art p{margin:8px 0}
    .art ul,.art ol{margin:8px 0;padding-left:22px}
    .art li{margin:4px 0}
    .art blockquote{margin:12px 0;padding:10px 18px;border-left:3px solid var(--highlight);background:#f0f5ff;color:var(--muted);border-radius:0 6px 6px 0;font-size:13.5px}
    .art code{font-family:"IBM Plex Mono",monospace;font-size:12.5px;background:var(--hair);padding:1px 5px;border-radius:3px}
    .art pre{background:#1d1d1f;color:#f5f5f7;padding:14px 18px;border-radius:8px;overflow:auto;margin:12px 0}
    .art pre code{background:none;padding:0;color:inherit;font-size:12.5px}
    .art img{max-width:100%;height:auto;border:1px solid var(--hair);border-radius:6px;margin:10px 0}
    .art table{border-collapse:collapse;margin:12px 0;width:100%;font-size:13px}
    .art th,.art td{border:1px solid var(--rule);padding:8px 12px;text-align:left}
    .art th{background:var(--bg);font-weight:600;font-family:"IBM Plex Mono",monospace;font-size:11.5px;letter-spacing:.3px}
    .art hr{border:none;border-top:1px solid var(--rule);margin:24px 0}
    .art strong{color:var(--ink)}

    @media(max-width:760px){
      .layout{grid-template-columns:1fr}
      .toc{position:static;max-height:none}
      .art{padding:18px 16px}
      .art h1{font-size:22px}
      .art h2{font-size:17px}
    }
  </style>
</head>
<body>
  <main>
    <header class="scope">
      <h1>RADAR<span class="sub">专项报告</span></h1>
      <a class="back" href="../events.html">← 全部专项</a>
      <div class="sweep"></div>
    </header>
    <div class="layout">
      <aside class="toc" id="toc"></aside>
      <article class="art" id="art"></article>
    </div>
  </main>
  <script>
    var SLUG = '__SLUG__';
    var MD_URL = 'events/' + SLUG + '.md';

    function buildToc() {
      var art = document.getElementById('art');
      var toc = document.getElementById('toc');
      var headings = art.querySelectorAll('h2');
      if (!headings.length) { toc.style.display = 'none'; return; }
      toc.innerHTML = '<div class="toc-title">目录 Contents</div>';
      headings.forEach(function(h, i) {
        var id = 'section-' + i;
        h.id = id;
        var a = document.createElement('a');
        a.href = '#' + id;
        a.textContent = h.textContent;
        toc.appendChild(a);
      });
      // IntersectionObserver for active highlight
      if ('IntersectionObserver' in window) {
        var obs = new IntersectionObserver(function(entries) {
          entries.forEach(function(e) {
            if (e.isIntersecting) {
              toc.querySelectorAll('a').forEach(function(a) { a.classList.remove('active'); });
              var link = toc.querySelector('a[href="#' + e.target.id + '"]');
              if (link) link.classList.add('active');
            }
          });
        }, { rootMargin: '-20% 0px -70% 0px' });
        headings.forEach(function(h) { obs.observe(h); });
      }
    }

    fetch(MD_URL).then(function(r) { return r.text(); }).then(function(md) {
      document.getElementById('art').innerHTML = marked.parse(md);
      buildToc();
    }).catch(function() {
      document.getElementById('art').innerHTML = '<p style="color:var(--red)">Failed to load report.</p>';
    });
  </script>
</body>
</html>
"""
