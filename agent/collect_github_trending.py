#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Collect端侧 AI-related GitHub repos created/trending this week.

Two sources:
1. github.com/trending?since=weekly (HTML, multiple languages) — parse repos + descriptions.
2. api.github.com/search/repositories (created:>DATE + edge keywords, sort=stars) — uses
   GITHUB_PERSONAL_ACCESS_TOKEN env var if set (avoids rate limit).
Filter for端侧 AI relevance, output data/_github_trending.json with repo + stars + url + created.
The seven-date window is computed at runtime; no weekly source edit is required.
"""
import argparse
import html as html_lib
import urllib.request, urllib.parse, re, sys, json, time, os
from datetime import datetime, timezone

from research_collection import collection_window, parse_collection_date, update_source_coverage

EDGE_KW = [
  "on-device","on device","edge","mobile","npu","embedded","mcu","iot","llm","agent",
  "inference","quantiz","speculat","distill","moe","attention","kv-cache","kv cache",
  "serving","vllm","sglang","llama.cpp","llama-cpp","executorch","mlc","tensorrt","tflite",
  "onnx","wasm","webgpu","rag","tiny","slm","small model","efficient","accelerat",
  "dspark","deepspec","jetson","raspberry","federated","lora","peft","bitnet","ternary",
  "gemma","minicpm","qwen","coreml","mlx","neural-engine","copilot","phi-","llama",
  "deepseek","xdna","ascend","rknn","hexagon","snapdragon",
]

# Repos from the trending *page* are not limited to this week's creations and the
# loose EDGE_KW above lets in any coding-agent tool ("agent", "llm"). To reach the
# display list they need both an on-device/local inference-stack signal and an AI
# signal. Bare "tiny"/"mobile" are deliberately absent: "tinyhumansai" and
# "web and mobile apps" are not edge AI.
EDGE_STACK_KW = [
  "on-device","on device","edge ai","edge device","edge inference","npu","embedded","mcu",
  "microcontroller","tinyml","iot","local-first","local llm","locally","offline","on your own machine",
  "your own device","llama.cpp","ggml","gguf","mlx","executorch","onnx","openvino","litert","tflite",
  "coreml","core ml","neural engine","apple silicon","quantiz","1-bit","bitnet","ternary","jetson",
  "raspberry","rknn","hexagon","snapdragon","webgpu","wasm","inference engine","inference framework",
  "android","ios app",
]
AI_KW = ["llm","language model","model","inference","neural","transformer","gemma","llama","qwen",
         " ai ","ai agent","agent","speech","vision"]


def is_edge_trending(item: dict) -> bool:
    """True when a trending-page repo is about running AI on-device / locally."""
    hay = " " + (item.get("repo", "") + " " + (item.get("desc") or "")).lower() + " "
    return any(k in hay for k in EDGE_STACK_KW) and any(k in hay for k in AI_KW)


def display_top(items: list, limit: int = 20) -> list:
    """Rank this week's GitHub leads by stars gained this week.

    New repos from the search API (created in the window) count every star as a
    weekly star; trending-page repos keep GitHub's "stars this week" figure but
    must pass ``is_edge_trending``.
    """
    pool = []
    for x in items:
        week = x.get("week_stars")
        if not week:
            continue
        if x.get("source") == "trending" and not is_edge_trending(x):
            continue
        pool.append(x)
    pool.sort(key=lambda x: (x["week_stars"], x.get("stars") or 0), reverse=True)
    return pool[:limit]


UA = "Mozilla/5.0 (compatible: edge-agent-github-collector/1.0)"
TOKEN = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN","")

def fetch(url, timeout=25, headers=None):
    h = {"User-Agent": UA, "Accept": "application/vnd.github+json"}
    if TOKEN: h["Authorization"] = f"Bearer {TOKEN}"
    if headers: h.update(headers)
    try:
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace"), r.status
    except urllib.error.HTTPError as e:
        return "", e.code
    except Exception:
        return "", 0

def _count(text):
    m = re.search(r"([\d,]+)", text or "")
    return int(m.group(1).replace(",", "")) if m else None


def parse_trending(html):
    """Return [(full_name, desc, total_stars, stars_this_week)] from trending HTML.

    ``<p[^>]*>`` would also match the SVG ``<path ...>`` in the star button and
    swallow "Star owner / repo" into the description, so the paragraph pattern
    requires a real ``<p>`` tag. Star counts come from the stargazers link and
    the "N stars this week" line; either may be None if GitHub changes markup.
    """
    out=[]
    for art in re.finditer(r'<article[^>]*>(.*?)</article>', html, re.S):
        body=art.group(1)
        m=re.search(r'<h2[^>]*>\s*<a[^>]*href="(/[^"]+)"', body)
        if not m: continue
        full=m.group(1).strip('/')
        dm=re.search(r'<p(?:\s[^>]*)?>(.*?)</p>', body, re.S)
        desc=re.sub(r'<[^>]+>','',(dm.group(1) if dm else '')).strip()
        desc=re.sub(r'\s+',' ',html_lib.unescape(desc))
        tm=re.search(r'href="/' + re.escape(full) + r'/stargazers"[^>]*>(.*?)</a>', body, re.S)
        total=_count(re.sub(r'<[^>]+>', '', tm.group(1))) if tm else None
        wm=re.search(r'([\d,]+)\s+stars\s+this\s+week', body)
        week=_count(wm.group(1)) if wm else None
        out.append((full,desc,total,week))
    return out

def search_api(query, date_from, per_page=30, date_to=None):
    # Bound BOTH ends. An open `created:>=` is harmless for the current week (nothing
    # is created in the future) but silently fills a backfilled window with every repo
    # created since — a historical run then ships repos months newer than its window.
    q=f"{query} created:{date_from}..{date_to}" if date_to else f"{query} created:>={date_from}"
    url=f"https://api.github.com/search/repositories?{urllib.parse.urlencode({'q':q,'sort':'stars','order':'desc','per_page':per_page})}"
    txt,st=fetch(url)
    if not txt: return []
    try:
        d=json.loads(txt)
        return [(it['full_name'], it.get('description','') or '', it.get('stargazers_count',0),
                 it.get('html_url',''), it.get('created_at','')[:10]) for it in d.get('items',[])]
    except: return []

def main(argv=None):
    parser = argparse.ArgumentParser(description="Refresh weekly edge-AI GitHub trending data.")
    parser.add_argument("--today", help="Override collection date as YYYY-MM-DD")
    parser.add_argument("--manifest", default="research_runs/collection-manifest.json")
    args = parser.parse_args(argv)
    run_date = parse_collection_date(args.today)
    window_start, window_end, _ = collection_window(run_date)
    date_from = window_start.isoformat()
    date_to = window_end.isoformat()

    repos={}  # full_name -> {desc, stars, url, created, source}
    # 1) trending
    for lang in ["","/python","/c","/c%2B%2B","/rust","/jupyter-notebook","/swift","/typescript"]:
        url=f"https://github.com/trending{lang}?since=weekly"
        html,st=fetch(url)
        if not html: continue
        for full,desc,total,week in parse_trending(html):
            if full not in repos:
                repos[full]={"desc":desc,"stars":total,"week_stars":week,"url":f"https://github.com/{full}","created":None,"source":"trending"}
        time.sleep(1)
    # 2) search API for端侧 keywords created this week
    for q in ['on-device LLM','edge AI inference','mobile LLM agent','NPU inference',
              'speculative decoding','local LLM engine','edge device agent','llama.cpp executorch']:
        for full,desc,stars,url,created in search_api(q, date_from, date_to=date_to):
            if full not in repos:
                # created inside the window, so every star was earned this week
                repos[full]={"desc":desc,"stars":stars,"week_stars":stars,"url":url,"created":created,"source":"search"}
        time.sleep(2)
    # filter端侧 relevance
    out=[]
    for full,r in repos.items():
        hay=(full+' '+r['desc']).lower()
        if not any(k in hay for k in EDGE_KW): continue
        # Keep the FULL description here. The 140-char cap belongs to the display file
        # (refresh_trending), and truncating twice left the translator a half sentence
        # with no way to see the tail.
        out.append({"repo":full,"desc":r['desc'],"stars":r['stars'],"week_stars":r.get('week_stars'),
                    "url":r['url'],"created":r['created'],"source":r['source']})
    out.sort(key=lambda x:(x['week_stars'] or 0), reverse=True)
    json.dump(out, open("data/_github_trending.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
    update_source_coverage(
        args.manifest,
        "github",
        {
            "trending_checked": True,
            "trending_candidate_count": len(out),
        },
        today=run_date,
    )
    print(f"# {len(out)}端侧-AI repos (trending + created:{date_from}..{date_to})")
    for r in out[:40]:
        print(f"  +{str(r['week_stars'] or '?'):>6}/wk {str(r['stars'] or '?'):>7}★ [{r['source']}] {r['repo']}  -- {r['desc'][:60]}")
        print(f"      {r['url']}")

if __name__=="__main__":
    main()
