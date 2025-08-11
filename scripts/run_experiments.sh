#!/usr/bin/env bash
set -euo pipefail

# Paths
ROOT="${HOME}/workspace/experiment"
SCRIPTS="${ROOT}/scripts"
MULTIFLOW="${ROOT}/multiflow"
SCHED_DIR="${SCRIPTS}/schedules"
PNG_OUT_DIR="${SCRIPTS}/results"
PERIOD_FILE="${MULTIFLOW}/period.file"

# Build the list of schedule IDs:
# - If args given: use them (e.g., 1 3 5)
# - If no args: run all *.rates in scripts/schedules (numeric sort)
declare -a SIDS=()
if [[ $# -gt 0 ]]; then
  for sid in "$@"; do
    if [[ -f "${SCHED_DIR}/${sid}.rates" ]]; then
      SIDS+=("$sid")
    else
      echo "Missing schedule file: ${SCHED_DIR}/${sid}.rates" >&2
      exit 1
    fi
  done
else
  shopt -s nullglob
  for f in "${SCHED_DIR}/"*.rates; do
    b="$(basename "$f")"
    sid="${b%.rates}"
    [[ "$sid" =~ ^[0-9]+$ ]] && SIDS+=("$sid")
  done
  # numeric sort
  IFS=$'\n' SIDS=($(sort -n <<<"${SIDS[*]}")); unset IFS
fi

# Ensure output dirs
mkdir -p "${PNG_OUT_DIR}"
mkdir -p "${MULTIFLOW}/results"

for SID in "${SIDS[@]}"; do
  echo "=== Schedule ${SID} ==="

  FLOWS_FILE="${SCHED_DIR}/${SID}.rates"
  OUTDIR="${MULTIFLOW}/results/s${SID}"

  # Fresh results folder for this schedule
  rm -rf "${OUTDIR}"
  mkdir -p "${OUTDIR}"

  # Generate period.file (and related conf files) from the schedule
  ( cd "${SCRIPTS}" && python3 rate_gen.py "${FLOWS_FILE}" --codes_flows_file "${PERIOD_FILE}" )

  # Keep a copy of the exact period.file used
  cp -f "${PERIOD_FILE}" "${OUTDIR}/period.file"

  # Run the simulation silently
#  ( cd "${MULTIFLOW}" && bash ./exec.sh >/dev/null 2>&1 )

  # Run the simulation but keep going even if it crashes
  status=0
  (
    cd "${MULTIFLOW}"
    bash ./exec.sh >/dev/null 2>&1
  ) || status=$?

  # Record exit code for this run
  echo "${status}" > "${OUTDIR}/exit_code.txt"
  if (( status != 0 )); then
    (( status > 128 )) && echo "exec.sh died by signal $((status-128)) for schedule ${SID}" >&2
    echo "exec.sh failed (exit ${status}) for schedule ${SID}; continuing…" >&2
  fi

  # Move ALL generated artifacts for this run into the schedule's results folder
  (
    cd "${MULTIFLOW}"
    shopt -s nullglob
    mv terminal-packet-stats-* "${OUTDIR}/" 2>/dev/null || true
    mv router-bw-tracker-*     "${OUTDIR}/" 2>/dev/null || true
    mv riodir-*                "${OUTDIR}/" 2>/dev/null || true
    mv ross*.csv               "${OUTDIR}/" 2>/dev/null || true
    mv ross_all_lp_stats       "${OUTDIR}/" 2>/dev/null || true
    mv *.flows.out             "${OUTDIR}/" 2>/dev/null || true
    mv *.json                  "${OUTDIR}/" 2>/dev/null || true
    mv *.png                   "${OUTDIR}/" 2>/dev/null || true
  )

  # Find the newest terminal stats file from this run
  TERM_FILE="$(ls -1t "${OUTDIR}"/terminal-packet-stats-* 2>/dev/null | head -n1 || true)"
  if [[ -z "${TERM_FILE}" ]]; then
    echo "Warning: no terminal-packet-stats-* in ${OUTDIR}; skipping plot." >&2
    continue
  fi

  # Create the PNG into scripts/results as multiflow<SID>.png
  python3 "${SCRIPTS}/flow_parser.py" "${TERM_FILE}" -o "${PNG_OUT_DIR}/r50_l100_multiflow${SID}.png"

  echo "Saved run artifacts -> ${OUTDIR}"
  echo "Saved plot          -> ${PNG_OUT_DIR}/r50_l100_multiflow${SID}.png"
done

echo "All done."
