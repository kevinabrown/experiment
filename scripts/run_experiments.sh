#!/usr/bin/env bash
set -euo pipefail

ROOT="$HOME/workspace/experiment"
SCRIPTS="$ROOT/scripts"
MULTIFLOW="$ROOT/multiflow"
SCHEDULES="$SCRIPTS/schedules.json"
OUT="$MULTIFLOW/period.file"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <schedule_id> [schedule_id ...]"
  exit 1
fi

for SID in "$@"; do
  echo "=== Generating period.file for schedule ${SID} ==="
  ( cd "$SCRIPTS" && python3 rate_gen.py -s "$SID" --schedules-file "$SCHEDULES" --out "$OUT" )

  echo "=== Running exec.sh (schedule ${SID}) ==="
  ts="$(date +%Y%m%d-%H%M%S)"
  outdir="$MULTIFLOW/results/s${SID}_$ts"
  mkdir -p "$outdir"
  cp -f "$OUT" "$outdir/period.file"

  # Run the simulation; capture log next to outputs
  ( cd "$MULTIFLOW" && bash ./exec.sh >/dev/null 2>&1 )

  # Move ALL generated artifacts into the result folder
  (
    cd "$MULTIFLOW"
    shopt -s nullglob
    mv router-bw-tracker-* "$outdir"/ 2>/dev/null || true
    mv terminal-packet-stats-* "$outdir"/ 2>/dev/null || true
    mv riodr-* "$outdir"/ 2>/dev/null || true
    mv ross*.csv "$outdir"/ 2>/dev/null || true
    mv *.flows.out "$outdir"/ 2>/dev/null || true
    # any left-over png/json/etc from the run
    mv *.png "$outdir"/ 2>/dev/null || true
    mv *.json "$outdir"/ 2>/dev/null || true
  )

  echo "=== Plotting (schedule ${SID}) ==="
  python3 "$SCRIPTS/flow_parser.py" --input "$outdir" --sid "$SID" --outdir "$outdir"

  echo "Results in: $outdir"
done

echo "All done."
