#!/usr/bin/env python3
"""Append this week's per-source collection counts to data/collection_history.json.

Run once per published week (after validate). The coverage anomaly gate in
build_run_week compares each new week against the recent median of this file.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent"))

from research_collection import load_collection_manifest, record_collection_history  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", default=str(ROOT / "research_runs" / "collection-manifest.json"))
    parser.add_argument("--today", help="Override collection date as YYYY-MM-DD")
    args = parser.parse_args(argv)
    manifest = load_collection_manifest(args.manifest, today=args.today)
    history = record_collection_history(manifest)
    print(f"[HISTORY] {len(history)} week(s) recorded; latest {manifest.get('window_start')}~{manifest.get('window_end')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
