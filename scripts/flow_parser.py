#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style

link_bw = 25

# Read Terminal Data
terminalfile = '../multiflow/terminal-packet-stats-0-601502-1754327151'
tdf = pd.read_table(terminalfile, sep=' ')

# Drop unused columns and sort
cols_to_drop = [col for col in tdf.columns if col.startswith('qos-')]
cols_to_drop = [col for col in tdf.columns if col.startswith('vc')]
cols_to_drop.append('Unnamed: 0')
cols_to_drop.append('qos-level')
cols_to_drop.append('downstream-credits')
tdf = tdf.drop(cols_to_drop, axis=1)

# Remove empty records with no bandwidth
tdf = tdf[tdf['bw-consumed'] != 0]

# Covert values
tdf['time-stamp'] = tdf['time-stamp'].apply(lambda x: x / 1000) # Convert ns to us
tdf['bw-consumed'] = tdf['bw-consumed'].apply(lambda x: (x * link_bw)/100) # Convert % to bw


tdf = tdf.sort_values(['time-stamp','term-id'])
print(tdf['term-id'].unique())


# Plot data
x0 = tdf[tdf['term-id'] == 14]['time-stamp']
y0 = tdf[tdf['term-id'] == 14]['bw-consumed']

x1 = tdf[tdf['term-id'] == 15]['time-stamp']
y1 = tdf[tdf['term-id'] == 15]['bw-consumed']

x2 = tdf[tdf['term-id'] == 1]['time-stamp']
y2 = tdf[tdf['term-id'] == 1]['bw-consumed']

fig, axs = plt.subplots(1, 3)

axs[0].set_title("Flow 0", fontsize=10)
axs[0].plot(x0, y0, marker='.', fillstyle='none', color='y')

axs[1].set_title("Flow 1", fontsize=10)
axs[1].plot(x1, y1, marker='.', fillstyle='none', color='y')

axs[2].set_title("Flow 2", fontsize=10)
axs[2].plot(x2, y2, marker='.', fillstyle='none', color='y')

for ax in axs.flat:
    ax.set (xlabel='Time (us)', ylabel='Flow Injection Rate (GB/s)')
    ax.set_ylim(0, 35)
    #ax.legend()
    ax.label_outer()
    ax.grid(True)

fig.set_figheight(4)
fig.set_figwidth(13)

plt.savefig('multiflow.png')
