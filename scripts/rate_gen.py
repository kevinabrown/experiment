#!/usr/bin/env python3
'''
    This scripts writes the period.file with flow rate adjustments
    
    This script converts the BW demands and inflection points
    into the format required for CODES simulations"

    To set the injection rate in CODES, you set the message size and 
    the delay between successive messages.
'''

import sys
import json
import argparse
from pprint import pprint

parser = argparse.ArgumentParser(description='Generate CODES flow configs for ModSim25 experiments.')
parser.add_argument('flows_file', help='The path to the flow rate information JSON-formatted file.')
parser.add_argument('--codes_flows_file', help='The path to the CODES config file to create', default='../multiflow/period.file')

# Parse arguments
args = parser.parse_args()
flowsfile = args.flows_file
codesflowsfile = args.codes_flows_file

# Open and read the JSON file
flowrates = {}
with open(flowsfile, 'r') as file:
    flowrates = json.load(file)

pprint(flowrates)

# Set base rate for 25GB bandwidth
message_size = 64
bw = 25*(1024*1024*1024)/(1000*1000*1000)
base_rate = message_size/bw


# Reshape schedules to isolate individual flows
flows = {0: [], 1: [], 2:[] }
for key in flowrates.keys():
    for k, v in flowrates[key].items():
        k = int(k)
        key = int(key)
        if v == 0:
            v = 0.1
        tmp = (v/25)*100
        myrate = base_rate * (100/tmp)
        flows[k].append((key, round(myrate, 6)))

pprint(flows)

# Create/overwrite rate file and use it as stdout
rate_file = open('../multiflow/period.file', 'w')
sys.stdout = rate_file

# Set and write injection delays for given rate changes
for flow in [0, 1, 2]:
    print(len(flows[flow]), end=' ')
    for i, rate in flows[flow]:
        print(f'{i*1000}:{rate}', end=' ')
    print()

# Write entry for allreduce SWM
print(0)
