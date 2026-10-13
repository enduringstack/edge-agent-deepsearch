#!/usr/bin/env python3
"""Tests for the GitHub trending lead list (agent/collect_github_trending.py)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent"))

import collect_github_trending as cgt  # noqa: E402

ARTICLE = """
<article class="Box-row">
  <div class="float-right d-flex"><a href="/login?return_to=%2Fmicrosoft%2FBitNet" class="btn">
    <svg class="octicon octicon-star"><path d="M8 .25a.75.75 0 0 1 .673.418Z"></path></svg>
    <span class="d-none d-md-inline">Star</span></a></div>
  <h2 class="h3 lh-condensed">
    <a href="/microsoft/BitNet" class="Link"><svg><path d="M2 2.5Z"></path></svg>
      <span class="text-normal">microsoft /</span> BitNet</a>
  </h2>
  <p class="col-9 color-fg-muted my-1 tmp-pr-4">
    Official inference framework for 1-bit LLMs &amp; more
  </p>
  <div class="f6 color-fg-muted mt-2">
    <a href="/microsoft/BitNet/stargazers" class="Link"><svg aria-label="star"><path d="M8 .25Z"></path></svg>
      32,901</a>
    <span class="d-inline-block float-sm-right"><svg><path d="M8 .25Z"></path></svg>
      2,854 stars this week</span>
  </div>
</article>
"""


class TrendingParseTest(unittest.TestCase):
    def test_description_skips_svg_path_and_stars_are_read(self):
        [(full, desc, total, week)] = cgt.parse_trending(ARTICLE)
        self.assertEqual(full, "microsoft/BitNet")
        self.assertEqual(desc, "Official inference framework for 1-bit LLMs & more")
        self.assertEqual((total, week), (32901, 2854))

    def test_missing_counts_become_none(self):
        html = '<article><h2><a href="/a/b">a / b</a></h2><p>Local LLM engine</p></article>'
        self.assertEqual(cgt.parse_trending(html), [("a/b", "Local LLM engine", None, None)])


class TrendingSelectionTest(unittest.TestCase):
    def test_edge_ai_trending_repos_are_kept(self):
        for repo, desc in [
            ("microsoft/BitNet", "Official inference framework for 1-bit LLMs"),
            ("trymirai/uzu", "A high-performance inference engine for AI models"),
            ("ggml-org/Llama-macOS", "A cosy home for your LLMs."),
            ("AtomicBot-ai/atomic-agent", "Atomic Agent is a local-first AI agent. Runs open-weight models"),
        ]:
            self.assertTrue(cgt.is_edge_trending({"repo": repo, "desc": desc}), repo)

    def test_keyword_collisions_are_rejected(self):
        for repo, desc in [
            ("tester-army/e2e", "Next generation e2e testing framework for web and mobile apps."),
            ("flutter/flutter", "Flutter makes it easy and fast to build beautiful apps for mobile and beyond"),
            ("tinyhumansai/openhuman", "The fastest, cheapest open-source agent harness."),
            ("thedotmack/claude-mem", "Persistent Context Across Sessions for Every Agent"),
            ("HunxByts/GhostTrack", "Useful tool to track location or mobile number"),
        ]:
            self.assertFalse(cgt.is_edge_trending({"repo": repo, "desc": desc}), repo)

    def test_ranked_by_weekly_stars_and_filtered(self):
        items = [
            {"repo": "x/new-phone-llm", "desc": "on-device LLM", "stars": 5, "week_stars": 5, "source": "search"},
            {"repo": "microsoft/BitNet", "desc": "inference framework for 1-bit LLMs", "stars": 32901,
             "week_stars": 2854, "source": "trending"},
            {"repo": "flutter/flutter", "desc": "apps for mobile", "stars": 170000, "week_stars": 900,
             "source": "trending"},
            {"repo": "y/no-count", "desc": "local LLM engine", "stars": None, "week_stars": None,
             "source": "trending"},
        ]
        self.assertEqual([x["repo"] for x in cgt.display_top(items)], ["microsoft/BitNet", "x/new-phone-llm"])


if __name__ == "__main__":
    unittest.main()
