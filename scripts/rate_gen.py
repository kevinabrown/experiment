#!/usr/bin/env python3
'''
    This script converts the BW demands and inflection points
    into the format required for CODES simulations"

    To set the injection rate in CODES, you set the message size and 
    the delay between successive messages.
'''

import sys

# Set schedule
change_schedule = {
    0: {0: 15, 1: 15, 2: 25} ,
    1: {0: 15, 1: 15, 2: 25} ,
    2: {0: 15, 1: 15, 2: 25} ,
    3: {0: 25, 1: 10, 2: 5} ,
    4: {0: 25, 1: 10, 2: 5} ,
    5: {0: 25, 1: 10, 2: 5} ,
    6: {0: 10, 1: 13, 2: 20} ,
    7: {0: 10, 1: 13, 2: 20} ,
    8: {0: 10, 1: 13, 2: 20} ,
    9: {0: 20, 1: 1, 2: 1} ,
    10: {0: 20, 1: 1, 2: 1} ,
    11: {0: 20, 1: 1, 2: 1} ,
    12: {0: 15, 1: 15, 2: 15} ,
}

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
