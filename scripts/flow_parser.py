#!/usr/bin/env python3

import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style  # kept for parity

# CLI
ap = argparse.ArgumentParser(description="Plot terminal stats for a run")
ap.add_argument("-i", "--input", required=True, help="terminal-packet-stats file OR a results directory containing it")
ap.add_argument("--sid", type=int, default=None, help="schedule id; if set, output is named multiflow_s<SID>.png")
ap.add_argument("--outdir", default=None, help="directory to write the PNG (default: alongside input)")
ap.add_argument("--ylim", type=float, default=35.0, help="max y-axis (default 35)")
args = ap.parse_args()

# Resolve input: accept a directory or a specific file
inp = Path(args.input).expanduser().resolve()
if inp.is_dir():
    candidates = sorted(inp.glob("terminal-packet-stats-*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise SystemExit(f"No terminal-packet-stats-* found in {inp}")
    terminalfile = str(candidates[0])
else:
    terminalfile = str(inp)

# Output location and name
outdir = Path(args.outdir).expanduser().resolve() if args.outdir else Path(terminalfile).parent
outdir.mkdir(parents=True, exist_ok=True)
png_name = f"multiflow_s{args.sid}.png" if args.sid is not None else "multiflow.png"
outpng = outdir / png_name

link_bw = 25

# Read terminal data (robust whitespace parsing)
tdf = pd.read_table(terminalfile, delim_whitespace=True)

# Drop unused columns and sort
cols_to_drop = [c for c in tdf.columns if c.startswith(("qos-", "vc"))]
for extra in ("Unnamed: 0", "qos-level", "downstream-credits"):
    if extra in tdf.columns:
        cols_to_drop.append(extra)
tdf = tdf.drop(cols_to_drop, axis=1, errors="ignore")

# Remove empty records with no bandwidth
tdf = tdf[tdf["bw-consumed"] != 0]

# Convert units
tdf["time-stamp"] = tdf["time-stamp"] / 1000.0                  # ns -> µs
tdf["bw-consumed"] = (tdf["bw-consumed"] * link_bw) / 100.0     # % -> GB/s

tdf = tdf.sort_values(["time-stamp", "term-id"])
print(tdf["term-id"].unique())

# Plot data (one subplot per flow id)
term_ids = list(tdf["term-id"].unique())
n = len(term_ids)
if n == 0:
    raise SystemExit("No flows to plot")

if n == 1:
    fig, axs = plt.subplots(1, 1)
    axs = [axs]
else:
    fig, axs = plt.subplots(1, n)

xmin, xmax = tdf["time-stamp"].min(), tdf["time-stamp"].max()

for k, fid in enumerate(term_ids):
    x = tdf.loc[tdf["term-id"] == fid, "time-stamp"]
    y = tdf.loc[tdf["term-id"] == fid, "bw-consumed"]
    axs[k].set_title(f"Flow {fid}", fontsize=10)
    axs[k].plot(x, y, marker=".", fillstyle="none", color="y")
    axs[k].set(xlabel="Time (us)", ylabel="Flow Injection Rate (GB/s)")
    axs[k].set_xlim(xmin, xmax)
    axs[k].set_ylim(0, args.ylim)
    axs[k].grid(True)
    axs[k].ticklabel_format(axis="x", style="plain", useOffset=False, scilimits=(0, 0))

fig.set_figheight(4)
fig.set_figwidth(13)
plt.savefig(outpng, dpi=200)
print(f"Wrote {outpng}")
