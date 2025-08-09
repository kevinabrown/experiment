#!/usr/bin/env python3
'''
    This scripts writes the period.file with flow rate adjustments
    
    This script converts the BW demands and inflection points
    into the format required for CODES simulations"

    To set the injection rate in CODES, you set the message size and 
    the delay between successive messages.
'''


import argparse
import json
import os
from pathlib import Path
import sys

# CLI args
parser = argparse.ArgumentParser(description="Generate period.file from schedule")
parser.add_argument(
    "-s", "--schedule", type=int, required=True,
    help="Schedule id to use (e.g., 1, 2, ...)"
)
parser.add_argument(
    "--schedules-file",
    default=str(Path(__file__).with_name("schedules.json")),
    help="Path to schedules JSON (default: scripts/schedules.json)"
)
parser.add_argument(
    "--out",
    default=str((Path(__file__).parent / "../multiflow/period.file").resolve()),
    help="Output period.file path (default: ../multiflow/period.file)"
)
args = parser.parse_args()

# Load schedules
with open(args.schedules_file, "r") as f:
    raw = json.load(f)

# convert keys to ints and values to floats consistently
def _normalize_schedule(sched_obj):
    # sched_obj: {"t": {"flow_id": value, ...}, ...}
    out = {}
    for t, flows in sched_obj.items():
        t_i = int(t)
        out[t_i] = {int(fid): float(val) for fid, val in flows.items()}
    return out

schedules = {int(k): _normalize_schedule(v) for k, v in raw.items()}
if args.schedule not in schedules:
    available = ", ".join(map(str, sorted(schedules.keys())))
    sys.exit(f"Schedule {args.schedule} not found. Available: {available}")

change_schedule = schedules[args.schedule]

# Collect all flow IDs that ever appear
all_flow_ids = sorted({fid for flows in change_schedule.values() for fid in flows.keys()})

print(f"schedule {args.schedule}:")
prev_vec = None
for t in sorted(change_schedule.keys()):
    # fill missing flows by carrying forward previous value or 0.0 if first time
    cur_vec = []
    for idx, fid in enumerate(all_flow_ids):
        prev_val = (prev_vec[idx] if prev_vec is not None else 0.0)
        cur_val = change_schedule[t].get(fid, prev_val)
        cur_vec.append(cur_val)
    if prev_vec is None or cur_vec != prev_vec:
        # print only when something changes
        print("[" + ", ".join(f"{v:g}" for v in cur_vec) + "]")
    prev_vec = cur_vec

# Set base rate for 25GB bandwidth
message_size = 64
bw = 25*(1024*1024*1024)/(1000*1000*1000)
base_rate = message_size/bw

# Reshape schedules to isolate individual flows
flows = {0: [], 1: [], 2:[] }
for key in change_schedule.keys():
    for k, v in change_schedule[key].items():
        if v == 0:
            v = 0.001
        tmp = (v/25)*100
        myrate = base_rate * (100/tmp)
        flows[k].append(round(myrate, 6))

# Create/overwrite rate file and use it as stdout
rate_file = open('../multiflow/period.file', 'w')
sys.stdout = rate_file

# Set and write injection delays for given rate changes
for flow in [0, 1, 2]:
    print(len(flows[flow]), end=' ')
    for i, rate in enumerate(flows[flow]):
        print(f'{i*1000}:{rate}', end=' ')
    print()

# Write entry for allreduce SWM
print(0)
