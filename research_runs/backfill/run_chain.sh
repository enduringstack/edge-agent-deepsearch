#!/usr/bin/env bash
# usage: run_chain.sh LABEL:END[:arxiv] ...   (":arxiv" reruns only the arXiv sweep for that week)
# Waits for export.arxiv.org before each week (it rate-limits/blocks for long stretches).
set -u
cd "$(dirname "$0")/../.."
probe() {
  for i in $(seq 1 72); do
    c=$(curl -s -o /dev/null -w "%{http_code}" -m 30 "https://export.arxiv.org/api/query?search_query=abs:edge&max_results=1")
    [ "$c" = 200 ] && return 0
    echo "$(date +%H:%M) arXiv probe $c, waiting"; sleep 600
  done
  return 1
}
for spec in "$@"; do
  IFS=: read -r L E MODE <<< "$spec"
  probe || { echo "arXiv unreachable for 12h, stopping before $L"; exit 1; }
  if [ "${MODE:-}" = arxiv ]; then
    export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 EDGE_RUN_DIR="$PWD/research_runs/backfill/$L"
    python -X utf8 agent/arxiv_curl_sweep.py --today "$E" --no-catchup --page-size 200 --max-pages 40 >> "$EDGE_RUN_DIR/collect.log" 2>&1
    echo "arxiv-only exit $? $L" >> "$EDGE_RUN_DIR/collect.log"
  else
    bash research_runs/backfill/collect_week.sh "$L" "$E"
  fi
  echo "chain done $L $(date +%H:%M)"
done
