#!/usr/bin/env bash
# usage: collect_week.sh LABEL END   (runs every scripted collector for one historical week)
set -u
cd "$(dirname "$0")/../.."
L=$1; E=$2
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 EDGE_RUN_DIR="$PWD/research_runs/backfill/$L"
mkdir -p "$EDGE_RUN_DIR"; LOG="$EDGE_RUN_DIR/collect.log"; : > "$LOG"
python -X utf8 agent/arxiv_curl_sweep.py --today "$E" --no-catchup --page-size 200 --max-pages 40 >> "$LOG" 2>&1; echo "arxiv exit $?" >> "$LOG"
python -X utf8 agent/collect_hf.py --today "$E" >> "$LOG" 2>&1; echo "hf exit $?" >> "$LOG"
python -X utf8 agent/collect_github_releases.py --today "$E" >> "$LOG" 2>&1; echo "gh exit $?" >> "$LOG"
python -X utf8 agent/refresh_trending.py --today "$E" >> "$LOG" 2>&1; echo "trending exit $?" >> "$LOG"
python -X utf8 agent/collect_vendors.py --today "$E" >> "$LOG" 2>&1; echo "vendors exit $?" >> "$LOG"
echo "DONE $L" >> "$LOG"
